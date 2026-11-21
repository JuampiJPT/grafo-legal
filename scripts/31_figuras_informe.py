"""Figuras del informe de avance (B64).

Lee solo resultados ya calculados en results/ y escribe PNG en docs/informe_avance/figuras/.
No llama a la API ni a Neo4j. Uso: python scripts/31_figuras_informe.py

Figuras:
  fig1_pipeline.png      diagrama del pipeline (Graphviz, si está `dot`)
  fig2_embudo.png        embudo de pérdidas del gold, dev y test (reglas v2)
  fig3_metodos.png       F1 en test de cada método con su IC 95 % (bootstrap)
  fig4_tipos.png         matrices de confusión del tipo (reglas v2 y LLM, 78 casos)
  fig5_errores.png       causas de los falsos positivos y negativos de test (reglas v2)
  fig6_pi4.png           F1 del vínculo en el digesto UNNOBA (PI4)
  fig7_consolidado.png   coincidencia por artículo del consolidado de la LCT con InfoLEG
"""
import csv
import json
import shutil
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
RES = RAIZ / "results"
OUT = RAIZ / "docs/informe_avance/figuras"

# Paleta: slots 1 y 2 de una paleta categórica validada para daltonismo; el resto, grises.
AZUL, NARANJA, GRIS, GRIS_CLARO, TINTA = "#2a78d6", "#eb6834", "#8a8984", "#d8d7d2", "#26251f"
plt.rcParams.update({
    "font.size": 10, "axes.edgecolor": GRIS, "axes.labelcolor": TINTA, "xtick.color": TINTA,
    "ytick.color": TINTA, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titleweight": "bold", "axes.titlesize": 11, "savefig.dpi": 200, "savefig.bbox": "tight",
})


def coma(x, fmt):
    """Número con coma decimal, como se escribe en el informe."""
    return format(x, fmt).replace(".", ",")


def guardar(fig, nombre):
    fig.savefig(OUT / nombre)
    plt.close(fig)
    print("escrito", nombre)


def leer_json(ruta):
    return json.loads((RES / ruta).read_text(encoding="utf-8"))


def fig_pipeline():
    """Diagrama del pipeline. El gold solo entra a la evaluación (nunca a los extractores)."""
    if not shutil.which("dot"):
        print("sin graphviz: se omite fig1")
        return
    dot = r'''
digraph G {
  rankdir=LR; nodesep=0.3; ranksep=0.35; newrank=true;
  node [shape=box, style="rounded,filled", fillcolor="#eef4fc", color="#2a78d6", fontname="Helvetica", fontsize=10];
  edge [color="#52514e", arrowsize=0.7];
  fuente [label="Fuente\n(InfoLEG HTML /\ndigesto PDF)", fillcolor="#f2f1ee", color="#8a8984"];
  adaptador [label="Adaptador\nde la fuente"];
  seg [label="Segmentación\n(VISTO, CONSIDERANDO,\narticulado, anexo)"];
  det [label="Detección\nde menciones"];
  norm [label="Normalización\n(id de norma)"];
  ext [label="Extracción de la relación\nreglas | LLM | híbrido"];
  sal [label="Salida estándar\n(con evidencia)"];
  grafo [label="Grafo Neo4j\n(normas, artículos,\naristas tipadas)"];
  ev [label="Evaluación\nP / R / F1", fillcolor="#fdf0ea", color="#eb6834"];
  gold [label="Gold InfoLEG\n(bases complementarias)", shape=note, fillcolor="#fdf0ea", color="#eb6834"];
  // dos filas, para que el diagrama entre a lo ancho de una página
  fuente -> adaptador -> seg -> det -> norm;
  norm -> ext [constraint=false];
  ext -> sal -> grafo -> ev [weight=2];
  sal -> ev [constraint=false];
  gold -> ev [style=dashed];
  {rank=same; fuente; ext;}
  {rank=same; adaptador; sal;}
  {rank=same; seg; grafo;}
  {rank=same; det; ev;}
  {rank=same; norm; gold;}
  fuente -> ext [style=invis];
  grafo -> ev [label=" ida y vuelta", fontsize=8, style=invis];
}'''
    subprocess.run(["dot", "-Tpng", "-Gdpi=200", "-o", str(OUT / "fig1_pipeline.png")],
                   input=dot.encode(), check=True)
    print("escrito fig1_pipeline.png")


