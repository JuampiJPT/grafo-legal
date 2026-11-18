"""Parser 3: híbrido en cascada (reglas que filtran + LLM que decide la zona gris).

Las reglas y el LLM no se corren por separado para después combinar sus salidas: es un solo
parser en el que cada uno hace la parte que mejor hace.

  1. ESTRUCTURA Y CANDIDATOS (determinista, igual que las reglas v3). El adaptador arma el árbol
     de la norma (VISTO, CONSIDERANDO, articulado, anexos, notas), el detector encuentra cada
     mención a otra norma y el catálogo la resuelve a una norma concreta (mundo cerrado, año
     escrito como fecha). Cada par (norma origen, norma destino) es un CANDIDATO, con todas sus
     menciones como evidencia. El LLM nunca inventa destinos ni números: solo juzga candidatos
     que el texto nombra y el catálogo resolvió.
  2. FILTRO POR REGLAS. Cada candidato cae en una de tres zonas:
       - DESCARTE: todas sus menciones son posteriores al origen (una norma no modifica a otra
         que todavía no existe) o están solo en anexos o notas de InfoLEG.
       - SEGURO: alguna mención está en el articulado, en una oración con verbo modificatorio y no
         es una cita de procedencia ("Sustitúyese el artículo 80 de la Ley 20.744"). En dev, el 91 %
         de estos pares está en InfoLEG.
       - ZONA GRIS: todo lo demás (VISTO, CONSIDERANDO, articulado sin verbo, nombre propio,
         procedencia). Ahí las reglas aciertan entre el 15 % y el 90 % según el caso: es lo que
         solo se decide leyendo la oración.
  3. JUICIO DEL LLM. Por cada norma origen, el LLM recibe sus candidatos (seguros y grises) con
     los fragmentos de texto donde se nombra cada destino (la mención marcada entre ⟦ ⟧) y
     responde, para cada uno: si hay relación, el tipo, el artículo destino y una cita textual.
  4. DECISIÓN. Seguro: se acepta (el LLM solo pone el tipo). Gris: decide el LLM. La política se
     eligió en dev (script 20).
  5. VERIFICACIÓN. La cita del LLM se busca en los fragmentos; si no está, el juicio no cuenta
     (el candidato gris se descarta y el seguro conserva el tipo de las reglas).

Mismo contrato que los otros parsers: devuelve relaciones en la salida estándar (salida.py), con
fuente = "hibrido", y cada relación queda trazable al fragmento de su evidencia.
"""

from __future__ import annotations

import json
import re

import pandas as pd

from ..salida import TIPOS
from .llm import ubicar

# v1 (descartado en dev): criterio estricto; el LLM rechazaba la mayoria de los pares de InfoLEG
# de la zona gris y en 199 respuestas escribio codigo (.replace(...)) dentro del JSON.
# v2: criterio amplio de InfoLEG, probabilidad para elegir el umbral en dev, la cita puede llevar ⟦ ⟧.
VERSION_PROMPT = "hibrido-v2-2026-11-18"
MAX_CANDIDATOS_POR_PEDIDO = 12
MAX_FRAGMENTOS = 3          # fragmentos por candidato (los más informativos primero)
VENTANA_ANTES, VENTANA_DESPUES = 450, 250

