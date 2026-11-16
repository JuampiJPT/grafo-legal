# Análisis de fallos del parser de reglas

Este documento reúne en un solo lugar **por qué falla cada cosa que falla**: las menciones que no se detectan, las que se vinculan mal, las relaciones que la regla descarta, las que propone y no existen, y los tipos mal asignados. Para cada fallo dice qué eslabón falló, por qué y con qué ejemplo real, y si la v3 lo corrigió.

Las fuentes son los resultados de los scripts:

- 12: evaluación por subtareas;
- 16: tipos;
- 18: causa de cada error;
- 19: ablación de la v3.

La lista caso por caso está en:

- `results/errores_explicados/errores_explicados.csv`, para la v2;
- `results/errores_explicados_v3/errores_explicados.csv`, para la v3.

Cómo funciona cada eslabón se explica en `docs/como_se_detecta_una_relacion.md`.

## 1. El embudo: dónde se pierde cada relación del gold

Un par del gold puede perderse en cualquier eslabón. El embudo cuenta cuántos pares sobreviven a cada uno.

| Eslabón | dev v2 | dev v3 | test v2 | test v3 |
|---|---|---|---|---|
| Pares del gold | 583 | 583 | 192 | 192 |
| … con texto en InfoLEG | 548 | 548 | 192 | 192 |
| … con la norma nombrada en el texto | 475 | 475 | 185 | 185 |
| … detectados | 473 | 473 | 185 | 185 |
| … bien normalizados | 464 | **473** | 184 | **185** |
| … aceptados por la regla | 418 | **431** | 168 | **169** |

Las dos primeras pérdidas no son errores del parser:

- **35 pares** no tienen texto en InfoLEG.
- **73 de dev y 7 de test** no se nombran en el texto (sección 3).

Del resto, casi todo se pierde en la **decisión de la regla**. Desde la v3, la normalización ya no pierde nada.

## 2. Detección

**Qué falla.** Dos pares de dev se pierden porque la norma se nombra con un nombre que el gazetteer no tenía:

- «Ley de Ministerios» (Ley 24.013 → Ley 22.520);
- «L.C.T.» (Decreto 328/88 → Ley 20.744).

En la muestra de 60 menciones revisadas a mano hubo además 2 detecciones dudosas: «Impuesto al Valor Agregado» e «impuesto a las ganancias», tomados como alias de su ley cuando el texto habla del tributo.

**Por qué.** Un gazetteer es una lista cerrada: lo que no está, no se encuentra. Y un nombre de tributo no es lo mismo que el nombre de su ley.

**v3.**

- Se agregó «Ley de Ministerios», y el par se recupera.
- «L.C.T.» se agregó con el punto final, que impide el límite de palabra, así que **sigue sin encontrarse**. Hay que escribirlo «l.c.t»; queda para la v4.
- Se sacaron los nombres sueltos de tributos y quedaron las formas con «Ley». Eso hizo perder un par de dev (Ley 25.561 → Ley 20.628), que solo se nombraba como «impuesto a las ganancias».

## 3. Relaciones que el texto no nombra

Son 73 pares en dev y 7 en test, y ningún parser que lea el texto puede encontrarlos. Se revisaron todos.

| Causa | dev | test | Ejemplo |
|---|---|---|---|
| Complementa sin citar | 36 | 0 | La Ley 23.691 da licencia paga para trámites; InfoLEG la registra como complementaria de la LCT, pero no la nombra. |
| Texto ordenado implícito | 4 | 5 | «Ley de Impuesto al Valor Agregado (t.o. en 1997)»: InfoLEG registra el Decreto 280/97, que aprobó ese texto ordenado. |
| Modificatorias de la ley citada | 8 | 0 | La LCT de 1974 deroga la Ley 11.317, e InfoLEG agrega también las normas que la habían modificado. |
| Derogación genérica | 8 | 0 | «toda otra disposición que se oponga». |
| Texto incompleto en InfoLEG | 7 | 0 | «El texto completo original … no se encuentra en nuestra base». |
| Referencia conceptual | 5 | 0 | «el convenio colectivo de la actividad». |
| Organismo en lugar de norma | 3 | 0 | Nombra la ANSES y no el Decreto 2741/91, que la creó. |
| Posible error del gold | 2 | 0 | El Decreto 12/99 designa un ministro interino e InfoLEG lo vincula con la Ley de Asociaciones Sindicales. |
| No verificable | 0 | 2 | El DNU 70/2023 con las leyes 23.789 y 18.345. |

