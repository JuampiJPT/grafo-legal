"""Adaptador del digesto de la UNNOBA (PI4: transferencia a otro corpus).

Es lo único del pipeline que se cambió para leer otra fuente. Tiene dos partes:

  1. TEXTO Y ESTRUCTURA. Los documentos son PDF: con texto embebido o escaneados (OCR con
     tesseract en español, bitácora B57). El texto de un PDF trae saltos de línea de la
     maquetación en medio de las oraciones, así que se unen las líneas y se dejan cortes solo
     antes de las fórmulas que abren un párrafo ("Que ...", "Artículo N", "Visto", "Por ello").
     Después se separan las partes como en InfoLEG: encabezado, VISTO, CONSIDERANDO y
     articulado (desde "RESUELVE:" u "ORDENA:").
  2. VOCABULARIO DE LA FUENTE. Las normas internas se citan distinto que las nacionales:
     "Resolución (CS) Nro. 44/08", "Ordenanza (CS) 14/2009", "Res. CD ET 28/2016",
     "Resolución Nro. 3565/2011" (del Rector) y en listas ("Resoluciones (CS) 32/2007, 92/2008
     y 77/2008"). Además de las normas nacionales (Ley N° 24.521, Decreto 499/95) y el
     Estatuto. El OCR a veces lee la barra como un "1" ("531/2012" -> "53112012"); se corrige.

Cada mención se normaliza a una clave TIPO-EMISOR-NUMERO-AÑO (por ejemplo RES-HCS-44-2008).
No hay un catálogo cerrado como en InfoLEG: el digesto publicado es parcial y muchas normas
citadas no están, así que la vinculación es por clave.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..extractores.menciones import anio_de_fecha

# ------------------------------------------------------------------------------------------
# 1. Texto y estructura
# ------------------------------------------------------------------------------------------
_CORTES = re.compile(
    r"\s*\n\s*(?=(?:Que\b|Art[ií]c\w*\s*\.?\s*\d|Vist[oa]\b|Consider[aá]ndo|Por\s+ello|"
    r"RESUELVE|Resuelve|ORDENA|Ordena|EL\s+CONSEJO|El\s+Consejo|La\s+Directora))")


def limpiar(texto: str) -> str:
    """Une las líneas de maquetación del PDF y deja un salto antes de cada fórmula de párrafo."""
    t = texto.replace("\f", "\n").replace("\r", "")
    t = re.sub(r"[ \t]+", " ", t)
    t = _CORTES.sub("\u2029", t)                 # marca los cortes reales
    t = t.replace("\n", " ").replace("\u2029", "\n")  # el resto de los saltos son de maquetacion
    return re.sub(r" {2,}", " ", t).strip()


_VISTO = re.compile(r"\bVist[oa]\s*[,:.;]?", re.I)
_CONSIDERANDO = re.compile(r"\bCons[il1]?der[aá]n?do\b|\bCO\S{0,3}siderando", re.I)
_DISPOSITIVO = re.compile(r"\b(?:RESUELVE|Resuelve|ORDENA|Ordena|DISPONE|Dispone)\s*[:;,.]")
_POR_ELLO = re.compile(r"\bPor\s+[eé]l?l?o\b", re.I)


@dataclass
class Parte:
    parte: str        # encabezado | visto | considerando | articulado
    inicio: int
    fin: int


def segmentar(texto: str) -> list[Parte]:
    """Partes del documento por posición. Si falta una fórmula, la parte queda vacía."""
    n = len(texto)
    v = _VISTO.search(texto)
    c = _CONSIDERANDO.search(texto, v.end() if v else 0)
    d = _DISPOSITIVO.search(texto, c.end() if c else (v.end() if v else 0))
    iv = v.start() if v else 0
    ic = c.start() if c else iv
    ia = d.end() if d else n
    # "Por ello, EL CONSEJO SUPERIOR ... en uso de sus atribuciones (Art. 76 del Estatuto)" queda en
    # el considerando, como la fórmula "Por ello, EL PRESIDENTE ... DECRETA:" en InfoLEG
    fc = d.start() if d else n
    return [Parte("encabezado", 0, iv), Parte("visto", iv, ic), Parte("considerando", ic, fc),
            Parte("articulado", ia, n)]


def parte_de(partes: list[Parte], pos: int) -> str:
    for p in partes:
        if p.inicio <= pos < p.fin:
            return p.parte
    return "otro"


# ------------------------------------------------------------------------------------------
# 2. Vocabulario de la fuente: menciones a normas
# ------------------------------------------------------------------------------------------
_EMISOR = (r"(?:\(\s*(?P<em1>[A-Za-z][A-Za-z.\s]{0,9}?)\s*\)|(?P<em2>H\.?\s*C\.?\s*S\.?|C\.\s*S\.|CS|"
           r"C\.?\s*D\.?\s*E\.?\s*T\.?|CD\s*ET|D\.?\s*E\.?\s*T\.?|ET|Ministerial|del\s+(?:Señor\s+)?Rector|"
           r"Rectoral|del\s+Consejo\s+Superior|de\s+Consejo\s+Superior))?")
_NRO = r"\s*(?:N\s*(?:ro|ros|°|º|\*|o|”|\?)?\s*[.,]?\s*|Número\s*)?"
_NUM_ANIO = r"(?P<num>\d{1,4})\s*/\s*(?P<anio>\d{2,4})"
_NUM_ANIO_OCR = r"(?P<num2>\d{2,4})1(?P<anio2>(?:19|20)\d{2})(?!\d)"   # 53112012 = 531/2012
_TIPO_RES = r"(?P<tipo>Resoluci[oó]n(?:es)?|Res\.|Ordenanzas?|Ord\.)"
_MENCION = re.compile(rf"{_TIPO_RES}\s*{_EMISOR}{_NRO}\s*(?:{_NUM_ANIO}|{_NUM_ANIO_OCR}|(?P<solo>\d{{1,4}})\b)",
                      re.I)
_SIGUE = re.compile(rf"\s*(?:,|\by\b|e\b)\s*{_NRO}(?:{_NUM_ANIO}|{_NUM_ANIO_OCR})")
_LEY = re.compile(r"\bLey(?:\s+de\s+(?P<nombre>Educaci[oó]n\s+Superior|Migraciones))?\s*"
                  r"(?:N\s*(?:ro|°|º|\*|o|”|\?)?\s*[.,]?\s*)?(?P<num>\d{1,2}[.,]?\d{3})\b", re.I)
_LES = re.compile(r"\bLey\s+de\s+Educaci[oó]n\s+Superior\b(?!\s*(?:N\s*\W?\s*)?\d)", re.I)
_DECRETO = re.compile(r"\bDecreto(?:\s+del\s+Poder\s+Ejecutivo\s+Nacional)?\s*"
                      r"(?:N\s*(?:ro|°|º|\*|o|”)?\s*[.,]?\s*)?(?P<num>\d{1,5})\s*/\s*(?P<anio>\d{2,4})", re.I)
_ESTATUTO = re.compile(r"\bEstatuto(?:\s+(?:Universitario|de\s+la\s+Universidad))?\b")


def _anio4(a: str) -> int:
    a = int(a)
    return a + (1900 if a >= 50 else 2000) if a < 100 else a


def _emisor(em: str | None, tipo: str, num: int) -> str:
    e = re.sub(r"[\s.]", "", (em or "")).upper()
    if e in ("CS", "HCS", "ES", "C5", "DELCONSEJOSUPERIOR", "DECONSEJOSUPERIOR"):
        return "HCS"
    if e in ("CDET", "CD", "CDET"):
        return "CDET"
    if e in ("DET", "ET"):
        return "DET"
    if e.startswith("MINISTERIAL"):
        return "MIN"
    if e.startswith("DEL") and "RECTOR" in e or e == "RECTORAL":
        return "REC"
    if not e and tipo == "RES" and num >= 1000:
        return "REC"            # numeración del Rector (miles), sin emisor escrito
    return "?"


@dataclass
class MencionUnnoba:
    clave: str
    inicio: int
    fin: int
    superficie: str
    metodo: str


def detectar(texto: str) -> list[MencionUnnoba]:
    out: list[MencionUnnoba] = []
    for m in _MENCION.finditer(texto):
        tipo = "ORD" if m.group("tipo").lower().startswith("ord") else "RES"
        em = m.group("em1") or m.group("em2")
        if m.group("num") or m.group("num2"):
            num = int(m.group("num") or m.group("num2"))
            anio = _anio4(m.group("anio") or m.group("anio2"))
        else:
            num = int(m.group("solo"))
            anio = anio_de_fecha(texto, m.end())            # "Ordenanza Nro. 2 ... de fecha 28 de diciembre de 2007"
            if anio is None:
                continue
        emisor = _emisor(em, tipo, num)
        out.append(MencionUnnoba(f"{tipo}-{emisor}-{num}-{anio}", m.start(), m.end(), m.group(0), "regex_numero"))
        fin = m.end()
        while (s := _SIGUE.match(texto, fin)):                 # listas: "32/2007, 92/2008 y 77/2008"
            n2 = int(s.group("num") or s.group("num2")); a2 = _anio4(s.group("anio") or s.group("anio2"))
            out.append(MencionUnnoba(f"{tipo}-{_emisor(em, tipo, n2)}-{n2}-{a2}", s.start(), s.end(),
                                     s.group(0).strip(), "regex_lista"))
            fin = s.end()
    for m in _LEY.finditer(texto):
        num = int(re.sub(r"\D", "", m.group("num")))
        if num == 24321:                                       # OCR de 24.521
            num = 24521
        out.append(MencionUnnoba(f"LEY-NAC-{num}", m.start(), m.end(), m.group(0), "regex_numero"))
    for m in _LES.finditer(texto):
        out.append(MencionUnnoba("LEY-NAC-24521", m.start(), m.end(), m.group(0), "alias"))
    for m in _DECRETO.finditer(texto):
        out.append(MencionUnnoba(f"DEC-NAC-{int(m.group('num'))}-{_anio4(m.group('anio'))}", m.start(), m.end(),
                                 m.group(0), "regex_numero"))
    for m in _ESTATUTO.finditer(texto):
        out.append(MencionUnnoba("ESTATUTO", m.start(), m.end(), m.group(0), "alias"))
    return sorted(out, key=lambda x: x.inicio)


# ------------------------------------------------------------------------------------------
# Claves: comparación tolerante (el emisor puede faltar en el texto)
# ------------------------------------------------------------------------------------------
def clave_comparable(clave: str) -> str:
    """Sin el emisor: RES-HCS-44-2008 y RES-?-44-2008 son la misma norma para comparar."""
    p = clave.split("-")
    if p[0] in ("RES", "ORD") and len(p) == 4:
        return f"{p[0]}-{p[2]}-{p[3]}"
    if p[0] == "LEY":
        return f"LEY-{p[2]}"
    return clave


def clave_origen(titulo: str) -> str:
    """'Resolución HCS Nº 312/10' -> RES-HCS-312-2010."""
    m = re.match(r"(Resoluci[oó]n|Ordenanza)\s+(\w+)\s+N\S*\s+(\d+)/(\d+)", titulo)
    tipo = "ORD" if m.group(1).startswith("Ord") else "RES"
    return f"{tipo}-{m.group(2)}-{int(m.group(3))}-{_anio4(m.group(4))}"


def anio_de_clave(clave: str) -> int | None:
    p = clave.split("-")
    return int(p[-1]) if p[0] in ("RES", "ORD", "DEC") and p[-1].isdigit() else None