def fig_embudo():
    emb = leer_json("subtareas/metricas.json")["embudo"]
    etapas = [("1_pares_gold", "Pares del gold"), ("2_con_texto", "Con texto en InfoLEG"),
              ("3_con_mencion_en_el_texto", "Nombran al destino"), ("4_detectados", "Detectados"),
              ("5_normalizados", "Normalizados"), ("6_extraidos_por_la_regla", "Aceptados por la regla")]
    fig, ejes = plt.subplots(1, 2, figsize=(9, 3.2), sharey=True)
    for eje, split, color in zip(ejes, ["dev", "test"], [GRIS, AZUL]):
        vals = [emb[split][k] for k, _ in etapas]
        y = range(len(etapas))[::-1]
        eje.barh(list(y), vals, color=color, height=0.6)
        for yi, v in zip(y, vals):
            eje.text(v + max(vals) * 0.01, yi, f"{v} ({coma(v / vals[0], '.0%')})", va="center", fontsize=8, color=TINTA)
        eje.set_yticks(list(y), [e for _, e in etapas])
        eje.set_xlim(0, max(vals) * 1.3)
        eje.set_title(f"{split} ({vals[0]} pares)")
        eje.tick_params(axis="y", length=0)
    fig.suptitle("Dónde se pierden los pares del gold (reglas v2)", fontweight="bold", y=1.04)
    guardar(fig, "fig2_embudo.png")


NOMBRES = {
    "reglas_v2_F": "Reglas v2 (referencia)", "reglas_v3_F3": "Reglas v3", "clasificador_superficie": "Clasificador (RF)",
    "contexto": "TF-IDF (contexto)", "contexto+superficie": "TF-IDF + superficie",
    "contexto_hibrido": "Híbrido reglas + TF-IDF", "contexto+superficie_hibrido": "Híbrido reglas + TF-IDF + sup.",
    "llm": "LLM", "hibrido_reglas_interseccion_llm": "Reglas ∩ LLM", "hibrido_reglas_union_llm": "Reglas ∪ LLM",
    "hibrido_cascada": "Híbrido en cascada",
}


def fig_metodos():
    with open(RES / "comparacion/comparacion_test.csv", encoding="utf-8") as f:
        filas = sorted(csv.DictReader(f), key=lambda r: float(r["f1"]))
    fig, eje = plt.subplots(figsize=(7.5, 4.2))
    ref = next(float(r["f1"]) for r in filas if r["metodo"] == "reglas_v2_F")
    eje.axvline(ref, color=GRIS_CLARO, lw=1, zorder=0)
    for i, r in enumerate(filas):
        f1, lo, hi = float(r["f1"]), float(r["f1_ic95_inf"]), float(r["f1_ic95_sup"])
        signif = float(r["dif_ic95_inf"]) > 0 or float(r["dif_ic95_sup"]) < 0
        color = AZUL if r["metodo"] == "reglas_v2_F" else (NARANJA if signif else GRIS)
        eje.plot([lo, hi], [i, i], color=color, lw=2)
        eje.plot(f1, i, "o", color=color, ms=7, mec="white", mew=1.5)
        eje.text(hi + 0.004, i, coma(f1, ".3f"), va="center", fontsize=8)
    eje.set_yticks(range(len(filas)), [NOMBRES.get(r["metodo"], r["metodo"]) for r in filas])
    eje.set_xlabel("F1 en test (192 pares) con IC 95 % por bootstrap")
    eje.set_title("Comparación de métodos sobre el mismo conjunto de prueba")
    eje.text(0.0, -0.16, "Naranja: diferencia con las reglas v2 significativa (el IC de la diferencia no toca el cero).",
             transform=eje.transAxes, fontsize=8, color=GRIS)
    eje.tick_params(axis="y", length=0)
    guardar(fig, "fig3_metodos.png")