SISTEMA = """Sos un analista de técnica legislativa argentina y trabajás con la base InfoLEG.

Te doy una norma ORIGEN (ley o decreto) y una lista de CANDIDATOS: otras normas que el texto de la \
norma origen nombra. Para cada candidato ves uno o más fragmentos del texto de la norma origen, con \
la mención del candidato marcada entre ⟦ y ⟧, y la parte de la norma donde está (VISTO, CONSIDERANDO, \
ARTICULADO).

Para cada candidato estimá si InfoLEG registra que la norma origen "modifica o complementa" a esa \
norma. InfoLEG usa un criterio AMPLIO:
- Hay vínculo cuando la norma origen la modifica, sustituye o le incorpora texto, la deroga (total o \
parcialmente), la reglamenta, la prorroga, suspende o exceptúa, aprueba su texto ordenado, o la \
complementa. Complementar es amplio: alcanza con que la norma origen se apoye en el régimen de esa \
norma para regular algo (lo aplica, lo extiende a nuevos casos, fija montos, plazos o condiciones \
dentro de él, lo usa para definir a quiénes alcanza o qué se paga, crea algo en su marco o se dicta \
para ejecutarla o reglamentar un régimen que depende de ella).
- Las leyes y decretos que un decreto cita en el VISTO como base normativa de la medida están \
vinculados la mayoría de las veces (alrededor del 80 %). Las normas citadas SOLO en el CONSIDERANDO \
lo están pocas veces (alrededor del 25 %), salvo que la medida recaiga sobre ellas.
- No hay vínculo cuando la mención es incidental: un dato histórico, una norma nombrada al pasar en \
una lista o como ejemplo, la norma que solo da la facultad general de dictar la medida (salvo que se \
la modifique), o una cita que solo dice de dónde proviene un texto ("t.o. por Decreto ...", \
"sustituido por el artículo 2 del Decreto ...").

Tipo del vínculo (si lo hay):
- SUSTITUYE: reemplaza el texto de una norma o artículo.
- INCORPORA: agrega texto nuevo a otra norma.
- DEROGA: deja sin efecto una norma o artículo.
- REGLAMENTA: la reglamenta.
- MODIFICA: cualquier otro efecto modificatorio o complementario.

Respondé SOLO con un JSON válido (sin código, sin texto antes ni después):
{"candidatos": [{"id": "C1", "probabilidad": 0.85, "relacion": true, "tipo": "SUSTITUYE", \
"articulo_destino": "80", "cita": "...", "motivo": "..."}]}
- Una entrada por cada candidato de la lista, en el mismo orden.
- "probabilidad": tu estimación, entre 0 y 1, de que InfoLEG registre el vínculo.
- "relacion": true si la probabilidad es 0,5 o más.
- "articulo_destino": número del artículo del candidato sobre el que recae el vínculo ("80", \
"92 bis"), o null si recae sobre la norma entera o no hay vínculo.
- "cita": copia textual y corta (de 5 a 120 caracteres) de uno de los fragmentos, la que mejor \
muestra el vínculo o la mención. Puede incluir los signos ⟦ ⟧ tal como aparecen.
- "motivo": una frase corta que explique la decisión."""


# --------------------------------------------------------------------------------------------
# Pasos 1 y 2: candidatos y zonas
# --------------------------------------------------------------------------------------------
def candidatos(ev: pd.DataFrame) -> pd.DataFrame:
    """Una fila por par (origen, destino) con su zona: descarte, seguro o gris.

    ev: evidencias de las reglas v3 (una fila por mención, con parte, zona, verbo, procedencia y
    condición temporal ya calculadas)."""
    ev = ev.copy()
    ev["_tok"] = ev.temporal_ok.astype(str) == "True"
    ev["_proc"] = ev.procedencia.astype(str) == "True"
    ev["_verbo"] = ev.verbo_oracion.astype(str) != ""
    filas = []
    for (o, d), x in ev.groupby(["id_origen", "id_destino"], sort=True):
        y = x[x._tok]
        if y.empty:
            zona, motivo = "descarte", "posterior_al_origen"
        elif y.zona.isin(["anexo", "notas"]).all():
            zona, motivo = "descarte", "solo_anexo_o_notas"
        elif ((y.zona == "articulado") & y._verbo & ~y._proc).any():
            zona, motivo = "seguro", "articulado_con_verbo"
        else:
            partes = sorted(set(y[~y.zona.isin(["anexo", "notas"])].parte))
            zona, motivo = "gris", "+".join(partes)
        # opinion previa de las reglas: ¿la regla F3 (v3) acepta el par?
        f3 = bool((y.empty is False) and (~y._proc & (
            (y.parte == "visto")
            | ((y.zona == "articulado") & (y.metodo == "regex_numero") & ((y.tipo_origen != "decreto") | y._verbo))
            | ((y.zona == "articulado") & (y.metodo == "alias") & y._verbo))).any())
        filas.append({"id_origen": o, "id_destino": d, "zona": zona, "motivo_zona": motivo,
                      "pasa_F3": f3, "n_menciones": len(x)})
    return pd.DataFrame(filas)


# --------------------------------------------------------------------------------------------
# Paso 3: el pedido al LLM
# --------------------------------------------------------------------------------------------
def fragmentos(ev_par: pd.DataFrame, texto: str) -> list[dict]:
    """Fragmentos de evidencia de un candidato: articulado primero, después VISTO y CONSIDERANDO;
    dentro de cada parte, las menciones con verbo primero."""
    x = ev_par[(ev_par.temporal_ok.astype(str) == "True") & ~ev_par.zona.isin(["anexo", "notas"])]
    if x.empty:
        x = ev_par
    orden_parte = {"articulado": 0, "visto": 1, "considerando": 2}
    x = x.assign(_p=x.parte.map(orden_parte).fillna(3), _v=(x.verbo_oracion.astype(str) == "").astype(int))
    x = x.sort_values(["_p", "_v", "inicio"])
    out, usados = [], []
    for r in x.itertuples(index=False):
        ini_sup = max(0, int(r.fin) - len(r.superficie))
        if any(abs(ini_sup - u) < VENTANA_ANTES for u in usados):   # misma zona del texto
            continue
        a, b = max(0, ini_sup - VENTANA_ANTES), min(len(texto), int(r.fin) + VENTANA_DESPUES)
        frag = (texto[a:ini_sup] + "⟦" + texto[ini_sup:int(r.fin)] + "⟧" + texto[int(r.fin):b])
        frag = re.sub(r"\s+", " ", frag).strip()
        out.append({"parte": str(r.parte).upper(), "articulo": str(r.articulo), "texto": frag,
                    "inicio": ini_sup, "fin": int(r.fin), "evidencia": r})
        usados.append(ini_sup)
        if len(out) == MAX_FRAGMENTOS:
            break
    return out


