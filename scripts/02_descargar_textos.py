"""
02_descargar_textos.py
TP Integrador - Sistemas Inteligentes (UNNOBA) - Problematica III

Descarga el HTML de cada norma de un corpus desde InfoLEG.

- Fuente preferida: texto original (norma.htm), que conserva la redaccion
  "Modificase / Sustituyese el articulo X de la Ley N..." que lee el extractor.
  Si la norma no tiene texto original, se usa el texto actualizado (texact.htm).
- InfoLEG sirve HTML estatico, asi que alcanza con requests. Pausa de 1 s entre pedidos y
  cache en disco: los textos ya descargados (por ejemplo los 168 del corpus v1) no se vuelven
  a pedir ni se modifican.
- El manifiesto (manifiesto_textos.csv) es incremental: conserva las filas existentes y agrega
  una fila por cada texto nuevo con URL, fecha, tamano original, charset y SHA-256.

Uso:
    python scripts/02_descargar_textos.py --corpus data/corpus_v2/corpus_normas.csv
"""

import argparse
import csv
import hashlib
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import abrir_para_escribir, escribir_texto  # noqa: E402
from grafo_legal.fuentes.infoleg import html_a_texto, segmentar  # noqa: E402

HOST = "https://servicios.infoleg.gob.ar"
PAUSA_SEG = 1.0
HEADERS = {"User-Agent": "TP-UNNOBA-SistemasInteligentes/1.0 (uso academico)"}
CAMPOS = ["id_norma", "fuente", "url", "fecha_descarga", "bytes_html_original", "charset_declarado",
          "chars_texto", "articulos", "sha256_html_utf8"]


def ruta(id_norma: str, archivo: str) -> str:
    n = int(id_norma)
    a = n // 5000 * 5000
    return f"{HOST}/infolegInternet/anexos/{a}-{a + 4999}/{n}/{archivo}"


def charset_de(raw: bytes) -> str:
    m = re.search(rb'charset=["\']?([\w-]+)', raw[:3000], re.I)
    cs = m.group(1).decode().lower() if m else "windows-1252"
    # InfoLEG declara iso-8859-1 pero usa caracteres de windows-1252 (comillas, guiones)
    return "windows-1252" if cs in ("iso-8859-1", "latin-1", "latin1") else cs


def main(corpus: Path, out: Path) -> None:
    html_dir = out / "html"
    html_dir.mkdir(parents=True, exist_ok=True)
    man_p = out / "manifiesto_textos.csv"
    existentes = {}
    if man_p.exists():
        with man_p.open(encoding="utf-8") as f:
            existentes = {r["id_norma"]: r for r in csv.DictReader(f)}

    with corpus.open(encoding="utf-8") as f:
        normas = list(csv.DictReader(f))

    sesion = requests.Session()
    sesion.headers.update(HEADERS)
    nuevos, recuperados, sin_link, fallidos = 0, 0, 0, []
    for r in normas:
        i = r["id_norma"]
        destino = html_dir / f"{i}.html"
        if destino.exists() and i in existentes:
            continue
        if r["texto_original"]:
            fuente, url = "original", ruta(i, "norma.htm")
        elif r["texto_actualizado"]:
            fuente, url = "actualizado", ruta(i, "texact.htm")
        else:
            sin_link += 1
            continue
        if destino.exists():
            # El HTML ya esta en disco pero falta en el manifiesto (por ejemplo, si una corrida
            # anterior se corto antes de escribirlo): se arma la fila desde el archivo, sin red.
            # fecha_descarga = fecha de modificacion del archivo; bytes_html_original = el texto
            # re-codificado con el charset declarado en el propio HTML.
            html_utf8 = destino.read_text(encoding="utf-8")
            cs = charset_de(html_utf8.encode("utf-8"))
            texto = html_a_texto(html_utf8)
            existentes[i] = {
                "id_norma": i, "fuente": fuente, "url": url,
                "fecha_descarga": datetime.fromtimestamp(destino.stat().st_mtime, timezone.utc)
                .isoformat(timespec="milliseconds").replace("+00:00", "Z"),
                "bytes_html_original": len(html_utf8.encode(cs, errors="replace")), "charset_declarado": cs,
                "chars_texto": len(texto), "articulos": sum(a.zona == "articulado" for a in segmentar(texto)),
                "sha256_html_utf8": hashlib.sha256(html_utf8.encode("utf-8")).hexdigest(),
            }
            recuperados += 1
            continue
        resp, error = None, None
        # InfoLEG sirve el mismo contenido por https y por http; si https falla (por ejemplo por
        # la cadena de certificados), se reintenta por http y se registra la URL realmente usada.
        for u in (url, url.replace("https://", "http://", 1)):
            for intento in range(3):
                try:
                    resp = sesion.get(u, timeout=30)
                    resp.raise_for_status()
                    url = u
                    break
                except requests.RequestException as e:
                    resp, error = None, e
                    time.sleep(2)
            if resp is not None:
                break
        if resp is None:
            fallidos.append((i, f"{type(error).__name__}: {error}"))
            print(f"  [fallo] {i}: {type(error).__name__}: {str(error)[:160]}", flush=True)
            continue
        raw = resp.content
        cs = charset_de(raw)
        html_utf8 = raw.decode(cs, errors="replace")
        destino.write_text(html_utf8, encoding="utf-8")
        texto = html_a_texto(html_utf8)
        existentes[i] = {
            "id_norma": i, "fuente": fuente, "url": url,
            "fecha_descarga": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "bytes_html_original": len(raw), "charset_declarado": cs, "chars_texto": len(texto),
            "articulos": sum(a.zona == "articulado" for a in segmentar(texto)),
            "sha256_html_utf8": hashlib.sha256(html_utf8.encode("utf-8")).hexdigest(),
        }
        nuevos += 1
        print(f"  [{nuevos}] {i} {fuente} {len(raw)} bytes", flush=True)
        time.sleep(PAUSA_SEG)

    with abrir_para_escribir(man_p) as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, lineterminator="\n")
        w.writeheader()
        for k in sorted(existentes, key=int):
            w.writerow(existentes[k])
    print(f"{nuevos} textos nuevos, {recuperados} recuperados del disco, {len(existentes)} en el manifiesto, {sin_link} normas sin link, "
          f"{len(fallidos)} fallidos")
    for i, e in fallidos:
        print("  fallo", i, e)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus_v2/corpus_normas.csv"))
    ap.add_argument("--out", type=Path, default=Path("data/textos/infoleg"))
    a = ap.parse_args()
    main(a.corpus, a.out)