def fig_tipos():
    tipos = ["SUSTITUYE", "INCORPORA", "DEROGA", "REGLAMENTA", "MODIFICA", "CITA"]
    with open(RES / "tipos/matrices.csv", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    fig, ejes = plt.subplots(1, 2, figsize=(9.5, 4.2))
    for eje, metodo, titulo in zip(ejes, ["reglas_v2", "llm"], ["Reglas v2 (tipo por verbo)", "LLM"]):
        pred = tipos + (["NO_EXTRAIDA"] if any(r["metodo"] == metodo and r["predicho"] == "NO_EXTRAIDA" for r in filas) else [])
        m = [[0] * len(tipos) for _ in pred]
        for r in filas:
            if r["metodo"] == metodo:
                m[pred.index(r["predicho"])] = [int(r[t]) for t in tipos]
        eje.imshow(m, cmap="Blues", vmin=0, vmax=max(max(x) for x in m))
        for i, fila in enumerate(m):
            for j, v in enumerate(fila):
                if v:
                    eje.text(j, i, v, ha="center", va="center", fontsize=8,
                             color="white" if v > max(max(x) for x in m) * 0.6 else TINTA)
        eje.set_xticks(range(len(tipos)), tipos, rotation=45, ha="right", fontsize=7)
        eje.set_yticks(range(len(pred)), [p.replace("NO_EXTRAIDA", "no extraída") for p in pred], fontsize=7)
        eje.set_xlabel("tipo real (revisión manual)")
        eje.set_ylabel("tipo predicho")
        eje.set_title(titulo)
        for s in eje.spines.values():
            s.set_visible(False)
    fig.suptitle("Tipo de relación: matrices de confusión sobre 78 casos", fontweight="bold")
    fig.tight_layout()
    guardar(fig, "fig4_tipos.png")


ETIQUETAS_CAUSA = {
    "cita_en_el_visto": "Cita en el VISTO", "remision_desde_ley": "Remisión desde una ley",
    "verbo_que_no_actua": "Verbo que no actúa", "decreto_sin_anio_mundo_cerrado": "Decreto sin año (mundo cerrado)",
    "otro_decreto_mismo_numero": "Otro decreto, mismo número", "procedencia_no_filtrada": "Procedencia no filtrada",
    "error_en_el_texto_fuente": "Error en el texto fuente", "considerando_y_decreto_sin_verbo": "CONSIDERANDO + decreto sin verbo",
    "texto_ordenado_implicito": "Texto ordenado implícito", "decreto_articulado_sin_verbo": "Decreto sin verbo en el articulado",
    "solo_considerando": "Solo en el CONSIDERANDO", "solo_alias": "Solo por su nombre propio",
    "no_verificable": "No verificable", "anio_como_fecha": "Año escrito como fecha", "solo_procedencia": "Solo cita de procedencia",
}


def fig_errores():
    test = leer_json("errores_explicados/resumen.json")["test"]
    fig, ejes = plt.subplots(1, 2, figsize=(9.5, 3.6))
    for eje, clase, color, titulo in zip(ejes, ["FP", "FN"], [NARANJA, AZUL],
                                         ["Falsos positivos", "Falsos negativos"]):
        items = sorted(test[clase].items(), key=lambda kv: kv[1])
        eje.barh(range(len(items)), [v for _, v in items], color=color, height=0.6)
        for i, (_, v) in enumerate(items):
            eje.text(v + 0.3, i, str(v), va="center", fontsize=8)
        eje.set_yticks(range(len(items)), [ETIQUETAS_CAUSA.get(k, k) for k, _ in items], fontsize=8)
        eje.set_title(f"{titulo} ({sum(v for _, v in items)})")
        eje.tick_params(axis="y", length=0)
    fig.suptitle("Causa de cada error en test (reglas v2)", fontweight="bold")
    fig.tight_layout()
    guardar(fig, "fig5_errores.png")


def fig_pi4():
    v = leer_json("pi4_unnoba/metricas.json")["vinculo"]
    metodos = [("F3_v3", "Reglas (v2 = v3)"), ("llm", "LLM, prompt InfoLEG"), ("llm_vocab", "LLM, prompt con vocabulario"),
               ("hibrido", "Híbrido, prompt InfoLEG"), ("hibrido_vocab", "Híbrido, prompt con vocabulario")]
    fig, eje = plt.subplots(figsize=(7, 3))
    vals = [v[k]["F1"] for k, _ in metodos]
    colores = [GRIS, NARANJA, AZUL, GRIS, AZUL]
    eje.barh(range(len(metodos))[::-1], vals, color=colores, height=0.6)
    for i, val in zip(range(len(metodos))[::-1], vals):
        eje.text(val + 0.01, i, coma(val, ".3f"), va="center", fontsize=8)
    eje.set_yticks(range(len(metodos))[::-1], [n for _, n in metodos])
    eje.set_xlim(0, 1.1)
    eje.set_xlabel("F1 del vínculo (MOD ∪ APLICA, 61 pares, 70 documentos)")
    eje.set_title("PI4: el mismo pipeline sobre el digesto de la UNNOBA")
    eje.tick_params(axis="y", length=0)
    guardar(fig, "fig6_pi4.png")


def fig_consolidado():
    m = leer_json("consolidado/evaluacion/metricas.json")["por_clase"]
    orden = ["idéntico", "casi idéntico (>=0,95)", "derogado en los dos", "diferencias menores (0,8-0,95)",
             "diferencia sustantiva (<0,8)", "InfoLEG derogado, consolidado vigente"]
    etiquetas = ["Idéntico", "Casi idéntico (≥ 0,95)", "Derogado en los dos", "Diferencia menor (0,80–0,95)",
                 "Diferencia sustantiva (< 0,80)", "Derogado en InfoLEG, vigente en el consolidado"]
    vals = [m[k] for k in orden]
    colores = [AZUL, AZUL, AZUL, GRIS, NARANJA, NARANJA]
    fig, eje = plt.subplots(figsize=(7, 3))
    eje.barh(range(len(orden))[::-1], vals, color=colores, height=0.6)
    for i, val in zip(range(len(orden))[::-1], vals):
        eje.text(val + 2, i, f"{val} ({coma(val / sum(vals), '.1%')})", va="center", fontsize=8)
    eje.set_yticks(range(len(orden))[::-1], etiquetas)
    eje.set_xlim(0, max(vals) * 1.25)
    eje.set_xlabel(f"Artículos de la LCT ({sum(vals)})")
    eje.set_title("Texto consolidado desde el grafo contra el texto actualizado de InfoLEG")
    eje.tick_params(axis="y", length=0)
    guardar(fig, "fig7_consolidado.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig_pipeline()
    fig_embudo()
    fig_metodos()
    fig_tipos()
    fig_errores()
    fig_pi4()
    fig_consolidado()
