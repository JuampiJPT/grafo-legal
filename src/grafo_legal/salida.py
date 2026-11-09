"""Salida estandar de cualquier parser: una tabla de relaciones entre normas.

Todo parser (reglas, LLM, hibrido) escribe este mismo formato, y el grafo se arma solo a partir
de el. Asi agregar un parser o una fuente nueva no cambia el esquema del grafo (bitacora B41).

Una fila es una relacion: un articulo de la norma origen hace algo (TIPO) sobre una norma
destino o sobre uno de sus articulos. La clave de la relacion es
(fuente, id_articulo_origen, tipo, id_norma_destino, articulo_destino).
"""

from __future__ import annotations

TIPOS = ("SUSTITUYE", "INCORPORA", "DEROGA", "REGLAMENTA", "MODIFICA", "CITA")

COLUMNAS = {
    "fuente": "parser que produjo la relacion (reglas_v2, llm, hibrido...)",
    "id_norma_origen": "norma que contiene el texto",
    "norma_origen": "etiqueta de la norma origen (Ley 27802)",
    "id_articulo_origen": "segmento de origen: id_norma#orden (el 0 es el encabezado)",
    "articulo_origen": "numero del articulo de origen ('0' = encabezado)",
    "parte_origen": "visto | considerando | articulado | anexo | notas",
    "tipo": "SUSTITUYE | INCORPORA | DEROGA | REGLAMENTA | MODIFICA | CITA",
    "id_norma_destino": "norma sobre la que recae la relacion",
    "norma_destino": "etiqueta de la norma destino",
    "articulo_destino": "numero del articulo destino; vacio si la relacion es con la norma entera",
    "verbo": "verbo del texto que determino el tipo (vacio en CITA)",
    "metodo": "como se detecto la mencion: regex_numero | alias | llm",
    "confianza": "probabilidad que da el parser, si la da (vacio en las reglas)",
    "n_menciones": "menciones del texto que sustentan la relacion",
    "inicio": "offset de la primera mencion en el texto limpio de la norma origen",
    "fin": "fin de esa mencion",
    "fragmento": "texto alrededor de la mencion (evidencia)",
}

CLAVE = ["fuente", "id_articulo_origen", "tipo", "id_norma_destino", "articulo_destino"]


def validar(df) -> list[str]:
    """Devuelve los problemas de una tabla de relaciones (lista vacia si cumple el formato)."""
    errores = []
    faltan = [c for c in COLUMNAS if c not in df.columns]
    if faltan:
        errores.append(f"faltan columnas: {faltan}")
        return errores
    malos = set(df.tipo) - set(TIPOS)
    if malos:
        errores.append(f"tipos desconocidos: {sorted(malos)}")
    dup = df.duplicated(CLAVE).sum()
    if dup:
        errores.append(f"{dup} relaciones repetidas para la misma clave")
    origen = df.id_articulo_origen.astype(str).str.split("#").str[0]
    if (origen != df.id_norma_origen.astype(str)).any():
        errores.append("id_articulo_origen no pertenece a id_norma_origen")
    return errores
