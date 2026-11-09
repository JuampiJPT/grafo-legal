"""
08_clasificador.py
Clasificador supervisado sobre data/dataset/pares_candidatos.csv: decide si un par candidato
(norma origen -> norma destino) es una relacion de InfoLEG. Es el punto de comparacion
estadistico de los parsers de reglas, LLM e hibrido.

Protocolo (bitacora B16, B37):
  - Seleccion de modelo y de umbral con validacion cruzada de 5 particiones sobre dev, agrupada
    por norma origen (los pares de una misma norma no se reparten entre entrenamiento y validacion).
  - El modelo elegido se entrena con todo dev y se evalua test una sola vez (--incluir-test).
  - Las metricas se calculan contra TODO el gold del split, no solo contra los candidatos: un par
    del gold que no es candidato cuenta como falso negativo. Asi se comparan con las reglas.

Salidas en results/clasificador/: metricas.json, predicciones.csv (probabilidad por candidato; en
dev es la de la validacion cruzada, en test la del modelo final)
e importancia.csv (coeficientes del modelo lineal o importancia de los arboles).

Uso:
    python scripts/08_clasificador.py
    python scripts/08_clasificador.py --incluir-test
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto              # noqa: E402
from grafo_legal.evaluacion import prf                       # noqa: E402

SEMILLA = 20261109
NO_ATRIBUTOS = ["id_norma_origen", "id_norma_destino", "split", "en_gold"]
CATEGORICOS = ["tipo_origen", "tipo_destino"]


def matriz(df: pd.DataFrame, columnas: list[str] | None = None) -> pd.DataFrame:
    X = pd.get_dummies(df.drop(columns=NO_ATRIBUTOS), columns=CATEGORICOS, dtype=float)
    if columnas is not None:
        X = X.reindex(columns=columnas, fill_value=0.0)
    return X.astype(float)


def modelos() -> dict:
    return {
        "regresion_logistica": make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000)),
        "random_forest": RandomForestClassifier(n_estimators=400, min_samples_leaf=3, random_state=SEMILLA,
                                                n_jobs=-1),
        "gradient_boosting": HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=300,
                                                            random_state=SEMILLA),
    }


def pares_gold(gold: pd.DataFrame, split: str) -> set:
    g = gold[gold.split == split]
    return set(zip(g.id_norma_modificatoria, g.id_norma_modificada))


def predichos(df: pd.DataFrame, prob: np.ndarray, umbral: float) -> set:
    sel = df[prob >= umbral]
    return set(zip(sel.id_norma_origen, sel.id_norma_destino))


def main(dataset: Path, corpus: Path, out: Path, incluir_test: bool) -> None:
    pares = pd.read_csv(dataset / "pares_candidatos.csv")
    gold = pd.read_csv(corpus / "gold_relaciones.csv")
    dev = pares[pares.split == "dev"].reset_index(drop=True)
    X, y, grupos = matriz(dev), dev.en_gold.to_numpy(), dev.id_norma_origen.to_numpy()
    gold_dev = pares_gold(gold, "dev")
    umbrales = np.round(np.arange(0.20, 0.81, 0.05), 2)

    # 1. validacion cruzada agrupada en dev: probabilidades fuera de la particion para cada modelo
    cv = GroupKFold(n_splits=5)
    resultados, oofs = {}, {}
    for nombre, modelo in modelos().items():
        oof = np.zeros(len(dev))
        for tr, va in cv.split(X, y, grupos):
            modelo.fit(X.iloc[tr], y[tr])
            oof[va] = modelo.predict_proba(X.iloc[va])[:, 1]
        oofs[nombre] = oof
        por_umbral = {float(u): prf(predichos(dev, oof, u), gold_dev) for u in umbrales}
        mejor = max(por_umbral, key=lambda u: por_umbral[u]["f1"])
        resultados[nombre] = {"umbral": mejor, "cv_dev": por_umbral[mejor],
                              "cv_dev_umbral_05": por_umbral[0.5]}
    elegido = max(resultados, key=lambda m: resultados[m]["cv_dev"]["f1"])
    umbral = resultados[elegido]["umbral"]

    # 2. modelo final: todo dev
    final = modelos()[elegido].fit(X, y)
    metricas = {"fecha": datetime.now(timezone.utc).isoformat(), "semilla": SEMILLA,
                "atributos": list(X.columns), "modelos": resultados, "elegido": elegido, "umbral": umbral}

    # en dev se guarda la probabilidad fuera de la particion: la del modelo final seria optimista
    filas = [dev.assign(prob=oofs[elegido])]
    if incluir_test:
        test = pares[pares.split == "test"].reset_index(drop=True)
        p_test = final.predict_proba(matriz(test, list(X.columns)))[:, 1]
        metricas["test"] = prf(predichos(test, p_test, umbral), pares_gold(gold, "test"))
        vistos_p = corpus / "pares_evaluados_en_v1.csv"
        if vistos_p.exists():
            v = pd.read_csv(vistos_p)
            vistos = set(zip(v.id_norma_modificatoria, v.id_norma_modificada))
            metricas["test_sin_pares_de_v1"] = prf(predichos(test, p_test, umbral) - vistos,
                                                   pares_gold(gold, "test") - vistos)
        filas.append(test.assign(prob=p_test))

    # 3. que atributos pesan
    if elegido == "regresion_logistica":
        imp = final[-1].coef_[0]
    elif elegido == "random_forest":
        imp = final.feature_importances_
    else:
        from sklearn.inspection import permutation_importance
        imp = permutation_importance(final, X, y, n_repeats=10, random_state=SEMILLA, scoring="f1").importances_mean
    importancia = pd.DataFrame({"atributo": X.columns, "importancia": imp}).sort_values(
        "importancia", key=np.abs, ascending=False)

    out.mkdir(parents=True, exist_ok=True)
    escribir_texto(out / "metricas.json", json.dumps(metricas, indent=2, ensure_ascii=False))
    pred = pd.concat(filas)[["id_norma_origen", "id_norma_destino", "split", "prob", "en_gold"]]
    pred["predicho"] = (pred.prob >= umbral).astype(int)
    pred.round(4).to_csv(out / "predicciones.csv", index=False, lineterminator="\n")
    importancia.round(4).to_csv(out / "importancia.csv", index=False, lineterminator="\n")

    print(f"{'modelo':22s} {'umbral':>6s} {'P':>6s} {'R':>6s} {'F1':>6s}  (CV agrupada en dev)")
    for m, r in resultados.items():
        c = r["cv_dev"]
        print(f"{m:22s} {r['umbral']:6.2f} {c['precision']:6.3f} {c['recall']:6.3f} {c['f1']:6.3f}")
    print(f"elegido: {elegido}, umbral {umbral}")
    if incluir_test:
        t = metricas["test"]
        print(f"test: P={t['precision']:.3f} R={t['recall']:.3f} F1={t['f1']:.3f}"
              + (f"  sin pares de v1: F1={metricas['test_sin_pares_de_v1']['f1']:.3f}"
                 if "test_sin_pares_de_v1" in metricas else ""))
    print(importancia.head(8).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path, default=Path("data/dataset"))
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    ap.add_argument("--out", type=Path, default=Path("results/clasificador"))
    ap.add_argument("--incluir-test", action="store_true")
    a = ap.parse_args()
    main(a.dataset, a.corpus, a.out, a.incluir_test)
