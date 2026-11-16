"""
13_modelo_contextual.py
Metodo basado en modelos "a partir del contexto textual" (consigna, alcance minimo) y primera
aproximacion al hibrido de la PI2.

El clasificador de 08 decide con atributos de superficie (cuantas menciones, en que zona, si hay
verbo). Aca el modelo lee las palabras que rodean cada mencion:

  1. Para cada par candidato (origen -> destino) se juntan los fragmentos de texto de todas sus
     menciones (+-150 caracteres alrededor de cada una, ya guardados por el parser en
     evidencias.csv). La mencion del destino se reemplaza por la palabra DESTINO y los digitos
     por '#', para que el modelo aprenda el contexto ("sustituyese el articulo # de la DESTINO")
     y no memorice numeros de normas. Cada fragmento lleva delante la parte del documento donde
     esta (PARTE_visto, PARTE_articulado, ...).
  2. Representacion TF-IDF de unigramas y bigramas de palabras.
  3. Regresion logistica. Dos variantes:
       contexto            solo el texto
       contexto+superficie el texto y los atributos de superficie de data/dataset/pares_candidatos.csv
  4. Mismo protocolo que 08: validacion cruzada de 5 particiones en dev agrupada por norma origen
     para elegir C y umbral; modelo final con todo dev; test evaluado una vez.

Hibrido (reglas + modelo). Las reglas son muy confiables en algunos casos y dudosas en otros.
Se separan los candidatos en tres grupos segun las mismas evidencias que usa la regla F:
  seguro_si   hay una mencion en el VISTO, o en el articulado con verbo modificatorio en la oracion
  seguro_no   ninguna mencion cuenta (solo notas, anexos, citas de procedencia o destino posterior)
  zona_gris   el resto: menciones en el articulado sin verbo, solo en el CONSIDERANDO o solo por alias
Las reglas deciden los dos primeros grupos; el modelo contextual decide la zona gris, con su
propio umbral elegido en la validacion cruzada de dev.

Todas las metricas se calculan contra TODO el gold del split (un par del gold que no es candidato
cuenta como falso negativo), igual que las reglas y el clasificador de 08.

Salidas en results/modelo_contextual/: metricas.json, predicciones.csv, terminos.csv (los n-gramas
con mas peso, para el analisis), comparacion.csv (reglas vs modelos vs hibrido).

Uso:
    python scripts/13_modelo_contextual.py              # solo dev
    python scripts/13_modelo_contextual.py --incluir-test
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto              # noqa: E402
from grafo_legal.evaluacion import prf                       # noqa: E402

SEMILLA = 20261116
NO_ATRIBUTOS = ["id_norma_origen", "id_norma_destino", "split", "en_gold"]
CATEGORICOS = ["tipo_origen", "tipo_destino"]
UMBRALES = np.round(np.arange(0.20, 0.81, 0.05), 2)
VALORES_C = [0.3, 1.0, 3.0, 10.0, 30.0, 100.0]


# --------------------------------------------------------------------------------------------
# 1. Texto de cada par candidato
# --------------------------------------------------------------------------------------------
def limpiar_fragmento(frag: str, superficie: str, parte: str) -> str:
    """Marca la mencion del destino, borra los numeros y antepone la parte del documento."""
    frag = str(frag)
    sup = str(superficie)
    if sup and sup in frag:
        frag = frag.replace(sup, " DESTINO ", 1)
    frag = re.sub(r"\d", "#", frag)
    return f"PARTE_{parte} {frag}"


def textos_por_par(evidencias: pd.DataFrame, max_frag: int = 12) -> pd.DataFrame:
    """Una fila por par (origen, destino) con el texto concatenado de sus menciones."""
    ev = evidencias.copy()
    ev["texto"] = [limpiar_fragmento(f, s, p) for f, s, p in zip(ev.fragmento, ev.superficie, ev.parte)]
    ev = ev.sort_values(["id_origen", "id_destino", "inicio"], kind="mergesort")
    filas = []
    for (o, d), g in ev.groupby(["id_origen", "id_destino"], sort=False):
        filas.append({"id_norma_origen": o, "id_norma_destino": d, "texto": " || ".join(g.texto.head(max_frag))})
    return pd.DataFrame(filas)


# --------------------------------------------------------------------------------------------
# 2. Grupos de confianza de las reglas (para el hibrido)
# --------------------------------------------------------------------------------------------
def grupo_regla(evidencias: pd.DataFrame) -> pd.DataFrame:
    ev = evidencias.copy()
    ev["verbo_oracion"] = ev.verbo_oracion.fillna("").astype(str)
    cuenta = ev.temporal_ok.astype(bool) & ~ev.procedencia.astype(bool) & ~ev.zona.isin(["notas", "anexo"])
    seguro = cuenta & ((ev.parte == "visto")
                       | ((ev.zona == "articulado") & (ev.metodo == "regex_numero") & (ev.verbo_oracion != "")))
    # regla F (reglas_v2.CONFIGS["F_visto_o_articulado_con_verbo_o_ley"]), por evidencia
    regla_f = (ev.temporal_ok.astype(bool) & ~ev.procedencia.astype(bool)) & (
        (ev.parte == "visto") | ((ev.zona == "articulado") & (ev.metodo == "regex_numero")
                                 & ((ev.tipo_origen != "decreto") | (ev.verbo_oracion != ""))))
    ev = ev.assign(_cuenta=cuenta, _seguro=seguro, _f=regla_f)
    g = ev.groupby(["id_origen", "id_destino"]).agg(cuenta=("_cuenta", "any"), seguro=("_seguro", "any"),
                                                     regla_f=("_f", "any")).reset_index()
    g["grupo"] = np.where(g.seguro, "seguro_si", np.where(~g.cuenta, "seguro_no", "zona_gris"))
    return g.rename(columns={"id_origen": "id_norma_origen", "id_destino": "id_norma_destino"})


# --------------------------------------------------------------------------------------------
# 3. Modelo
# --------------------------------------------------------------------------------------------
def atributos_superficie(df: pd.DataFrame, columnas=None) -> pd.DataFrame:
    X = pd.get_dummies(df.drop(columns=NO_ATRIBUTOS + ["texto", "grupo", "regla_f", "cuenta", "seguro"],
                               errors="ignore"), columns=CATEGORICOS, dtype=float)
    if columnas is not None:
        X = X.reindex(columns=columnas, fill_value=0.0)
    return X.astype(float)


class ModeloContextual:
    """TF-IDF de los fragmentos (+ atributos de superficie escalados) -> regresion logistica."""

    def __init__(self, C: float, con_superficie: bool):
        self.C, self.con_superficie = C, con_superficie

    def _X(self, df, ajustar: bool):
        if ajustar:
            self.vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True,
                                       strip_accents="unicode", lowercase=True)
            T = self.vec.fit_transform(df.texto)
        else:
            T = self.vec.transform(df.texto)
        if not self.con_superficie:
            return T
        if ajustar:
            S = atributos_superficie(df)
            self.cols = list(S.columns)
            self.esc = StandardScaler().fit(S)
        else:
            S = atributos_superficie(df, self.cols)
        return hstack([T, csr_matrix(self.esc.transform(S))]).tocsr()

    def fit(self, df, y):
        self.lr = LogisticRegression(C=self.C, max_iter=5000, class_weight=None)
        self.lr.fit(self._X(df, True), y)
        return self

    def predict_proba(self, df):
        return self.lr.predict_proba(self._X(df, False))[:, 1]


def pares(df, mask) -> set:
    s = df[mask]
    return set(zip(s.id_norma_origen, s.id_norma_destino))


def pares_gold(gold, split) -> set:
    g = gold[gold.split == split]
    return set(zip(g.id_norma_modificatoria, g.id_norma_modificada))


def hibrido(df, prob, umbral) -> set:
    """Reglas para los grupos seguros, modelo para la zona gris."""
    m = (df.grupo == "seguro_si").to_numpy() | ((df.grupo == "zona_gris").to_numpy() & (prob >= umbral))
    return pares(df, m)


def main(dataset: Path, corpus: Path, evid: Path, out: Path, incluir_test: bool) -> None:
    cand = pd.read_csv(dataset / "pares_candidatos.csv")
    ev = pd.read_csv(evid, keep_default_na=False, dtype={"verbo_oracion": str})
    ev["temporal_ok"] = ev.temporal_ok.astype(str) == "True"
    ev["procedencia"] = ev.procedencia.astype(str) == "True"
    gold = pd.read_csv(corpus / "gold_relaciones.csv")

    df = (cand.merge(textos_por_par(ev), on=["id_norma_origen", "id_norma_destino"], how="left")
              .merge(grupo_regla(ev), on=["id_norma_origen", "id_norma_destino"], how="left"))
    df["texto"] = df.texto.fillna("")
    df["grupo"] = df.grupo.fillna("seguro_no")
    df["regla_f"] = df.regla_f.fillna(False).astype(bool)

    dev = df[df.split == "dev"].reset_index(drop=True)
    y, grupos = dev.en_gold.to_numpy(), dev.id_norma_origen.to_numpy()
    gold_dev = pares_gold(gold, "dev")
    cv = GroupKFold(n_splits=5)

    # --- validacion cruzada: probabilidades fuera de la particion para cada variante y C ---
    resultados, oofs = {}, {}
    for variante, con_sup in (("contexto", False), ("contexto+superficie", True)):
        mejor = None
        for C in VALORES_C:
            oof = np.zeros(len(dev))
            for tr, va in cv.split(dev, y, grupos):
                oof[va] = ModeloContextual(C, con_sup).fit(dev.iloc[tr], y[tr]).predict_proba(dev.iloc[va])
            for u in UMBRALES:
                r = prf(pares(dev, oof >= u), gold_dev)
                h = prf(hibrido(dev, oof, u), gold_dev)
                if mejor is None or r["f1"] > mejor["cv_dev"]["f1"]:
                    mejor = {"C": C, "umbral": float(u), "cv_dev": r, "_oof": oof}
                key = f"{variante}|hibrido"
                if key not in resultados or h["f1"] > resultados[key]["cv_dev"]["f1"]:
                    resultados[key] = {"C": C, "umbral": float(u), "cv_dev": h, "_oof": oof}
        resultados[variante] = mejor
    for k in resultados:
        oofs[k] = resultados[k].pop("_oof")

    # --- referencias sobre el mismo dev: reglas F y clasificador de superficie (08) ---
    ref = {"reglas_F": {"dev": prf(pares(dev, dev.regla_f.to_numpy()), gold_dev)}}
    clf_p = Path("results/clasificador/predicciones.csv")
    clf = pd.read_csv(clf_p) if clf_p.exists() else None
    if clf is not None:
        u08 = json.load(open("results/clasificador/metricas.json"))["umbral"]
        c_dev = clf[clf.split == "dev"]
        ref["clasificador_superficie_08"] = {"dev": prf(pares(c_dev, c_dev.prob >= u08), gold_dev)}

    metricas = {"fecha": datetime.now(timezone.utc).isoformat(), "semilla": SEMILLA,
                "candidatos_dev": int(len(dev)), "grupos_dev": dev.grupo.value_counts().to_dict(),
                "en_gold_por_grupo_dev": dev.groupby("grupo").en_gold.mean().round(3).to_dict(),
                "variantes": resultados, "referencias": ref}

    # una columna de probabilidad por variante (cada una con su C); "prob_contexto" y
    # "prob_contexto_sup" son las de las variantes no hibridas
    col = {k: "prob_" + k.replace("+superficie", "_sup").replace("|", "_") for k in resultados}
    filas = [dev.assign(**{col[k]: oofs[k] for k in resultados})]
    finales = {}
    if incluir_test:
        test = df[df.split == "test"].reset_index(drop=True)
        gold_test = pares_gold(gold, "test")
        probs = {}
        for k, r in resultados.items():
            variante = k.split("|")[0]
            m = ModeloContextual(r["C"], variante == "contexto+superficie").fit(dev, y)
            finales[k] = m
            p = m.predict_proba(test)
            probs[k] = p
            r["test"] = prf(hibrido(test, p, r["umbral"]) if k.endswith("hibrido")
                            else pares(test, p >= r["umbral"]), gold_test)
        ref["reglas_F"]["test"] = prf(pares(test, test.regla_f.to_numpy()), gold_test)
        if clf is not None:
            c_t = clf[clf.split == "test"]
            ref["clasificador_superficie_08"]["test"] = prf(pares(c_t, c_t.prob >= u08), gold_test)
        metricas["grupos_test"] = test.grupo.value_counts().to_dict()
        filas.append(test.assign(**{col[k]: probs[k] for k in resultados}))

    # --- n-gramas con mas peso del modelo de solo contexto (entrenado con todo dev) ---
    m_ctx = finales.get("contexto") or ModeloContextual(resultados["contexto"]["C"], False).fit(dev, y)
    voc = np.array(m_ctx.vec.get_feature_names_out())
    coef = m_ctx.lr.coef_[0][: len(voc)]
    orden = np.argsort(coef)
    terminos = pd.DataFrame({"termino": np.r_[voc[orden[::-1][:30]], voc[orden[:30]]],
                             "peso": np.r_[coef[orden[::-1][:30]], coef[orden[:30]]]})

    out.mkdir(parents=True, exist_ok=True)
    escribir_texto(out / "metricas.json", json.dumps(metricas, indent=2, ensure_ascii=False))
    pd.concat(filas)[["id_norma_origen", "id_norma_destino", "split", "grupo", "regla_f",
                      *col.values(), "en_gold"]].round(4).to_csv(
        out / "predicciones.csv", index=False, lineterminator="\n")
    terminos.round(4).to_csv(out / "terminos.csv", index=False, lineterminator="\n")

    comp = []
    for nombre, d in ref.items():
        for s, m in d.items():
            comp.append({"metodo": nombre, "split": s, **{k: m[k] for k in ("precision", "recall", "f1", "tp", "fp", "fn")}})
    for k, r in resultados.items():
        comp.append({"metodo": k, "split": "dev_cv", **{x: r["cv_dev"][x] for x in ("precision", "recall", "f1", "tp", "fp", "fn")}})
        if "test" in r:
            comp.append({"metodo": k, "split": "test", **{x: r["test"][x] for x in ("precision", "recall", "f1", "tp", "fp", "fn")}})
    pd.DataFrame(comp).to_csv(out / "comparacion.csv", index=False, lineterminator="\n")
    print(pd.DataFrame(comp).to_string(index=False))
    print({k: (r["C"], r["umbral"]) for k, r in resultados.items()})
    print(metricas["grupos_dev"], metricas["en_gold_por_grupo_dev"])
    print(terminos.head(15).to_string(index=False))
    print(terminos.tail(15).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path, default=Path("data/dataset"))
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    ap.add_argument("--evidencias", type=Path, default=Path("results/reglas_v2/evidencias.csv"))
    ap.add_argument("--out", type=Path, default=Path("results/modelo_contextual"))
    ap.add_argument("--incluir-test", action="store_true")
    a = ap.parse_args()
    main(a.dataset, a.corpus, a.evidencias, a.out, a.incluir_test)
