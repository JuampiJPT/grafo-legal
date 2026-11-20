"""PI4: grafos del digesto de la UNNOBA, uno por parser, con el mismo modelo que los de InfoLEG.

Se arma con las mismas piezas que el grafo de InfoLEG: la salida estándar (salida.py), las
relaciones por artículo (relaciones.desde_evidencias) y el grafo genérico (grafo.construir y
grafo.cargar_neo4j). Lo único propio de la fuente es la traducción de sus claves a nodos.

  - Cada norma del digesto (las 70 de la muestra y las que ellas citan) es un nodo :Norma. Como el
    grafo usa id_norma enteros (los de InfoLEG), a las normas del digesto se les asigna un id desde
    9.000.001, que no choca con los de InfoLEG; la clave del digesto queda en `numero` y `nombre`.
    split = "unnoba_muestra" (tiene texto) o "unnoba_citada" (solo se la nombra).
  - La identidad de una norma es su clave sin emisor (RES-44-2008), igual que en la evaluación.
  - Fuentes: unnoba_reglas_v3, unnoba_llm (prompt «vocab»: el de InfoLEG no ve las resoluciones)
    y unnoba_hibrido. Cada una va a su carpeta y no pisa los grafos de InfoLEG.

Datos personales: el texto de los artículos y el fragmento de cada relación pueden traer nombres
y DNI. En los CSV se tapan los DNI y relaciones.csv no va a git (.gitignore); a Neo4j se cargan
con los DNI tapados.

Uso:
  python scripts/22_grafo_unnoba.py                        # arma los CSV de los tres grafos
  export NEO4J_PASSWORD=$(cat .neo4j_password)
  python scripts/22_grafo_unnoba.py --uri bolt://localhost:7688   # y los carga (sin borrar nada)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from grafo_legal.archivos import escribir_texto  # noqa: E402
from grafo_legal.extractores import hibrido, llm  # noqa: E402
from grafo_legal.extractores.relaciones import desde_evidencias  # noqa: E402
from grafo_legal.fuentes import unnoba  # noqa: E402
from grafo_legal.grafo import cargar_neo4j, construir  # noqa: E402
from grafo_legal.salida import CLAVE, COLUMNAS, validar  # noqa: E402

# el adaptador y las corridas de la PI4 viven en el script 21: se reusan tal cual
_spec = importlib.util.spec_from_file_location("pi4", RAIZ / "scripts/21_pi4_unnoba.py")
pi4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pi4)

ID_BASE = 9_000_000
_DNI = re.compile(r"\b\d{1,2}[.,]\s?\d{3}[.,]\s?\d{3}\b")
_MESES = "enero febrero marzo abril mayo junio julio agosto septiembre setiembre octubre noviembre diciembre".split()
_FECHA = re.compile(r"(\d{1,2})\s*(?:°|º)?\s+de\s+(" + "|".join(_MESES) + r")\s+(?:de|del)\s+(\d{4})", re.I)

TIPO = {"RES": "Resolución", "ORD": "Ordenanza", "LEY": "Ley", "DEC": "Decreto", "ESTATUTO": "Estatuto"}
ORGANISMO = {"HCS": "UNNOBA - Consejo Superior", "REC": "UNNOBA - Rector", "CDET": "UNNOBA - Consejo Directivo, Escuela de Tecnología",
             "DET": "UNNOBA - Dirección, Escuela de Tecnología", "MIN": "Ministerio de Educación", "NAC": "Nación",
             "PROV": "Provincia de Buenos Aires", "?": ""}


def tapar(t: str) -> str:
    return _DNI.sub("[DNI]", t) if isinstance(t, str) else t


def _mes(nombre: str) -> int:
    orden = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
             "noviembre", "diciembre"]
    return orden.index("septiembre" if nombre.lower() == "setiembre" else nombre.lower()) + 1


def fecha_de(texto: str) -> str:
    m = _FECHA.search(texto[:600])
    return f"{m.group(3)}-{_mes(m.group(2)):02d}-{int(m.group(1)):02d}" if m else ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--uri", help="bolt://localhost:7688; sin --uri solo se arman los CSV")
    ap.add_argument("--user", default="neo4j")
    a = ap.parse_args()

    docs = [json.loads(l) for l in pi4.TEXTOS.read_text(encoding="utf-8").splitlines() if l.strip()]
    preps = [pi4.preparar(d) for d in docs]
    ev = pd.DataFrame([x for i, (d, p) in enumerate(zip(docs, preps)) for x in pi4.evidencias(i, d, p)])

    # ---- normas: ids enteros para las claves del digesto ----------------------------------
    origen_doc = {i: unnoba.clave_comparable(unnoba.clave_origen(d["titulo"])) for i, d in enumerate(docs)}
    # clave completa (con emisor) de cada norma: la del título si es de la muestra, si no la más
    # frecuente entre las menciones que tienen emisor
    completa = {origen_doc[i]: unnoba.clave_origen(d["titulo"]) for i, d in enumerate(docs)}
    for k, grp in ev.groupby("id_destino"):
        if k not in completa:
            con = grp[~grp.clave.str.contains(r"-\?-", regex=True)].clave
            completa[k] = (con if len(con) else grp.clave).value_counts().index[0]
    claves = list(dict.fromkeys(list(origen_doc.values()) + sorted(set(ev.id_destino))))
    id_de = {k: ID_BASE + n for n, k in enumerate(claves, 1)}

    def etiqueta(k: str) -> str:
        c = completa.get(k, k).split("-")
        if c[0] == "ESTATUTO":
            return "Estatuto UNNOBA"
        if c[0] == "LEY":
            return f"Ley {c[-1] if len(c) < 4 else c[2]}"
        emisor = "" if len(c) < 4 or c[1] in ("?", "NAC") else f" {c[1]}"
        return f"{TIPO.get(c[0], c[0])}{emisor} {c[-2]}/{c[-1]}"

    filas_n = []
    for k in claves:
        c = completa.get(k, k).split("-")
        doc_i = next((i for i, o in origen_doc.items() if o == k), None)
        fecha = fecha_de(preps[doc_i]["texto"]) if doc_i is not None else (c[-1] if c[-1].isdigit() and len(c[-1]) == 4 else "")
        # numero = la etiqueta sin el tipo ("HCS 44/2008"), así el nombre del nodo queda legible
        filas_n.append({"id_norma": id_de[k], "tipo_norma": TIPO.get(c[0], c[0]),
                        "numero_norma": etiqueta(k).split(" ", 1)[1],
                        "fecha_boletin": "", "fecha_sancion": fecha,
                        "titulo_resumido": docs[doc_i]["titulo"] if doc_i is not None else etiqueta(k),
                        "titulo_sumario": (f"clave {k} · " + docs[doc_i].get("secciones", "")) if doc_i is not None else f"clave {k}",
                        "organismo_origen": ORGANISMO.get(c[1] if len(c) > 1 else "", "") if c[0] != "ESTATUTO" else "UNNOBA",
                        "split": "unnoba_muestra" if doc_i is not None else "unnoba_citada"})
    normas = pd.DataFrame(filas_n)
    etq = {id_de[k]: etiqueta(k) for k in claves}

    # ---- artículos: encabezado (#0) y un segmento por artículo del dispositivo ----------------
    filas_a, textos = [], {}
    for i, p in enumerate(preps):
        o, t = id_de[origen_doc[i]], tapar(p["texto"])
        textos[o] = t
        ini_art = next(x for x in p["partes"] if x.parte == "articulado").inicio
        filas_a.append({"id_norma": o, "orden": 0, "zona": "encabezado", "articulo": "0", "inicio": 0,
                        "fin": ini_art, "texto": t[:ini_art]})
        for n, (num, ai, af) in enumerate(p["articulos"], 1):
            filas_a.append({"id_norma": o, "orden": n, "zona": "articulado", "articulo": num, "inicio": ai,
                            "fin": af, "texto": t[ai:af]})
    articulos = pd.DataFrame(filas_a)

    # ---- reglas: las mismas relaciones por artículo que en InfoLEG ---------------------------
    e = ev.copy()
    e["id_origen"] = e.doc.map(lambda i: id_de[origen_doc[i]])
    e["id_destino"] = e.id_destino.map(id_de)
    e["fragmento"] = [re.sub(r"\s+", " ", textos[o][max(0, s - 150): f + 150]).strip()
                      for o, s, f in zip(e.id_origen, e.inicio, e.fin)]
    rel_reglas = desde_evidencias(e, textos, articulos, etq, fuente="unnoba_reglas_v3")

    # ---- híbrido: como en el script 20, sobre las relaciones de las reglas --------------------
    #   par aceptado: queda con el tipo de las reglas si alguna relación lo tiene; si todas son
    #   CITA, la primera del articulado (o la primera) toma el tipo del híbrido.
    #   par no aceptado: todas sus relaciones quedan como CITA.
    h = pd.read_csv(pi4.SALIDA / "relaciones_hibrido.csv")
    h["o"] = h.doc.map(lambda i: id_de[origen_doc[i]])
    h["d"] = h.id_destino.map(id_de)
    acept = {(o, d): t for o, d, t, ac in zip(h.o, h.d, h.tipo, h.acepta) if ac}
    partes = []
    for k, grp in rel_reglas.assign(fuente="unnoba_hibrido").groupby(["id_norma_origen", "id_norma_destino"], sort=False):
        grp = grp.copy()
        if k not in acept:
            grp["tipo"], grp["verbo"] = "CITA", ""
        elif (grp.tipo == "CITA").all():
            i_rep = grp[grp.parte_origen == "articulado"].index.min() if (grp.parte_origen == "articulado").any() else grp.index[0]
            grp.loc[i_rep, "tipo"] = acept[k]
            prob = h[(h.o == k[0]) & (h.d == k[1])].probabilidad.iloc[0]
            grp.loc[i_rep, "confianza"] = "" if pd.isna(prob) else str(round(float(prob), 2))
        partes.append(grp)
    rel_hib = pd.concat(partes, ignore_index=True).drop_duplicates(CLAVE)

    # ---- LLM (prompt «vocab»): de la cache, con la ubicación de cada cita ---------------------
    cli = llm.ClienteLLM(pi4.SALIDA / "cache_llm", clave=None, sistema=pi4.con_vocab(llm.SISTEMA, pi4._VOCAB_LLM),
                         version=llm.VERSION_PROMPT + "+vocab-unnoba")
    filas_l = []
    for i, (d, p) in enumerate(zip(docs, preps)):
        t, o = p["texto"], id_de[origen_doc[i]]
        segs = []
        enc = [x for x in p["partes"] if x.parte in ("visto", "considerando")]
        ini, fin = min(x.inicio for x in enc), max(x.fin for x in enc)
        if fin > ini:
            segs.append(llm.Segmento(i, 0, "0", "encabezado", ini, t[ini:fin]))
        for n, (num, ai, af) in enumerate(p["articulos"], 1):
            segs.append(llm.Segmento(i, n, num, "articulado", ai, t[ai:af]))
        for lote in llm.lotes(segs):
            resp = cli.pedir(llm.mensaje_usuario(d["titulo"], lote))
            por_seg = {f"S{s.orden}": (s, off, txt) for s, off, txt in lote}
            for r in llm.leer_json(resp["respuesta"]):
                seg = por_seg.get(str(r.get("segmento")))
                if seg is None:
                    continue
                s, off, txt = seg
                cita = str(r.get("cita") or "")
                pos = llm.ubicar(cita, txt)
                clave = pi4.clave_llm(r)
                if pos < 0 or clave is None or clave == origen_doc[i]:
                    continue                        # cita no verificada o autorreferencia
                if clave not in id_de:              # norma que solo encontró el LLM
                    claves.append(clave); id_de[clave] = ID_BASE + len(claves); etq[id_de[clave]] = etiqueta(clave)
                    c = clave.split("-")
                    normas.loc[len(normas)] = {"id_norma": id_de[clave], "tipo_norma": TIPO.get(c[0], c[0]),
                                               "numero_norma": etiqueta(clave).split(" ", 1)[1], "fecha_boletin": "", "fecha_sancion": "",
                                               "titulo_resumido": etiqueta(clave), "titulo_sumario": f"clave {clave}",
                                               "organismo_origen": "", "split": "unnoba_citada"}
                inicio = s.inicio + off + pos
                tipo = str(r.get("tipo") or "CITA").upper()
                tipo = tipo if tipo in ("SUSTITUYE", "INCORPORA", "DEROGA", "REGLAMENTA", "MODIFICA", "CITA") else "CITA"
                art = r.get("articulo_destino")
                filas_l.append({
                    "fuente": "unnoba_llm", "id_norma_origen": o, "norma_origen": etq[o],
                    "id_articulo_origen": f"{o}#{s.orden}", "articulo_origen": s.articulo,
                    "parte_origen": "articulado" if s.zona == "articulado" else unnoba.parte_de(p["partes"], inicio),
                    "tipo": tipo, "id_norma_destino": id_de[clave], "norma_destino": etq[id_de[clave]],
                    "articulo_destino": "" if art in (None, "", "null") else str(art).strip().lower(),
                    "verbo": str(r.get("verbo") or "") if tipo != "CITA" else "", "metodo": "llm", "confianza": "",
                    "n_menciones": 1, "inicio": inicio, "fin": inicio + len(cita),
                    "fragmento": tapar(re.sub(r"\s+", " ", txt[max(0, pos - 150): pos + len(cita) + 150]).strip())})
    rel_llm = pd.DataFrame(filas_l, columns=list(COLUMNAS))
    n = rel_llm.groupby(CLAVE).size().rename("n_menciones")
    rel_llm = rel_llm.drop(columns="n_menciones").drop_duplicates(CLAVE).join(n, on=CLAVE)[list(COLUMNAS)]

    # ---- grafos ------------------------------------------------------------------------------
    pw = os.environ.get("NEO4J_PASSWORD")
    if a.uri and not pw:
        sys.exit("Falta la variable de entorno NEO4J_PASSWORD")
    resumenes = {}
    for nombre, rel in (("reglas", rel_reglas), ("llm", rel_llm), ("hibrido", rel_hib)):
        rel = rel.copy()
        rel["fragmento"] = rel.fragmento.map(tapar)
        errores = validar(rel)
        if errores:
            sys.exit(f"{nombre}: la salida no cumple el formato: {errores}")
        g = construir(normas, articulos, rel)
        out = RAIZ / f"data/grafo_unnoba_{nombre}"
        out.mkdir(parents=True, exist_ok=True)
        for arch, df in (("normas.csv", g["normas"]), ("articulos.csv", g["articulos"].drop(columns="texto")),
                         ("relaciones.csv", g["relaciones"])):
            df.to_csv(out / arch, index=False, lineterminator="\n")
        r = g["relaciones"]
        no_cita = r[r.tipo != "CITA"]
        resumenes[nombre] = {
            "fuente": r.fuente.iloc[0],
            "nodos": {"Norma": len(g["normas"]), "Norma_con_texto": int(g["normas"].tiene_texto.sum()),
                      "Articulo": len(g["articulos"]), "Articulo_sin_texto": int((~g["articulos"].tiene_texto).sum())},
            "aristas": {"CONTIENE": len(g["articulos"]), **r.tipo.value_counts().to_dict()},
            "pares_con_relacion_no_cita": int(no_cita[["id_norma_origen", "id_norma_destino"]].drop_duplicates().shape[0]),
            "relaciones_a_articulo": int(r.destino_es_articulo.sum()),
        }
        escribir_texto(out / "resumen.json", json.dumps(resumenes[nombre], indent=2, ensure_ascii=False))
        if a.uri:
            resumenes[nombre]["neo4j"] = cargar_neo4j(g, a.uri, a.user, pw, borrar=False)
    print(json.dumps(resumenes, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
