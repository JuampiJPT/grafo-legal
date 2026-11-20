"""Texto consolidado de una ley a partir del grafo (B60).

Entrada: el manifiesto que sale de Neo4j (scripts/23_consultar_consolidado.py --manifiesto):
  - los artículos de la ley y de su texto ordenado (para la LCT: Decreto 390/76, t.o. 1976);
  - todas las relaciones que llegan a la ley, con el artículo de origen y qué parsers la encontraron.
Además, el texto completo de cada norma modificatoria (data/dataset/articulos.csv): a veces el
texto nuevo («por el siguiente: "Artículo 245…"») quedó en el segmento que sigue al artículo.

Pasos:
  1. Texto base: el t.o. 1976 partido en artículos.
  2. Eventos: cada artículo de otra norma, posterior al t.o., que según el grafo SUSTITUYE,
     INCORPORA, DEROGA o MODIFICA algo de la ley (REGLAMENTA y CITA no cambian el texto).
  3. Extracción (LLM): de cada artículo modificatorio se sacan las operaciones sobre la ley:
     qué artículo, qué operación y el texto nuevo literal. Se verifica que el texto nuevo esté
     tal cual en la norma modificatoria; si no está, la operación no se aplica.
  4. Aplicación, en orden cronológico:
       SUSTITUYE / INCORPORA: el texto nuevo verificado reemplaza o agrega el artículo (sin LLM);
       DEROGA: el artículo queda derogado (sin LLM);
       MODIFICA_PARCIAL (un inciso, un párrafo, una frase): el LLM reescribe el artículo y se
       verifica que el resultado salga del texto anterior y de la norma modificatoria (cobertura
       de 4-gramas >= 0,9). Si no pasa, el cambio queda pendiente y se informa.
  5. Salida con trazabilidad: cada artículo vigente con su historia (norma, artículo, fecha, qué
     parsers vieron la relación) y la lista de lo que no se pudo aplicar, con el motivo.

Uso:
  python scripts/24_consolidar.py --estimar
  python scripts/24_consolidar.py --hilos 6
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from grafo_legal.extractores import llm  # noqa: E402

OUT = RAIZ / "results/consolidado"
LEY, TO = 25552, 229909                      # Ley 20.744 y Decreto 390/76 (t.o. 1976)
FECHA_TO = "1976-05-21"
VERSION = "consolidado-v1-2026-11-20"

SIS_EXTRAER = """Sos un analista de técnica legislativa argentina. Te doy UN artículo de una norma que, según \
un grafo de relaciones, modifica la Ley de Contrato de Trabajo (LCT, Ley 20.744, texto ordenado 1976 por \
Decreto 390/76). Listá las operaciones que ESE artículo hace sobre artículos de la LCT.

Operaciones:
- SUSTITUYE: reemplaza un artículo completo de la LCT. "texto_nuevo" = el texto completo del artículo nuevo, \
copiado LITERALMENTE de la norma (sin las comillas de apertura y cierre).
- INCORPORA: agrega un artículo nuevo a la LCT (p. ej. "92 bis"). "texto_nuevo" literal, como arriba.
- DEROGA: deroga un artículo completo. "texto_nuevo" vacío.
- MODIFICA_PARCIAL: cambia solo una parte (un inciso, un párrafo, una frase, un monto), agrega o deroga \
un inciso o párrafo. "parte" = qué parte; "texto_nuevo" = el texto literal nuevo de esa parte si lo hay.

Reglas:
- Solo artículos de la LCT. Si el artículo modifica OTRA ley (aunque la mencione junto a la LCT), no la \
incluyas. Si no hace nada sobre la LCT, devolvé una lista vacía.
- "articulo": número del artículo de la LCT tal como lo usa el texto ordenado 1976 ("245", "92 bis").
- Copiá el texto nuevo exactamente: no corrijas, no resumas, no agregues.

Respondé SOLO con JSON: {"operaciones": [{"articulo": "245", "operacion": "SUSTITUYE", "parte": "", \
"texto_nuevo": "..."}]}"""

SIS_APLICAR = """Sos un analista de técnica legislativa argentina. Te doy el texto VIGENTE de un artículo de la \
Ley de Contrato de Trabajo y un artículo de otra norma que le hace una modificación PARCIAL (un inciso, un \
párrafo, una frase, un monto). Devolvé el texto completo del artículo después de aplicar SOLO esa \
modificación.

