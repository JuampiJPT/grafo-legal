"""Parser 2: extraccion de relaciones con un LLM (modelo de lenguaje grande).

Mismo contrato que el parser de reglas: recibe los segmentos del adaptador (encabezado y
articulos de una norma) y devuelve relaciones en la salida estandar (salida.py). Lo unico que
cambia es QUIEN lee el texto: en vez de expresiones regulares, un LLM.

Como funciona, paso a paso:

  1. PREFILTRO (barato, sin LLM). Solo se mandan los segmentos del encabezado y del articulado
     que contienen alguna palabra que pueda introducir una norma ("ley", "decreto", "codigo",
     "regimen"...). Un articulo que no nombra ninguna norma no puede tener una relacion con otra.
     Las notas de InfoLEG y los anexos no se mandan, igual que en las reglas.
  2. LOTES. Los segmentos de una norma se agrupan en lotes de hasta ~12 mil caracteres. Cada
     segmento va con un identificador ([S12] = segmento de orden 12) para que el LLM diga de que
     articulo sale cada relacion.
  3. PROMPT. El LLM recibe la definicion de los seis tipos de relacion (SUSTITUYE, INCORPORA,
     DEROGA, REGLAMENTA, MODIFICA, CITA) y devuelve un JSON con una entrada por relacion: de que
     segmento sale, la cita textual exacta, tipo y numero de la norma destino, articulo destino,
     tipo de relacion y verbo. Temperatura 0.
  4. VERIFICACION (anti-alucinacion). La cita que devuelve el LLM se busca en el texto del
     segmento. Si aparece, se guardan sus offsets: la relacion queda trazable a la evidencia,
     igual que en las reglas. Si no aparece, la relacion se descarta y se cuenta (tasa de citas
     inventadas).
  5. NORMALIZACION. El tipo, numero y ano que devolvio el LLM se resuelven contra el MISMO
     catalogo que usan las reglas (catalogo.py, mundo cerrado). Asi la comparacion entre
     parsers mide solo la lectura del texto, no la normalizacion.
  6. CACHE. Cada respuesta se guarda en disco con la huella SHA-256 del pedido (modelo + prompt
     + texto). Volver a correr no vuelve a llamar a la API y da exactamente lo mismo: el
     experimento es reproducible sin la clave y sin costo.

El LLM nunca ve el gold de InfoLEG.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path

from ..catalogo import Catalogo
from ..salida import TIPOS

MODELO_POR_DEFECTO = "claude-sonnet-5-5"
MAX_CHARS_LOTE = 12000
VERSION_PROMPT = "v1-2026-11-16"

# Palabras que pueden introducir una referencia normativa (paso 1, prefiltro)
_PREFILTRO = re.compile(r"\b(?:ley|leyes|decreto|decretos|dnu|c[oó]digo|r[eé]gimen|estatuto)\b", re.I)
_CONSIDERANDO = re.compile(r"\bconsiderando\b", re.I)

SISTEMA = """Sos un analista de técnica legislativa argentina. Leés fragmentos de una norma (ley o decreto) \
y extraés las referencias que hace a OTRAS normas (leyes, decretos, decretos-leyes, decretos de \
necesidad y urgencia, códigos).

Para cada referencia devolvés el TIPO de relación que establece el texto:
- SUSTITUYE: reemplaza el texto de una norma o artículo ("Sustitúyese el artículo 80 de la Ley 20.744 \
por el siguiente", "quedará redactado de la siguiente manera").
- INCORPORA: agrega texto nuevo a otra norma ("Incorpórase como artículo 92 bis de la Ley ...", "Agrégase").
- DEROGA: deja sin efecto una norma o artículo ("Derógase", "Déjase sin efecto", "Abrógase", "Suprímese").
- REGLAMENTA: reglamenta otra norma ("Apruébase la reglamentación de la Ley ...", "Reglaméntase").
- MODIFICA: cualquier otro efecto modificatorio explícito (modifica, prorroga, suspende, amplía, \
exceptúa, observa, promulga, ratifica, aprueba el texto ordenado).
- CITA: la norma solo se menciona, como fundamento o remisión, sin modificarla ("conforme la Ley ...", \
"en los términos del Decreto ..."). Las menciones del VISTO y del CONSIDERANDO son CITA salvo que el \
propio texto diga que se la modifica. Una mención que solo indica de dónde proviene un texto \
("t.o. por Decreto 390/76", "sustituido por el artículo 2 del Decreto 1278/00") es CITA.

