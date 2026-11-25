"""
33_grafo_modelos.py
Arma el grafo de los modelos que aprenden: el random forest (B37), el TF-IDF con regresión
logística (B46) y el híbrido de reglas + TF-IDF (B46, el de F1 0,839 en test). Bitácora B73.

Por qué hace falta este paso. Esos modelos son CLASIFICADORES de relaciones: para cada par de
normas que propone el detector de menciones (norma A menciona a norma B) dicen si es una relación
real («modifica o complementa») o una cita al pasar. No buscan las menciones ni dicen el artículo
ni el tipo. Por eso su grafo se arma igual que el del híbrido con LLM (scripts/20):
  - la evidencia (artículo de origen, fragmento, offsets) es la de las menciones que encontró el
    detector, tomada de la salida estándar de las reglas v2;
  - par ACEPTADO por el modelo: sus aristas conservan el tipo que les dio la regla (SUSTITUYE,
    DEROGA...); si todas eran CITA, la mejor evidencia pasa a MODIFICA, la relación general de la
    consigna («modifica o complementa»), porque el modelo no distingue tipos;
  - par RECHAZADO: todas sus aristas quedan como CITA (se nombra, no se modifica);
  - la columna confianza lleva la probabilidad del modelo para el par.

Cobertura. Los 1.091 pares candidatos son TODOS los pares que el detector encuentra en las 306
normas con texto del corpus (dev hasta 2019 y test desde 2020): el grafo cubre el corpus entero,
igual que el de las reglas. En dev la probabilidad es la de la validación cruzada (fuera de la
partición), para no usar un modelo que ya vio ese par; en test es la del modelo final.

En estos grafos una relación entre normas es un par con alguna arista distinta de CITA. El script
comprueba que el grafo reconstruido (en memoria, con el mismo código que carga Neo4j) devuelve
exactamente los pares que aceptó el modelo, y mide P/R/F1 contra InfoLEG.

Salidas:
  results/relaciones_modelos/relaciones_{random_forest,tfidf,hibrido_tfidf}.csv  (salida estándar)
  results/relaciones_modelos/metricas.json
Uso:
    python3 scripts/33_grafo_modelos.py
    bash scripts/34_cargar_modelos_neo4j.sh        # carga en Neo4j, sin --borrar
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto                    # noqa: E402
from grafo_legal.evaluacion import prf                             # noqa: E402
from grafo_legal.grafo import a_networkx, construir, exportar_networkx  # noqa: E402
from grafo_legal.salida import COLUMNAS, validar                   # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / "results" / "relaciones_modelos"

# Umbrales congelados en dev por los scripts 08 y 13 (no se tocan acá)
UMBRAL_RF = 0.45            # results/clasificador/metricas.json
UMBRAL_TFIDF = 0.20         # variante «contexto+superficie» (TF-IDF + atributos), C = 30
UMBRAL_HIB = 0.20           # variante «contexto+superficie|hibrido»


def decisiones() -> dict[str, pd.DataFrame]:
    """Para cada modelo: par, split, probabilidad y si lo acepta."""
    rf = pd.read_csv(RAIZ / "results/clasificador/predicciones.csv")
    mc = pd.read_csv(RAIZ / "results/modelo_contextual/predicciones.csv")
    k = ["id_norma_origen", "id_norma_destino", "split"]
    return {
        "random_forest": rf[k].assign(prob=rf.prob, acepta=rf.predicho == 1),
        "tfidf": mc[k].assign(prob=mc.prob_contexto_sup, acepta=mc.prob_contexto_sup >= UMBRAL_TFIDF),
        # híbrido: las reglas deciden los pares seguros; el modelo solo la zona gris
        "hibrido_tfidf": mc[k].assign(
            prob=mc.prob_contexto_sup_hibrido,
            acepta=(mc.grupo == "seguro_si") | ((mc.grupo == "zona_gris") & (mc.prob_contexto_sup_hibrido >= UMBRAL_HIB))),
    }


def prioridad(g: pd.DataFrame) -> pd.Series:
    """Qué evidencia representa al par: primero el articulado con número, después el VISTO."""
    return ((g.parte_origen == "articulado") & (g.metodo != "alias")).astype(int) * 2 + (g.parte_origen == "visto").astype(int)


def fila_desde_evidencia(e, etq, articulos, fuente) -> dict:
    """Arista para un par aceptado que no tiene relaciones en las reglas (p. ej. solo citas de
    procedencia): se arma con la primera mención del detector, como en scripts/20."""
    a = articulos[(articulos.id_norma == e.id_origen) & (articulos.inicio <= e.inicio)]
    orden = int(a.orden.iloc[-1]) if len(a) else 0
    return {"fuente": fuente, "id_norma_origen": e.id_origen, "norma_origen": etq[e.id_origen],
            "id_articulo_origen": f"{e.id_origen}#{orden}", "articulo_origen": str(e.articulo),
            "parte_origen": e.parte, "tipo": "MODIFICA", "id_norma_destino": e.id_destino,
            "norma_destino": etq[e.id_destino], "articulo_destino": "", "verbo": e.verbo_oracion or "",
            "metodo": e.metodo, "confianza": "", "n_menciones": 1, "inicio": int(e.inicio),
            "fin": int(e.fin), "fragmento": e.fragmento}


def armar(fuente, dec, base, ev, etq, articulos) -> pd.DataFrame:
    prob = {(o, d): p for o, d, p in zip(dec.id_norma_origen, dec.id_norma_destino, dec.prob)}
    acept = set(zip(dec[dec.acepta].id_norma_origen, dec[dec.acepta].id_norma_destino))
    rel = []
    for k, grp in base.assign(fuente=fuente).groupby(["id_norma_origen", "id_norma_destino"], sort=False):
        grp = grp.copy()
        grp["confianza"] = "" if k not in prob else f"{prob[k]:.2f}"
        if k not in acept:
            grp["tipo"], grp["verbo"] = "CITA", ""
        elif (grp.tipo == "CITA").all():
            grp.loc[prioridad(grp).idxmax(), "tipo"] = "MODIFICA"
        rel.append(grp)
    extra = []
    for k in sorted(acept - set(zip(base.id_norma_origen, base.id_norma_destino))):
        e = ev[(ev.id_origen == k[0]) & (ev.id_destino == k[1])].sort_values("inicio").iloc[0]
        f = fila_desde_evidencia(e, etq, articulos, fuente)
        f["confianza"] = f"{prob[k]:.2f}"
        extra.append(f)
    rel = pd.concat(rel + [pd.DataFrame(extra, columns=list(COLUMNAS))], ignore_index=True)
    rel = rel.drop_duplicates(["id_articulo_origen", "tipo", "id_norma_destino", "articulo_destino"])
    rel["n_menciones"] = rel.n_menciones.fillna(1).astype(int)
    rel = rel[list(COLUMNAS)].sort_values(["id_norma_origen", "inicio", "id_norma_destino"], kind="mergesort")
    errores = validar(rel)
    if errores:
        sys.exit(f"{fuente}: la salida no cumple el formato: " + "; ".join(errores))
    return rel


def main() -> None:
    normas = pd.read_csv(RAIZ / "data/corpus/corpus_normas.csv", dtype=str, keep_default_na=False)
    etq = {int(r.id_norma): f"{r.tipo_norma} {r.numero_norma}" for r in normas.itertuples()}
    split = {int(r.id_norma): r.split for r in normas.itertuples()}
    gold = pd.read_csv(RAIZ / "data/corpus/gold_relaciones.csv")
    art = pd.read_csv(RAIZ / "data/dataset/articulos.csv", keep_default_na=False, dtype={"articulo": str},
                      usecols=["id_norma", "orden", "zona", "articulo", "inicio", "fin", "texto"])
    articulos = art[["id_norma", "orden", "inicio"]].sort_values(["id_norma", "inicio"])
    base = pd.read_csv(RAIZ / "results/relaciones/relaciones_reglas_v2.csv", keep_default_na=False,
                       dtype={"articulo_destino": str})
    ev = pd.read_csv(RAIZ / "results/reglas_v2/evidencias.csv", keep_default_na=False)
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"fecha": datetime.now(timezone.utc).isoformat(), "base": "relaciones_reglas_v2 + evidencias v2",
           "umbrales": {"random_forest": UMBRAL_RF, "tfidf": UMBRAL_TFIDF, "hibrido_tfidf": UMBRAL_HIB},
           "modelos": {}}
    for fuente, dec in decisiones().items():
        rel = armar(fuente, dec, base, ev, etq, articulos)
        rel.to_csv(OUT / f"relaciones_{fuente}.csv", index=False, lineterminator="\n")
        # ida y vuelta por el mismo código que arma el grafo (networkx en memoria)
        g = exportar_networkx(a_networkx(construir(normas, art, rel)))
        g_pares = set(zip(g[g.tipo != "CITA"].id_norma_origen.astype(int), g[g.tipo != "CITA"].id_norma_destino.astype(int)))
        acept = set(zip(dec[dec.acepta].id_norma_origen, dec[dec.acepta].id_norma_destino))
        m = {"aristas": len(rel), "por_tipo": rel.tipo.value_counts().to_dict(),
             "pares_aceptados": len(acept), "grafo_igual_al_modelo": g_pares == acept,
             "normas_origen": int(rel.id_norma_origen.nunique()), "infoleg": {}}
        for s in ("dev", "test"):
            ref = set(zip(gold[gold.split == s].id_norma_modificatoria, gold[gold.split == s].id_norma_modificada))
            m["infoleg"][s] = prf({p for p in g_pares if split[p[0]] == s}, ref)
        res["modelos"][fuente] = m
        print(fuente, len(rel), "aristas;", m["pares_aceptados"], "pares;",
              "grafo = modelo" if m["grafo_igual_al_modelo"] else "¡DIFIERE!",
              {s: round(v["f1"], 3) for s, v in m["infoleg"].items()})
    escribir_texto(OUT / "metricas.json", json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
