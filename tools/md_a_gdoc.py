"""Convierte un Markdown simple en un pedido batchUpdate de Google Docs que reemplaza todo el cuerpo.

Sirve para mantener la copia en el Drive de los documentos que viven en el repositorio, editando el
mismo Google Doc (el link no cambia). Soporta: titulos (#..####), parrafos, listas con - o 1.,
tablas con |, bloques de codigo (como texto en Courier), **negrita**, `codigo` y [links](url).

Uso: python tools/md_a_gdoc.py entrada.md fin_del_cuerpo revision_id [--agregar] > pedido.json
     --agregar agrega al final del cuerpo en lugar de reemplazarlo (para mandar un documento largo por partes).
     fin_del_cuerpo = endIndex del ultimo elemento del cuerpo (docs_index.py outline lo imprime)
"""

import json
import re
import sys

ESTILO = {1: "HEADING_1", 2: "HEADING_2", 3: "HEADING_3", 4: "HEADING_4"}
_INLINE = re.compile(r"\*\*(.+?)\*\*|`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)|(?<![\w*])\*([^*\n]+?)\*(?![\w*])")


def inline(texto):
    """Devuelve (texto_plano, [(ini, fin, estilo)]) con offsets relativos al texto plano."""
    plano, estilos, i = "", [], 0
    for m in _INLINE.finditer(texto):
        plano += texto[i:m.start()]
        ini = len(plano)
        if m.group(1) is not None:
            sub, sub_est = inline(m.group(1))
            plano += sub
            estilos += [(ini + a, ini + b, e) for a, b, e in sub_est]
            estilos.append((ini, len(plano), {"bold": True}))
        elif m.group(2) is not None:
            plano += m.group(2)
        elif m.group(3) is not None:
            plano += m.group(3)
            estilos.append((ini, len(plano), {"link": {"url": m.group(4)}}))
        else:
            sub, sub_est = inline(m.group(5))
            plano += sub
            estilos += [(ini + x, ini + y, e) for x, y, e in sub_est]
            estilos.append((ini, len(plano), {"italic": True}))
        i = m.end()
    plano += texto[i:]
    return plano, estilos


def bloques(md):
    lineas = md.splitlines()
    i = 0
    while i < len(lineas):
        l = lineas[i]
        if not l.strip() or l.strip().startswith("<!--"):
            i += 1
            continue
        if l.startswith("```"):
            j = i + 1
            while j < len(lineas) and not lineas[j].startswith("```"):
                j += 1
            yield ("codigo", "\n".join(lineas[i + 1:j]))
            i = j + 1
            continue
        if l.lstrip().startswith("|"):
            filas = []
            while i < len(lineas) and lineas[i].lstrip().startswith("|"):
                if not re.match(r"^\|[\s:|-]+\|$", lineas[i].strip()):
                    filas.append([c.strip() for c in lineas[i].strip().strip("|").split("|")])
                i += 1
            yield ("tabla", filas)
            continue
        m = re.match(r"^(#{1,4}) (.*)", l)
        if m:
            yield ("titulo", (len(m.group(1)), m.group(2)))
            i += 1
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.) (.*)", l)
        if m:
            yield ("item", (m.group(2)[0].isdigit(), m.group(3)))
            i += 1
            continue
        # parrafo: junta lineas hasta una linea vacia o un bloque distinto
        partes = [l.strip()]
        i += 1
        while i < len(lineas) and lineas[i].strip() and not re.match(r"^(#{1,4} |\s*\||```|\s*([-*]|\d+\.) )", lineas[i]):
            partes.append(lineas[i].strip())
            i += 1
        yield ("parrafo", " ".join(partes))