**Qué significa.** Una parte del gold son vínculos de **documentación** que agrega el equipo de InfoLEG, no citas del texto. Al evaluar hay que tenerlo en cuenta: el techo de recall de un parser textual en dev es 475/583 = 81 %.

## 4. Normalización

**Qué fallaba en la v2.** Los decretos se citan muchas veces con el año escrito como fecha: «Decreto N° 467 del 14 de abril de 1988». La v2 solo leía el año en la forma «467/88».

- Si el corpus tenía **varios** decretos con ese número, la mención quedaba ambigua y se perdía. Fueron 9 pares del gold en dev y 1 en test.
- Si tenía **uno solo**, se vinculaba a ese aunque fuera de otro año. De 117 vinculaciones verificables, 31 estaban mal, y produjeron 8 falsos positivos en dev y 1 en test. Ejemplo: «Decreto 267 del 29 de diciembre de 2015», en el DNU 70/2023, terminaba vinculado al Decreto 267 de 2006.

**v3.** El detector lee el año de la fecha, también en listas («658 y 659, ambos del 24 de junio de 1996») y en «13/03/2001». Con eso:

- las menciones ambiguas bajan de 580 a 251;
- las vinculaciones erróneas verificables bajan de 31 a 0;
- **no se pierde ningún par del gold en la normalización**.

Es el cambio que más aporta en la ablación: +1,5 puntos de F1 en dev, él solo.

**Lo que queda.**

- 251 menciones de decretos sin ningún año, ni en número ni en fecha. Son indecidibles sin más contexto.
- 4.190 menciones a normas reales que no están en el corpus. No son errores: el grafo es de mundo cerrado.

## 5. Extracción: la regla descarta relaciones reales

Son los falsos negativos que sí se nombran, se detectan y se normalizan, pero la regla no acepta. En test, v3: 16 de 23.

| Causa | dev v3 | test v3 | Por qué se descarta | Ejemplo |
|---|---|---|---|---|
| CONSIDERANDO y decreto sin verbo | 9 | 8 | La mención en el CONSIDERANDO no cuenta, y en el articulado de un decreto no hay verbo. | Decreto 266/20: «creado mediante el Decreto N° 590/97». |
| Decreto, articulado sin verbo | 10 | 4 | En un decreto, una mención sin verbo se trata como remisión. | «en los términos del apartado 2 … del artículo 6º de la Ley Nº 24.557». |
| Solo en el CONSIDERANDO | 6 | 1 | Solo el 24 % de esos pares está en InfoLEG; aceptarlos baja la precisión más de lo que sube el recall. | «la emergencia sanitaria establecida por la Ley N° 27.541». |
| Solo cita de procedencia | 3 | 1 | «t.o. por Decreto 106/98» dice de dónde viene el texto, pero InfoLEG sí lo vincula. | Ley 18.345 (t.o. por Decreto Nº 106/98). |
| **Procedencia mal filtrada (regresión de v3)** | 0 | **2** | El filtro nuevo toma «texto sustituido por la ley 24.674» como procedencia, y ahí nombra la ley que se modifica. | Leyes 27.742 y 27.802 → Ley 24.674. |
| Solo por nombre, sin verbo | 10 | 0 | La norma solo se nombra por su nombre y la oración no tiene verbo. | — |
| Solo en anexos o notas | 4 | 0 | Los anexos y las notas de InfoLEG no son texto dispositivo. | — |

**Por qué la regla es así.** Cada condición se eligió en dev para el mejor F1. Relajarla, por ejemplo aceptando el CONSIDERANDO, recupera estos pares pero agrega más falsos positivos de los que gana. Los modelos aprendidos (script 13) tampoco separan mejor estos casos: el texto del CONSIDERANDO de un par real y el de una remisión se parecen.

**v3.** El alias con verbo recuperó «Modifícase la Ley de Impuesto a las Ganancias»: 4 pares en dev y 2 en test. El año escrito como fecha recuperó Decreto 342/24 → Decreto 467/88 en test. La regresión de procedencia **no se corrige en la v3**, porque se vio en test; queda para la v4.

## 6. Extracción: relaciones propuestas que InfoLEG no registra

Son los falsos positivos. En test, v3: 48.

