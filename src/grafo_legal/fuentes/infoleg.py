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

_BLOQUE = re.compile(r"(?i)<br\s*/?>|</?(?:p|div|h\d|tr|li|table|center|blockquote)\b[^>]*>")
_ART = re.compile(
    r"(?im)^[ \t]*(?:ART[IÍ]CULO|ART\.)[ \t]*(\d+)[ \t]*(?:[º°o](?![a-z]))?[ \t]*"
    r"(bis|ter|qu[aá]ter)?[ \t]*(?:[º°o](?![a-z]))?[ \t]*[.\-–—:]"
)
_ANEXO = re.compile(r"(?im)^[ \t]*ANEXO\b[^\n]{0,80}$")
_NOTA = re.compile(r"(?im)^[ \t]*(?:\(?Nota\s+Infoleg|Antecedentes\s*:|e\.\s*\d+/\d+/\d+)")


@dataclass
class Articulo:
    numero: str          # "1", "2 bis", ... ("0" para el encabezado)
    zona: str            # encabezado | articulado | anexo | notas
    inicio: int          # offset en el texto plano
    fin: int
    texto: str


def html_a_texto(html_str: str) -> str:
    """Quita scripts/estilos/etiquetas y conserva los cortes de parrafo como saltos de linea."""
    s = re.sub(r"(?is)<(script|style|head|header|map)\b.*?</\1>", " ", html_str)
    s = re.sub(r"(?is)<!--.*?-->", " ", s)
    s = re.sub(r"[\r\n]+", " ", s)               # los saltos del fuente no son cortes de parrafo
    s = _BLOQUE.sub("\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def segmentar(texto: str) -> list[Articulo]:
    marcas = list(_ART.finditer(texto))
    if not marcas:
        return [Articulo("0", "articulado", 0, len(texto), texto)]
    m_anexo = next((m for m in _ANEXO.finditer(texto) if m.start() > marcas[0].start()), None)
    fin_artic = m_anexo.start() if m_anexo else len(texto)
    m_nota = next((m for m in _NOTA.finditer(texto) if m.start() > marcas[0].start()), None)
    if m_nota and m_nota.start() < fin_artic:
        fin_artic = m_nota.start()

    arts = [Articulo("0", "encabezado", 0, marcas[0].start(), texto[: marcas[0].start()])]
    dentro = [m for m in marcas if m.start() < fin_artic]
    for i, m in enumerate(dentro):
        fin = dentro[i + 1].start() if i + 1 < len(dentro) else fin_artic
        num = m.group(1) + (f" {m.group(2).lower()}" if m.group(2) else "")
        arts.append(Articulo(num, "articulado", m.start(), fin, texto[m.start():fin]))
    if fin_artic < len(texto):
        zona = "anexo" if m_anexo and fin_artic == m_anexo.start() else "notas"
        arts.append(Articulo("-", zona, fin_artic, len(texto), texto[fin_artic:]))
    return arts


def cargar(id_norma: int | str, html_dir: Path) -> tuple[str, list[Articulo]] | None:
    p = Path(html_dir) / f"{id_norma}.html"
    if not p.exists():
        return None
    texto = html_a_texto(p.read_text(encoding="utf-8"))
    return texto, segmentar(texto)
