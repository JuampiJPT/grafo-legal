"""Parser 1: reglas (regex sobre la estructura de articulos).

Pipeline por norma:
  1. adaptador de la fuente -> texto plano + articulos con zona (encabezado/articulado/anexo/notas)
  2. deteccion de menciones (numero + alias) en cada articulo
  3. normalizacion contra el catalogo (mundo cerrado: solo normas del corpus)
  4. reglas de relacion: zona, verbo modificatorio y restriccion temporal
  5. salida: una evidencia por mencion, con articulo, offsets, fragmento, metodo y reglas cumplidas

La prediccion a nivel de par (origen -> destino) se arma agregando evidencias que cumplen la
configuracion elegida; asi la ablacion se calcula sobre la misma salida.

Relacion objetivo: la de la base complementaria de InfoLEG, que es amplia ("modifica o
complementa"): incluye sustituir, incorporar, derogar, reglamentar, promulgar, prorrogar, etc.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

from ..catalogo import Catalogo, sin_tildes
from ..fuentes.infoleg import cargar
from .menciones import detectar, detectar_alias

VERBOS = re.compile(
    r"\b(?:"
    r"modif[ií]c(?:a|an|ase|anse|ar|ado|ada|ados|adas)|modif[ií]qu(?:e|ese|ense)|"
    r"sustit[uú]y(?:e|en|ese|ense|ase|anse)|sustitu(?:ir|ido|ida|idos|idas)|"
    r"reempl[aá]z(?:a|an|ase|anse)|reempl[aá]c(?:e|ese|ense)|reemplaz(?:ar|ado|ada)|"
    r"incorp[oó]r(?:a|an|ase|anse|ese|ense)|incorpor(?:ar|ado|ada)|"
    r"agr[eé]g(?:a|an|ase|anse)|agr[eé]gu(?:e|ese|ense)|agreg(?:ar|ado|ada)|"
    r"der[oó]g(?:a|an|ase|anse)|der[oó]gu(?:e|ese|ense)|derog(?:ar|ado|ada|ados|adas)|abr[oó]g(?:ase|anse)|"
    r"supr[ií]m(?:e|en|ese|ense)|suprim(?:ir|ido|ida)|"
    r"d[eé]j(?:ase|anse)\s+sin\s+efecto|"
    r"pr[oó]rr[oó]g(?:a|ase|anse)|prorrog(?:ar|ado|ada)|"
    r"susp[eé]nd(?:e|ese|ense)|"
    r"reglam[eé]nt(?:a|ase|anse)|reglamentaci[oó]n|reglamentari[oa]s?|"
    r"prom[uú]lg(?:a|ase)|t[eé]ngase\s+por\s+ley|"
    r"obs[eé]rv(?:a|ase|anse)|"
    r"ratif[ií]c(?:a|ase|anse)|"
    r"complement(?:a|ase|anse|aria|arias|ario)|"
    r"texto\s+ordenado|"
    r"(?:quedar[aá]|quedan)\s+redactad[oa]s?|tendr[aá]\s+la\s+siguiente\s+redacci[oó]n|"
    r"exc[eé]pt[uú](?:a|ase|anse)|exim(?:e|ese)|"
    r"ampl[ií](?:a|ase|anse)|"
    r"sustituci[oó]n|modificaci[oó]n|derogaci[oó]n|incorporaci[oó]n"
    r")\b", re.I)

_ORACION = re.compile(r"[^.;\n]*(?:\.(?=\s|$)|;|\n|$)")


@dataclass
class Evidencia:
    id_origen: int
    id_destino: int
    norma_destino: str
    articulo: str
    zona: str
    inicio: int
    fin: int
    superficie: str
    metodo: str            # regex_numero | alias
    verbo_articulo: str    # primer verbo modificatorio en el articulo ("" si no hay)
    verbo_oracion: str     # verbo en la misma oracion que la mencion
    temporal_ok: bool      # el destino no es posterior al origen
    fragmento: str


def _oracion(texto: str, ini: int, fin: int) -> tuple[int, int]:
    a = max(texto.rfind(".", 0, ini), texto.rfind(";", 0, ini), texto.rfind("\n", 0, ini)) + 1
    cands = [i for i in (texto.find(". ", fin), texto.find(";", fin), texto.find("\n", fin)) if i != -1]
    b = min(cands) + 1 if cands else len(texto)
    return a, b


def extraer(id_origen: int, html_dir: Path, cat: Catalogo) -> list[Evidencia] | None:
    doc = cargar(id_origen, html_dir)
    if doc is None:
        return None
    texto, arts = doc
    origen = cat.normas.get(id_origen)
    out: list[Evidencia] = []
    for art in arts:
        bruto = [(cat.resolver(m.tipo, m.numero, m.anio), m.inicio, m.fin, m.superficie, "regex_numero")
                 for m in detectar(art.texto)]
        bruto += [(cat.normas.get(i), a, b, s, "alias") for i, a, b, s in detectar_alias(art.texto)]
        v_art = VERBOS.search(art.texto)
        for norma, a, b, sup, metodo in bruto:
            if norma is None or norma.id == id_origen:
                continue
            oa, ob = _oracion(art.texto, a, b)
            v_or = VERBOS.search(art.texto[oa:ob])
            temporal = not (origen and norma.fecha and origen.fecha and norma.fecha > origen.fecha)
            out.append(Evidencia(
                id_origen, norma.id, norma.etiqueta, art.numero, art.zona,
                art.inicio + a, art.inicio + b, sup, metodo,
                v_art.group(0) if v_art else "", v_or.group(0) if v_or else "", temporal,
                re.sub(r"\s+", " ", art.texto[max(0, a - 150): b + 150]).strip()))
    return out


# Configuraciones de la ablacion: cada una es un filtro sobre evidencias.
CONFIGS = {
    "A_todas_las_menciones": lambda e: True,
    "B_articulado": lambda e: e.zona == "articulado",
    "C_articulado_temporal": lambda e: e.zona == "articulado" and e.temporal_ok,
    "D_C_mas_verbo_en_articulo": lambda e: e.zona == "articulado" and e.temporal_ok and bool(e.verbo_articulo),
    "E_C_mas_verbo_en_oracion": lambda e: e.zona == "articulado" and e.temporal_ok and bool(e.verbo_oracion),
}


def a_dict(e: Evidencia) -> dict:
    return asdict(e)
