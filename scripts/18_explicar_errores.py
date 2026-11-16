"""
18_explicar_errores.py
Explica, uno por uno, cada error del parser de reglas v2 (configuracion F): por que fallo.

Lee la clasificacion de errores de 12 (categorias de la consigna) y le agrega a cada falso
negativo y falso positivo:
  causa        un codigo corto del motivo concreto (ver CAUSAS)
  explicacion  una frase que lo explica para ese caso
  evidencia    el fragmento del texto que lo muestra

Como se asigna la causa:
  - Falsos negativos descartados por la regla: automaticamente, a partir de las evidencias del
    par (en que parte del documento estan las menciones y si la oracion tiene verbo). Es la misma
    informacion que uso la regla F para decidir, asi que la causa es exacta.
  - Falsos negativos mal normalizados: el ano del decreto estaba escrito como fecha.
  - Falsos negativos sin mencion explicita: no hay ninguna mencion que mirar, asi que la causa
    sale de leer el texto. Se asignan con reglas (el destino es un decreto de texto ordenado,
    InfoLEG no publica el texto completo, la destinataria modificaba a una ley derogada...) y,
    para el resto, con una revision manual caso por caso (SIN_MENCION_MANUAL), hecha por Claude
    y pendiente de validacion humana.
  - Falsos positivos: automaticamente, segun por que paso la regla F (cita en el VISTO,
    remision desde el articulado de una ley, verbo que no actua sobre el destino, alias), con
    algunos casos corregidos a mano (FP_MANUAL).

Salidas en results/errores_explicados/: errores_explicados.csv y resumen.json.

Uso:
    python scripts/18_explicar_errores.py
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto       # noqa: E402
from grafo_legal.fuentes.infoleg import cargar        # noqa: E402

HTML = Path("data/textos/infoleg/html")

CAUSAS = {
    # --- falsos negativos ---
    "sin_texto": "InfoLEG no publica el texto de la norma modificatoria.",
    "solo_considerando": "La norma destino solo se nombra en el CONSIDERANDO, donde la regla F no acepta menciones "
                         "(en dev, solo el 24 % de esos pares está en InfoLEG).",
    "decreto_articulado_sin_verbo": "Un decreto nombra la norma en el articulado, pero sin verbo modificatorio en la "
                                    "oración: la regla F lo trata como una remisión.",
    "considerando_y_decreto_sin_verbo": "Las menciones están en el CONSIDERANDO y en el articulado de un decreto sin "
                                        "verbo: ninguna pasa la regla F.",
    "solo_alias": "La norma solo aparece por su nombre propio (sin número), y la regla F exige número en el articulado.",
    "solo_procedencia": "La única mención es una cita de procedencia («t.o. por Decreto …»), que la regla descarta a "
                        "propósito.",
    "solo_anexo_o_notas": "La mención está en un anexo o en una nota de InfoLEG, que no son texto dispositivo.",
    "anio_como_fecha": "El decreto se cita con el año escrito como fecha («Decreto 1694 del 22 de noviembre de 2006»). "
                       "El detector no lee ese año y, como el corpus tiene más de un decreto con ese número, la "
                       "mención queda sin resolver.",
    "nombre_no_reconocido": "El texto nombra la norma con un nombre o abreviatura que no está en el gazetteer del "
                            "detector («Ley de Ministerios», «L.C.T.»).",
    "texto_ordenado_implicito": "El texto cita la ley por su texto ordenado («t.o. 1976», «texto ordenado en 2019») y "
                                "InfoLEG registra el vínculo con el decreto que aprobó ese texto ordenado, que el texto "
                                "no nombra.",
    "texto_incompleto_en_infoleg": "InfoLEG no publica el texto completo (norma anterior a 1997 o anexo no publicado): la "
                                   "mención puede estar en la parte que falta.",
    "modificatorias_de_la_citada": "El texto nombra una ley y deroga o modifica también «sus modificatorias»; InfoLEG "
                                   "registra el vínculo con cada una, aunque no se nombren.",
    "derogacion_generica": "El vínculo viene de una derogación genérica («toda otra disposición que se oponga») o del "
                           "reemplazo de un régimen anterior, sin nombrar la norma.",
    "complementa_sin_citar": "La norma regula la misma materia (licencias, empleo, asignaciones…) y InfoLEG la registra "
                             "como complementaria, pero el texto no la nombra.",
    "referencia_conceptual": "El texto nombra otra norma o una figura que pertenece a la destino (el convenio colectivo, "
                             "la personería gremial, el CUIL) y no a la norma misma.",
    "organismo_en_lugar_de_norma": "El texto nombra al organismo que la norma creó (la ANSES) y no a la norma.",
    "posible_error_del_gold": "El texto no tiene ninguna relación visible con la norma destino: probable error de "
                              "InfoLEG.",
    "no_verificable": "El texto no nombra la norma y no se encontró una relación indirecta que explique el vínculo de "
                      "InfoLEG.",
    # --- falsos positivos ---
    "cita_en_el_visto": "La norma aparece en la enumeración de fundamentos del VISTO. La regla F acepta todo el VISTO "
                        "(el 80 % de esos pares está en InfoLEG), y este es del 20 % restante.",
    "remision_desde_ley": "Una ley nombra la norma en su articulado como remisión («en los términos de», «creado por», "
                          "«establecido en»), sin modificarla.",
    "verbo_que_no_actua": "La oración tiene un verbo modificatorio, pero no actúa sobre la norma destino: es nominal "
                          "(«y su modificación», «la reglamentación») o se refiere a otra norma.",
    "procedencia_no_filtrada": "La mención indica de dónde viene un texto («modificado por el Decreto 267», «creado por "
                               "la ley 25.565 y modificado por …»), una forma de procedencia que el filtro no cubre.",
    "alias_de_tributo": "El alias es el nombre de un tributo («Impuesto a las Ganancias», «Valor Agregado») y no una "
                        "cita a la ley.",
    "otro_decreto_mismo_numero": "El texto cita un decreto con el año escrito como fecha; el detector no lee ese año y "
                                 "lo vinculó al único decreto del corpus con ese número, que es de otro año: es otro "
                                 "decreto.",
    "decreto_sin_anio_mundo_cerrado": "Decreto citado sin año: se vinculó al único del corpus con ese número, pero en "
                                      "InfoLEG hay varios y puede no ser el correcto.",
    "alias_ley_sin_vinculo": "La ley se nombra por su nombre («Ley de Impuesto al Valor Agregado») con un verbo en la "
                             "oración (regla F3 de v3), pero el verbo actúa sobre otra cosa e InfoLEG no registra el "
                             "vínculo.",
    "procedencia_mal_filtrada": "Regresión de v3: el filtro de procedencia descarta «texto sustituido por la ley 24.674», "
                                "que en realidad nombra la ley que se está modificando.",
    "alias_de_otra_ley": "El alias es el comienzo del nombre de otra ley («Ley de Convenciones Colectivas de Trabajo de "
                         "la Administración Pública Nacional», que es la 24.185) y se vinculó a la equivocada.",
    "error_en_el_texto_fuente": "El propio texto de la norma tiene un error que confunde al detector.",
    "posible_omision_del_gold": "El texto modifica a la norma (hay un verbo que actúa sobre ella) y InfoLEG no registra "
                                "el vínculo.",
}

# Revision manual de los pares del gold que el texto no nombra (Claude, pendiente de validacion).
SIN_MENCION_MANUAL = {
    ("Ley 23691", "Ley 20744"): ("complementa_sin_citar", "Licencia paga para concurrir a citaciones y trámites: complementa el régimen de licencias de la LCT."),
    ("Ley 23789", "Ley 20744"): ("complementa_sin_citar", "Telegrama gratuito para las comunicaciones del contrato de trabajo."),
    ("Ley 24716", "Ley 20744"): ("complementa_sin_citar", "Licencia por nacimiento de hijo con síndrome de Down, que extiende la de maternidad de la LCT."),
    ("Ley 24658", "Ley 20744"): ("complementa_sin_citar", "Aprueba el Protocolo de San Salvador (derechos laborales); no nombra la LCT."),
    ("Ley 25255", "Ley 20744"): ("complementa_sin_citar", "Aprueba el Convenio 182 de la OIT sobre trabajo infantil."),
    ("Decreto 719", "Ley 20744"): ("complementa_sin_citar", "Crea la Comisión Nacional para la Erradicación del Trabajo Infantil."),
    ("Decreto 254", "Ley 20744"): ("complementa_sin_citar", "Plan de igualdad de oportunidades entre varones y mujeres en el trabajo."),
    ("Decreto 1273", "Ley 20744"): ("complementa_sin_citar", "Asignación no remunerativa para los trabajadores del sector privado."),
    ("Decreto 2641", "Ley 20744"): ("complementa_sin_citar", "Asignación no remunerativa para los trabajadores del sector privado."),
    ("Decreto 392", "Ley 20744"): ("complementa_sin_citar", "Incremento de la remuneración básica de los trabajadores del sector privado."),
    ("Decreto 101", "Ley 20744"): ("complementa_sin_citar", "Delegación de facultades en ministros; el vínculo con la LCT no es visible en el texto."),
    ("Ley 25561", "Ley 20744"): ("complementa_sin_citar", "Suspende los despidos sin causa y duplica la indemnización, sin nombrar la LCT."),
    ("Ley 25963", "Ley 20744"): ("complementa_sin_citar", "Inembargabilidad de prestaciones asistenciales y de empleo."),
    ("Ley 25963", "Ley 24013"): ("complementa_sin_citar", "Inembargabilidad de prestaciones de programas de empleo."),
    ("Ley 25963", "Decreto 484"): ("complementa_sin_citar", "Inembargabilidad: misma materia que el Decreto 484/87 sobre inembargabilidad de salarios."),
    ("Ley 24626", "Ley 24013"): ("complementa_sin_citar", "Seguro de desempleo para deudores hipotecarios."),
    ("Ley 24626", "Ley 24557"): ("complementa_sin_citar", "Seguro de desempleo para deudores hipotecarios; el vínculo con riesgos del trabajo no es visible."),
    ("Decreto 257", "Ley 24013"): ("complementa_sin_citar", "Crea el Consejo Nacional del Trabajo y del Empleo."),
    ("Decreto 558", "Ley 24013"): ("complementa_sin_citar", "Reforma del Estado con programas de empleo."),
    ("Decreto 770", "Ley 24013"): ("complementa_sin_citar", "Nuevo régimen de asignaciones familiares, acordado en el Acuerdo Marco para el Empleo."),
    ("Decreto 772", "Ley 24013"): ("complementa_sin_citar", "Sistema integrado de inspección del trabajo."),
    ("Decreto 852", "Ley 24013"): ("complementa_sin_citar", "Fondo de Reconversión Laboral del sector público."),
    ("Decreto 302", "Ley 24013"): ("complementa_sin_citar", "Convenio con Buenos Aires sobre empleo y capacitación laboral."),
    ("Decreto 405", "Ley 24013"): ("complementa_sin_citar", "Convenio con Catamarca sobre empleo y capacitación laboral."),
    ("Decreto 949", "Ley 24013"): ("complementa_sin_citar", "Convenio con Córdoba sobre empleo y capacitación laboral."),
    ("Decreto 1037", "Ley 24013"): ("complementa_sin_citar", "Convenio con Río Negro sobre empleo y capacitación laboral."),
    ("Decreto 724", "Ley 24013"): ("complementa_sin_citar", "Préstamo del BID para un programa de empleabilidad de jóvenes."),
    ("Decreto 1122", "Ley 24013"): ("complementa_sin_citar", "Simplificación de la inscripción laboral y de la seguridad social."),
    ("Decreto 1122", "Ley 24241"): ("complementa_sin_citar", "Simplificación de la inscripción laboral y de la seguridad social."),
    ("Ley 24699", "Ley 24013"): ("complementa_sin_citar", "Prórroga del Pacto Federal para el Empleo."),
    ("Ley 25212", "Ley 24013"): ("complementa_sin_citar", "Ratifica el Pacto Federal del Trabajo; los programas de empleo están en sus anexos."),
    ("Ley 25212", "Ley 20744"): ("complementa_sin_citar", "Ratifica el Pacto Federal del Trabajo, que no nombra la LCT."),
    ("Ley 25785", "Ley 24013"): ("complementa_sin_citar", "Cupo para personas con discapacidad en los programas de empleo."),
    ("Ley 24642", "Ley 23551"): ("complementa_sin_citar", "Procedimiento de cobro de las cuotas sindicales."),
    ("Decreto 1141", "Ley 23551"): ("complementa_sin_citar", "Opción entre obras sociales sindicales."),
    ("Decreto 847", "Decreto 773"): ("complementa_sin_citar", "Ámbito del régimen de asignaciones familiares (Decreto 770/96); el 773/96 es de la misma serie."),
    ("Decreto 2005", "Decreto 2641"): ("complementa_sin_citar", "Nueva asignación no remunerativa que continúa la del Decreto 2641/02."),
    ("Ley 24700", "Decreto 770"): ("complementa_sin_citar", "Contribución para el financiamiento de las asignaciones familiares del Decreto 770/96."),
    ("Ley 24938", "Ley 24241"): ("complementa_sin_citar", "Presupuesto 1998: créditos previsionales."),
    ("Ley 24938", "Ley 24467"): ("complementa_sin_citar", "Presupuesto 1998: cargos de la Secretaría PyME."),
    ("Ley 24938", "Decreto 2741"): ("organismo_en_lugar_de_norma", "Presupuesto 1998: nombra la ANSES, creada por el Decreto 2741/91."),
    ("Ley 25565", "Decreto 2741"): ("organismo_en_lugar_de_norma", "Presupuesto 2002: nombra la ANSES, creada por el Decreto 2741/91."),
    ("Decreto 796", "Decreto 2741"): ("organismo_en_lugar_de_norma", "Pago directo a cargo de la ANSES, creada por el Decreto 2741/91."),
    ("Ley 24576", "Ley 24013"): ("referencia_conceptual", "Modifica la LCT (formación profesional); InfoLEG lo vincula también con la Ley de Empleo, que regula la formación."),
    ("Ley 24692", "Ley 24013"): ("referencia_conceptual", "Sustituye el art. 140 de la LCT para exigir CUIT y CUIL, que vienen de la Ley de Empleo."),
    ("Ley 23947", "Ley 14250"): ("referencia_conceptual", "Remite al «convenio colectivo de la actividad», regulado por la Ley 14.250."),
    ("Decreto 843", "Ley 14250"): ("referencia_conceptual", "Remite a las prestaciones fijadas «mediante convenio colectivo»."),
    ("Decreto 1183", "Ley 23551"): ("referencia_conceptual", "Habla de «asociaciones sindicales con personería gremial», figura de la Ley 23.551."),
    ("Ley 23551", "Ley 14455"): ("derogacion_generica", "Nuevo régimen de asociaciones sindicales que reemplaza al de la Ley 14.455."),
    ("Ley 23551", "Ley 20615"): ("derogacion_generica", "Nuevo régimen de asociaciones sindicales que reemplaza al de la Ley 20.615."),
    ("Ley 20744", "Ley 18345"): ("derogacion_generica", "La LCT de 1974 deroga «toda otra disposición legal o reglamentaria» que se le oponga."),
    ("Ley 20744", "Ley 12713"): ("derogacion_generica", "La LCT de 1974 deroga «toda otra disposición legal o reglamentaria» que se le oponga."),
    ("Ley 20744", "Ley 18204"): ("derogacion_generica", "La LCT de 1974 deroga «toda otra disposición legal o reglamentaria» que se le oponga."),
    ("Ley 20744", "Decreto/Ley 14538"): ("derogacion_generica", "La LCT de 1974 deroga «toda otra disposición legal o reglamentaria» que se le oponga."),
    ("Ley 20744", "Ley 15984"): ("derogacion_generica", "La LCT de 1974 deroga «toda otra disposición legal o reglamentaria» que se le oponga."),
    ("Ley 23041", "Ley 20744"): ("derogacion_generica", "Fija el cálculo del aguinaldo y deroga «todas las disposiciones que se opongan»."),
    ("Ley 27423", "Ley 24432"): ("modificatorias_de_la_citada", "«Deróganse la ley 21.839 y su modificatoria»: la modificatoria es la Ley 24.432."),
    ("Decreto 12", "Ley 23551"): ("posible_error_del_gold", "Designa un ministro interino de Relaciones Exteriores."),
    ("Decreto 415", "Ley 24557"): ("posible_error_del_gold", "Designa subsecretarios del Ministerio de Economía."),
    ("Decreto 70", "Ley 23789"): ("no_verificable", "El DNU no nombra la ley del telegrama gratuito."),
    ("Decreto 70", "Ley 18345"): ("no_verificable", "El DNU no nombra la ley de procedimiento laboral."),
}

# Falsos positivos corregidos a mano (la causa automatica no alcanza)
FP_MANUAL = {
    ("Decreto 841", "Ley 20628"): ("error_en_el_texto_fuente", "El VISTO dice «Ley de Impuesto a las Ganancias N° 20.744»: el nombre es de otra ley y el alias lo toma."),
    ("Decreto 70", "Decreto 267"): ("otro_decreto_mismo_numero", "«modificado por el Decreto 267 del 29 de diciembre de 2015»: además es una cita de procedencia."),
    ("Ley 27742", "Ley 25565"): ("procedencia_no_filtrada", "«creado por la ley 25.565 y ampliado y modificado por ley 27.637»."),
    ("Decreto 214", "Ley 14250"): ("alias_de_otra_ley", ""),
    ("Decreto 334", "Ley 24241"): ("verbo_que_no_actua", "El decreto reglamenta la Ley 24.557; la 24.241 solo se cita."),
    ("Decreto 491", "Ley 24241"): ("verbo_que_no_actua", "El decreto modifica la reglamentación de la Ley 24.557; la 24.241 solo se cita."),
    ("Decreto 817", "Ley 24241"): ("verbo_que_no_actua", "«reglamenta» se refiere a otra norma; la 24.241 aparece en una remisión."),
    ("Ley 24241", "Ley 20091"): ("verbo_que_no_actua", "«dando cumplimiento … a la ley 20.091»: el verbo de la oración no actúa sobre ella."),
}

_PROCEDENCIA_FP = re.compile(r"(?:modificad|sustituid|reemplazad|incorporad)[oa]s?\s+por\s+(?:el|la)\s+"
                             r"(?:art[ií]culo|decreto|ley)", re.I)

_NOMINAL = re.compile(r"^(modificaci[oó]n|reglamentaci[oó]n|texto ordenado|sustituci[oó]n|derogaci[oó]n|incorporaci[oó]n|"
                      r"modificatori[oa]s?|reglamentari[oa]s?)$", re.I)
_TRIBUTO = re.compile(r"impuesto|valor agregado|ganancias", re.I)


def causa_fn_regla(g: pd.DataFrame) -> str:
    """Por que ninguna mencion del par paso la regla F (g: evidencias del par)."""
    validas = g[g.temporal_ok & ~g.procedencia]
    if validas.empty:
        return "solo_procedencia" if g.procedencia.any() else "solo_anexo_o_notas"
    partes = set(validas.parte)
    if partes <= {"anexo", "notas"}:
        return "solo_anexo_o_notas"
    if (validas.metodo == "alias").all():
        return "solo_alias"
    if partes <= {"considerando", "anexo", "notas"}:
        return "solo_considerando"
    if "considerando" in partes:
        return "considerando_y_decreto_sin_verbo"
    return "decreto_articulado_sin_verbo"


def causa_fp(g: pd.DataFrame, tipo_origen: str) -> tuple[str, pd.DataFrame]:
    """Por que el par paso la regla F (g: evidencias del par que pasan la regla).
    Devuelve la causa y las evidencias que la muestran. Orden: una accion real sobre el destino
    pesa mas que una cita en el VISTO, y esta mas que una remision."""
    if (g.metodo == "alias").all():
        if g.superficie.str.lower().str.startswith("ley").all():
            return "alias_ley_sin_vinculo", g
        return ("alias_de_tributo" if g.superficie.str.contains(_TRIBUTO).all() else "solo_alias"), g
    art = g[(g.zona == "articulado") & (g.metodo == "regex_numero")]
    con_verbo = art[art.verbo_oracion != ""]
    nominal = con_verbo.verbo_oracion.str.match(_NOMINAL)
    proced = con_verbo.fragmento.str.contains(_PROCEDENCIA_FP)
    iva = (con_verbo.verbo_oracion.str.lower().str.startswith("agregad")
           & con_verbo.fragmento.str.contains("alor agregado", case=False))
    real = con_verbo[~nominal & ~proced & ~iva]
    if not real.empty:
        return "posible_omision_del_gold", real
    visto = g[g.parte == "visto"]
    if not visto.empty:
        return "cita_en_el_visto", visto
    if proced.any():
        return "procedencia_no_filtrada", con_verbo[proced]
    if not con_verbo.empty:
        return "verbo_que_no_actua", con_verbo
    if not art.empty and tipo_origen != "decreto":
        return "remision_desde_ley", art
    return "cita_en_el_visto", g


def main(parser: str = "v2") -> None:
    suf = "" if parser == "v2" else f"_{parser}"
    out = Path(f"results/errores_explicados{suf}")
    errores = pd.read_csv(f"results/subtareas{suf}/errores.csv")
    ev = pd.read_csv(f"results/reglas_{parser}/evidencias.csv", keep_default_na=False)
    ev["temporal_ok"] = ev.temporal_ok.astype(str) == "True"
    ev["procedencia"] = ev.procedencia.astype(str) == "True"
    ev["pasa_F"] = ev.temporal_ok & ~ev.procedencia & (
        (ev.parte == "visto") | ((ev.zona == "articulado") & (ev.metodo == "regex_numero")
                                 & ((ev.tipo_origen != "decreto") | (ev.verbo_oracion != ""))))
    if parser == "v3":   # F3: en el articulado, un alias con verbo tambien cuenta
        ev["pasa_F"] |= ev.temporal_ok & ~ev.procedencia & (ev.zona == "articulado") & (ev.metodo == "alias") \
            & (ev.verbo_oracion != "")
    normas = pd.read_csv("data/corpus/corpus_normas.csv", dtype=str, keep_default_na=False)
    titulo = dict(zip(normas.id_norma.astype(int), normas.titulo_resumido))
    sumario = dict(zip(normas.id_norma.astype(int), normas.titulo_sumario))
    tipo = dict(zip(normas.id_norma.astype(int), normas.tipo_norma.str.lower()))
    fallos_det = pd.read_csv(f"results/subtareas{suf}/deteccion_fallos.csv", keep_default_na=False)
    textos: dict[int, str] = {}

    def texto(i):
        if i not in textos:
            d = cargar(i, HTML)
            textos[i] = d[0] if d else ""
        return textos[i]

    filas = []
    for r in errores.itertuples(index=False):
        par = (r.origen, r.destino)
        g = ev[(ev.id_origen == r.id_origen) & (ev.id_destino == r.id_destino)]
        evidencia, nota = "", ""
        if r.error == "FN":
            if r.categoria == "fuera_de_alcance_sin_texto":
                causa = "sin_texto"
            elif r.categoria == "norma_no_detectada":
                causa = "nombre_no_reconocido"
                f = fallos_det[(fallos_det.id_origen == r.id_origen) & (fallos_det.id_destino == r.id_destino)]
                evidencia = f.contexto.iloc[0] if len(f) else ""
            elif r.categoria == "norma_mal_normalizada":
                causa = "anio_como_fecha"
                num = re.sub(r"\D", "", r.destino.split()[-1])
                m = re.search(rf"Decreto[^.;]{{0,15}}?{num[:-3] + r'.?' + num[-3:] if len(num) > 3 else num}"
                              rf"\s+(?:de\s+fecha|del)\s+\d{{1,2}}[^.;]{{0,30}}\d{{4}}", texto(r.id_origen))
                evidencia = re.sub(r"\s+", " ", m.group(0)) if m else ""
            elif r.categoria == "relacion_descartada_por_la_regla":
                causa = causa_fn_regla(g)
                if causa == "solo_procedencia" and g.fragmento.str.contains("texto sustituido por", case=False).any():
                    causa = "procedencia_mal_filtrada"
                x = g.sort_values("inicio").iloc[0]
                evidencia = f"[{x.parte}] {x.fragmento[60:320]}"
            else:   # sin mencion explicita
                t = texto(r.id_origen)
                if "TEXTO ORDENADO" in titulo.get(r.id_destino, ""):
                    causa = "texto_ordenado_implicito"
                    # la cita a la ley por su texto ordenado: se busca la materia del decreto destino
                    # ("IMPUESTOS INTERNOS") cerca de "t.o." o "texto ordenado"
                    tema = {"IMPUESTOS INTERNOS": "impuestos internos", "IMPUESTO AL VALOR AGREGADO": "valor agregado",
                            "IMPUESTO A LAS GANANCIAS": "ganancias"}.get(sumario.get(r.id_destino, ""), "")
                    patron = (rf"[^.]{{0,100}}{tema}[^.]{{0,60}}(?:t\.\s*o\.?|texto ordenado|texto sustituido)[^.]{{0,40}}"
                              if tema else r"[^.]{0,100}(?:20\.744|contrato de trabajo)[^.]{0,20}t\.\s*o\.?\s*1976[^.]{0,20}")
                    m = re.search(patron, t, re.I)
                    evidencia = re.sub(r"\s+", " ", m.group(0)) if m else ""
                elif "11317" in titulo.get(r.id_destino, "") or "11.317" in titulo.get(r.id_destino, ""):
                    causa = "modificatorias_de_la_citada"
                    nota = "La destino modificaba a la Ley 11.317, que la LCT (o la ley origen) deroga o modifica."
                    m = re.search(r"[^.]{0,80}11\.317[^.]{0,80}", t)
                    evidencia = re.sub(r"\s+", " ", m.group(0)) if m else ""
                elif "NO SE ENCUENTRA EN NUESTRA BASE" in t or "se publica sin el anexo" in t.lower():
                    causa = "texto_incompleto_en_infoleg"
                    m = re.search(r"[^.]{0,40}(?:NO SE ENCUENTRA EN NUESTRA BASE|se publica sin el anexo)[^.]{0,60}", t, re.I)
                    evidencia = re.sub(r"\s+", " ", m.group(0)) if m else ""
                elif par in SIN_MENCION_MANUAL:
                    causa, nota = SIN_MENCION_MANUAL[par]
                else:
                    causa = "no_verificable"
                if not evidencia and t:
                    evidencia = re.sub(r"\s+", " ", t[:200])
        else:
            pasa = g[g.pasa_F]
            if par in FP_MANUAL:
                causa, nota = FP_MANUAL[par]
            elif r.categoria == "norma_mal_normalizada":
                causa = "otro_decreto_mismo_numero"
            elif r.categoria == "referencia_ambigua" and not (pasa.metodo == "alias").all():
                causa = "decreto_sin_anio_mundo_cerrado"
            else:
                causa, muestra = causa_fp(pasa, tipo.get(r.id_origen, ""))
                pasa = muestra if len(muestra) else pasa
            x = pasa.sort_values("inicio").iloc[0] if len(pasa) else g.iloc[0]
            evidencia = f"[{x.parte}] {x.fragmento[60:320]}"
        evidencia = "" if str(evidencia) == "nan" else evidencia
        filas.append({"split": r.split, "error": r.error, "origen": r.origen, "destino": r.destino,
                      "categoria_consigna": r.categoria, "causa": causa,
                      "explicacion": CAUSAS[causa] + (f" {nota}" if nota else ""), "evidencia": evidencia})

    df = pd.DataFrame(filas)
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "errores_explicados.csv", index=False, lineterminator="\n")
    resumen = {s: {e: dict(Counter(df[(df.split == s) & (df.error == e)].causa)) for e in ("FN", "FP")}
               for s in ("dev", "test")}
    resumen["causas"] = CAUSAS
    escribir_texto(out / "resumen.json", json.dumps(resumen, indent=2, ensure_ascii=False))
    print(pd.crosstab([df.split, df.error, df.categoria_consigna], df.causa).T.to_string())
    print(json.dumps({k: v for k, v in resumen.items() if k != "causas"}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--parser", choices=["v2", "v3"], default="v2")
    main(ap.parse_args().parser)
