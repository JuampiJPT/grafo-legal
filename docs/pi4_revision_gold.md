# PI4 · Revisión del gold del digesto (revisión 2)

**Qué es.** La segunda pasada sobre la anotación de los 70 documentos de la PI4, hecha por Claude el 20/11 (B58). Se releyeron los 108 pares en su contexto (las oraciones donde aparece cada norma, no solo la nota), con una pregunta: *¿la clase sale de las definiciones escritas antes de correr los métodos, aplicadas igual en todos los documentos?*

**Resultado.** Se cambiaron 16 pares y se agregó 1. Todos están marcados en `data/corpus_unnoba/gold_pi4.tsv` con `[revision 2: …]`.

## Las definiciones (no cambiaron)

- **MOD:** el documento actúa sobre la norma: la modifica, sustituye, deroga, deja sin efecto, ratifica, prorroga, reglamenta o extiende.
- **APLICA:** el articulado aplica la norma o se dicta en su marco.
- **CITA:** antecedente, competencia, remisión o mención incidental.

**Regla de trabajo:** la clase sale del texto del documento, no de lo que uno sabe de la UNNOBA.

## La decisión principal: las remisiones de las resoluciones de inscripción

**El caso.** Siete resoluciones que aprueban el curso de ingreso de cada año (docs 33, 34, 35, 36, 38, 39 y 40) tienen dos menciones que se repiten:

1. En un artículo del dispositivo dicen: *«Establecer que los aspirantes con título secundario extranjero y no incluidos en la Resolución Ministerial N° 1523/90 quedan comprendidos en los términos de la presente Resolución, y que deberán presentar en la Universidad el título secundario…»*.
2. En el modelo de constancia que aprueban dicen: *«Se deja constancia que el/la aspirante… fue inscripto/a en el marco del art. 7° de la Ley de Migraciones N° 25.871 y deberá cumplimentar…»*.

En la revisión 1 las dos se anotaron como **CITA** («remisión»). Esa sola decisión explicaba 14 de los 18 falsos positivos de las reglas y los 14 del híbrido.

**Argumentos para CITA:**
- la resolución no modifica ninguna de las dos normas;
- la Ley de Migraciones aparece dentro de un formulario, no en una orden;
- en InfoLEG, una norma nombrada al pasar o como remisión no se cuenta como vínculo.

**Argumentos para APLICA, que son los que deciden:**

1. **Coherencia con el resto del gold.** En los docs 25 y 26 se anotó como APLICA la misma construcción: *«aquellos alumnos incluidos en las situaciones contempladas por la Resolución Nro. 1122/08, ratificada por Resolución (CS) 97/2008 y Resolución (CS) 106/2008»*. Ahí, la norma citada sirve para decir **a quién alcanza** lo que se dispone. La Res. Ministerial 1523/90 cumple exactamente esa función: separa a los aspirantes extranjeros que siguen el régimen ministerial de los que quedan alcanzados por esta resolución. Anotar una como APLICA y la otra como CITA es incoherente.
2. **Está en el dispositivo, no en los fundamentos.** Es un artículo que ordena algo («Establecer que…»), no un «Que…» del considerando.
3. **La constancia ejecuta la ley.** Inscribir a un aspirante sin la situación migratoria regularizada «en el marco del art. 7° de la Ley 25.871» es aplicar ese artículo, que garantiza el acceso a la educación sin importar esa situación. El modelo de constancia lo aprueba el articulado.
4. **Coincide con el criterio de InfoLEG** que el TP usa como referencia: hay vínculo cuando la norma origen «se apoya en el régimen de esa norma para regular algo (…) lo usa para definir a quiénes alcanza». Es el mismo criterio que el prompt del híbrido le da al LLM.

**Decisión: APLICA** para los 14 pares. Con eso el vínculo pasa de 45 a 59 pares.

## Los otros cambios

| Doc | Norma | Antes | Ahora | Motivo |
|---|---|---|---|---|
| 12 | Res. (CD.ET) 278/2016 | CITA | APLICA | El art. 2 ordena presentar el programa «en el formato aprobado por esta instancia según resolución 278/2016»: el dispositivo exige cumplir esa norma. |
| 10 | Res. (D.ET) 313/2016 | CITA | MOD | El considerando dice que la Directora la dictó ad referéndum del Consejo. El Consejo «aprobó lo actuado» y otorga lo mismo: es una ratificación implícita, como las de los docs 9, 24, 28, 30 y 41, que dicen «Ratificar». |
| 15 | Estatuto | — | CITA | Se había salteado: «por aplicación de los preceptos del Artículo 70, inciso 32 del Estatuto» (competencia). |

## Lo que se revisó y se mantuvo

- **Res. (CS) 368/2010 en los docs 57 a 66: CITA.** Solo aparece como origen de los formularios agregados al expediente («a Fs. 1 se adjunta anexo I de la resolución (CS) 368/2010 Formulario A»). El articulado designa un jurado y no la nombra. Es probable que sea el reglamento de las PPS, pero el texto no lo dice, y la regla es anotar desde el texto.
- **Estatuto como competencia: CITA en todos los casos**, también cuando aparece en el articulado («Ratificar… conforme lo preceptuado en el Artículo 76 inciso 32 del Estatuto»). Dar la facultad de dictar la medida no es aplicarla; en InfoLEG tampoco cuenta.
- **Plan Estratégico (Res. 657/2013, doc 2), bibliografía (Ley 13.016, doc 12) y sello «copia fiel» (Res. 1/2001, doc 17): CITA.** Son menciones incidentales, aunque estén en el articulado.
- **Res. 556/98 (doc 21): CITA.** Se nombra en el VISTO solo para describir el marco del Decreto 499/95.
- **Ordenanza 12/2009 (doc 17): MOD.** La Ordenanza 40/2014 se presenta como «proyecto de modificación de la citada Ordenanza» y deroga «toda disposición en contrario». Aunque el articulado no la nombre, la reemplaza.
- **Ordenanza 14/2009 (doc 15): MOD.** Se ratifica la resolución que la modificó, y el efecto sobre la ordenanza es real.
- **Planes de estudio del doc 0: APLICA.** Las tablas de equivalencias que se aprueban son entre esos planes y se dictan en su marco.
- **Res. 531/2012 en los docs 7 y 47 a 51: APLICA.** Se otorga un beneficio previsto en ella. **Res. 633/2013 (doc 50): MOD.** Se revisa el beneficio que había otorgado.

## Cómo pesa en los números

Los 16 cambios pasan pares de CITA a vínculo, y los métodos ya los predecían. Por eso todos los F1 suben:

| Método | Revisión 1 | Revisión 2 |
|---|---|---|
| Reglas | 0,788 | 0,917 |
| Híbrido | 0,854 | 0,958 |
| LLM vocab | 0,706 | 0,864 |

La revisión se hizo después de ver los resultados, y eso tiene un riesgo. Para acotarlo:

- se aplicaron las definiciones previas, sin agregar ninguna;
- cada cambio queda escrito con su texto y su motivo;
- se informan las dos versiones (`metricas.json`, `sensibilidad_gold_revision_1`).

El orden de los métodos es el mismo con las dos. Lo que cambia es la significancia: con la revisión 2, el híbrido le gana a las reglas por +0,041, con un IC 95 % de −0,002 a +0,101, que toca el cero.

**Pendiente:** que un segundo anotador del equipo repita una parte, para el kappa.
