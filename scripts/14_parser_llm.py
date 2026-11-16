"""
14_parser_llm.py
Corre el parser LLM (src/grafo_legal/extractores/llm.py) sobre todas las normas con texto y
escribe sus relaciones en la salida estandar, en una carpeta propia: no toca las salidas de las
reglas ni el grafo actual.

  results/relaciones_llm/relaciones_llm.csv   relaciones tipadas (fuente = llm)
  results/relaciones_llm/resumen.json         uso de la API, descartes y conteos
  results/relaciones_llm/cache/               una respuesta del LLM por lote (reproducible)

Con --estimar no llama a la API: cuenta lotes y tokens aproximados para saber el costo.

Uso:
    python scripts/14_parser_llm.py --estimar
    export ANTHROPIC_API_KEY=$(cat .anthropic_key)
    python scripts/14_parser_llm.py --limite 5          # piloto con 5 normas
    python scripts/14_parser_llm.py                     # todo el corpus
    python scripts/14_parser_llm.py --modelo claude-haiku-5-5 --out results/relaciones_llm_haiku
"""

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto                       # noqa: E402
from grafo_legal.catalogo import Catalogo                              # noqa: E402
from grafo_legal.extractores import llm                                # noqa: E402
from grafo_legal.salida import CLAVE, COLUMNAS, validar                # noqa: E402

CHARS_POR_TOKEN = 3.5   # aproximado para castellano juridico


def segmentos_por_norma(articulos: pd.DataFrame) -> dict[int, list[llm.Segmento]]:
    out: dict[int, list[llm.Segmento]] = {}
    for r in articulos.itertuples(index=False):
        out.setdefault(int(r.id_norma), []).append(
            llm.Segmento(int(r.id_norma), int(r.orden), str(r.articulo), r.zona, int(r.inicio), str(r.texto)))
    return out


def deduplicar(rel: pd.DataFrame) -> pd.DataFrame:
    """Una fila por clave; si el LLM devolvio la misma relacion dos veces (por ejemplo en dos
    pedazos de un articulo largo), se queda la primera y se suman las menciones."""
    if rel.empty:
        return rel
    rel = rel.sort_values(["id_norma_origen", "inicio"], kind="mergesort")
    n = rel.groupby(CLAVE, sort=False).n_menciones.transform("sum")
    rel = rel.assign(n_menciones=n).drop_duplicates(CLAVE, keep="first")
    return rel.reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    ap.add_argument("--dataset", type=Path, default=Path("data/dataset"))
    ap.add_argument("--out", type=Path, default=Path("results/relaciones_llm"))
    ap.add_argument("--modelo", default=llm.MODELO_POR_DEFECTO)
    ap.add_argument("--limite", type=int, help="procesar solo las primeras N normas (piloto)")
    ap.add_argument("--estimar", action="store_true", help="no llama a la API: cuenta lotes y tokens")
    a = ap.parse_args()

    normas = pd.read_csv(a.corpus / "corpus_normas.csv", dtype=str, keep_default_na=False)
    etiquetas = {int(r.id_norma): f"{r.tipo_norma} {r.numero_norma}" for r in normas.itertuples()}
    cat = Catalogo.desde_corpus(a.corpus / "corpus_normas.csv")
    art = pd.read_csv(a.dataset / "articulos.csv", keep_default_na=False, dtype={"articulo": str},
                      usecols=["id_norma", "orden", "zona", "articulo", "inicio", "texto"])
    segs = segmentos_por_norma(art)
    ids = sorted(segs)[: a.limite] if a.limite else sorted(segs)

    plan = {i: llm.lotes(llm.seleccionar(segs[i])) for i in ids}
    n_lotes = sum(len(v) for v in plan.values())
    chars = sum(len(llm.mensaje_usuario(etiquetas[i], lt)) for i, v in plan.items() for lt in v)
    tok_in = int((chars + n_lotes * len(llm.SISTEMA)) / CHARS_POR_TOKEN)
    print(f"{len(ids)} normas, {n_lotes} lotes, ~{tok_in:,} tokens de entrada")
    if a.estimar:
        return

    cliente = llm.ClienteLLM(a.out / "cache", a.modelo, os.environ.get("ANTHROPIC_API_KEY"))
    filas, conteo = [], Counter()
    for k, i in enumerate(ids, 1):
        for lt in plan[i]:
            reg = cliente.pedir(llm.mensaje_usuario(etiquetas[i], lt))
            if reg.get("stop_reason") == "max_tokens":
                conteo["respuestas_cortadas"] += 1
            f, c = llm.a_relaciones(i, etiquetas[i], lt, llm.leer_json(reg["respuesta"]), cat, etiquetas)
            filas += f
            conteo.update(c)
        if k % 20 == 0 or k == len(ids):
            print(f"  {k}/{len(ids)} normas  {dict(cliente.uso)}", flush=True)

    rel = deduplicar(pd.DataFrame(filas, columns=list(COLUMNAS)))
    errores = validar(rel)
    if errores:
        sys.exit("La salida no cumple el formato: " + "; ".join(errores))
    a.out.mkdir(parents=True, exist_ok=True)
    tmp = a.out / ".relaciones_llm.csv.tmp"
    rel.to_csv(tmp, index=False, lineterminator="\n")
    tmp.replace(a.out / "relaciones_llm.csv")
    resumen = {
        "modelo": a.modelo, "version_prompt": llm.VERSION_PROMPT, "normas": len(ids), "lotes": n_lotes,
        "uso_api_esta_corrida": cliente.uso,
        "entradas_del_llm": dict(conteo),
        # proporcion de citas que el LLM dio y no estan en el texto (alucinaciones de evidencia)
        "tasa_cita_no_encontrada": round(conteo["cita_no_encontrada"] / conteo["crudas"], 4) if conteo["crudas"] else 0,
        "relaciones": len(rel), "por_tipo": rel.tipo.value_counts().to_dict(),
        "por_parte_origen": rel.parte_origen.value_counts().to_dict(),
        "pares_de_normas": int(rel[["id_norma_origen", "id_norma_destino"]].drop_duplicates().shape[0]),
    }
    escribir_texto(a.out / "resumen.json", json.dumps(resumen, indent=2, ensure_ascii=False))
    print(json.dumps(resumen, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
