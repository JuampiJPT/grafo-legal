"""Catalogo de normas conocidas, usado para normalizar menciones a id_norma.

Decision de diseno (mundo cerrado): por defecto el catalogo es el corpus. Una mencion que no
resuelve a una norma del catalogo se conserva como evidencia, pero no genera arista evaluable.
Esto se documenta en la bitacora: con el catalogo completo de InfoLEG (~490 mil normas) se
podrian resolver mas menciones, pero el gold se limita igualmente a pares dentro del corpus.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


def sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm_numero(num: str) -> str:
    return re.sub(r"[.\s]", "", num).lstrip("0") or "0"


def tipo_canonico(t: str) -> str:
    t = sin_tildes(t).lower()
    if "ley" in t and "decreto" in t:
        return "decreto/ley"
    if t.startswith("decreto") or t in ("dnu", "dec", "dto"):
        return "decreto"
    if t.startswith("ley"):
        return "ley"
    return t


# Nombres propios con los que el texto cita a una norma sin dar su numero.
# Se arma a mano y se documenta: es la parte "gazetteer" del parser de reglas.
ALIAS = {
    25552: ["ley de contrato de trabajo", "regimen de contrato de trabajo", "regimen del contrato de trabajo"],
    109500: ["codigo de comercio"],
    17699: ["ley de impuesto a las ganancias", "impuesto a las ganancias"],
    16092: ["ley de impuesto al valor agregado", "impuesto al valor agregado"],
    412: ["ley nacional de empleo", "ley de empleo"],
    27971: ["ley de riesgos del trabajo"],
    20993: ["ley de asociaciones sindicales"],
    46379: ["ley de convenciones colectivas de trabajo"],
    192152: ["regimen de trabajo agrario"],
    210489: ["regimen especial de contrato de trabajo para el personal de casas particulares"],
    25379: ["ley de concursos y quiebras"],
}


@dataclass
class Norma:
    id: int
    tipo: str            # canonico: ley | decreto | decreto/ley
    numero: str          # normalizado, sin puntos
    anio: int | None
    fecha: str
    etiqueta: str


class Catalogo:
    def __init__(self, normas: list[Norma]):
        self.normas = {n.id: n for n in normas}
        self._idx: dict[tuple[str, str], list[Norma]] = {}
        for n in normas:
            fam = "decreto" if n.tipo in ("decreto", "decreto/ley") else n.tipo
            self._idx.setdefault((fam, n.numero), []).append(n)

    @classmethod
    def desde_corpus(cls, ruta: Path) -> "Catalogo":
        normas = []
        with open(ruta, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                fecha = r["fecha_sancion"] or r["fecha_boletin"]
                normas.append(Norma(
                    id=int(r["id_norma"]), tipo=tipo_canonico(r["tipo_norma"]),
                    numero=norm_numero(r["numero_norma"]), anio=int(fecha[:4]) if fecha else None,
                    fecha=r["fecha_boletin"] or r["fecha_sancion"],
                    etiqueta=f"{r['tipo_norma']} {r['numero_norma']}"))
        return cls(normas)

    def resolver(self, tipo: str, numero: str, anio: int | None = None) -> Norma | None:
        """Ley: el numero es unico. Decreto: el numero se repite cada ano, se exige el ano si
        hay mas de un candidato; si hay uno solo y no hay ano, se acepta (riesgo documentado)."""
        t = tipo_canonico(tipo)
        fam = "decreto" if t in ("decreto", "decreto/ley") else t
        cands = self._idx.get((fam, norm_numero(numero)), [])
        if fam == "decreto":
            if anio is not None:
                cands = [c for c in cands if c.anio is not None and c.anio == anio]
            if len(cands) == 1:
                return cands[0]
        elif len(cands) == 1:
            return cands[0]
        # Los "decretos-leyes" de los gobiernos de facto 1966-73 y 1976-83 se numeran en la serie
        # de leyes e InfoLEG los cataloga como Ley ("Decreto-Ley 17.258/67" = Ley 17.258).
        if t == "decreto/ley":
            leyes = self._idx.get(("ley", norm_numero(numero)), [])
            if len(leyes) == 1 and (anio is None or leyes[0].anio == anio):
                return leyes[0]
        return None
