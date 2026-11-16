"""Parser 1, version 3 de las reglas (diseñada solo sobre dev, 16/11/2026, bitacora B52).

Corrige los fallos que encontro el analisis caso por caso de la v2 (B51,
results/errores_explicados/). La v2 queda congelada; v3 comparte con ella todo lo demas.

Cambios, cada uno con el fallo que corrige:

  1. Ano escrito como fecha (normalizacion). "Decreto N° 1694 del 22 de noviembre de 2006" no
     trae "/06", y como el corpus tiene dos decretos 1694 la mencion quedaba sin resolver; si
     tenia uno solo, se vinculaba a ese aunque fuera de otro ano. Ahora el detector lee el ano de
     la fecha que sigue a la mencion (menciones.detectar(..., anio_por_fecha=True)).
  2. Gazetteer (deteccion). Se agregan nombres que faltaban ("Ley de Ministerios", "L.C.T.") y
     se quitan los nombres de tributos sueltos ("impuesto a las ganancias", "impuesto al valor
     agregado"): nombran el impuesto, no la ley. Quedan las formas con "ley" ("Ley de Impuesto a
     las Ganancias", "Ley del Impuesto al Valor Agregado").
  3. "Valor Agregado" no es un verbo (extraccion y tipado). "Agregado" contaba como verbo de
     incorporacion cuando era parte del nombre del impuesto.
  4. Procedencia extendida (extraccion). Ademas de "t.o. por" y "sustituido por el articulo N
     del", se descartan "modificado por el Decreto", "reemplazado por el articulo N de la ley",
     "y ampliado y modificado por ley": indican de donde viene un texto, no que se lo modifique.
     "aprobado por" NO se agrega: en dev atrapaba citas reales de la LCT (B36).
  5. Alias con verbo en el articulado (extraccion). La regla F exigia numero en el articulado.
     Una ley que dice "Modificase la Ley de Impuesto a las Ganancias" sin numero tambien
     modifica: ahora cuenta si la oracion tiene un verbo modificatorio.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..catalogo import ALIAS, Catalogo
from ..fuentes.infoleg import cargar
from .menciones import detectar, detectar_alias
from .reglas import VERBOS, _oracion
from .reglas_v2 import _ADJETIVOS, _CONSIDERANDO, _PROCEDENCIA, EvidenciaV2, _cuenta

# 2. Gazetteer v3: sin nombres de tributos sueltos y con los nombres que faltaban
_TRIBUTOS_SUELTOS = {"impuesto a las ganancias", "impuesto al valor agregado"}
ALIAS_V3 = {i: [n for n in ns if n not in _TRIBUTOS_SUELTOS] for i, ns in ALIAS.items()}
ALIAS_V3[17699] = ALIAS_V3[17699] + ["ley del impuesto a las ganancias"]
ALIAS_V3[16092] = ALIAS_V3[16092] + ["ley del impuesto al valor agregado"]
ALIAS_V3[48853] = ["ley de ministerios"]                     # Ley 22.520
ALIAS_V3[25552] = ALIAS_V3[25552] + ["l.c.t."]               # Ley de Contrato de Trabajo

# 4. Procedencia v3: lo que precede pegado a la mencion
_PROCEDENCIA_V3 = re.compile(
    r"(?:(?:t\.\s*o\.?|texto\s+ordenado)(?:\s*\d{4})?(?:\s+(?:por|seg[uú]n))?(?:\s+(?:el|la))?"
    r"|(?:modificad|sustituid|incorporad|reemplazad)[oa]s?\s+por\s+el\s+art[ií]culo\s+[\dº°]+(?:\s+del?)?(?:\s+(?:la|el))?"
    # nuevo en v3: "modificado por el Decreto N°", "y ampliado y modificado por ley"
    r"|(?:modificad|sustituid|reemplazad|ampliad)[oa]s?\s+por(?:\s+(?:el|la))?)$",
    re.I)


# Cambios activos. Todos van en la v3; el script 19 los apaga de a uno para medir cuanto aporta
# cada uno (ablacion sobre dev).
CAMBIOS = {"fecha", "gazetteer", "valor_agregado", "procedencia", "alias_con_verbo"}


def verbo_real(texto: str) -> str:
    """Como en v2, y ademas 3: "agregado" de "Valor Agregado" no es un verbo."""
    for m in VERBOS.finditer(texto):
        if _ADJETIVOS.match(m.group(0)):
            continue
        if "valor_agregado" in CAMBIOS and m.group(0).lower().startswith("agregad") and re.search(r"valor\s*$", texto[:m.start()], re.I):
            continue
        return m.group(0)
    return ""


def extraer(id_origen: int, html_dir: Path, cat: Catalogo) -> list[EvidenciaV2] | None:
    """Igual que reglas_v2.extraer, con los cambios 1 a 4 (el 5 esta en CONFIGS)."""
    doc = cargar(id_origen, html_dir)
    if doc is None:
        return None
    texto, arts = doc
    origen = cat.normas.get(id_origen)
    out: list[EvidenciaV2] = []
    for art in arts:
        # cambio 1: el ano escrito como fecha completa las menciones sin "/ano"
        bruto = [(cat.resolver(m.tipo, m.numero, m.anio), m.inicio, m.fin, m.superficie, "regex_numero")
                 for m in detectar(art.texto, anio_por_fecha="fecha" in CAMBIOS)]
        # cambio 2: gazetteer v3
        bruto += [(cat.normas.get(i), a, b, s, "alias") for i, a, b, s in detectar_alias(art.texto, ALIAS_V3 if "gazetteer" in CAMBIOS else ALIAS)]
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
                bool((_PROCEDENCIA_V3 if "procedencia" in CAMBIOS else _PROCEDENCIA).search(previo)),  # cambio 4
                re.sub(r"\s+", " ", art.texto[max(0, a - 150): b + 150]).strip()))
    return out


CONFIGS = {
    # la regla F de v2 sobre las evidencias v3 (aisla los cambios 1 a 4)
    "F_v2_sobre_evidencias_v3": lambda e: _cuenta(e) and (
        e.parte == "visto"
        or (e.zona == "articulado" and e.metodo == "regex_numero"
            and (e.tipo_origen != "decreto" or bool(e.verbo_oracion)))),
    # F3 = F + cambio 5: en el articulado, un alias tambien cuenta si la oracion tiene verbo
    "F3_alias_con_verbo": lambda e: _cuenta(e) and (
        e.parte == "visto"
        or (e.zona == "articulado" and e.metodo == "regex_numero"
            and (e.tipo_origen != "decreto" or bool(e.verbo_oracion)))
        or ("alias_con_verbo" in CAMBIOS and e.zona == "articulado" and e.metodo == "alias"
            and bool(e.verbo_oracion))),
}


def a_dict(e: EvidenciaV2) -> dict:
    from dataclasses import asdict
    return asdict(e)
