"""Adaptador de InfoLEG: HTML de una norma -> texto plano segmentado en zonas y articulos.

Zonas:
  encabezado  : desde el inicio hasta el primer articulo (incluye VISTO / CONSIDERANDO).
  articulado  : articulos dispositivos de la norma.
  anexo       : desde la primera linea "ANEXO ..." posterior al articulado (textos ordenados,
                convenios, planillas). Sus articulos no son dispositivos de la norma que se lee.
  notas       : notas de InfoLEG al pie (ej. "Nota Infoleg: ..."), que NO son texto normativo.

El adaptador es lo unico especifico de la fuente: para otro digesto se escribe otro adaptador
que devuelva la misma estructura (lista de Articulo).
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

# --- Expresiones regulares del adaptador -------------------------------------------------
# _BLOQUE: etiquetas HTML que en pantalla cortan el renglon (<br>, <p>, <div>, <tr>, ...).
#          Se reemplazan por un salto de linea para no pegar dos parrafos en uno.
_BLOQUE = re.compile(r"(?i)<br\s*/?>|</?(?:p|div|h\d|tr|li|table|center|blockquote)\b[^>]*>")
# _ART: el comienzo de un articulo, al principio de un renglon. Reconoce las variantes que
#       aparecen en InfoLEG:  "ARTICULO 1°.-"  "Art. 2º —"  "ARTÍCULO 14 bis.-"  "Artículo 5o:"
#   ^[ \t]*                    principio de renglon (re.M), con espacios opcionales
#   (?:ART[IÍ]CULO|ART\.)       la palabra, completa o abreviada
#   (\d+)                       grupo 1: el numero del articulo
#   [º°o](?![a-z])              el ordinal opcional ("1°", "1o"), pero no la "o" de una palabra
#   (bis|ter|qu[aá]ter)         grupo 2: sufijo opcional
#   [.\-–—:]                    y un separador: el punto, guion o raya que sigue al numero
_ART = re.compile(
    r"(?im)^[ \t]*(?:ART[IÍ]CULO|ART\.)[ \t]*(\d+)[ \t]*(?:[º°o](?![a-z]))?[ \t]*"
    r"(bis|ter|qu[aá]ter)?[ \t]*(?:[º°o](?![a-z]))?[ \t]*[.\-–—:]"
)
# _ANEXO: un renglon que empieza con "ANEXO" (los anexos traen textos ordenados, convenios,
#         planillas: sus "articulos" no son de la norma que se esta leyendo)
_ANEXO = re.compile(r"(?im)^[ \t]*ANEXO\b[^\n]{0,80}$")
# _NOTA: las notas editoriales que InfoLEG agrega al pie ("Nota Infoleg:", "Antecedentes:",
#        la firma "e. 12/03/2020"). No son texto normativo.
_NOTA = re.compile(r"(?im)^[ \t]*(?:\(?Nota\s+Infoleg|Antecedentes\s*:|e\.\s*\d+/\d+/\d+)")


@dataclass
class Articulo:
    numero: str          # "1", "2 bis", ... ("0" para el encabezado)
    zona: str            # encabezado | articulado | anexo | notas
    inicio: int          # offset en el texto plano
    fin: int
    texto: str


def html_a_texto(html_str: str) -> str:
    """Quita scripts/estilos/etiquetas y conserva los cortes de parrafo como saltos de linea.

    Paso 1 del pipeline (procesamiento del texto). El resultado es el "texto limpio": todos los
    offsets (inicio, fin) que guardan las evidencias y el grafo se cuentan sobre este texto.
    """
    # 1. fuera lo que no es contenido: scripts, estilos, cabecera, comentarios HTML
    s = re.sub(r"(?is)<(script|style|head|header|map)\b.*?</\1>", " ", html_str)
    s = re.sub(r"(?is)<!--.*?-->", " ", s)
    # 2. los saltos de linea del codigo HTML no significan nada; los de las etiquetas de bloque si
    s = re.sub(r"[\r\n]+", " ", s)               # los saltos del fuente no son cortes de parrafo
    s = _BLOQUE.sub("\n", s)
    # 3. se borra el resto de las etiquetas y se decodifican las entidades (&aacute; -> á, &nbsp;)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s).replace("\xa0", " ")
    # 4. espacios normalizados: uno solo entre palabras y como mucho una linea en blanco
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def segmentar(texto: str) -> list[Articulo]:
    """Paso 2 del pipeline: corta el texto limpio en segmentos (encabezado, articulos, anexo, notas).

    Ejemplo, Decreto 70/2023:
        [0] encabezado  "Bs. As., 20/12/2023 VISTO el Expediente ... CONSIDERANDO: Que ..."
        [1] articulado  "ARTÍCULO 1°.- ..."
        ...
        [n] anexo/notas lo que viene despues del ultimo articulo dispositivo
    """
    marcas = list(_ART.finditer(texto))
    # una norma sin articulos (p. ej. un decreto de una linea) es un unico segmento
    if not marcas:
        return [Articulo("0", "articulado", 0, len(texto), texto)]
    # el articulado termina donde empieza el primer ANEXO o la primera nota de InfoLEG
    # (lo que llegue antes), siempre despues del primer articulo
    m_anexo = next((m for m in _ANEXO.finditer(texto) if m.start() > marcas[0].start()), None)
    fin_artic = m_anexo.start() if m_anexo else len(texto)
    m_nota = next((m for m in _NOTA.finditer(texto) if m.start() > marcas[0].start()), None)
    if m_nota and m_nota.start() < fin_artic:
        fin_artic = m_nota.start()

    # todo lo anterior al primer articulo es el encabezado (titulo, VISTO, CONSIDERANDO)
    arts = [Articulo("0", "encabezado", 0, marcas[0].start(), texto[: marcas[0].start()])]
    # cada articulo va desde su marca hasta la marca siguiente; las marcas que caen dentro de un
    # anexo (articulos de un texto ordenado o de un convenio) no abren un articulo nuevo
    dentro = [m for m in marcas if m.start() < fin_artic]
    for i, m in enumerate(dentro):
        fin = dentro[i + 1].start() if i + 1 < len(dentro) else fin_artic
        num = m.group(1) + (f" {m.group(2).lower()}" if m.group(2) else "")
        arts.append(Articulo(num, "articulado", m.start(), fin, texto[m.start():fin]))
    # el resto (anexo o notas) queda como un solo segmento, con su zona
    if fin_artic < len(texto):
        zona = "anexo" if m_anexo and fin_artic == m_anexo.start() else "notas"
        arts.append(Articulo("-", zona, fin_artic, len(texto), texto[fin_artic:]))
    return arts


def cargar(id_norma: int | str, html_dir: Path) -> tuple[str, list[Articulo]] | None:
    """Punto de entrada del adaptador: id de la norma -> (texto limpio, segmentos), o None si
    InfoLEG no publica su texto."""
    p = Path(html_dir) / f"{id_norma}.html"
    if not p.exists():
        return None
    texto = html_a_texto(p.read_text(encoding="utf-8"))
    return texto, segmentar(texto)
