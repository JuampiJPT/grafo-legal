"""Deteccion de menciones a normas en texto plano (regex), con soporte de enumeraciones.

Ejemplos que reconoce:
  "Ley N° 20.744 (t.o. 1976)"                    -> ley 20744
  "Leyes Nros. 24.013, 24.465 y 24.467"          -> ley 24013, ley 24465, ley 24467
  "las Leyes Nros. 20.744 (t.o. 1976) y sus modificatorias y 24.013" -> ley 20744, ley 24013
  "Ley de Contrato de Trabajo Nº 20.744"         -> ley 20744 (nombre intercalado)
  "Decreto N° 1694/06"                           -> decreto 1694, ano 2006
  "Decreto-Ley N° 1740/45"                       -> decreto/ley 1740, ano 1945
  "Decreto de Necesidad y Urgencia N° 70/23"     -> decreto 70, ano 2023
  "ley núm. 11.729", "Ley N.° 11.729", "Ley NQ 12.713" (OCR) -> ley ...

Errores conocidos que se documentan y no se corrigen aca: menciones partidas por notas al pie,
numeros escritos en letras, y referencias anaforicas ("la citada ley", "dicho decreto").
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..catalogo import ALIAS, sin_tildes

_TIPO = (r"(?P<tipo>decretos?[\s\-]+ley(?:es)?|decretos?\s+de\s+necesidad\s+y\s+urgencia|"
         r"decretos?|leyes|ley|dnu)")
# "N°", "Nº", "Nro.", "Nros.", "Nos.", "N.°", "núm.", "número", "NQ" (error de OCR de "Nº")
_NRO = r"(?:n(?:ros?|os?|ro)?\s*\.?\s*[º°]?|n[uú]m(?:ero)?s?\.?|nq)"
# nombre propio intercalado entre el tipo y el numero: "Ley de Contrato de Trabajo Nº 20.744"
_NOMBRE = (r"(?:(?:de|del|sobre|complementaria|nacional|general|org[aá]nica)\b"
           r"(?:(?!\b(?:ley|leyes|decreto|decretos|texto|t\.o)\b)[^\d\n.;:()]){0,110}?)")
_NUM = r"\d{1,3}(?:\.\d{3})+|\d+"
_UNO = rf"(?:{_NUM})(?:\s*/\s*\d{{2,4}})?"
# entre items de una lista pueden aparecer "(t.o. 1976)", "y sus modificatorias", etc.
_RELLENO = (r"(?:\s*\([^()\n]{0,60}\))?(?:\s*,?\s*(?:y\s+)?sus?\s+(?:modificatorias?|modificaciones|"
            r"complementarias|normas\s+(?:modificatorias|complementarias|reglamentarias))(?:\s+y\s+complementarias)?)?")
_SEP = r"\s*(?:,|;|\by\b|\be\b)\s*"
_LISTA = rf"(?P<lista>{_UNO}(?:{_RELLENO}{_SEP}(?:{_NRO}\s*)?{_UNO})*)"
_PATRON = re.compile(
    rf"(?:\b|(?<=por)|(?<=del)){_TIPO}\s*(?:{_NOMBRE}\s*)?(?:{_NRO}\s*)?{_LISTA}", re.I)
_PAREN = re.compile(r"\([^()\n]{0,60}\)")
_ITEM = re.compile(rf"(?P<num>{_NUM})(?:\s*/\s*(?P<anio>\d{{2,4}}))?")


@dataclass
class Mencion:
    tipo: str
    numero: str
    anio: int | None
    inicio: int
    fin: int
    superficie: str
    metodo: str = "regex_numero"   # o "alias"


def _anio(s: str | None) -> int | None:
    if not s:
        return None
    a = int(s)
    if len(s) == 2:
        a += 1900 if a > 30 else 2000
    return a


def _tipo(t: str) -> str:
    t = sin_tildes(t).lower()
    if "necesidad" in t or t == "dnu":
        return "decreto"
    if "ley" in t and "decreto" in t:
        return "decreto/ley"
    return "ley" if t.startswith("ley") else "decreto"


def detectar(texto: str) -> list[Mencion]:
    out: list[Mencion] = []
    for m in _PATRON.finditer(texto):
        tipo = _tipo(m.group("tipo"))
        base = m.start("lista")
        # los parentesis ("t.o. 1976") se blanquean para no leer su ano como numero de norma
        lista = _PAREN.sub(lambda p: " " * len(p.group(0)), m.group("lista"))
        for it in _ITEM.finditer(lista):
            num = it.group("num")
            # un numero de ley/decreto no tiene mas de 6 cifras (descarta montos)
            if len(num.replace(".", "")) > 6:
                continue
            ini, fin = base + it.start(), base + it.end()
            out.append(Mencion(tipo, num, _anio(it.group("anio")), ini, fin, texto[m.start():fin]))
    return out


def detectar_alias(texto: str) -> list[tuple[int, int, int, str]]:
    """Devuelve (id_norma, inicio, fin, superficie) de las menciones por nombre propio."""
    plano = "".join((sin_tildes(c) or c).lower() for c in texto)   # misma longitud que texto
    out = []
    for id_norma, nombres in ALIAS.items():
        for nombre in nombres:
            for m in re.finditer(r"\b" + re.escape(nombre) + r"\b", plano):
                out.append((id_norma, m.start(), m.end(), texto[m.start():m.end()]))
    return out