Reglas:
- No cambies nada que la modificación no toque. Copiá literal lo que queda igual.
- El texto nuevo tiene que salir literal de la norma modificatoria.
- Si la modificación no se puede aplicar a este texto (no existe el inciso, no coincide), devolvé \
"aplicada": false y explicá por qué en "motivo".

Respondé SOLO con JSON: {"aplicada": true, "texto": "...", "motivo": "..."}"""


def norm(t: str) -> str:
    t = unicodedata.normalize("NFKC", t or "")
    t = re.sub(r"[“”«»\"']", "", t)
    return re.sub(r"\s+", " ", t).strip().lower()


def contenido(sub: str, texto: str) -> bool:
    s, t = norm(sub), norm(texto)
    return bool(s) and (s in t or (len(s) > 300 and s[:150] in t and s[-150:] in t))


def cobertura(nuevo: str, fuentes: str, n: int = 4) -> float:
    w = norm(nuevo).split()
    f = " " + norm(fuentes) + " "
    if len(w) < n:
        return 1.0 if norm(nuevo) in f else 0.0
    grams = [" ".join(w[i:i + n]) for i in range(len(w) - n + 1)]
    return sum((" " + g + " ") in f for g in grams) / len(grams)


def leer_json(t: str) -> dict:
    m = re.search(r"\{.*\}", t, re.S)
    try:
        return json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        return {}


def numero_art(n: str) -> str:
    n = re.sub(r"\s+", " ", str(n).lower().replace("°", "").replace("º", "")).strip()
    return n


def base_to(art: pd.DataFrame) -> dict[str, dict]:
    t = art[(art.id_norma == TO) & (art.zona == "anexo")].texto.iloc[0]
    ms = list(re.finditer(r"(?:Art[ií]culo|Art\.)\s*(\d+)\s*(bis|ter|qu[aá]ter)?\s*[°º]?\s*[.—–-]", t))
    base = {}
    for i, m in enumerate(ms):
        n = numero_art(m.group(1) + (" " + m.group(2) if m.group(2) else ""))
        txt = t[m.start(): ms[i + 1].start() if i + 1 < len(ms) else len(t)]
        # los títulos y capítulos que quedan al final del artículo anterior se sacan del texto
        txt = re.split(r"\n\s*(?:TITULO|CAPITULO|Título|Capítulo)\s+[IVXL]+", txt)[0]
        base[n] = {"texto": txt.strip(), "historia": [{"fecha": "1976-05-21", "norma": "Decreto 390/76 (t.o. 1976)",
                                                       "operacion": "TEXTO_ORDENADO"}], "vigente": True}
    return base


def ampliado(dataset: pd.DataFrame, id_articulo: str) -> str:
    """El artículo modificatorio y los segmentos que lo siguen hasta el próximo artículo de la norma."""
    nid, orden = id_articulo.split("#")
    d = dataset[dataset.id_norma == int(nid)].sort_values("orden")
    d = d[d.orden >= int(orden)]
    if d.empty:
        return ""
    partes, num0 = [d.texto.iloc[0]], d.articulo.iloc[0]
    sig = str(int(num0) + 1) if str(num0).isdigit() else None
    for r in d.iloc[1:5].itertuples():
        if r.zona != "articulado" or (sig and str(r.articulo) == sig):
            break
        partes.append(r.texto)
    return "\n\n".join(partes)[:20000]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimar", action="store_true")
    ap.add_argument("--hilos", type=int, default=6)
    a = ap.parse_args()

    art = pd.read_json(OUT / f"manifiesto_{LEY}_articulos.json")
    rel = pd.read_json(OUT / f"manifiesto_{LEY}_relaciones.json")
    dataset = pd.read_csv(RAIZ / "data/dataset/articulos.csv", keep_default_na=False, dtype={"articulo": str})
    rel["fecha"] = rel.fecha_origen.astype(str).str[:10]
    rel = rel[(rel.id_origen != TO) & (rel.fecha > FECHA_TO) & rel.tipo.isin(["SUSTITUYE", "INCORPORA", "DEROGA", "MODIFICA"])]

    # un evento por artículo de origen, con las pistas del grafo
    eventos = []
    for k, g in rel.groupby("id_articulo_origen", sort=False):
        eventos.append({"id_articulo_origen": k, "id_origen": int(g.id_origen.iloc[0]), "norma": g.norma_origen.iloc[0],
                        "articulo_origen": str(g.articulo_origen.iloc[0]), "fecha": g.fecha.iloc[0],
                        "fuentes": sorted(set(g.fuente)),
                        "pistas": sorted({(t, str(d)) for t, d in zip(g.tipo, g.articulo_destino)}),
                        "texto": ampliado(dataset, k)})
    eventos.sort(key=lambda e: (e["fecha"], e["id_origen"], int(e["id_articulo_origen"].split("#")[1])))
    print(len(eventos), "artículos modificatorios de", len({e["id_origen"] for e in eventos}), "normas")
    if a.estimar:
        return

    clave = os.environ.get("ANTHROPIC_API_KEY") or (RAIZ / ".anthropic_key").read_text().strip()
    c_ext = llm.ClienteLLM(OUT / "cache", clave=clave, sistema=SIS_EXTRAER, version=VERSION + "-extraer")
    c_apl = llm.ClienteLLM(OUT / "cache", clave=clave, sistema=SIS_APLICAR, version=VERSION + "-aplicar")

    # 3. extracción (en paralelo: cada artículo modificatorio es independiente)
    def extraer(e):
        pistas = "; ".join(f"{t} art. {d or '(sin artículo)'}" for t, d in e["pistas"])
        msg = (f"Norma: {e['norma']} (publicada {e['fecha']}), artículo {e['articulo_origen']}.\n"
               f"Lo que vieron los parsers en el grafo: {pistas}.\n\nTEXTO DEL ARTÍCULO:\n{e['texto']}")
        return leer_json(c_ext.pedir(msg)["respuesta"]).get("operaciones", []) or []
    with ThreadPoolExecutor(a.hilos) as pool:
        ops_por_evento = list(pool.map(extraer, eventos))

    ops = []
    for e, lista in zip(eventos, ops_por_evento):
        for o in lista:
            if not isinstance(o, dict):
                continue
            op = str(o.get("operacion", "")).upper()
            nuevo = str(o.get("texto_nuevo") or "")
            verif = op in ("DEROGA",) or (op == "MODIFICA_PARCIAL" and (not nuevo or contenido(nuevo, e["texto"]))) \
                or (op in ("SUSTITUYE", "INCORPORA") and contenido(nuevo, e["texto"]))
            ops.append({**{k: e[k] for k in ("id_articulo_origen", "norma", "articulo_origen", "fecha", "fuentes")},
                        "articulo": numero_art(o.get("articulo", "")), "operacion": op, "parte": o.get("parte", ""),
                        "texto_nuevo": nuevo, "verificada": bool(verif), "texto_modificatorio": e["texto"]})
    ops = pd.DataFrame(ops)

    # 4. aplicación: cada artículo de la ley es una cadena independiente; dentro de ella, en orden
    base = base_to(art)
    pendientes = []

    def aplicar_cadena(num, grupo):
        estado = base.get(num, {"texto": "", "historia": [], "vigente": False, "nuevo": True})
        estado = {**estado, "historia": list(estado["historia"])}
        for o in grupo.itertuples():
            h = {"fecha": o.fecha, "norma": o.norma, "articulo_origen": o.articulo_origen, "operacion": o.operacion,
                 "parte": o.parte, "fuentes": o.fuentes}
            if not o.verificada:
                pendientes.append({**h, "articulo": num, "motivo": "el texto nuevo no está literal en la norma modificatoria"})
                continue
            if o.operacion in ("SUSTITUYE", "INCORPORA"):
                estado.update(texto=o.texto_nuevo.strip(), vigente=True)
            elif o.operacion == "DEROGA":
                estado.update(vigente=False)
            elif o.operacion == "MODIFICA_PARCIAL":
                if not estado["vigente"] or not estado["texto"]:
                    pendientes.append({**h, "articulo": num, "motivo": "el artículo no está vigente o no tiene texto"})
                    continue
                msg = (f"ARTÍCULO VIGENTE (art. {num} LCT):\n{estado['texto']}\n\n"
                       f"MODIFICACIÓN ({o.norma}, art. {o.articulo_origen}, {o.fecha}; parte: {o.parte}):\n{o.texto_modificatorio}")
                r = leer_json(c_apl.pedir(msg)["respuesta"])
                nuevo = str(r.get("texto") or "")
                cob = cobertura(nuevo, estado["texto"] + " " + o.texto_modificatorio) if nuevo else 0.0
                if not r.get("aplicada") or cob < 0.9 or norm(nuevo) == norm(estado["texto"]):
                    motivo = r.get("motivo") or ("cobertura %.2f" % cob if nuevo else "sin texto")
                    pendientes.append({**h, "articulo": num, "motivo": f"no se aplicó: {motivo}"})
                    continue
                estado["texto"] = nuevo.strip()
                h["cobertura"] = round(cob, 3)
            else:
                pendientes.append({**h, "articulo": num, "motivo": f"operación desconocida {o.operacion}"})
                continue
            estado["historia"].append(h)
        return num, estado

    if len(ops):
        ops = ops[ops.articulo != ""]
        cadenas = list(ops.groupby("articulo", sort=False))
        with ThreadPoolExecutor(a.hilos) as pool:
            resultado = dict(pool.map(lambda x: aplicar_cadena(*x), cadenas))
    else:
        resultado = {}
    consolidado = {**{k: {**v, "historia": list(v["historia"])} for k, v in base.items()}, **resultado}

    def clave_orden(n):
        m = re.match(r"(\d+)\s*(.*)", n)
        suf = {"": 0, "bis": 1, "ter": 2, "quater": 3, "quáter": 3}.get(m.group(2).strip(), 9) if m else 9
        return (int(m.group(1)) if m else 9999, suf)

    salida = [{"articulo": n, **consolidado[n]} for n in sorted(consolidado, key=clave_orden)]
    (OUT / "lct_consolidada.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    ops.drop(columns=["texto_modificatorio"]).to_csv(OUT / "operaciones.csv", index=False)
    pd.DataFrame(pendientes).to_csv(OUT / "no_aplicadas.csv", index=False)

    # 5. texto con trazabilidad
    L = ["# Ley de Contrato de Trabajo — texto consolidado desde el grafo", "",
         "Base: texto ordenado 1976 (Decreto 390/76). Modificaciones aplicadas en orden cronológico a partir de las "
         "relaciones del grafo (Neo4j) y del texto de cada norma modificatoria. Generado automáticamente: ver "
         "`docs/consolidado_lct.md` para el método y la evaluación.", ""]
    for x in salida:
        L.append(f"## Artículo {x['articulo']}" + ("" if x["vigente"] else " — DEROGADO"))
        if x["vigente"]:
            L += ["", x["texto"], ""]
        hist = [h for h in x["historia"] if h["operacion"] != "TEXTO_ORDENADO"]
        if hist:
            L.append("*Historia:* " + "; ".join(
                f"{h['operacion'].lower().replace('_', ' ')}{(' (' + h['parte'] + ')') if h.get('parte') else ''} por "
                f"{h['norma']}, art. {h.get('articulo_origen', '')} ({h['fecha']}; parsers: {', '.join(h.get('fuentes', []))})"
                for h in hist) + ".")
        else:
            L.append("*Historia:* sin cambios desde el t.o. 1976.")
        L.append("")
    (OUT / "lct_consolidada.md").write_text("\n".join(L), encoding="utf-8")

    res = {"eventos": len(eventos), "operaciones": int(len(ops)),
           "por_operacion": ops.operacion.value_counts().to_dict() if len(ops) else {},
           "verificadas": int(ops.verificada.sum()) if len(ops) else 0,
           "no_aplicadas": len(pendientes), "articulos": len(salida),
           "derogados": sum(not x["vigente"] for x in salida),
           "modificados": sum(len(x["historia"]) > 1 for x in salida),
           "incorporados": sum(x.get("nuevo", False) for x in salida),
           "uso": {"extraer": c_ext.uso, "aplicar": c_apl.uso}}
    (OUT / "resumen.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
