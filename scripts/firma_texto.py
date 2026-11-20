"""Firma de un artículo para comparar textos sin moverlos (B60).

La misma normalización y los mismos hashes se calculan en el navegador sobre el texto actualizado
de InfoLEG (que desde el entorno de Claude no se puede descargar), así se comparan los artículos
sin copiar el texto: hash exacto del texto normalizado y MinHash (32) de 4-gramas de palabras.
Las notas de InfoLEG («(Artículo sustituido por art. 2 de la Ley N° …)») se sacan antes.
"""
import re
import unicodedata

NOTA = re.compile(r"\((?:art[íi]culo|p[áa]rrafo|inciso|incisos|texto|expresi[óo]n|denominaci[óo]n|cap[íi]tulo|t[íi]tulo|nota|"
                  r"observad|ver |[úu]ltimo|segundo|primer|tercer|cuarto|quinto|sexto|apartado|punto)[^)]{0,600}\)", re.I)
M32 = 0xFFFFFFFF


def fnv(s: str) -> int:
    h = 0x811C9DC5
    for ch in s:
        h ^= ord(ch)
        h = (h * 16777619) & M32
    return h


def fmix(h: int) -> int:
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & M32
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & M32
    h ^= h >> 16
    return h


SEEDS = [fmix((i * 2654435761) & M32) for i in range(32)]


def normalizar(t: str) -> str:
    t = unicodedata.normalize("NFKC", t).lower()
    t = re.sub(r"[\W_]+", " ", t).strip()
    return re.sub(r"^(?:art|artículo|articulo)\s+\d+(?:\s+(?:bis|ter|quater|quáter))?\s+", "", t)


def firma(texto: str) -> tuple[int, str, list[int]]:
    n = normalizar(NOTA.sub(" ", texto))
    w = n.split() if n else []
    sh = {fnv(" ".join(w[j:j + 4])) for j in range(len(w) - 3)}
    if w and len(w) < 4:
        sh.add(fnv(" ".join(w)))
    mh = [min((fmix(h ^ s) for h in sh), default=M32) for s in SEEDS]
    return len(w), _b36(fnv(n)), mh


def _b36(x: int) -> str:
    d = "0123456789abcdefghijklmnopqrstuvwxyz"
    s = ""
    while True:
        x, r = divmod(x, 36)
        s = d[r] + s
        if not x:
            return s


def jaccard(a: list[int], b: list[int]) -> float:
    return sum(x == y for x, y in zip(a, b)) / len(a)
