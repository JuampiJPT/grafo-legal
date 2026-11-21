"""
32_curva_aprendizaje.py
Curva de aprendizaje de los dos modelos supervisados (bitacora B68).

Pregunta: los modelos de los scripts 08 y 13 empatan o pierden contra las reglas.
Es porque se entrenaron con pocos datos, o porque su representacion no alcanza?

Metodo (solo dev; test no se toca, regla de la bitacora B16):
  - Validacion cruzada agrupada por norma de origen (GroupKFold, 5 particiones), igual que 08 y 13.
  - En cada particion se entrena con una FRACCION de las normas de origen del entrenamiento
    (10 %, 20 %, 30 %, 50 %, 70 %, 100 %), sorteada REPETICIONES veces. Se submuestrea por norma,
    no por par, para que la curva mida "cuantas normas etiquetadas hacen falta".
  - Se evalua siempre sobre la misma particion de validacion, completa.
  - Hiperparametros FIJOS, los que eligieron 08 y 13 con todo dev (no se re-eligen por fraccion):
      random forest: 400 arboles, min_samples_leaf=3, umbral 0.45
      contexto+superficie (TF-IDF + 22 atributos, regresion logistica): C=30, umbral 0.20
      contexto solo (TF-IDF, regresion logistica): C=10, umbral 0.40
  - Metricas a nivel de par candidato (etiqueta en_gold):
      F1 con el umbral fijo, y precision promedio (AP, area bajo la curva precision-recall),
      que no depende del umbral.
      Tambien F1 sobre los datos de entrenamiento, para ver la brecha de sobreajuste.
  - Referencia: la regla F de las reglas v2 (columna regla_f), que no se entrena.

Nota: estas F1 son sobre candidatos (lo que el clasificador puede decidir), no sobre el gold completo
como en 08 y 13. El gold completo agrega los pares que el detector no propone, que ningun clasificador
puede recuperar (techo de recall de los candidatos en dev: 0,81).

Salidas en results/curva_aprendizaje/: curva.csv (una fila por modelo, fraccion, particion y repeticion),
resumen.csv (media y desvio por modelo y fraccion), metricas.json, RESULTADOS.md se escribe a mano.
Figura: docs/informe_avance/figuras/fig8_curva_aprendizaje.png

Uso:
    python scripts/32_curva_aprendizaje.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, f1_score
from sklearn.model_selection import GroupKFold

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from grafo_legal.archivos import escribir_texto  # noqa: E402

SEMILLA = 20261121
FRACCIONES = [0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
REPETICIONES = 5


def cargar_modulo(nombre: str, archivo: str):
    """Importa un script cuyo nombre empieza con numero (08_..., 13_...)."""
    spec = importlib.util.spec_from_file_location(nombre, RAIZ / "scripts" / archivo)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m08 = cargar_modulo("clasificador", "08_clasificador.py")
m13 = cargar_modulo("contextual", "13_modelo_contextual.py")


def armar_dev() -> pd.DataFrame:
    """Mismo armado que el script 13: candidatos + texto de las menciones + grupo de las reglas."""
    cand = pd.read_csv(RAIZ / "data/dataset/pares_candidatos.csv")
    ev = pd.read_csv(RAIZ / "results/reglas_v2/evidencias.csv", keep_default_na=False,
                     dtype={"verbo_oracion": str})
    ev["temporal_ok"] = ev.temporal_ok.astype(str) == "True"
    ev["procedencia"] = ev.procedencia.astype(str) == "True"
    df = (cand.merge(m13.textos_por_par(ev), on=["id_norma_origen", "id_norma_destino"], how="left")
              .merge(m13.grupo_regla(ev), on=["id_norma_origen", "id_norma_destino"], how="left"))
    df["texto"] = df.texto.fillna("")
    df["grupo"] = df.grupo.fillna("seguro_no")
    df["regla_f"] = df.regla_f.fillna(False).astype(bool)
    return df[df.split == "dev"].reset_index(drop=True)


# Cada modelo: (funcion que entrena y devuelve un predictor de probabilidades, umbral fijo)
def ajustar_rf(tr: pd.DataFrame):
    cols_rf = list(m08.matriz(dev_global[m08.NO_ATRIBUTOS + COLS_08]).columns)
    X = m08.matriz(tr[m08.NO_ATRIBUTOS + COLS_08], cols_rf)
    rf = RandomForestClassifier(n_estimators=400, min_samples_leaf=3, random_state=SEMILLA, n_jobs=-1)
    rf.fit(X, tr.en_gold)
    return lambda d: rf.predict_proba(m08.matriz(d[m08.NO_ATRIBUTOS + COLS_08], cols_rf))[:, 1]


def ajustar_ctx(C: float, con_sup: bool):
    def f(tr: pd.DataFrame):
        m = m13.ModeloContextual(C, con_sup).fit(tr, tr.en_gold.to_numpy())
        return m.predict_proba
    return f


MODELOS = {
    "random_forest_22_atributos": (ajustar_rf, 0.45),
    "tfidf_contexto+superficie": (ajustar_ctx(30.0, True), 0.20),
    "tfidf_contexto": (ajustar_ctx(10.0, False), 0.40),
}


def main() -> None:
    global dev_global, COLS_08
    dev = armar_dev()
    dev_global = dev
    cand_cols = pd.read_csv(RAIZ / "data/dataset/pares_candidatos.csv", nrows=1).columns
    COLS_08 = [c for c in cand_cols if c not in m08.NO_ATRIBUTOS]   # los 22 atributos del script 08
    y = dev.en_gold.to_numpy()
    grupos = dev.id_norma_origen.to_numpy()
    rng = np.random.default_rng(SEMILLA)
    filas = []

    for k, (tr_idx, va_idx) in enumerate(GroupKFold(n_splits=5).split(dev, y, grupos)):
        tr_all, va = dev.iloc[tr_idx], dev.iloc[va_idx]
        normas_tr = np.unique(tr_all.id_norma_origen)
        # referencia: la regla F no se entrena, su valor es el mismo en todas las fracciones
        filas.append({"modelo": "reglas_F", "fraccion": np.nan, "particion": k, "rep": 0,
                      "n_normas": 0, "n_pares": 0, "n_pos": 0,
                      "f1_val": f1_score(va.en_gold, va.regla_f), "ap_val": np.nan, "f1_train": np.nan})
        for frac in FRACCIONES:
            reps = 1 if frac == 1.0 else REPETICIONES
            for r in range(reps):
                elegidas = rng.choice(normas_tr, size=max(2, round(frac * len(normas_tr))), replace=False)
                tr = tr_all[tr_all.id_norma_origen.isin(elegidas)]
                if tr.en_gold.nunique() < 2:          # muestra sin las dos clases: no se puede entrenar
                    continue
                for nombre, (ajustar, umbral) in MODELOS.items():
                    pred = ajustar(tr)
                    p_va, p_tr = pred(va), pred(tr)
                    filas.append({"modelo": nombre, "fraccion": frac, "particion": k, "rep": r,
                                  "n_normas": len(elegidas), "n_pares": len(tr), "n_pos": int(tr.en_gold.sum()),
                                  "f1_val": f1_score(va.en_gold, p_va >= umbral),
                                  "ap_val": average_precision_score(va.en_gold, p_va),
                                  "f1_train": f1_score(tr.en_gold, p_tr >= umbral)})
        print(f"particion {k} lista", flush=True)

    curva = pd.DataFrame(filas)
    out = RAIZ / "results/curva_aprendizaje"
    out.mkdir(parents=True, exist_ok=True)
    curva.round(4).to_csv(out / "curva.csv", index=False, lineterminator="\n")

    # promedio por particion primero (las repeticiones son ruido de muestreo), despues entre particiones
    por_part = curva.groupby(["modelo", "fraccion", "particion"], dropna=False).mean(numeric_only=True).reset_index()
    resumen = (por_part.groupby(["modelo", "fraccion"], dropna=False)
               .agg(n_normas=("n_normas", "mean"), n_pares=("n_pares", "mean"),
                    f1_val=("f1_val", "mean"), f1_val_sd=("f1_val", "std"),
                    ap_val=("ap_val", "mean"), ap_val_sd=("ap_val", "std"),
                    f1_train=("f1_train", "mean"))
               .reset_index())
    resumen.round(4).to_csv(out / "resumen.csv", index=False, lineterminator="\n")

    # pendiente de la ultima tramo (50 % -> 100 %): cuanto F1 se gana por cada 100 pares mas
    pend = {}
    for nombre in MODELOS:
        s = resumen[resumen.modelo == nombre].set_index("fraccion")
        pend[nombre] = {
            "f1_por_100_pares_50a100": round(100 * (s.f1_val[1.0] - s.f1_val[0.5]) / (s.n_pares[1.0] - s.n_pares[0.5]), 4),
            "ap_por_100_pares_50a100": round(100 * (s.ap_val[1.0] - s.ap_val[0.5]) / (s.n_pares[1.0] - s.n_pares[0.5]), 4),
            "brecha_train_val_100": round(s.f1_train[1.0] - s.f1_val[1.0], 4),
        }
    escribir_texto(out / "metricas.json", json.dumps(
        {"semilla": SEMILLA, "fracciones": FRACCIONES, "repeticiones": REPETICIONES,
         "pares_dev": len(dev), "normas_dev": int(dev.id_norma_origen.nunique()),
         "pendientes": pend}, indent=2, ensure_ascii=False))
    print(resumen.round(3).to_string(index=False))
    print(json.dumps(pend, indent=2))
    figura(resumen)


def figura(resumen: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colores = {"random_forest_22_atributos": "#2a6fdb", "tfidf_contexto+superficie": "#e07b39",
               "tfidf_contexto": "#8a8a8a"}
    etiquetas = {"random_forest_22_atributos": "Random forest (22 atributos)",
                 "tfidf_contexto+superficie": "TF-IDF + atributos (reg. logística)",
                 "tfidf_contexto": "TF-IDF solo (reg. logística)"}
    fig, ejes = plt.subplots(1, 2, figsize=(11, 4.2), dpi=150)
    for ax, met, titulo in ((ejes[0], "f1_val", "F1 en validación (umbral fijo)"),
                            (ejes[1], "ap_val", "Precisión promedio en validación")):
        for nombre, color in colores.items():
            s = resumen[resumen.modelo == nombre].sort_values("n_pares")
            ax.errorbar(s.n_pares, s[met], yerr=s[met + "_sd"], color=color, marker="o", ms=5, lw=2,
                        capsize=3, label=etiquetas[nombre])
        if met == "f1_val":
            ref = resumen[resumen.modelo == "reglas_F"].f1_val.iloc[0]
            ax.axhline(ref, color="#333333", ls="--", lw=1.2, label="Reglas F (sin entrenar)")
        ax.set_title(titulo, fontsize=11)
        ax.set_xlabel("pares de entrenamiento (dev, por partición)")
        ax.grid(alpha=0.25)
        ax.spines[["top", "right"]].set_visible(False)
    ejes[0].legend(fontsize=8, frameon=False, loc="lower right")
    fig.tight_layout()
    dest = RAIZ / "docs/informe_avance/figuras/fig8_curva_aprendizaje.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest)
    print("figura:", dest)


if __name__ == "__main__":
    main()
