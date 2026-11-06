"""
06_muestra_ley14250.py
Verifica la decision de no expandir la Ley 14.250 (Convenciones Colectivas de Trabajo).

La Ley 14.250 figura como modificada por ~42.600 normas. La hipotesis es que casi todas son
resoluciones y disposiciones que homologan convenios colectivos, no modificaciones de la ley.
Este script:
  1. cuenta las normas que la "modifican" por tipo_norma,
  2. saca una muestra aleatoria estratificada (semilla fija) de 30 normas que NO son Ley/Decreto,
     con su titulo y link, para revisar a mano,
  3. lista todas las Leyes, Decretos y Decretos-Leyes que la modifican (las que si importan).

Lee los zips que dejo en cache 01_obtener_corpus.py (data/raw).

Uso:
    python scripts/06_muestra_ley14250.py --raw data/raw --out docs/revision_manual
"""

import argparse
import io
import zipfile
from pathlib import Path

import pandas as pd

ID_14250 = 46379
SEMILLA = 20261106


def leer(zip_p: Path) -> pd.DataFrame:
    with zipfile.ZipFile(zip_p) as z:
        n = [x for x in z.namelist() if x.endswith(".csv")][0]
        return pd.read_csv(io.BytesIO(z.read(n)), dtype=str, keep_default_na=False, encoding="utf-8-sig")


def main(raw: Path, out: Path) -> None:
    mod = leer(raw / "modificatorias.zip")
    base = leer(raw / "base.zip").drop_duplicates("id_norma").set_index("id_norma")
    m = mod[mod.id_norma_modificada == str(ID_14250)].drop_duplicates(["id_norma_modificatoria"])
    ids = m.id_norma_modificatoria
    info = base.reindex(ids)
    info["id_norma"] = ids.values
    print(f"normas que modifican a la Ley 14.250: {len(info)}")
    conteo = info.tipo_norma.value_counts()
    print(conteo.to_string())

    out.mkdir(parents=True, exist_ok=True)
    conteo.rename_axis("tipo_norma").reset_index(name="cantidad").to_csv(
        out / "ley14250_modificatorias_por_tipo.csv", index=False, lineterminator="\n")

    cols = ["id_norma", "tipo_norma", "numero_norma", "organismo_origen", "fecha_boletin",
            "titulo_resumido", "titulo_sumario", "texto_resumido", "texto_original"]
    otras = info[~info.tipo_norma.isin(["Ley", "Decreto", "Decreto/Ley"])]
    partes = [d.sample(n=min(len(d), max(1, round(30 * len(d) / len(otras)))), random_state=SEMILLA)
              for _, d in otras.groupby("tipo_norma")]
    muestra = pd.concat(partes).head(30)
    muestra = muestra[cols].assign(es_homologacion_de_convenio="", modifica_el_texto_de_la_ley="", nota="")
    muestra.to_csv(out / "ley14250_muestra_30.csv", index=False, lineterminator="\n")

    leyes = info[info.tipo_norma.isin(["Ley", "Decreto", "Decreto/Ley"])][cols]
    leyes.sort_values("fecha_boletin").to_csv(out / "ley14250_leyes_y_decretos.csv", index=False, lineterminator="\n")
    print(f"muestra: {len(muestra)} filas; leyes/decretos que la modifican: {len(leyes)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=Path("data/raw"))
    ap.add_argument("--out", type=Path, default=Path("docs/revision_manual"))
    a = ap.parse_args()
    main(a.raw, a.out)
