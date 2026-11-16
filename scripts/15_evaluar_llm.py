"""
15_evaluar_llm.py
Evalua el parser LLM contra el gold de InfoLEG con el mismo protocolo que las reglas, y lo combina
con las reglas (hibrido reglas + LLM). El gold se usa solo para medir.

1. Proyeccion a pares de normas. El LLM devuelve relaciones tipadas por articulo; InfoLEG solo
   dice "A modifica o complementa a B". Se prueban varias proyecciones y se elige UNA en dev:
     sin_cita            el par tiene alguna relacion que no es CITA
     visto_o_sin_cita    ademas, cualquier mencion del VISTO cuenta (como en la regla F)
     regla_F_sobre_llm   la regla F aplicada a las relaciones del LLM (VISTO, o articulado y no
                         CITA o el origen no es un decreto)
     todas               cualquier relacion
   En todas se exige que el destino no sea posterior al origen (la misma restriccion temporal
   de las reglas: una norma no puede modificar a otra que todavia no existe).
2. Hibridos con las reglas, sobre la proyeccion elegida:
     union         reglas F o LLM (mas recall)
     interseccion  reglas F y LLM (mas precision)
3. Diagnostico del LLM: tasa de citas que no estan en el texto, referencias no resueltas.

Salidas en results/evaluacion_llm/: metricas.json, comparacion.csv y errores.csv.

Uso:
    python scripts/15_evaluar_llm.py
    python scripts/15_evaluar_llm.py --relaciones results/relaciones_llm_haiku/relaciones_llm.csv \
        --out results/evaluacion_llm_haiku
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto                 # noqa: E402
from grafo_legal.evaluacion import prf                          # noqa: E402

PROYECCIONES = {
    "sin_cita": lambda r: r.tipo != "CITA",
    "visto_o_sin_cita": lambda r: (r.parte_origen == "visto") | (r.tipo != "CITA"),
    "regla_F_sobre_llm": lambda r: (r.parte_origen == "visto") | (
        (r.parte_origen == "articulado") & ((r.tipo != "CITA") | (r.tipo_origen != "decreto"))),
    "todas": lambda r: pd.Series(True, index=r.index),
}


def pares(df) -> set:
    return set(zip(df.id_norma_origen.astype(int), df.id_norma_destino.astype(int)))


def main(corpus: Path, rel_llm: Path, rel_reglas: Path, ev_reglas: Path, out: Path) -> None:
    normas = pd.read_csv(corpus / "corpus_normas.csv", dtype=str, keep_default_na=False)
    normas["fecha"] = normas.fecha_boletin.where(normas.fecha_boletin != "", normas.fecha_sancion)
    fecha = dict(zip(normas.id_norma.astype(int), normas.fecha))
    tipo = dict(zip(normas.id_norma.astype(int), normas.tipo_norma.str.lower()))
    split = dict(zip(normas.id_norma.astype(int), normas.split))
    gold = pd.read_csv(corpus / "gold_relaciones.csv")
    g = {s: set(zip(gold[gold.split == s].id_norma_modificatoria, gold[gold.split == s].id_norma_modificada))
         for s in ("dev", "test")}

    r = pd.read_csv(rel_llm, keep_default_na=False, dtype={"articulo_destino": str})
    r["tipo_origen"] = r.id_norma_origen.map(tipo)
    # restriccion temporal, igual que en las reglas
    fo, fd = r.id_norma_origen.map(fecha), r.id_norma_destino.map(fecha)
    r = r[~((fo != "") & (fd != "") & (fd > fo))]

    # pares de la regla F de las reglas v2 (mismas evidencias que 04_evaluar.py)
    ev = pd.read_csv(ev_reglas, keep_default_na=False)
    ok = (ev.temporal_ok.astype(str) == "True") & (ev.procedencia.astype(str) != "True")
    f = ok & ((ev.parte == "visto") | ((ev.zona == "articulado") & (ev.metodo == "regex_numero")
                                       & ((ev.tipo_origen != "decreto") | (ev.verbo_oracion != ""))))
    reglas = set(zip(ev[f].id_origen, ev[f].id_destino))

    res = {"fecha": datetime.now(timezone.utc).isoformat(), "relaciones_llm": len(r), "proyecciones": {}}
    for nombre, filtro in PROYECCIONES.items():
        p = pares(r[filtro(r)])
        res["proyecciones"][nombre] = {s: prf({x for x in p if split.get(x[0]) == s}, g[s]) for s in ("dev", "test")}
    elegida = max(PROYECCIONES, key=lambda n: res["proyecciones"][n]["dev"]["f1"])
    res["proyeccion_elegida_en_dev"] = elegida
    llm = pares(r[PROYECCIONES[elegida](r)])

    filas = []
    for metodo, p in (("reglas_F", reglas), (f"llm_{elegida}", llm), ("hibrido_union", reglas | llm),
                      ("hibrido_interseccion", reglas & llm)):
        for s in ("dev", "test"):
            m = prf({x for x in p if split.get(x[0]) == s}, g[s])
            filas.append({"metodo": metodo, "split": s, **{k: m[k] for k in ("precision", "recall", "f1", "tp", "fp", "fn")}})
    comp = pd.DataFrame(filas)
    res["comparacion"] = filas

    # errores del LLM con la proyeccion elegida, junto con lo que hicieron las reglas
    err = []
    for s in ("dev", "test"):
        ps = {x for x in llm if split.get(x[0]) == s}
        for x in sorted(g[s] - ps):
            err.append({"split": s, "error": "FN", "id_origen": x[0], "id_destino": x[1], "reglas_lo_tienen": x in reglas})
        for x in sorted(ps - g[s]):
            err.append({"split": s, "error": "FP", "id_origen": x[0], "id_destino": x[1], "reglas_lo_tienen": x in reglas})

    resumen_p = rel_llm.parent / "resumen.json"
    if resumen_p.exists():
        res["diagnostico_llm"] = json.loads(resumen_p.read_text(encoding="utf-8"))

    out.mkdir(parents=True, exist_ok=True)
    escribir_texto(out / "metricas.json", json.dumps(res, indent=2, ensure_ascii=False))
    comp.to_csv(out / "comparacion.csv", index=False, lineterminator="\n")
    pd.DataFrame(err).to_csv(out / "errores.csv", index=False, lineterminator="\n")
    for n, d in res["proyecciones"].items():
        print(f"{n:20s} dev F1={d['dev']['f1']:.3f}  test F1={d['test']['f1']:.3f}")
    print("elegida en dev:", elegida)
    print(comp.to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    ap.add_argument("--relaciones", type=Path, default=Path("results/relaciones_llm/relaciones_llm.csv"))
    ap.add_argument("--reglas", type=Path, default=Path("results/relaciones/relaciones_reglas_v2.csv"))
    ap.add_argument("--evidencias", type=Path, default=Path("results/reglas_v2/evidencias.csv"))
    ap.add_argument("--out", type=Path, default=Path("results/evaluacion_llm"))
    a = ap.parse_args()
    main(a.corpus, a.relaciones, a.reglas, a.evidencias, a.out)
