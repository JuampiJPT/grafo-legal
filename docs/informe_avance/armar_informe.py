"""Arma el informe de avance (B64): une las secciones, agrega la bitácora como anexo y genera el .docx.

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


def bitacora() -> str:
    """La bitácora del repo, con los títulos un nivel más abajo para que queden dentro del anexo."""
    texto = (RAIZ / "docs/drive/00_bitacora.md").read_text(encoding="utf-8")
    texto = texto.split("\n", 1)[1]  # se saca su título: el anexo ya lo tiene
    return re.sub(r"^(#{1,5}) ", lambda m: "#" + m.group(1) + " ", texto, flags=re.M)


def main():
    md = "\n\n".join((AQUI / p).read_text(encoding="utf-8").rstrip() for p in PARTES)
    # El epígrafe de cada figura va como párrafo propio debajo de la imagen: al convertir el .docx a Google
    # Doc, el epígrafe que pandoc genera desde el texto alternativo se pierde.
    md = re.sub(r"^!\[(Figura [^\]]+)\]\(([^)]+)\)$", r"![](\2){width=100%}\n\n*\1*", md, flags=re.M)
    md += "\n\n" + bitacora()
    (AQUI / "informe_avance.md").write_text(md, encoding="utf-8")
    subprocess.run(["pandoc", "informe_avance.md", "-o", "informe_avance.docx", "--resource-path=.", "-f", "markdown"],
                   cwd=AQUI, check=True)
    print("escrito informe_avance.md e informe_avance.docx")


if __name__ == "__main__":
    main()