| Causa | dev v3 | test v3 | Por qué pasa la regla | Ejemplo |
|---|---|---|---|---|
| Cita en el VISTO | 49 | 25 | La regla acepta todo el VISTO, porque el 80 % de esos pares está en InfoLEG; el 20 % restante son fundamentos que no se modifican. | El Decreto 39/21 enumera «las Leyes 24.241, 24.557, 26.122, 26.773, 27.348 y 27.541» y modifica solo una. |
| Remisión desde una ley | 66 | 14 | Una ley que nombra otra con número en su articulado se acepta aunque no tenga verbo. | «exenta del impuesto a las ganancias establecido en la ley 20.628» (Ley 27.555). |
| Verbo que no actúa | 6 | 3 | Hay verbo en la oración, pero actúa sobre otra norma o es nominal. | «… Ley N° 24.557 y sus modificaciones». |
| Ley nombrada con verbo, sin vínculo (v3) | 6 | 3 | La regla F3: «Ley de Impuesto al Valor Agregado» con un verbo en la oración que no actúa sobre ella. | Decreto 242 → Leyes de IVA y Ganancias. |
| Procedencia no filtrada | 1 | 1 | «creado por la ley 25.565 y ampliado y modificado por ley 27.637»: «creado por» no está en el filtro. | Ley 27.742. |
| Decreto sin año, mundo cerrado | 1 | 1 | Se vinculó a la única candidata del corpus sin poder verificar el año. | — |
| Error en el texto fuente | 0 | 1 | El Decreto 841/22 escribe «Ley de Impuesto a las Ganancias N° 20.744», que es el número de la LCT. | — |
| Posible omisión del gold | 5 | 0 | El texto modifica a la norma e InfoLEG no lo registra. | Ley 24.347, «Modificación de la Ley Nº 24.241». |

**Qué significa.** El 80 % de los falsos positivos de test son las **citas del VISTO** y las **remisiones desde leyes**. Son el costo de las dos condiciones de la regla que más recall aportan. Distinguir, dentro del VISTO, la norma que se modifica de las que solo fundamentan requiere entender la oración. Ese es el caso donde el parser con LLM tiene más para aportar.

## 7. Tipo de relación

Sobre 78 casos revisados a mano, con ponderación por tipo:

| | v2 | v3 |
|---|---|---|
| Macro-F1 | 0,672 | 0,703 |
| Exactitud | 0,754 | 0,755 |

| Fallo | Por qué | v3 |
|---|---|---|
| MODIFICA y REGLAMENTA salen como CITA | El verbo está en otra oración o es un sustantivo («la modificación de …»), y la oración de la mención no tiene verbo. | Sin cambio. |
| INCORPORA en lugar de CITA | «Impuesto al Valor **Agregado**» se leía como verbo. | Corregido. |
| Artículo destino equivocado | Se tomaba el número del propio artículo origen («Artículo 1° — Apruébase la reglamentación de la Ley …»). | Corregido. |
| SUSTITUYE en lugar de MODIFICA | El gold no distingue entre sustituir un artículo y modificarlo. | Sin cambio: es una convención del gold. |

La mejora de la v3 en el tipado es **optimista**: las dos correcciones salieron de esta misma muestra. Para medirla sin sesgo hace falta una muestra nueva.

## 8. Resultado honesto de la v3

| | dev F1 | test P | test R | test F1 |
|---|---|---|---|---|
| Reglas v2 | 0,733 | 0,785 | 0,875 | 0,828 |
| Reglas v3 | 0,750 | 0,779 | 0,880 | 0,826 |

En dev, la v3 mejora 1,7 puntos. En test empata: −0,1 puntos, con intervalo del 95 % entre −1,9 y +1,3.

Las dos versiones difieren en 9 pares:

- **3 ganancias:** el decreto con el año en la fecha y las dos leyes nombradas con verbo.
- **1 falso positivo eliminado:** el decreto homónimo de otro año.
- **3 falsos positivos nuevos:** leyes nombradas con un verbo que no actúa sobre ellas.
- **2 pares perdidos:** la regresión de procedencia.

**Conclusión para el artículo.**

- Los fallos de **detección y normalización están resueltos**: ninguna relación del gold se pierde ahí y ninguna vinculación verificable es errónea.
- Lo que limita al parser es la **decisión de la regla** (VISTO, CONSIDERANDO y remisiones): con superficie y posición no se puede decidir mejor sin entender la oración.
- Otra parte del gold son **vínculos que el texto no contiene**.

## 9. Pendientes para una v4, a diseñar sobre dev

1. Sacar «texto sustituido por la ley N» del filtro de procedencia.
2. Escribir «l.c.t» sin el punto final en el gazetteer.
3. Agregar «creado por» al filtro de procedencia e «inclúyense» a los verbos.
4. Para la regla F3, exigir que el verbo esté **antes** de la mención y en la misma proposición, para evitar «Ley de IVA» con un verbo ajeno.