def mensaje(origen: str, titulo: str, cands: list[dict]) -> str:
    """cands: [{"id": "C1", "destino": "Ley 20744", "titulo": ..., "fragmentos": [...]}]"""
    partes = [f"NORMA ORIGEN: {origen} — {titulo}", "", "CANDIDATOS:"]
    for c in cands:
        partes.append(f"\n[{c['id']}] {c['destino']} — {c['titulo']}")
        for i, f in enumerate(c["fragmentos"], 1):
            art = "" if f["articulo"] in ("", "0") else f", artículo {f['articulo']}"
            partes.append(f"  ({i}) {f['parte']}{art}: «{f['texto']}»")
    return "\n".join(partes)


def leer(texto: str) -> dict[str, dict]:
    """Respuesta del LLM -> {id_candidato: juicio}. Tolera ```json``` alrededor."""
    # el LLM a veces escribe codigo dentro del JSON ("...".replace("⟦","")): se limpia antes
    texto = re.sub(r'\.replace\(\s*"[^"]*"\s*,\s*"[^"]*"\s*\)', "", texto)
    m = re.search(r"\{.*\}", texto, re.S)
    if not m:
        return {}
    try:
        datos = json.loads(m.group(0))
    except json.JSONDecodeError:
        return {}
    out = {}
    for c in datos.get("candidatos", []) if isinstance(datos, dict) else []:
        if isinstance(c, dict) and c.get("id"):
            out[str(c["id"])] = c
    return out


# --------------------------------------------------------------------------------------------
# Pasos 4 y 5: verificación y decisión
# --------------------------------------------------------------------------------------------
def verificar(juicio: dict, frags: list[dict]) -> tuple[bool, dict | None]:
    """¿La cita del LLM está en algún fragmento? Devuelve (verificada, fragmento donde está)."""
    cita = str(juicio.get("cita") or "").replace("⟦", "").replace("⟧", "")
    for f in frags:
        limpio = f["texto"].replace("⟦", "").replace("⟧", "")
        if ubicar(cita, limpio) >= 0:
            return True, f
    return False, None


def probabilidad(juicio: dict | None) -> float | None:
    try:
        return float(juicio.get("probabilidad")) if juicio else None
    except (TypeError, ValueError):
        return None


def decidir(zona: str, juicio: dict | None, verificada: bool, politica: str, umbral: float = 0.5,
            pasa_f3: bool = False, umbral_bajo: float = 0.15) -> bool:
    """¿Se acepta el candidato?

    politicas:
      cascada      seguro -> sí; gris -> sí si la probabilidad del LLM >= umbral (cita verificada)
      llm_veta     como cascada, pero el LLM también puede rechazar un seguro
      solo_reglas  seguro -> sí; gris -> no (control: equivale a no usar el LLM en la zona gris)
      previa       seguro -> sí; gris -> la regla F3 da la opinion previa y el LLM la corrige
                   con confianza: un par que F3 acepta se descarta solo si el LLM le da menos de
                   umbral_bajo; un par que F3 rechaza se acepta si el LLM le da umbral o mas
    """
    if zona == "descarte":
        return False
    p = probabilidad(juicio)
    dice_si = bool(juicio and verificada and (p >= umbral if p is not None else juicio.get("relacion") is True))
    if zona == "seguro":
        if politica == "llm_veta" and juicio is not None and verificada and not dice_si:
            return False
        return True
    if politica == "previa":
        if not (juicio and verificada and p is not None):
            return pasa_f3                     # sin juicio verificado, queda la regla
        return p >= umbral_bajo if pasa_f3 else p >= umbral
    return dice_si if politica in ("cascada", "llm_veta") else False


def tipo_final(juicio: dict | None, verificada: bool, tipo_reglas: str) -> tuple[str, str]:
    """Tipo de la relación aceptada: el del LLM si su juicio está verificado, si no el de las
    reglas. Devuelve (tipo, de_donde)."""
    if juicio and verificada:
        t = str(juicio.get("tipo") or "").upper().strip()
        if t in TIPOS and t != "CITA":
            return t, "llm"
    return (tipo_reglas or "MODIFICA"), "reglas"
