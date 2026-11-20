"""Pruebas del adaptador del digesto de la UNNOBA (PI4)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from grafo_legal.fuentes import unnoba  # noqa: E402


def claves(t):
    return [m.clave for m in unnoba.detectar(t)]


def test_menciones_internas_y_listas():
    t = "Visto las Resoluciones (CS) 32/2007, 92/2008 y 77/2008, la Ordenanza (CS) 14/09 y la Res. (CD.ET) 64/2013"
    assert claves(t) == ["RES-HCS-32-2007", "RES-HCS-92-2008", "RES-HCS-77-2008", "ORD-HCS-14-2009", "RES-CDET-64-2013"]


def test_rector_ocr_y_nacionales():
    t = "Ratificar la Resolución Nro. 3565/2011. Que por Resolución (CS) 53112012 se aprobó. Ley N° 24.521. Decreto 499/95"
    assert claves(t) == ["RES-REC-3565-2011", "RES-HCS-531-2012", "LEY-NAC-24521", "DEC-NAC-499-1995"]


def test_partes_y_claves():
    t = unnoba.limpiar("Resolución (CS) 1/2010\nVisto,\nlo actuado, y;\nConsiderando:\nQue el\nEstatuto ...\nPor ello,\n"
                       "EL CONSEJO SUPERIOR RESUELVE:\nArtículo 1: Modificar la Ordenanza (CS) 14/2009.")
    partes = unnoba.segmentar(t)
    m = [x for x in unnoba.detectar(t) if x.clave.startswith("ORD")][0]
    assert unnoba.parte_de(partes, m.inicio) == "articulado"
    e = [x for x in unnoba.detectar(t) if x.clave == "ESTATUTO"][0]
    assert unnoba.parte_de(partes, e.inicio) == "considerando"
    assert unnoba.clave_comparable("RES-?-44-2008") == unnoba.clave_comparable("RES-HCS-44-2008")
    assert unnoba.clave_origen("Resolución HCS Nº 084/08") == "RES-HCS-84-2008"
