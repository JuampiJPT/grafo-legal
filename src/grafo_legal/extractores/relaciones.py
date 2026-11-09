"""De las menciones del parser de reglas v2 a relaciones tipadas en la salida estandar.

Para cada mencion que no es de procedencia, ni posterior al origen, ni de las notas editoriales:
  - tipo: por el verbo de la oracion (Sustituyese -> SUSTITUYE, Derogase -> DEROGA, ...).
    Sin verbo, o en el VISTO / CONSIDERANDO, es una CITA.
  - articulo destino: el "articulo N de la" que precede a la mencion en la misma oracion
    ("Sustituyese el articulo 245 de la Ley 20.744"). Si hay varios ("articulos 232, 233 y 245"),
    una relacion por articulo; un rango corto ("43 a 65") se expande. Si no hay, la relacion es
    con la norma entera.
Las menciones que coinciden en la clave de la salida estandar se agrupan en una sola relacion.
"""

from __future__ import annotations

import re
import unicodedata

import pandas as pd

from ..salida import CLAVE, COLUMNAS

# orden importa: la primera raiz que aparece en el verbo decide el tipo
_RAICES = [
    ("sustitu", "SUSTITUYE"), ("reemplaz", "SUSTITUYE"), ("reemplac", "SUSTITUYE"),
    ("redactad", "SUSTITUYE"), ("redaccion", "SUSTITUYE"),
    ("incorpor", "INCORPORA"), ("agreg", "INCORPORA"),
    ("derog", "DEROGA"), ("abrog", "DEROGA"), ("sin efecto", "DEROGA"), ("suprim", "DEROGA"),
    ("reglament", "REGLAMENTA"),
]

_N = r"\d+\s*[°ºo]?(?:\s*(?:bis|ter|qu[aá]ter|quinquies))?"
_ART_LISTA = re.compile(
    rf"art[ií]culos?\s+(?:n[°º]\s*)?(?P<lista>{_N}(?:\s*(?:,|\by\b|\be\b|\ba\b|\bal\b)\s*{_N})*)", re.I)
# entre "articulo N" y la mencion: un tramo corto, sin otra norma ni fin de oracion
_PUENTE = re.compile(r"^[^.;:]{0,90}?\b(?:de\s+la|del|de)\s*$", re.I)
_OTRA_NORMA = re.compile(r"\b(?:ley|leyes|decreto|decretos|resoluci[oó]n|c[oó]digo|reglamento)\b", re.I)
_ITEM = re.compile(r"(\d+)\s*[°ºo]?(?:\s*(bis|ter|qu[aá]ter|quinquies))?", re.I)


def tipo_por_verbo(verbo: str) -> str:
    if not verbo:
        return "CITA"
    v = unicodedata.normalize("NFKD", verbo.lower()).encode("ascii", "ignore").decode()
    for raiz, tipo in _RAICES:
        if raiz in v:
            return tipo
    return "MODIFICA"     # prorroga, suspende, amplia, exime, ratifica, texto ordenado, modifica...


def articulos_destino(previo: str) -> list[str]:
    """Numeros de articulo que se refieren a la norma mencionada justo despues de `previo`."""
    m = None
    for m in _ART_LISTA.finditer(previo):
        pass
    if m is None:
        return []
    puente = previo[m.end():]
    if not _PUENTE.match(puente) or _OTRA_NORMA.search(puente):
        return []
    lista = m.group("lista")
    items = [(int(n), (s or "").lower().replace("á", "a")) for n, s in _ITEM.findall(lista)]
    nums = []
    rango = re.search(rf"({_N})\s*\b(?:a|al)\b\s*({_N})", lista, re.I)
    if rango and len(items) == 2 and not items[0][1] and not items[1][1] and 0 < items[1][0] - items[0][0] <= 40:
        nums = [str(i) for i in range(items[0][0], items[1][0] + 1)]
    else:
        nums = [f"{n} {s}".strip() for n, s in items]
    return list(dict.fromkeys(nums))


def desde_evidencias(ev: pd.DataFrame, textos: dict[int, str], articulos: pd.DataFrame,
                     etiquetas: dict[int, str], fuente: str = "reglas_v2") -> pd.DataFrame:
    """ev: evidencias.csv de reglas_v2. textos: texto limpio por norma. articulos: articulos.csv."""
    # las notas son anotaciones editoriales de la fuente (InfoLEG), no texto de la norma
    ev = ev[(ev.temporal_ok.astype(str) == "True") & (ev.procedencia.astype(str) != "True")
            & (ev.zona != "notas")].copy()
    art = articulos.sort_values(["id_norma", "inicio"])
    art = art.assign(id_articulo=art.id_norma.astype(str) + "#" + art.orden.astype(str))
    ev = pd.merge_asof(ev.sort_values("inicio"),
                       art[["id_norma", "inicio", "id_articulo"]].rename(columns={"id_norma": "id_origen"})
                       .sort_values("inicio"), on="inicio", by="id_origen", direction="backward")
    filas = []
    for r in ev.itertuples(index=False):
        texto = textos[r.id_origen]
        ini_sup = max(0, r.fin - len(r.superficie))
        en_texto = r.parte not in ("visto", "considerando")
        tipo = tipo_por_verbo(r.verbo_oracion) if en_texto else "CITA"
        # la oracion de la mencion empieza en el ultimo punto, punto y coma o salto de linea
        a = max(texto.rfind(". ", 0, ini_sup), texto.rfind(";", 0, ini_sup), texto.rfind("\n", 0, ini_sup)) + 1
        destinos = articulos_destino(texto[max(a, ini_sup - 200):ini_sup]) or [""]
        for art_dest in destinos:
            filas.append({
                "fuente": fuente, "id_norma_origen": r.id_origen, "norma_origen": etiquetas[r.id_origen],
                "id_articulo_origen": r.id_articulo, "articulo_origen": r.articulo, "parte_origen": r.parte,
                "tipo": tipo, "id_norma_destino": r.id_destino, "norma_destino": etiquetas[r.id_destino],
                "articulo_destino": art_dest, "verbo": r.verbo_oracion if tipo != "CITA" else "",
                "metodo": r.metodo, "confianza": "", "inicio": r.inicio, "fin": r.fin, "fragmento": r.fragmento,
            })
    df = pd.DataFrame(filas)
    # una relacion por clave: VISTO antes que CONSIDERANDO, numero antes que alias, primera mencion
    df["_p"] = (df.parte_origen != "visto").astype(int)
    df["_m"] = (df.metodo != "regex_numero").astype(int)
    df = df.sort_values(CLAVE + ["_p", "_m", "inicio"], kind="mergesort")
    n = df.groupby(CLAVE, sort=False).size().rename("n_menciones")
    df = df.drop_duplicates(CLAVE).drop(columns=["_p", "_m"]).join(n, on=CLAVE)
    return df[list(COLUMNAS)].sort_values(["id_norma_origen", "inicio", "id_norma_destino", "articulo_destino",
                                            "tipo"], kind="mergesort").reset_index(drop=True)
