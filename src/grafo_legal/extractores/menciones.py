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

# --- Como se arma el patron de una mencion -----------------------------------------------
# Una mencion es: TIPO + (NOMBRE intercalado opcional) + (abreviatura de numero opcional) + LISTA
#   "Decreto de Necesidad y Urgencia N° 70/23"
#    \_____________ TIPO _____________/ \NRO/ \LISTA/
#   "Ley de Contrato de Trabajo Nº 20.744"
#    TIPO \______ NOMBRE ________/ NRO  LISTA
#   "Leyes Nros. 24.013, 24.465 y 24.467"  -> una LISTA con tres numeros: tres menciones
#
# _TIPO: la clase de norma. Se capturan los plurales para las enumeraciones.
_TIPO = (r"(?P<tipo>decretos?[\s\-]+ley(?:es)?|decretos?\s+de\s+necesidad\s+y\s+urgencia|"
         r"decretos?|leyes|ley|dnu)")
# "N°", "Nº", "Nro.", "Nros.", "Nos.", "N.°", "núm.", "número", "NQ" (error de OCR de "Nº")
_NRO = r"(?:n(?:ros?|os?|ro)?\s*\.?\s*[º°]?|n[uú]m(?:ero)?s?\.?|nq)"
# nombre propio intercalado entre el tipo y el numero: "Ley de Contrato de Trabajo Nº 20.744"
_NOMBRE = (r"(?:(?:de|del|sobre|complementaria|nacional|general|org[aá]nica)\b"
           r"(?:(?!\b(?:ley|leyes|decreto|decretos|texto|t\.o)\b)[^\d\n.;:()]){0,110}?)")
# _NUM: "20.744" (con punto de miles) o "20744"
_NUM = r"\d{1,3}(?:\.\d{3})+|\d+"
# _UNO: un numero con ano opcional: "1694/06", "70/2023"
_UNO = rf"(?:{_NUM})(?:\s*/\s*\d{{2,4}})?"
# entre items de una lista pueden aparecer "(t.o. 1976)", "y sus modificatorias", etc.
_RELLENO = (r"(?:\s*\([^()\n]{0,60}\))?(?:\s*,?\s*(?:y\s+)?sus?\s+(?:modificatorias?|modificaciones|"
            r"complementarias|normas\s+(?:modificatorias|complementarias|reglamentarias))(?:\s+y\s+complementarias)?)?")
# _SEP: separador entre items de una enumeracion: coma, punto y coma, "y", "e"
_SEP = r"\s*(?:,|;|\by\b|\be\b)\s*"
# _LISTA: uno o mas numeros separados, con relleno permitido entre ellos
_LISTA = rf"(?P<lista>{_UNO}(?:{_RELLENO}{_SEP}(?:{_NRO}\s*)?{_UNO})*)"
# _PATRON: la mencion completa. "(?<=por)" y "(?<=del)" admiten textos pegados por el OCR
# ("porla Ley", "delDecreto").
_PATRON = re.compile(
    rf"(?:\b|(?<=por)|(?<=del)){_TIPO}\s*(?:{_NOMBRE}\s*)?(?:{_NRO}\s*)?{_LISTA}", re.I)
_PAREN = re.compile(r"\([^()\n]{0,60}\)")
# _ITEM: dentro de una LISTA, cada numero (y su ano, si lo tiene) es una mencion separada
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
    """Ano de dos cifras -> cuatro: "06" -> 2006, "76" -> 1976 (corte en 30)."""
    if not s:
        return None
    a = int(s)
    if len(s) == 2:
        a += 1900 if a > 30 else 2000
    return a


def _tipo(t: str) -> str:
    """Texto del tipo -> tipo canonico: "Decretos-Leyes" -> decreto/ley, "DNU" -> decreto."""
    t = sin_tildes(t).lower()
    if "necesidad" in t or t == "dnu":
        return "decreto"
    if "ley" in t and "decreto" in t:
        return "decreto/ley"
    return "ley" if t.startswith("ley") else "decreto"


# --- Ano escrito como fecha (solo reglas v3) -------------------------------------------
# "Decreto N° 1694 del 22 de noviembre de 2006", "Decreto Nº 84 de fecha 23 de enero de 2014",
# "Decretos Nros. 658 y 659, ambos del 24 de junio de 1996", "Decreto 410 del 13/03/2001".
_MESES = r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|sep?tiembre|octubre|noviembre|diciembre)"
_FECHA = re.compile(
    rf"^\s*,?\s*(?:ambos\s+|todos\s+)?(?:de\s+fecha|del|de)\s+(?:\d{{1,2}}\s*[°º]?\s+de\s+{_MESES}\s+(?:de|del)\s+"
    rf"(?P<a1>\d{{4}})|\d{{1,2}}/\d{{1,2}}/(?P<a2>\d{{4}}))", re.I)
_AMBOS = re.compile(r"^\s*,?\s*(?:ambos|todos)\b", re.I)


def anio_de_fecha(texto: str, fin: int) -> int | None:
    """Ano de la fecha que sigue inmediatamente a una mencion, o None."""
    m = _FECHA.match(texto[fin:fin + 80])
    if not m:
        return None
    return int(m.group("a1") or m.group("a2"))


def detectar(texto: str, anio_por_fecha: bool = False) -> list[Mencion]:
    """Paso 3 del pipeline (deteccion): todas las menciones por tipo y numero de un segmento.

    Cada mencion conserva sus offsets dentro del segmento, para poder volver a la evidencia.
    La deteccion no decide si la mencion es una relacion: eso lo hacen las reglas despues.
    """
    # anio_por_fecha=False es el comportamiento congelado de las reglas v1 y v2. Con True (reglas
    # v3), si la mencion no trae "/ano", se lee el ano de la fecha que la sigue.
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
        if anio_por_fecha:
            _completar_anios(texto, out, m.end())
    return out


def _completar_anios(texto: str, menciones: list[Mencion], fin_lista: int) -> None:
    """Reglas v3: completa el ano de las menciones sin "/ano" con la fecha que las sigue.

    - "Decreto N° 1694 del 22 de noviembre de 2006": la fecha sigue al numero.
    - "Decretos Nros. 658 y 659, ambos del 24 de junio de 1996": la fecha vale para toda la lista.
    """
    for mm in menciones:
        if mm.anio is None and mm.metodo == "regex_numero":
            mm.anio = anio_de_fecha(texto, mm.fin) or mm.anio
    resto = texto[fin_lista:fin_lista + 80]
    if _AMBOS.match(resto):
        a = anio_de_fecha(texto, fin_lista)
        if a:
            for mm in menciones:
                if mm.anio is None and mm.fin <= fin_lista:
                    mm.anio = a


def detectar_alias(texto: str, alias: dict | None = None) -> list[tuple[int, int, int, str]]:
    """Devuelve (id_norma, inicio, fin, superficie) de las menciones por nombre propio.

    Busca los nombres del gazetteer ALIAS ("ley de contrato de trabajo" -> Ley 20.744) sobre una
    copia del texto en minusculas y sin tildes, del mismo largo que el original, asi los offsets
    sirven tambien para el texto original.
    """
    plano = "".join((sin_tildes(c) or c).lower() for c in texto)   # misma longitud que texto
    out = []
    for id_norma, nombres in (alias or ALIAS).items():
        for nombre in nombres:
            for m in re.finditer(r"\b" + re.escape(nombre) + r"\b", plano):
                out.append((id_norma, m.start(), m.end(), texto[m.start():m.end()]))
    return out