def construir(md, fin_cuerpo, revision, agregar=False):
    """Arma el pedido en tres pasadas: inserciones (texto agrupado y tablas, en orden), un reseteo
    global de estilos y despues los estilos puntuales (titulos, negritas, links, vinetas)."""
    ins, estilos, listas = [], [], []
    cur = fin_cuerpo - 1 if agregar else 1
    inicio = cur
    buf, buf_ini = "", cur

    def flush():
        nonlocal buf, buf_ini
        if buf:
            ins.append({"insertText": {"location": {"index": buf_ini}, "text": buf}})
        buf, buf_ini = "", cur

    def parrafo(texto, estilo=None, mono=False):
        nonlocal cur, buf
        plano, est = inline(texto)
        ini = cur
        buf += plano + "\n"
        cur += len(plano) + 1
        if estilo:
            estilos.append({"updateParagraphStyle": {"range": {"startIndex": ini, "endIndex": cur},
                                                     "paragraphStyle": {"namedStyleType": estilo}, "fields": "namedStyleType"}})
        if mono and plano:
            est = est + [(0, len(plano), {"weightedFontFamily": {"fontFamily": "Courier New"}})]
        for a, b, e in est:
            if b > a:
                estilos.append({"updateTextStyle": {"range": {"startIndex": ini + a, "endIndex": ini + b},
                                                    "textStyle": e, "fields": ",".join(e)}})
        return ini, cur

    pendiente = None
    for tipo, val in bloques(md):
        if tipo != "item" and pendiente:
            listas.append(tuple(pendiente))
            pendiente = None
        if tipo == "titulo":
            parrafo(val[1], ESTILO[val[0]])
        elif tipo == "parrafo":
            parrafo(val)
        elif tipo == "item":
            ordenada, texto = val
            a, b = parrafo(texto)
            if pendiente and pendiente[2] == ordenada:
                pendiente[1] = b
            else:
                if pendiente:
                    listas.append(tuple(pendiente))
                pendiente = [a, b, ordenada]
        elif tipo == "codigo":
            for linea in val.splitlines() or [""]:
                parrafo(linea, mono=True)
        elif tipo == "tabla":
            flush()
            filas = val
            R, C = len(filas), max(len(f) for f in filas)
            filas = [f + [""] * (C - len(f)) for f in filas]
            i0 = cur
            ins.append({"insertTable": {"rows": R, "columns": C, "location": {"index": i0}}})
            celdas = [[inline(c) for c in f] for f in filas]
            for r in range(R - 1, -1, -1):
                for c in range(C - 1, -1, -1):
                    t = celdas[r][c][0]
                    if t:
                        ins.append({"insertText": {"location": {"index": i0 + 4 + r * (2 * C + 1) + 2 * c}, "text": t}})
            acumulado = 0
            for r in range(R):
                for c in range(C):
                    t, est = celdas[r][c]
                    pos = i0 + 4 + r * (2 * C + 1) + 2 * c + acumulado
                    if t and r == 0:
                        estilos.append({"updateTextStyle": {"range": {"startIndex": pos, "endIndex": pos + len(t)},
                                                            "textStyle": {"bold": True}, "fields": "bold"}})
                    for a, b, e in est:
                        if t and b > a:
                            estilos.append({"updateTextStyle": {"range": {"startIndex": pos + a, "endIndex": pos + b},
                                                                "textStyle": e, "fields": ",".join(e)}})
                    acumulado += len(t)
            cur = i0 + 3 + R * (2 * C + 1) + acumulado
            buf_ini = cur
    if pendiente:
        listas.append(tuple(pendiente))
    flush()

    req = []
    if fin_cuerpo > 2 and not agregar:
        req.append({"deleteContentRange": {"range": {"startIndex": 1, "endIndex": fin_cuerpo - 1}}})
    req += ins
    req.append({"updateParagraphStyle": {"range": {"startIndex": inicio, "endIndex": cur},
                                         "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"}, "fields": "namedStyleType"}})
    req.append({"updateTextStyle": {"range": {"startIndex": inicio, "endIndex": cur}, "textStyle": {},
                                    "fields": "bold,italic,link,weightedFontFamily"}})
    req += estilos
    for a, b, ordenada in listas:
        req.append({"createParagraphBullets": {"range": {"startIndex": a, "endIndex": b - 1},
                                               "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN" if ordenada
                                               else "BULLET_DISC_CIRCLE_SQUARE"}})
    return {"requests": req, "writeControl": {"requiredRevisionId": revision}}


if __name__ == "__main__":
    md = open(sys.argv[1], encoding="utf-8").read()
    agregar = len(sys.argv) > 4 and sys.argv[4] == "--agregar"
    print(json.dumps(construir(md, int(sys.argv[2]), sys.argv[3], agregar), ensure_ascii=False))
