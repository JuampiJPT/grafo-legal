"""Tests sin red: menciones, catalogo y el script 01 sobre zips sinteticos.  Correr: pytest -q"""

import csv
import io
import subprocess
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from grafo_legal.catalogo import Catalogo, Norma                # noqa: E402
from grafo_legal.extractores.menciones import detectar          # noqa: E402
from grafo_legal.fuentes.infoleg import html_a_texto, segmentar  # noqa: E402


def nums(s):
    return [(m.tipo, m.numero.replace(".", ""), m.anio) for m in detectar(s)]


def test_menciones_basicas():
    assert nums("Sustitúyese el artículo 2° de la Ley N° 20.744 (t.o. 1976)") == [("ley", "20744", None)]
    assert nums("Leyes Nros. 24.013, 24.465 y 24.467") == [("ley", "24013", None), ("ley", "24465", None),
                                                           ("ley", "24467", None)]
    assert nums("Decreto N° 1694/06") == [("decreto", "1694", 2006)]
    assert nums("Decreto-Ley N° 1740/45") == [("decreto/ley", "1740", 1945)]
    assert nums("DECRETO DE NECESIDAD Y URGENCIA N° 70/23") == [("decreto", "70", 2023)]


def test_menciones_dificiles():
    assert nums("las Leyes Nros. 20.744 (t.o. 1976) y sus modificatorias y 24.013") == [
        ("ley", "20744", None), ("ley", "24013", None)]
    assert nums("Ley de Contrato de Trabajo Nº 20.744") == [("ley", "20744", None)]
    assert nums("la ley núm. 11.729.") == [("ley", "11729", None)]
    assert nums("Ley NQ 12.713") == [("ley", "12713", None)]
    # el ano del texto ordenado no es una ley
    assert ("ley", "1976", None) not in nums("Ley N° 20.744 (t.o. 1976)")


def test_catalogo_decretos_y_decretos_leyes():
    cat = Catalogo([Norma(1, "decreto", "27", 2018, "2018-01-11", "Decreto 27"),
                    Norma(2, "decreto", "27", 2021, "2021-01-20", "Decreto 27"),
                    Norma(3, "ley", "17258", 1967, "1967-05-04", "Ley 17258")])
    assert cat.resolver("decreto", "27", None) is None          # ambiguo sin ano
    assert cat.resolver("decreto", "27", 2021).id == 2
    assert cat.resolver("decreto/ley", "17.258", 1967).id == 3  # decreto-ley catalogado como Ley


def test_segmentacion():
    html = ("<p>VISTO la Ley N° 1.</p><p>DECRETA:</p><p>Artículo 1° — Modifícase la Ley N° 2.</p>"
            "<p>Art. 2° — Comuníquese.</p><p>ANEXO</p><p>Artículo 1° — texto del anexo</p>")
    arts = segmentar(html_a_texto(html))
    assert [a.zona for a in arts] == ["encabezado", "articulado", "articulado", "anexo"]


def _zip(p: Path, nombre: str, filas: list[dict]):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(filas[0]))
    w.writeheader()
    w.writerows(filas)
    with zipfile.ZipFile(p, "w") as z:
        z.writestr(nombre, buf.getvalue())


