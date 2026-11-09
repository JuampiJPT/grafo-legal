"""Parser 1, version 2 de las reglas (diseñada solo sobre el dev del corpus unico, 09/11/2026).

Comparte la deteccion de menciones y la normalizacion con v1 (reglas.py, que queda congelado).
Cambios respecto de v1, cada uno motivado por los errores de dev (bitacora B36):

  1. Parte del encabezado. Una mencion en el encabezado se marca como "visto" o "considerando".
     En dev, los pares citados en el VISTO estan en el gold el 80 % de las veces; los citados
     solo en el CONSIDERANDO, el 24 %.
  2. Citas de procedencia. "Ley 20.744 (t.o. por Decreto 390/76)" o "articulo 2 (sustituido por
     el articulo 2 del Decreto 1278/00)" nombran la norma que dio origen al texto, no la que se
     modifica ahora. Esas menciones se descartan. En dev son 55, 29 al Decreto 390/76. Solo
     13 son de pares del gold: InfoLEG a veces vincula el decreto del t.o. cuando se modifica la LCT.
  3. Verbos. Los adjetivos "complementarias" y "reglamentarios" (de "sus normas complementarias"
     o "sus decretos reglamentarios") ya no cuentan como verbo modificatorio.
  4. Regla de par (configuracion F): se predice el par si hay una mencion, no posterior al origen
     y que no sea de procedencia, que cumpla alguna de:
       a) esta en el VISTO;
       b) esta en el articulado, con numero, y el origen es una ley o la oracion tiene un verbo.
     Un decreto que nombra una norma en el articulado sin verbo suele remitir a ella: en dev,
     de los pares de un decreto que solo aparecen asi, el 19 % esta en el gold.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

from ..catalogo import Catalogo
from ..fuentes.infoleg import cargar
from .menciones import detectar, detectar_alias
from .reglas import VERBOS, _oracion

_ADJETIVOS = re.compile(r"complement(?:aria|arias|ario|arios)\b|reglamentari[oa]s?\b", re.I)
_CONSIDERANDO = re.compile(r"\bconsiderando\b", re.I)
# lo que precede a una cita de procedencia, pegado a la mencion
_PROCEDENCIA = re.compile(
    r"(?:(?:t\.\s*o\.?|texto\s+ordenado)(?:\s*\d{4})?(?:\s+(?:por|seg[uú]n))?(?:\s+(?:el|la))?"
    r"|(?:modificad|sustituid|incorporad)[oa]s?\s+por\s+el\s+art[ií]culo\s+[\dº°]+(?:\s+del?)?(?:\s+(?:la|el))?)$",
    re.I)


def verbo_real(texto: str) -> str:
    """Primer verbo modificatorio que no sea uno de los adjetivos de _ADJETIVOS ("" si no hay)."""
    for m in VERBOS.finditer(texto):
        if not _ADJETIVOS.match(m.group(0)):
            return m.group(0)
    return ""


@dataclass
class EvidenciaV2:
    id_origen: int
    id_destino: int
    norma_destino: str
    tipo_origen: str       # ley | decreto | decreto/ley
    articulo: str
    zona: str
    parte: str             # visto | considerando para el encabezado; la zona en los demas casos
    inicio: int
    fin: int
    superficie: str
    metodo: str            # regex_numero | alias
    verbo_articulo: str
    verbo_oracion: str
    temporal_ok: bool
    procedencia: bool      # cita de procedencia (t.o., "sustituido por ..."): no cuenta
    fragmento: str


def extraer(id_origen: int, html_dir: Path, cat: Catalogo) -> list[EvidenciaV2] | None:
    doc = cargar(id_origen, html_dir)
    if doc is None:
        return None
    texto, arts = doc
    origen = cat.normas.get(id_origen)
    out: list[EvidenciaV2] = []
    for art in arts:
        bruto = [(cat.resolver(m.tipo, m.numero, m.anio), m.inicio, m.fin, m.superficie, "regex_numero")
                 for m in detectar(art.texto)]
        bruto += [(cat.normas.get(i), a, b, s, "alias") for i, a, b, s in detectar_alias(art.texto)]
        v_art = verbo_real(art.texto)
        cons = _CONSIDERANDO.search(art.texto) if art.zona == "encabezado" else None
        for norma, a, b, sup, metodo in bruto:
            if norma is None or norma.id == id_origen:
                continue
            oa, ob = _oracion(art.texto, a, b)
            ini_sup = max(0, b - len(sup))
            parte = art.zona
            if art.zona == "encabezado":
                parte = "considerando" if cons and ini_sup >= cons.start() else "visto"
            temporal = not (origen and norma.fecha and origen.fecha and norma.fecha > origen.fecha)
            previo = art.texto[max(0, ini_sup - 80):ini_sup].rstrip()
            out.append(EvidenciaV2(
                id_origen, norma.id, norma.etiqueta, origen.tipo if origen else "", art.numero, art.zona, parte,
                art.inicio + a, art.inicio + b, sup, metodo, v_art, verbo_real(art.texto[oa:ob]), temporal,
                bool(_PROCEDENCIA.search(previo)),
                re.sub(r"\s+", " ", art.texto[max(0, a - 150): b + 150]).strip()))
    return out


def _cuenta(e) -> bool:
    return e.temporal_ok and not e.procedencia


CONFIGS = {
    # las de v1, recalculadas con los cambios 2 y 3, para comparar sobre la misma salida
    "A_todas_las_menciones": lambda e: _cuenta(e),
    "C_articulado_temporal": lambda e: _cuenta(e) and e.zona == "articulado",
    "F_visto_o_articulado_con_verbo_o_ley": lambda e: _cuenta(e) and (
        e.parte == "visto"
        or (e.zona == "articulado" and e.metodo == "regex_numero"
            and (e.tipo_origen != "decreto" or bool(e.verbo_oracion)))),
    # ablacion de F: sin cada una de sus dos condiciones
    "F_sin_visto": lambda e: _cuenta(e) and e.zona == "articulado" and e.metodo == "regex_numero"
        and (e.tipo_origen != "decreto" or bool(e.verbo_oracion)),
    "F_sin_condicion_de_decreto": lambda e: _cuenta(e) and (
        e.parte == "visto" or (e.zona == "articulado" and e.metodo == "regex_numero")),
}


def a_dict(e: EvidenciaV2) -> dict:
    return asdict(e)
