"""
17_comparar_metodos.py
Tabla final de la PI1/PI2: todos los metodos sobre el mismo test, con intervalos de confianza.

Metodos (cada uno ya evaluado una vez en test por su propio script):
  reglas_v2_F                 regla F (04_evaluar.py)
  clasificador_superficie     random forest de 08
  contexto, contexto+superficie, y sus hibridos con las reglas (13)
  llm y sus hibridos con las reglas (15), si existe la salida del LLM

Intervalos: bootstrap pareado por norma origen (las relaciones de una misma norma no son
independientes, asi que se remuestrean normas, no pares). 2000 replicas, semilla fija. Para cada
metodo se da el F1 con su intervalo del 95 %, y la diferencia de F1 contra las reglas con su
intervalo: si el intervalo de la diferencia contiene al 0, la diferencia no es significativa.

Salida: results/comparacion/comparacion_test.csv y metricas.json.

Uso:
    python scripts/17_comparar_metodos.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto       # noqa: E402

SEMILLA = 20261116
REPLICAS = 2000


def f1(pred: set, gold: set) -> float:
    tp = len(pred & gold)
    return 2 * tp / (len(pred) + len(gold)) if pred or gold else 0.0


def main() -> None:
    gold_df = pd.read_csv("data/corpus/gold_relaciones.csv")
    gold = set(zip(gold_df[gold_df.split == "test"].id_norma_modificatoria,
                   gold_df[gold_df.split == "test"].id_norma_modificada))
    normas = pd.read_csv("data/corpus/corpus_normas.csv")
    origenes = sorted(set(normas[normas.split == "test"].id_norma))

    metodos: dict[str, set] = {}
    # reglas F
    ev = pd.read_csv("results/reglas_v2/evidencias.csv", keep_default_na=False)
    ok = (ev.temporal_ok.astype(str) == "True") & (ev.procedencia.astype(str) != "True")
    f = ok & ((ev.parte == "visto") | ((ev.zona == "articulado") & (ev.metodo == "regex_numero")
                                       & ((ev.tipo_origen != "decreto") | (ev.verbo_oracion != ""))))
    metodos["reglas_v2_F"] = set(zip(ev[f].id_origen, ev[f].id_destino))
    # reglas v3, configuracion F3 (F + alias con verbo en el articulado)
    v3p = Path("results/reglas_v3/evidencias.csv")
    if v3p.exists():
        e3 = pd.read_csv(v3p, keep_default_na=False)
        ok3 = (e3.temporal_ok.astype(str) == "True") & (e3.procedencia.astype(str) != "True")
        f3 = ok3 & ((e3.parte == "visto") | ((e3.zona == "articulado") & (e3.metodo == "regex_numero")
                                             & ((e3.tipo_origen != "decreto") | (e3.verbo_oracion != "")))
                    | ((e3.zona == "articulado") & (e3.metodo == "alias") & (e3.verbo_oracion != "")))
        metodos["reglas_v3_F3"] = set(zip(e3[f3].id_origen, e3[f3].id_destino))
    # parser hibrido en cascada (reglas filtran, LLM decide la zona gris; script 20)
    hp = Path("results/hibrido/relaciones_hibrido.csv")
    if hp.exists():
        h = pd.read_csv(hp, keep_default_na=False)
        h = h[h.tipo != "CITA"]          # un par es vinculo si tiene alguna relacion que no es CITA
        metodos["hibrido_cascada"] = set(zip(h.id_norma_origen.astype(int), h.id_norma_destino.astype(int)))
    # clasificador de superficie
    c = pd.read_csv("results/clasificador/predicciones.csv")
    c = c[(c.split == "test") & (c.predicho == 1)]
    metodos["clasificador_superficie"] = set(zip(c.id_norma_origen, c.id_norma_destino))
    # modelo contextual e hibridos
    mc = json.load(open("results/modelo_contextual/metricas.json"))["variantes"]
    p = pd.read_csv("results/modelo_contextual/predicciones.csv")
    p = p[p.split == "test"]
    for k, r in mc.items():
        prob = p["prob_" + k.replace("+superficie", "_sup").replace("|", "_")]
        if k.endswith("hibrido"):
            m = (p.grupo == "seguro_si") | ((p.grupo == "zona_gris") & (prob >= r["umbral"]))
        else:
            m = prob >= r["umbral"]
        metodos[k.replace("|", "_")] = set(zip(p[m].id_norma_origen, p[m].id_norma_destino))
    # LLM, si existe
    llm_p = Path("results/evaluacion_llm/metricas.json")
    if llm_p.exists():
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import importlib
        ev_llm = importlib.import_module("15_evaluar_llm")
        m = json.load(open(llm_p))
        r = pd.read_csv("results/relaciones_llm/relaciones_llm.csv", keep_default_na=False)
        tipo = dict(zip(normas.id_norma, normas.tipo_norma.str.lower()))
        fecha = dict(zip(normas.id_norma, normas.fecha_boletin.fillna(normas.fecha_sancion)))
        r["tipo_origen"] = r.id_norma_origen.map(tipo)
        fo, fd = r.id_norma_origen.map(fecha), r.id_norma_destino.map(fecha)
        r = r[~(fo.notna() & fd.notna() & (fd > fo))]
        sel = r[ev_llm.PROYECCIONES[m["proyeccion_elegida_en_dev"]](r)]
        llm = set(zip(sel.id_norma_origen, sel.id_norma_destino))
        metodos["llm"] = llm
        metodos["hibrido_reglas_union_llm"] = metodos["reglas_v2_F"] | llm
        metodos["hibrido_reglas_interseccion_llm"] = metodos["reglas_v2_F"] & llm

    metodos = {k: {x for x in v if x[0] in set(origenes)} for k, v in metodos.items()}
    por_origen_gold = {o: {x for x in gold if x[0] == o} for o in origenes}
    por_origen = {k: {o: {x for x in v if x[0] == o} for o in origenes} for k, v in metodos.items()}

    rng = np.random.default_rng(SEMILLA)
    muestras = [rng.choice(len(origenes), len(origenes), replace=True) for _ in range(REPLICAS)]
    base = "reglas_v2_F"
    filas = []
    f1_base = []
    for idx in muestras:
        os_ = [origenes[i] for i in idx]
        # en el remuestreo una norma puede salir dos veces: se etiquetan las copias
        g = {(j, x) for j, o in enumerate(os_) for x in por_origen_gold[o]}
        f1_base.append(f1({(j, x) for j, o in enumerate(os_) for x in por_origen[base][o]}, g))
    f1_base = np.array(f1_base)
    for k in metodos:
        vals = []
        for idx in muestras:
            os_ = [origenes[i] for i in idx]
            g = {(j, x) for j, o in enumerate(os_) for x in por_origen_gold[o]}
            vals.append(f1({(j, x) for j, o in enumerate(os_) for x in por_origen[k][o]}, g))
        vals = np.array(vals)
        d = vals - f1_base
        pred = metodos[k]
        tp = len(pred & gold)
        filas.append({"metodo": k, "precision": round(tp / len(pred), 4) if pred else 0,
                      "recall": round(tp / len(gold), 4), "f1": round(f1(pred, gold), 4),
                      "f1_ic95_inf": round(float(np.percentile(vals, 2.5)), 4),
                      "f1_ic95_sup": round(float(np.percentile(vals, 97.5)), 4),
                      "dif_vs_reglas": round(f1(pred, gold) - f1(metodos[base], gold), 4),
                      "dif_ic95_inf": round(float(np.percentile(d, 2.5)), 4),
                      "dif_ic95_sup": round(float(np.percentile(d, 97.5)), 4)})
    t = pd.DataFrame(filas).sort_values("f1", ascending=False)
    out = Path("results/comparacion")
    out.mkdir(parents=True, exist_ok=True)
    t.to_csv(out / "comparacion_test.csv", index=False, lineterminator="\n")
    escribir_texto(out / "metricas.json", json.dumps({"semilla": SEMILLA, "replicas": REPLICAS,
                                                      "normas_origen_test": len(origenes),
                                                      "pares_gold_test": len(gold),
                                                      "metodos": filas}, indent=2, ensure_ascii=False))
    print(t.to_string(index=False))


if __name__ == "__main__":
    main()