def test_script01_sintetico(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    vacio = {k: "" for k in ["clase_norma", "organismo_origen", "numero_boletin", "pagina_boletin",
                             "titulo_resumido", "titulo_sumario", "texto_resumido", "observaciones",
                             "texto_original", "texto_actualizado", "modificada_por", "modifica_a"]}
    base = [dict(id_norma="25552", tipo_norma="Ley", numero_norma="20744", fecha_sancion="1974-09-05",
                 fecha_boletin="1974-09-27", **vacio),
            dict(id_norma="10", tipo_norma="Ley", numero_norma="99999", fecha_sancion="2020-01-01",
                 fecha_boletin="2020-01-02", **vacio),
            dict(id_norma="11", tipo_norma="Resolución", numero_norma="5", fecha_sancion="2020-01-01",
                 fecha_boletin="2020-01-02", **vacio)]
    mod = [{"id_norma_modificatoria": "10", "id_norma_modificada": "25552"},
           {"id_norma_modificatoria": "10", "id_norma_modificada": "25552"},
           {"id_norma_modificatoria": "11", "id_norma_modificada": "25552"}]
    _zip(raw / "base.zip", "base.csv", base)
    _zip(raw / "modificatorias.zip", "m.csv", mod)
    _zip(raw / "modificadas.zip", "m2.csv", mod)
    out = tmp_path / "corpus"
    subprocess.run([sys.executable, str(RAIZ / "scripts/01_obtener_corpus.py"),
                    "--out", str(out), "--raw", str(raw)], check=True, cwd=tmp_path)
    nodos = list(csv.DictReader(open(out / "corpus_normas.csv")))
    gold = list(csv.DictReader(open(out / "gold_relaciones.csv")))
    assert {n["id_norma"] for n in nodos} == {"25552", "10"}   # la resolucion queda afuera
    assert len(gold) == 1 and gold[0]["split"] == "test"        # duplicado eliminado


def test_reglas_v2_procedencia_y_verbos():
    from grafo_legal.extractores.reglas_v2 import _PROCEDENCIA, verbo_real
    assert _PROCEDENCIA.search("Ley N° 20.744 (t.o. por")
    assert _PROCEDENCIA.search("artículo 46 de la Ley N° 24.557 (sustituido por el artículo 2° del")
    assert not _PROCEDENCIA.search("Modifícase el artículo 2° de la")
    assert verbo_real("la Ley 24.013 y sus normas complementarias") == ""
    assert verbo_real("sus decretos reglamentarios. Sustitúyese el artículo 5") == "Sustitúyese"


def test_relaciones_tipo_y_articulo_destino():
    from grafo_legal.extractores.relaciones import articulos_destino, tipo_por_verbo
    assert tipo_por_verbo("Sustitúyese") == "SUSTITUYE"
    assert tipo_por_verbo("Deróganse") == "DEROGA"
    assert tipo_por_verbo("Incorpórase") == "INCORPORA"
    assert tipo_por_verbo("prorrógase") == "MODIFICA"
    assert tipo_por_verbo("") == "CITA"
    assert articulos_destino("Sustitúyese el artículo 245 de la ") == ["245"]
    assert articulos_destino("previstas en los artículos 232, 233 y 245 de la ") == ["232", "233", "245"]
    assert articulos_destino("modalidades previstas en los artículos 43 a 46 de la ") == ["43", "44", "45", "46"]
    assert articulos_destino("Incorpórase el artículo 4° bis del ") == ["4 bis"]
    # el articulo es de otra norma que se nombra en el medio
    assert articulos_destino("el artículo 5 de la Ley 24.013 y la ") == []


def test_grafo_ida_y_vuelta():
    """El grafo en memoria devuelve exactamente las relaciones de la salida estandar."""
    import pandas as pd
    from grafo_legal.grafo import a_networkx, construir, exportar_networkx
    from grafo_legal.salida import CLAVE, validar
    rel_p = RAIZ / "results" / "relaciones" / "relaciones_reglas_v2.csv"
    if not rel_p.exists():
        return
    rel = pd.read_csv(rel_p, keep_default_na=False, dtype={"articulo_destino": str})
    assert validar(rel) == []
    normas = pd.read_csv(RAIZ / "data" / "corpus" / "corpus_normas.csv", dtype=str, keep_default_na=False)
    art = pd.read_csv(RAIZ / "data" / "dataset" / "articulos.csv", keep_default_na=False, dtype={"articulo": str},
                      usecols=["id_norma", "orden", "zona", "articulo", "inicio", "fin", "texto"])
    g = exportar_networkx(a_networkx(construir(normas, art, rel)))
    clave = lambda df: set(map(tuple, df[CLAVE].astype(str).values.tolist()))  # noqa: E731
    assert clave(g) == clave(rel)


# ---------- parser LLM (sin red: respuestas simuladas) ----------

def _cat_chico():
    return Catalogo([Norma(25552, "ley", "20744", 1974, "1974-09-27", "Ley 20744"),
                     Norma(1, "decreto", "70", 2023, "2023-12-21", "Decreto 70"),
                     Norma(2, "decreto", "1694", 2006, "2006-11-23", "Decreto 1694"),
                     Norma(3, "decreto", "1694", 2009, "2009-11-06", "Decreto 1694")])


def test_catalogo_candidatos_cuenta_ambiguedad():
    cat = _cat_chico()
    assert len(cat.candidatos("decreto", "1694")) == 2           # sin ano: dos candidatos
    assert [n.id for n in cat.candidatos("decreto", "1694", 2009)] == [3]
    assert cat.resolver("decreto", "1694") is None               # el parser no adivina


def test_llm_verifica_cita_y_normaliza():
    from grafo_legal.extractores import llm
    seg = llm.Segmento(1, 5, "77", "articulado", 1000,
                       "ARTÍCULO 77.- Sustitúyese el artículo 143 de la Ley N° 20.744 (t.o. 1976), por el siguiente:")
    lote = [(seg, 0, seg.texto)]
    crudas = llm.leer_json('```json\n{"relaciones": ['
                           '{"segmento": "S5", "cita": "Ley N° 20.744", "tipo_norma": "ley", "numero": "20744",'
                           ' "articulo_destino": "143", "tipo": "SUSTITUYE", "verbo": "Sustitúyese"},'
                           '{"segmento": "S5", "cita": "Ley 99.999", "tipo_norma": "ley", "numero": "99999", "tipo": "CITA"},'
                           '{"segmento": "S9", "cita": "x", "tipo": "CITA"}]}\n```')
    filas, conteo = llm.a_relaciones(1, "Decreto 70", lote, crudas, _cat_chico(), {})
    assert conteo["aceptadas"] == 1 and conteo["cita_no_encontrada"] == 1 and conteo["segmento_invalido"] == 1
    f = filas[0]
    assert (f["tipo"], f["id_norma_destino"], f["articulo_destino"]) == ("SUSTITUYE", 25552, "143")
    # offset en el texto de la norma = inicio del segmento + posicion de la cita en el segmento
    assert seg.texto[f["inicio"] - 1000: f["fin"] - 1000] == "Ley N° 20.744"


def test_llm_prefiltro_y_lotes():
    from grafo_legal.extractores import llm
    segs = [llm.Segmento(1, 0, "0", "encabezado", 0, "VISTO la Ley 20.744"),
            llm.Segmento(1, 1, "1", "articulado", 20, "Comuníquese, publíquese."),
            llm.Segmento(1, 2, "-", "notas", 50, "Nota Infoleg: Ley 1")]
    sel = llm.seleccionar(segs)
    assert [s.orden for s in sel] == [0]                         # ni el articulo sin normas ni las notas
    largo = llm.Segmento(1, 3, "2", "articulado", 0, "ley " * 5000)
    pedazos = [p for lt in llm.lotes([largo], max_chars=6000) for p in lt]
    assert sum(len(p[2]) for p in pedazos) == len(largo.texto) and pedazos[1][1] == 6000


def test_modelo_contextual_marca_destino_y_borra_numeros():
    sys.path.insert(0, str(RAIZ / "scripts"))
    import importlib
    m = importlib.import_module("13_modelo_contextual")
    t = m.limpiar_fragmento("Sustitúyese el artículo 80 de la Ley N° 20.744 por", "Ley N° 20.744", "articulado")
    assert t == "PARTE_articulado Sustitúyese el artículo ## de la  DESTINO  por"


def test_anio_escrito_como_fecha():
    sys.path.insert(0, str(RAIZ / "scripts"))
    import importlib
    m = importlib.import_module("12_evaluar_subtareas")
    t = "el Decreto N° 1694 del 22 de noviembre de 2006 y"
    assert m.anio_por_fecha(t, t.index("1694") + 4) == 2006
    t = "el Decreto Nº 1.694 de fecha 5 de noviembre de 2009,"
    assert m.anio_por_fecha(t, t.index("1.694") + 5) == 2009
    assert m.anio_por_fecha("Decreto 1694/06 y", 12) is None
