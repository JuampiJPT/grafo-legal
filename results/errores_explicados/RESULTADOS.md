# Por qué falla cada error del parser

`scripts/18_explicar_errores.py` le asigna a cada falso negativo y a cada falso positivo del parser de reglas v2 (configuración F) una **causa concreta**, una **explicación** y la **evidencia** del texto que la muestra (bitácora B51). La lista completa, caso por caso, está en `errores_explicados.csv`: 304 errores de dev y 70 de test.

## Cómo se asignó la causa

- **Falsos negativos que descarta la regla:** automáticamente, mirando dónde están las menciones del par y si la oración tiene verbo. Es la misma información que usó la regla para decidir, así que la causa es exacta.
- **Falsos negativos sin mención explícita:** no hay mención que mirar, así que hubo que leer el texto.
  - Una parte se asigna con reglas: el destino es un decreto de texto ordenado, InfoLEG no publica el texto completo, o la norma destino modificaba a una ley que el origen deroga.
  - El resto (57 pares) se revisó a mano. La revisión es de Claude y está pendiente de validación humana.
- **Falsos positivos:** automáticamente, según por qué pasó la regla (cita en el VISTO, remisión desde una ley, verbo que no actúa sobre el destino, alias). Hay 8 casos corregidos a mano.
- **Errores de normalización:** se detectan leyendo la fecha que sigue a la mención. «Decreto N° 84 del 23 de enero de 2014» dice el año aunque no esté escrito «84/14».

## Falsos negativos: relaciones de InfoLEG que el parser no encontró

| Eslabón | Causa | dev | test | Qué pasó |
|---|---|---|---|---|
| Fuera de alcance | Sin texto | 35 | 0 | InfoLEG no publica el texto de la modificatoria. |
| Detección | Nombre no reconocido | 2 | 0 | Se nombra con un nombre que no está en el gazetteer: «Ley de Ministerios» (Ley 24.013 → Ley 22.520) y «L.C.T.» (Decreto 328/88 → LCT). |
| Normalización | Año escrito como fecha | 9 | 1 | «Decreto N° 467 del 14 de abril de 1988»: el detector no lee el año de la fecha y en el corpus hay tres decretos 467, así que la mención queda sin resolver. |
| Extracción | CONSIDERANDO y decreto sin verbo | 10 | 6 | Ejemplo: el Decreto 266/20 nombra el Decreto 590/97 en el CONSIDERANDO y en el articulado («creado mediante el Decreto N° 590/97»), sin verbo. |
| Extracción | Decreto, articulado sin verbo | 10 | 4 | «en los términos del apartado 2 … del artículo 6º de la Ley Nº 24.557» (Decreto 875/20). La regla F lo trata como remisión. |
| Extracción | Solo en el CONSIDERANDO | 6 | 3 | «la emergencia pública en materia sanitaria establecida por la Ley N° 27.541» (Decreto 367/20). |
| Extracción | Solo por nombre propio | 14 | 2 | La Ley 27.802 modifica «la Ley de Impuesto a las Ganancias, texto ordenado en 2019» sin dar el número, y la regla exige número en el articulado. |
| Extracción | Solo cita de procedencia | 2 | 1 | «Ley 18.345 (t.o. por Decreto Nº 106/98)»: la regla descarta a propósito estas citas, e InfoLEG sí vincula el decreto del texto ordenado. |
| Extracción | Solo en anexos o notas | 4 | 0 | Las menciones están en un anexo o en una nota de InfoLEG. |
| Sin mención | Texto ordenado implícito | 4 | 5 | La Ley 27.802 cita la «Ley de Impuesto al Valor Agregado (t.o. en 1997)», e InfoLEG registra el vínculo con el Decreto 280/97, que aprobó ese texto ordenado y el texto no nombra. |
| Sin mención | Complementa sin citar | 36 | 0 | Regula la misma materia sin nombrar la norma. Ejemplo: la Ley 23.691 da licencia paga para trámites, e InfoLEG la registra como complementaria de la LCT. |
| Sin mención | Modificatorias de la ley citada | 8 | 0 | La LCT de 1974 deroga la Ley 11.317, e InfoLEG registra el vínculo también con las normas que habían modificado a esa ley. |
| Sin mención | Derogación genérica | 8 | 0 | «toda otra disposición legal o reglamentaria que se oponga» (LCT de 1974). |
| Sin mención | Texto incompleto en InfoLEG | 7 | 0 | «El texto completo original … no se encuentra en nuestra base», o el decreto «se publica sin el anexo I». |
| Sin mención | Referencia conceptual | 5 | 0 | «el convenio colectivo de la actividad» (Ley 14.250), «asociaciones sindicales con personería gremial» (Ley 23.551). |
| Sin mención | Organismo en lugar de norma | 3 | 0 | Nombra la ANSES y no el Decreto 2741/91 que la creó. |
| Sin mención | Posible error del gold | 2 | 0 | El Decreto 12/99 designa un ministro interino de Relaciones Exteriores e InfoLEG lo vincula con la Ley de Asociaciones Sindicales; el Decreto 415/01 designa subsecretarios de Economía y aparece vinculado a la Ley de Riesgos del Trabajo. |
| Sin mención | No verificable | 0 | 2 | El DNU 70/2023 no nombra la Ley 23.789 (telegrama gratuito) ni la 18.345 (procedimiento laboral), y no se encontró un vínculo indirecto. |

