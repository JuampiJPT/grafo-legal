"""Arma el informe de avance (B64, revisado en B70): une las secciones, agrega la bitácora como anexo y genera el .docx.

Uso: python docs/informe_avance/armar_informe.py
Salida: docs/informe_avance/informe_avance.md (fuente única) e informe_avance.docx (para subir al Drive como
Google Doc y exportar a PDF). Requiere pandoc. Las figuras se regeneran antes con scripts/31_figuras_informe.py.
"""
import re
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
PARTES = ["01_intro_antecedentes.md", "02_datos_diseno.md", "03_diseno_verificacion.md",
          "04_resultados.md", "05_discusion_plan_refs.md"]


# Entradas que no van al anexo: el video explicativo y la revisión final del informe (B70). Están en la
# bitácora completa del Drive y del repositorio.
FUERA_DEL_ANEXO = {"B65", "B66", "B67", "B69", "B70"}


def bitacora() -> str:
    """La bitácora del repo como anexo de entrega (B70).

    Se transcribe sin cambiar el texto de las entradas, salvo cuatro omisiones que el anexo declara:
      - la columna Estado del índice (abierta o cerrada es de uso interno); el índice va como lista;
      - la sección final «Cuestiones abiertas» (lo pendiente está en la sección 8 del informe);
      - las entradas de FUERA_DEL_ANEXO;
      - el bloque «Abierto» de B64, que eran las tareas de esta misma entrega.
    Los títulos bajan un nivel para quedar dentro del anexo.
    """
    texto = (RAIZ / "docs/drive/00_bitacora.md").read_text(encoding="utf-8")
    texto = texto.split("\n", 1)[1]                      # se saca su título: el anexo ya lo tiene
    texto = texto.split("\n## Cuestiones abiertas")[0]   # la lista interna de tareas
    texto = texto.replace(" Estado: abierta o cerrada.", "")
    # solo se toca la tabla del índice: desde su encabezado hasta la primera línea que no es tabla
    lineas, en_indice = [], False
    for ln in texto.split("\n"):
        # el índice va como lista y no como tabla: al convertir a Google Doc, una tabla de 65 filas con
        # columnas angostas se partía en varias páginas y cortaba «B01» y las fechas
        if ln.startswith("| ID | Fecha | Tipo | Tema | Estado |"):
            en_indice = True
            continue
        if en_indice and not ln.startswith("|"):
            en_indice = False
        if en_indice:
            if ln.startswith("|---"):
                continue
            celdas = [c.strip() for c in ln.strip().strip("|").split("|")]
            if celdas[0] in FUERA_DEL_ANEXO:
                continue
            ln = f"- **{celdas[0]}** · {celdas[1]} · {celdas[2]} · {celdas[3]}"   # sin la columna Estado
        lineas.append(ln)
    texto = "\n".join(lineas)
    # entradas completas fuera del anexo
    partes = re.split(r"(?m)^(?=### B\d+ · )", texto)
    partes = [p for p in partes if not (re.match(r"### (B\d+) ", p) and re.match(r"### (B\d+) ", p).group(1) in FUERA_DEL_ANEXO)]
    texto = "".join(partes)
    # el bloque «Abierto» de B64 (tareas de esta entrega)
    texto = re.sub(r"(?s)(### B64 · .*?)\n\*\*Abierto\.\*\*\n.*?(?=\n### B|\Z)", r"\1\n", texto)
    return re.sub(r"^(#{1,5}) ", lambda m: "#" + m.group(1) + " ", texto, flags=re.M)


def anchos_de_tablas(md: str) -> str:
    """Ajusta el separador de cada tabla para que pandoc reparta el ancho según el contenido (B70).

    En una tabla con filas largas, pandoc fija el ancho relativo de cada columna por la cantidad de guiones
    del separador. Con «|---|---|» todas las columnas quedan iguales y las de texto largo se ven angostas.
    Acá cada columna recibe guiones en proporción al largo medio de sus celdas, con un mínimo.
    """
    lineas = md.split("\n")
    for i in range(1, len(lineas)):
        if not re.match(r"^\|(\s*:?-{3,}:?\s*\|)+\s*$", lineas[i]) or not lineas[i - 1].startswith("|"):
            continue
        filas = [lineas[i - 1]]
        j = i + 1
        while j < len(lineas) and lineas[j].startswith("|"):
            filas.append(lineas[j])
            j += 1
        celdas = [[c.strip() for c in f.strip().strip("|").split("|")] for f in filas]
        n = len(celdas[0])
        # peso de cada columna: el largo medio de sus celdas, pero nunca menos que su palabra más larga
        # (así «B01», «27/10» o «Cuestionamiento» no se cortan)
        def peso(k):
            textos = [c[k] for c in celdas if k < len(c)]
            medio = sum(len(x) for x in textos) / len(textos)
            palabra = max((len(w) for x in textos for w in x.replace("*", "").split()), default=3)
            return max(medio, palabra * 2.2, 7)
        largo = [peso(k) for k in range(n)]
        total = sum(largo)
        guiones = [max(6, round(100 * l / total)) for l in largo]
        lineas[i] = "|" + "|".join("-" * g for g in guiones) + "|"
    return "\n".join(lineas)


def main():
    md = "\n\n".join((AQUI / p).read_text(encoding="utf-8").rstrip() for p in PARTES)
    # El epígrafe de cada figura va como párrafo propio debajo de la imagen: al convertir el .docx a Google
    # Doc, el epígrafe que pandoc genera desde el texto alternativo se pierde.
    md = re.sub(r"^!\[(Figura [^\]]+)\]\(([^)]+)\)$", r"![](\2){width=100%}\n\n*\1*", md, flags=re.M)
    md += "\n\n" + bitacora()
    md = anchos_de_tablas(md)
    (AQUI / "informe_avance.md").write_text(md, encoding="utf-8")
    subprocess.run(["pandoc", "informe_avance.md", "-o", "informe_avance.docx", "--resource-path=.", "-f", "markdown"],
                   cwd=AQUI, check=True)
    print("escrito informe_avance.md e informe_avance.docx")


if __name__ == "__main__":
    main()