Reglas:
- Una entrada por cada combinación distinta de (segmento, norma destino, artículo destino, tipo).
- No incluyas la propia norma que estás leyendo ("la presente ley", "este decreto").
- "cita" debe ser una copia EXACTA y corta (de 3 a 80 caracteres) del texto donde se nombra la norma \
destino, tal como aparece en el segmento, por ejemplo "Ley N° 20.744" o "Decreto Nº 1694/06".
- Si el texto nombra la norma solo por su nombre ("Ley de Contrato de Trabajo") y sabés su número, \
completalo; si no lo sabés, poné numero null.
- "articulo_destino": número del artículo de la norma destino sobre el que recae la relación \
("80", "92 bis"), o null si la relación es con la norma entera.
- "anio": año de la norma destino si el texto lo da (por ejemplo 2006 para "1694/06"), si no null.
- "verbo": el verbo del texto que determina el tipo, copiado tal cual ("Sustitúyese"); vacío en CITA.

Respondé SOLO con un JSON válido, sin texto antes ni después, con esta forma:
{"relaciones": [{"segmento": "S12", "cita": "...", "tipo_norma": "ley|decreto|decreto/ley", \
"numero": "20744", "anio": null, "articulo_destino": "80", "tipo": "SUSTITUYE", "verbo": "Sustitúyese"}]}
Si no hay ninguna referencia, respondé {"relaciones": []}."""


@dataclass
class Segmento:
    id_norma: int
    orden: int
    articulo: str
    zona: str
    inicio: int           # offset del segmento en el texto limpio de la norma
    texto: str


# --------------------------------------------------------------------------------------------
# Pasos 1 y 2: prefiltro y lotes
# --------------------------------------------------------------------------------------------
def seleccionar(segmentos: list[Segmento]) -> list[Segmento]:
    return [s for s in segmentos if s.zona in ("encabezado", "articulado") and _PREFILTRO.search(s.texto)]


def lotes(segmentos: list[Segmento], max_chars: int = MAX_CHARS_LOTE) -> list[list[tuple[Segmento, int, str]]]:
    """Agrupa segmentos en lotes. Un segmento mas largo que max_chars se parte en pedazos;
    cada pedazo recuerda su desplazamiento dentro del segmento (para los offsets)."""
    piezas = []
    for s in segmentos:
        for i in range(0, max(len(s.texto), 1), max_chars):
            piezas.append((s, i, s.texto[i:i + max_chars]))
    out, actual, largo = [], [], 0
    for p in piezas:
        if actual and largo + len(p[2]) > max_chars:
            out.append(actual)
            actual, largo = [], 0
        actual.append(p)
        largo += len(p[2])
    if actual:
        out.append(actual)
    return out


def mensaje_usuario(norma: str, lote: list[tuple[Segmento, int, str]]) -> str:
    partes = [f"Norma que se está leyendo: {norma}.", "Segmentos:"]
    for s, _, txt in lote:
        etiqueta = "ENCABEZADO (VISTO y CONSIDERANDO)" if s.zona == "encabezado" else f"Artículo {s.articulo}"
        partes.append(f"[S{s.orden}] {etiqueta}\n{txt}")
    return "\n\n".join(partes)


# --------------------------------------------------------------------------------------------
# Paso 3 y 6: llamada al LLM con cache
# --------------------------------------------------------------------------------------------
class ClienteLLM:
    """Envuelve la API de Anthropic con una cache en disco. Sin clave, solo lee la cache."""

    def __init__(self, cache_dir: Path, modelo: str = MODELO_POR_DEFECTO, clave: str | None = None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.modelo = modelo
        self.clave = clave or os.environ.get("ANTHROPIC_API_KEY")
        self._cliente = None
        self.uso = {"llamadas_api": 0, "desde_cache": 0, "tokens_entrada": 0, "tokens_salida": 0}

    def _huella(self, usuario: str) -> str:
        return hashlib.sha256(f"{self.modelo}\n{VERSION_PROMPT}\n{SISTEMA}\n{usuario}".encode()).hexdigest()

    def pedir(self, usuario: str) -> dict:
        ruta = self.cache_dir / f"{self._huella(usuario)}.json"
        if ruta.exists():
            self.uso["desde_cache"] += 1
            return json.loads(ruta.read_text(encoding="utf-8"))
        if not self.clave:
            raise RuntimeError("Falta ANTHROPIC_API_KEY y el pedido no esta en la cache")
        if self._cliente is None:
            import anthropic
            self._cliente = anthropic.Anthropic(api_key=self.clave)
        for intento in range(5):
            try:
                r = self._cliente.messages.create(
                    model=self.modelo, max_tokens=8000, temperature=0, system=SISTEMA,
                    messages=[{"role": "user", "content": usuario}])
                break
            except Exception:  # limites de uso o cortes de red: se reintenta con espera creciente
                if intento == 4:
                    raise
                time.sleep(5 * (intento + 1))
        texto = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
        reg = {"modelo": self.modelo, "version_prompt": VERSION_PROMPT, "respuesta": texto,
               "tokens_entrada": r.usage.input_tokens, "tokens_salida": r.usage.output_tokens,
               "stop_reason": r.stop_reason}
        tmp = ruta.with_suffix(".tmp")
        tmp.write_text(json.dumps(reg, ensure_ascii=False), encoding="utf-8")
        tmp.replace(ruta)
        self.uso["llamadas_api"] += 1
        self.uso["tokens_entrada"] += reg["tokens_entrada"]
        self.uso["tokens_salida"] += reg["tokens_salida"]
        return reg


def leer_json(texto: str) -> list[dict]:
    """Extrae la lista de relaciones del texto del LLM (tolera ```json ... ``` alrededor)."""
    m = re.search(r"\{.*\}", texto, re.S)
    if not m:
        return []
    try:
        datos = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    rel = datos.get("relaciones", []) if isinstance(datos, dict) else []
    return [r for r in rel if isinstance(r, dict)]


# --------------------------------------------------------------------------------------------
# Pasos 4 y 5: verificacion de la cita y normalizacion
# --------------------------------------------------------------------------------------------
def ubicar(cita: str, texto: str) -> int:
    """Offset de la cita dentro del texto del segmento, o -1. Tolera diferencias de espacios."""
    if not cita:
        return -1
    i = texto.find(cita)
    if i >= 0:
        return i
    patron = r"\s+".join(re.escape(p) for p in cita.split())
    m = re.search(patron, texto, re.I) if patron else None
    return m.start() if m else -1


def a_relaciones(id_norma: int, etiqueta: str, lote, crudas: list[dict], cat: Catalogo,
                 etiquetas: dict[int, str]) -> tuple[list[dict], dict]:
    """Convierte las entradas del LLM en filas de la salida estandar. Devuelve tambien conteos
    de lo descartado, para medir alucinaciones y referencias no resueltas."""
    por_id = {f"S{s.orden}": (s, desde, txt) for s, desde, txt in lote}
    conteo = {"crudas": len(crudas), "segmento_invalido": 0, "cita_no_encontrada": 0,
              "tipo_invalido": 0, "no_resuelta": 0, "autorreferencia": 0, "aceptadas": 0}
    filas = []
    for r in crudas:
        seg = por_id.get(str(r.get("segmento", "")).strip())
        if seg is None:
            conteo["segmento_invalido"] += 1
            continue
        s, desde, txt = seg
        cita = str(r.get("cita") or "")
        pos = ubicar(cita, txt)
        if pos < 0:
            conteo["cita_no_encontrada"] += 1
            continue
        tipo = str(r.get("tipo", "")).upper().strip()
        if tipo not in TIPOS:
            conteo["tipo_invalido"] += 1
            continue
        numero = r.get("numero")
        anio = r.get("anio")
        try:
            anio = int(anio) if anio not in (None, "") else None
        except (TypeError, ValueError):
            anio = None
        norma = cat.resolver(str(r.get("tipo_norma") or ""), str(numero), anio) if numero else None
        if norma is None:
            conteo["no_resuelta"] += 1
            continue
        if norma.id == id_norma:
            conteo["autorreferencia"] += 1
            continue
        inicio = s.inicio + desde + pos
        parte = s.zona
        if s.zona == "encabezado":
            c = _CONSIDERANDO.search(s.texto)
            parte = "considerando" if c and desde + pos >= c.start() else "visto"
        art_dest = r.get("articulo_destino")
        art_dest = "" if art_dest in (None, "", "null") else re.sub(r"\s+", " ", str(art_dest)).strip().lower()
        fragmento = re.sub(r"\s+", " ", txt[max(0, pos - 150): pos + len(cita) + 150]).strip()
        filas.append({
            "fuente": "llm", "id_norma_origen": id_norma, "norma_origen": etiqueta,
            "id_articulo_origen": f"{id_norma}#{s.orden}", "articulo_origen": s.articulo,
            "parte_origen": parte, "tipo": tipo, "id_norma_destino": norma.id,
            "norma_destino": etiquetas.get(norma.id, norma.etiqueta), "articulo_destino": art_dest,
            "verbo": "" if tipo == "CITA" else str(r.get("verbo") or ""), "metodo": "llm", "confianza": "",
            "n_menciones": 1, "inicio": inicio, "fin": inicio + len(cita), "fragmento": fragmento})
        conteo["aceptadas"] += 1
    return filas, conteo
