"""Parser 3: híbrido en cascada (reglas que filtran + LLM que decide la zona gris).

Explicación completa del método en src/grafo_legal/extractores/hibrido.py.

    export ANTHROPIC_API_KEY=$(cat .anthropic_key)
    python scripts/20_parser_hibrido.py --estimar          # cuenta pedidos y tokens, sin llamar
    python scripts/20_parser_hibrido.py --hilos 8          # corre (o lee la cache) y evalua en dev
    python scripts/20_parser_hibrido.py --incluir-test     # una vez congelado: evalua tambien test

Protocolo: la politica de decision se elige en dev. Test se mira una sola vez, con
--incluir-test, despues de congelar el prompt (VERSION_PROMPT) y la politica (POLITICA).

Salidas (results/hibrido/):
    cache/                    respuestas del LLM (huella SHA-256 del pedido)
    candidatos.csv            un candidato por fila: zona, juicio del LLM, cita verificada, decision
    relaciones_hibrido.csv    salida estandar (fuente = hibrido)
    metricas.json             P/R/F1 por zona y por politica en dev (y test si se pide)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto                       # noqa: E402
from grafo_legal.evaluacion import prf                                # noqa: E402
from grafo_legal.extractores import hibrido, llm                      # noqa: E402
from grafo_legal.fuentes.infoleg import cargar                        # noqa: E402
from grafo_legal.salida import COLUMNAS, validar                      # noqa: E402

# Congelado el 18/11/2026 mirando solo dev (metricas.json: "politicas" y "barrido"):
POLITICA = "previa"           # la regla F3 opina primero; el LLM la corrige con confianza
UMBRAL = 0.5                  # para ACEPTAR un par gris que F3 rechaza
UMBRAL_BAJO = 0.15            # para DESCARTAR un par gris que F3 acepta
POLITICAS = ["solo_reglas", "cascada", "llm_veta", "previa"]


def etiqueta(r) -> str:
    return f"{r.tipo_norma} {r.numero_norma}"


def titulo(r) -> str:
    t = (r.titulo_sumario or r.titulo_resumido or "").strip()
    anio = (r.fecha_sancion or "")[:4]
    return f"{t.capitalize()[:90]} ({anio})" if anio else t.capitalize()[:90]


def armar_pedidos(cand, ev, normas, html_dir):
    """Un pedido por norma origen (en tandas de MAX_CANDIDATOS_POR_PEDIDO)."""
    info = {int(r.id_norma): r for r in normas.itertuples()}
    por_par = {k: g for k, g in ev.groupby(["id_origen", "id_destino"])}
    pedidos, frags = [], {}
    for o, cs in cand[cand.zona != "descarte"].groupby("id_origen"):
        texto = cargar(o, html_dir)[0]
        lista = []
        for r in cs.itertuples(index=False):
            f = hibrido.fragmentos(por_par[(r.id_origen, r.id_destino)], texto)
            frags[(r.id_origen, r.id_destino)] = f
            lista.append((r.id_destino, f))
        for k in range(0, len(lista), hibrido.MAX_CANDIDATOS_POR_PEDIDO):
            tanda = lista[k:k + hibrido.MAX_CANDIDATOS_POR_PEDIDO]
            items = [{"id": f"C{j}", "destino": etiqueta(info[d]), "titulo": titulo(info[d]),
                      "fragmentos": [{x: f_[x] for x in ("parte", "articulo", "texto")} for f_ in fr]}
                     for j, (d, fr) in enumerate(tanda, 1)]
            pedidos.append({"id_origen": o, "ids": {f"C{j}": d for j, (d, _) in enumerate(tanda, 1)},
                            "mensaje": hibrido.mensaje(etiqueta(info[o]), titulo(info[o]), items)})
    return pedidos, frags


def fila_relacion(o, d, frag, tipo, art_dest, verbo, etq, articulos):
    """Una relacion en la salida estandar a partir del fragmento de evidencia elegido."""
    e = frag["evidencia"]
    a = articulos[(articulos.id_norma == o) & (articulos.inicio <= frag["inicio"])]
    orden = int(a.orden.iloc[-1]) if len(a) else 0
    return {"fuente": "hibrido", "id_norma_origen": o, "norma_origen": etq[o],
            "id_articulo_origen": f"{o}#{orden}", "articulo_origen": str(e.articulo), "parte_origen": e.parte,
            "tipo": tipo, "id_norma_destino": d, "norma_destino": etq[d],
            "articulo_destino": "" if art_dest in (None, "null") else str(art_dest),
            "verbo": verbo, "metodo": e.metodo, "confianza": "", "n_menciones": 1,
            "inicio": int(e.inicio), "fin": int(e.fin), "fragmento": e.fragmento}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    ap.add_argument("--html", type=Path, default=Path("data/textos/infoleg/html"))
    ap.add_argument("--evidencias", type=Path, default=Path("results/reglas_v3/evidencias.csv"))
    ap.add_argument("--rel-reglas", type=Path, default=Path("results/relaciones/relaciones_reglas_v3.csv"))
    ap.add_argument("--out", type=Path, default=Path("results/hibrido"))
    ap.add_argument("--modelo", default=llm.MODELO_POR_DEFECTO)
    ap.add_argument("--hilos", type=int, default=1)
    ap.add_argument("--estimar", action="store_true")
    ap.add_argument("--incluir-test", action="store_true")
    a = ap.parse_args()

    normas = pd.read_csv(a.corpus / "corpus_normas.csv", dtype=str, keep_default_na=False)
    etq = {int(r.id_norma): etiqueta(r) for r in normas.itertuples()}
    split = {int(r.id_norma): r.split for r in normas.itertuples()}
    gold = pd.read_csv(a.corpus / "gold_relaciones.csv")
    ev = pd.read_csv(a.evidencias, keep_default_na=False)
    articulos = pd.read_csv("data/dataset/articulos.csv", usecols=["id_norma", "orden", "inicio"]) \
        .sort_values(["id_norma", "inicio"])
    rel_reglas = pd.read_csv(a.rel_reglas, keep_default_na=False, dtype={"articulo_destino": str})

    # Pasos 1 y 2: candidatos y zonas
    cand = hibrido.candidatos(ev)
    pedidos, frags = armar_pedidos(cand, ev, normas, a.html)
    chars = sum(len(p["mensaje"]) + len(hibrido.SISTEMA) for p in pedidos)
    print(f"{len(cand)} candidatos ({dict(cand.zona.value_counts())}); {len(pedidos)} pedidos, "
          f"~{int(chars / 3.3):,} tokens de entrada")
    if a.estimar:
        return

    # Paso 3: juicio del LLM (cache por huella del pedido; en paralelo si --hilos > 1)
    cliente = llm.ClienteLLM(a.out / "cache", a.modelo, os.environ.get("ANTHROPIC_API_KEY"),
                             sistema=hibrido.SISTEMA, version=hibrido.VERSION_PROMPT)
    with ThreadPoolExecutor(max(1, a.hilos)) as ex:
        regs = list(ex.map(lambda p: cliente.pedir(p["mensaje"]), pedidos))
    print("uso:", cliente.uso)
    juicios = {}
    cortadas = 0
    for p, reg in zip(pedidos, regs):
        cortadas += reg.get("stop_reason") == "max_tokens"
        j = hibrido.leer(reg["respuesta"])
        for cid, d in p["ids"].items():
            juicios[(p["id_origen"], d)] = j.get(cid)

    # Pasos 4 y 5: verificacion y decision (para cada politica, para elegir en dev)
    tipo_reglas = (rel_reglas[rel_reglas.tipo != "CITA"].groupby(["id_norma_origen", "id_norma_destino"])
                   .tipo.first().to_dict())
    filas = []
    for r in cand.itertuples(index=False):
        k = (r.id_origen, r.id_destino)
        j = juicios.get(k)
        ok, f = hibrido.verificar(j, frags.get(k, [])) if j else (False, None)
        fila = {"id_origen": r.id_origen, "id_destino": r.id_destino, "origen": etq[r.id_origen],
                "destino": etq[r.id_destino], "split": split[r.id_origen], "zona": r.zona,
                "motivo_zona": r.motivo_zona, "pasa_F3": r.pasa_F3, "llm_respondio": j is not None,
                "llm_relacion": None if j is None else j.get("relacion"),
                "llm_tipo": "" if j is None else str(j.get("tipo") or ""),
                "llm_articulo": "" if j is None else str(j.get("articulo_destino") or ""),
                "llm_motivo": "" if j is None else str(j.get("motivo") or ""),
                "llm_probabilidad": hibrido.probabilidad(j),
                "cita_verificada": ok}
        for pol in POLITICAS:
            fila[f"acepta_{pol}"] = hibrido.decidir(r.zona, j, ok, pol, UMBRAL, r.pasa_F3, UMBRAL_BAJO)
        filas.append(fila)
    tabla = pd.DataFrame(filas)

    # Salida estandar con la politica congelada. Se parte de las relaciones de las reglas v3 (una
    # por articulo origen, tipo y destino) para que el grafo tenga el mismo detalle que los otros
    # parsers:
    #   - par aceptado: la relacion donde esta la cita del LLM toma su tipo y su articulo destino;
    #     las demas relaciones del par quedan como las tipo la regla.
    #   - par no aceptado: todas sus relaciones quedan como CITA (se nombra, no se modifica).
    acept = set(zip(tabla[tabla[f"acepta_{POLITICA}"]].id_origen, tabla[tabla[f"acepta_{POLITICA}"]].id_destino))
    base = rel_reglas.assign(fuente="hibrido")
    rel = []
    for k, grp in base.groupby(["id_norma_origen", "id_norma_destino"], sort=False):
        grp = grp.copy()
        if k not in acept:
            grp["tipo"], grp["verbo"] = "CITA", ""
            rel.append(grp)
            continue
        j = juicios.get(k)
        ok, f = hibrido.verificar(j, frags.get(k, [])) if j else (False, None)
        tipo, de = hibrido.tipo_final(j, ok, tipo_reglas.get(k, ""))
        if ok:
            i_rep = (grp.inicio - f["inicio"]).abs().idxmin()
            grp.loc[i_rep, "tipo"] = tipo
            art = j.get("articulo_destino")
            if art not in (None, "", "null"):
                grp.loc[i_rep, "articulo_destino"] = str(art)
            grp.loc[i_rep, "confianza"] = "" if hibrido.probabilidad(j) is None else str(round(hibrido.probabilidad(j), 2))
        elif (grp.tipo == "CITA").all():
            grp.loc[grp.index[0], "tipo"] = tipo
        rel.append(grp)
    # pares aceptados sin relaciones de las reglas (p. ej. solo citas de procedencia): se arman
    # desde el fragmento de la evidencia
    hechos = set(zip(base.id_norma_origen, base.id_norma_destino))
    extra = []
    for k in acept - hechos:
        j = juicios.get(k)
        ok, f = hibrido.verificar(j, frags[k]) if j else (False, None)
        tipo, _ = hibrido.tipo_final(j, ok, "")
        f = f or frags[k][0]
        art = (j or {}).get("articulo_destino") if ok else ""
        verbo = str(f["evidencia"].verbo_oracion) if f["evidencia"].verbo_oracion else ""
        extra.append(fila_relacion(k[0], k[1], f, tipo, art, verbo, etq, articulos))
    rel = pd.concat(rel + [pd.DataFrame(extra, columns=list(COLUMNAS))], ignore_index=True)
    rel = rel.drop_duplicates(["id_articulo_origen", "tipo", "id_norma_destino", "articulo_destino"])
    rel["n_menciones"] = rel.n_menciones.fillna(1).astype(int)
    rel = rel[list(COLUMNAS)].sort_values(["id_norma_origen", "inicio", "id_norma_destino"], kind="mergesort")
    errores = validar(rel)
    if errores:
        sys.exit("La salida no cumple el formato: " + "; ".join(errores))

    # Evaluacion contra InfoLEG (pares de normas)
    splits = ["dev", "test"] if a.incluir_test else ["dev"]
    res = {"fecha": datetime.now(timezone.utc).isoformat(), "modelo": a.modelo,
           "version_prompt": hibrido.VERSION_PROMPT, "politica_congelada": POLITICA,
           "uso": cliente.uso, "respuestas_cortadas": cortadas,
           "candidatos": {z: int(n) for z, n in tabla.zona.value_counts().items()},
           "llm_sin_respuesta": int((~tabla.llm_respondio & (tabla.zona != "descarte")).sum()),
           "cita_no_verificada": int((tabla.llm_respondio & ~tabla.cita_verificada).sum()),
           "politicas": {}, "por_zona": {}}
    for s in splits:
        g = set(zip(gold[gold.split == s].id_norma_modificatoria, gold[gold.split == s].id_norma_modificada))
        t = tabla[tabla.split == s]
        res["politicas"][s] = {pol: prf(set(zip(t[t[f"acepta_{pol}"]].id_origen, t[t[f"acepta_{pol}"]].id_destino)), g)
                               for pol in POLITICAS}
        # en la zona gris: que tan bien decide el LLM (precision y recall dentro de la zona)
        zg = t[t.zona == "gris"]
        en_gold = [(o, d) in g for o, d in zip(zg.id_origen, zg.id_destino)]
        acepta = zg[f"acepta_{POLITICA}"].tolist()
        tp = sum(x and y for x, y in zip(acepta, en_gold))
        res["por_zona"][s] = {
            "gris": {"candidatos": len(zg), "en_gold": int(sum(en_gold)), "acepta_llm": int(sum(acepta)),
                     "tp": tp, "precision": round(tp / max(1, sum(acepta)), 4),
                     "recall_en_la_zona": round(tp / max(1, sum(en_gold)), 4)},
            "seguro": {"candidatos": int((t.zona == "seguro").sum()),
                       "en_gold": int(sum((o, d) in g for o, d in zip(t[t.zona == "seguro"].id_origen,
                                                                       t[t.zona == "seguro"].id_destino))),
                       "llm_dice_no": int(((t.zona == "seguro") & (t.llm_relacion == False)).sum())}}  # noqa: E712
        # barrido del umbral (solo para elegirlo en dev; en test se informa el congelado)
        if s == "dev":
            res["barrido"] = {}
            for pol in ["cascada", "llm_veta"]:
                for u in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
                    acc = [hibrido.decidir(z, juicios.get((o, d)), v, pol, u)
                           for z, o, d, v in zip(t.zona, t.id_origen, t.id_destino, t.cita_verificada)]
                    m = prf(set((o, d) for o, d, x in zip(t.id_origen, t.id_destino, acc) if x), g)
                    res["barrido"][f"{pol}@{u}"] = m
            for ub in [0.05, 0.1, 0.15, 0.2, 0.3]:
                for u in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
                    acc = [hibrido.decidir(z, juicios.get((o, d)), v, "previa", u, f, ub)
                           for z, o, d, v, f in zip(t.zona, t.id_origen, t.id_destino, t.cita_verificada, t.pasa_F3)]
                    res["barrido"][f"previa@{ub}/{u}"] = prf(
                        set((o, d) for o, d, x in zip(t.id_origen, t.id_destino, acc) if x), g)
        for pol in POLITICAS:
            m = res["politicas"][s][pol]
            print(f"{s:4} {pol:12} P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f}")
        print(f"{s:4} zona gris: {res['por_zona'][s]['gris']}")
    tabla["en_gold"] = [(o, d) in set(zip(gold.id_norma_modificatoria, gold.id_norma_modificada))
                        for o, d in zip(tabla.id_origen, tabla.id_destino)]
    if not a.incluir_test:       # no se mira test hasta congelar
        tabla["en_gold"] = tabla.en_gold.astype(object)
        tabla.loc[tabla.split == "test", "en_gold"] = None
    a.out.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(a.out / "candidatos.csv", index=False, lineterminator="\n")
    rel.to_csv(a.out / "relaciones_hibrido.csv", index=False, lineterminator="\n")
    escribir_texto(a.out / "metricas.json", json.dumps(res, indent=2, ensure_ascii=False))
    print(f"relaciones: {len(rel)}  tipos: {dict(Counter(rel.tipo))}")


if __name__ == "__main__":
    main()
