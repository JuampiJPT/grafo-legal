"""Convierte el JSON de documents.get (Google Docs API) a Markdown.

Se usa para guardar en el repo una copia de los documentos del Drive del TP (bitacora, informes
por etapa). Soporta titulos, negrita, cursiva, links, listas y tablas, que es lo que usan esos docs.

Uso: python tools/gdoc_a_md.py documento.json salida.md
"""

import json
import sys

NIVEL = {"TITLE": "#", "HEADING_1": "#", "HEADING_2": "##", "HEADING_3": "###", "HEADING_4": "####"}


def runs(elems, en_titulo=False):
    out = []
    for e in elems:
        tr = e.get("textRun")
        if not tr:
            continue
        t = tr["content"].replace("\n", "")
        if not t:
            continue
        st = tr.get("textStyle", {})
        core = t.strip()
        if core and not en_titulo:
            lead, trail = t[: len(t) - len(t.lstrip())], t[len(t.rstrip()):]
            if st.get("link", {}).get("url"):
                core = f"[{core}]({st['link']['url']})"
            if st.get("bold"):
                core = f"**{core}**"
            if st.get("italic"):
                core = f"*{core}*"
            t = lead + core + trail
        out.append(t)
    s = "".join(out)
    return s.replace("****", "")


def bloque(c, listas):
    if "paragraph" in c:
        p = c["paragraph"]
        estilo = p.get("paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT")
        texto = runs(p["elements"], en_titulo=estilo in NIVEL).strip()
        if not texto:
            return ""
        if estilo in NIVEL:
            return f"{NIVEL[estilo]} {texto}\n"
        if "bullet" in p:
            b = p["bullet"]
            nivel = b.get("nestingLevel", 0)
            props = listas.get(b["listId"], {}).get("listProperties", {}).get("nestingLevels", [{}])
            lv = props[min(nivel, len(props) - 1)]
            ordenada = "glyphSymbol" not in lv and lv.get("glyphType") not in ("GLYPH_TYPE_UNSPECIFIED", "NONE", None)
            return "  " * nivel + ("1. " if ordenada else "- ") + texto
        return texto + "\n"
    if "table" in c:
        filas = []
        for r in c["table"]["tableRows"]:
            celdas = []
            for cell in r["tableCells"]:
                txt = " ".join(bloque(x, listas).strip() for x in cell["content"]).strip()
                celdas.append(txt.replace("|", "\\|").replace("\n", " "))
            filas.append("| " + " | ".join(celdas) + " |")
        if filas:
            n = filas[0].count(" | ") + 1
            filas.insert(1, "|" + "---|" * n)
        return "\n".join(filas) + "\n"
    return ""


def main(src, dst):
    d = json.load(open(src, encoding="utf-8"))
    d = d.get("content", d)
    tab = d["tabs"][0]["documentTab"] if "tabs" in d else d
    listas = tab.get("lists", {})
    md, prev_lista = "", False
    for c in tab["body"]["content"]:
        b = bloque(c, listas).rstrip("\n")
        if not b:
            continue
        es_lista = "paragraph" in c and "bullet" in c["paragraph"]
        md += ("\n" if (es_lista and prev_lista) else "\n\n") + b
        prev_lista = es_lista
    encabezado = (f"<!-- Copia del Google Doc \"{d['title']}\" (id {d['documentId']}, revision {d['revisionId'][:12]}). "
                  f"La version editable es la del Drive; esta copia se regenera con tools/gdoc_a_md.py. -->\n\n")
    open(dst, "w", encoding="utf-8").write(encabezado + md.strip() + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