## Falsos positivos: pares que el parser propuso y InfoLEG no registra

| Eslabón | Causa | dev | test | Qué pasó |
|---|---|---|---|---|
| Extracción | Cita en el VISTO | 48 | 24 | La norma está en la lista de fundamentos del VISTO. Ejemplo: el Decreto 39/21 enumera «las Leyes Nros. 24.241, 24.557, 26.122, 26.773, 27.348 y 27.541», y solo modifica a una. La regla acepta todo el VISTO porque el 80 % de esos pares está en InfoLEG. |
| Extracción | Remisión desde una ley | 66 | 14 | «quedará exenta del pago del impuesto a las ganancias establecido en la ley 20.628» (Ley 27.555). Una ley nombra la norma en su articulado sin modificarla. |
| Extracción | Verbo que no actúa | 6 | 3 | Hay un verbo en la oración, pero es nominal o actúa sobre otra norma: «… Ley N° 24.557 y sus modificaciones», «Reglamentación» de otra ley. |
| Extracción | Procedencia no filtrada | 4 | 1 | «creado por la ley 25.565 y ampliado y modificado por ley 27.637» (Ley 27.742). El filtro de procedencia solo cubre «t.o.» y «sustituido por el artículo N del». |
| Normalización | Otro decreto con el mismo número | 8 | 1 | «Decreto 267 del 29 de diciembre de 2015» (DNU 70/2023), vinculado al único Decreto 267 del corpus, que es de 2006: es otro decreto. |
| Normalización | Decreto sin año, mundo cerrado | 1 | 2 | Decreto citado sin año, que en InfoLEG tiene varias candidatas. |
| Detección | Alias de otra ley | 1 | 0 | «Ley de Convenciones Colectivas de Trabajo de la Administración Pública Nacional Nº 24.185» empieza igual que el nombre de la Ley 14.250. |
| Detección | Error en el texto fuente | 0 | 1 | El Decreto 841/22 dice «Ley de Impuesto a las Ganancias N° 20.744», que es el número de la LCT. |
| Gold | Posible omisión del gold | 5 | 0 | El texto modifica a la norma e InfoLEG no lo registra. Ejemplo: la Ley 24.347, «Modificación de la Ley Nº 24.241», incorpora un texto a esa ley. |

## Detección: los 2 errores de la muestra de 60

Las dos menciones dudosas son nombres de tributos que el gazetteer toma como alias de su ley: «Impuesto al Valor Agregado» y «impuesto a las ganancias». En «Exención del Impuesto a las Ganancias» el texto habla del tributo, no cita la ley. El mismo problema aparece en los falsos negativos («solo por nombre propio») y en el tipado (B47), donde «Agregado» se lee como verbo.

## Normalización: por qué no se resuelve una mención

| Estado | Menciones | Por qué |
|---|---|---|
| Fuera del corpus | 3.868 | Son normas reales de InfoLEG que no están entre las 340 del corpus (mundo cerrado). No es un error. |
| Ambigua | 580 | Decreto citado sin «/año», con varias candidatas en InfoLEG. **En 360 el año está escrito como fecha** («del 20 de noviembre de 1974»); leyéndolo, se resolverían. |
| Resuelta solo por mundo cerrado | 147 | El corpus tiene un solo decreto con ese número y se vincula a ese. En 117 el año de la fecha permite verificarlo: **86 bien y 31 mal** (otro decreto con el mismo número). Los otros 30 no se pueden verificar. |
| No encontrada | 37 | No está en ningún catálogo. Casi todos son decretos de 1930 a 1980 que InfoLEG no tiene catalogados (por ejemplo el Decreto 20.268/46), y algunos tienen el año cambiado. |

Con la verificación por fecha, la **exactitud de vinculación estimada es 99,1 %**: de las 3.547 vinculaciones que se pueden verificar, 31 son erróneas. Antes se reportaba 95,9 %, contando como dudosas todas las de mundo cerrado.

## Qué cambia respecto de B45

Explicar cada error caso por caso corrigió la clasificación de B45:

- **La detección pierde 2 pares en dev.** Son nombres que el gazetteer no tiene. El recall de detección pasa de 1,000 a 0,996 en dev; en test sigue en 1,000.
- **La normalización pierde 9 pares en dev y 1 en test** por no leer el año escrito como fecha. Antes contaban como descartados por la regla.
- **9 falsos positivos son vinculaciones erróneas**, no relaciones inexistentes: el decreto citado es otro con el mismo número.

El parser congelado no cambia. Leer el año de la fecha es la mejora con más efecto sobre la normalización: resuelve 360 menciones ambiguas y corrige 31 vinculaciones. Queda como v3, para diseñar sobre dev y medir aparte.
