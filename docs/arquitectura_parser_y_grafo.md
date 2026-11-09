# Parser y grafo normativo: arquitectura y construcción paso a paso

TP Integrador de Sistemas Inteligentes (UNNOBA), Problemática III. Estado al 09/11/2026.

Este documento cuenta cómo se construyó el sistema, en el orden en que se hizo. Cada etapa dice qué se hizo, qué se encontró y por qué se pasó a la siguiente. Al final hay un ejemplo que recorre todo el sistema con un artículo real, el mapa de archivos y lo que falta. Las decisiones están numeradas como en la bitácora (B) y en `docs/decisiones.md` (D).

## 0. El objetivo

Se busca un parser que lea cualquier documento normativo argentino (una ley, un decreto, una resolución universitaria) y extraiga qué hace sobre otras normas: qué artículos sustituye, cuáles incorpora, qué deroga, qué reglamenta o a qué remite. Con eso se arma un grafo que se puede consultar en lenguaje natural, y cada respuesta se puede justificar con el texto que la sustenta.

InfoLEG cumple dos papeles. Es la primera fuente de documentos y, además, publica qué normas modifican a cuáles, así que sirve de referencia para medir el parser. Esa referencia es amplia («modifica o complementa») y no dice el tipo de relación (B02, B27).

La arquitectura final tiene cinco piezas:

```
documento normativo (HTML, PDF o texto, de cualquier fuente)
   │
   1. Adaptador de la fuente     → texto plano            ← lo único que cambia por fuente
   2. Segmentación               → encabezado (VISTO, CONSIDERANDO), artículos, anexos
   3. Detección de menciones     → «Ley 20.744», «Decreto 1694/09», «artículo 245»
   4. Tipado de la relación      → sustituye, incorpora, deroga, reglamenta, modifica, cita
   │
   5. Salida estándar            → una tabla de relaciones, igual para cualquier parser
   │
   Grafo en Neo4j  ←── evaluación: se lee de vuelta y se compara con InfoLEG
```

## Etapa 1. El corpus: qué normas y con qué referencia

**Qué se hizo.** InfoLEG publica tres bases en su portal de datos: normativa nacional (430.834 normas), normas modificatorias y normas modificadas. Se eligió el dominio laboral y se armó el corpus expandiendo desde cinco semillas: la Ley de Contrato de Trabajo (20.744), la Ley 27.802 de Modernización Laboral, la Ley de Empleo (24.013), la de Riesgos del Trabajo (24.557) y la de Asociaciones Sindicales (23.551). Para cada semilla se tomaron las leyes, decretos y decretos-leyes que la modifican o que ella modifica (un salto). Las Leyes 14.250 y 27.742 entraron como nodos, pero no se expandieron: la 14.250 tiene más de 42.000 «modificatorias», casi todas resoluciones que homologan convenios (B30, D9).

**Resultado.** 340 normas, de las cuales 306 tienen texto en InfoLEG, y 775 relaciones de referencia entre ellas.

**Decisiones:**

- **Snapshot congelado (D1, D11).** El portal publica una versión nueva cada mes y no guarda las anteriores. El corpus se congeló en la descarga del 06/11/2026, con los hashes de los archivos. `correr_pipeline.sh` lo regenera desde los zips guardados y comprueba que dé byte a byte lo mismo.
- **Un solo corpus (D11, B33).** Hubo un corpus más chico (v1, 183 normas) sobre el que se diseñaron las primeras reglas. Se unificó en este, que lo contiene, y sus pares se marcan para medir aparte lo que el parser nunca vio.
- **Split temporal.** Dev son las relaciones cuya norma modificatoria es de hasta 2019 (583 pares); test, las de 2020 en adelante (192). Las reglas se diseñan solo mirando dev, y test se evalúa una vez por versión congelada (B16).

Archivos: `scripts/01_obtener_corpus.py`, `data/corpus/` (`SNAPSHOT.md`, `corpus_normas.csv`, `gold_relaciones.csv`).

## Etapa 2. Los textos y el adaptador de la fuente

**Qué se hizo.** `scripts/02_descargar_textos.py` baja el HTML de cada norma (texto actualizado o, si no hay, el original) y guarda un manifiesto con URL, fecha y SHA-256. El adaptador `src/grafo_legal/fuentes/infoleg.py` convierte el HTML en texto plano: quita scripts y estilos, conserva los cortes de párrafo y normaliza los espacios.

Esta es **la única pieza propia de InfoLEG**. Para el digesto de la UNNOBA o para un PDF hace falta otro adaptador que entregue el mismo texto plano; todo lo que sigue es igual.

**Dificultades.** Después de 138 descargas seguidas, InfoLEG empezó a responder 404, y algunos archivos quedaron sin permiso de escritura. Se resolvió con escritura atómica (temporal y renombre) y armando el manifiesto desde los archivos que ya estaban en disco (D10).

## Etapa 3. Segmentación: encabezado, artículos, anexos

**Qué se hizo.** El texto se corta en segmentos por zona:

| Zona | Qué es | Segmentos en el corpus |
|---|---|---|
| encabezado | desde el principio hasta el primer artículo: VISTO y CONSIDERANDO | 303 |
| articulado | un segmento por artículo («ARTÍCULO 1°.-», «Art. 2 bis —») | 7.667 |
| anexo | desde el primer «ANEXO» después del articulado | 42 |
| notas | notas editoriales de InfoLEG («Nota Infoleg:…») | 54 |

Cada segmento guarda sus posiciones (`inicio`, `fin`) en el texto limpio. Así cualquier relación se puede rastrear hasta el fragmento exacto del que salió. Los segmentos están en `data/dataset/articulos.csv`, que también es la entrada para el parser LLM.

**Por qué importa.** La zona resultó ser la señal más fuerte del parser (etapas 5 y 6). En la etapa 6 el encabezado se divide además en VISTO y CONSIDERANDO.

## Etapa 4. Detección y normalización de menciones

**Qué se hizo.** `src/grafo_legal/extractores/menciones.py` busca con expresiones regulares las formas en que un texto nombra una norma:

| Forma | Ejemplo | Resultado |
|---|---|---|
| tipo y número | «Ley N° 20.744 (t.o. 1976)» | ley 20744 |
| listas | «Leyes Nros. 24.013, 24.465 y 24.467» | tres menciones |
| nombre intercalado | «Ley de Contrato de Trabajo Nº 20.744» | ley 20744 |
| decreto con año | «Decreto N° 1694/06» | decreto 1694 de 2006 |
| decreto-ley | «Decreto-Ley N° 1740/45» | se busca en la serie de leyes |
| DNU | «Decreto de Necesidad y Urgencia N° 70/23» | decreto 70 de 2023 |
| errores de OCR | «Ley NQ 12.713», «ley núm. 11.729» | ley 12713, ley 11729 |
| solo el nombre (alias) | «la Ley de Contrato de Trabajo» | ley 20744 |

Cada mención se resuelve contra un catálogo cerrado: las normas del corpus (`src/grafo_legal/catalogo.py`, D4). Los números de decreto se repiten cada año, así que si la mención da el año tiene que coincidir; si no lo da, se acepta solo cuando hay un único candidato (D5).

**Resultado.** 4.430 menciones resueltas en las 306 normas con texto: 3.577 por número y 853 por nombre. Cada una se guarda como evidencia, con su artículo, zona, posición, fragmento y verbo (`results/reglas_v2/evidencias.csv`).

**Verificación.** En una revisión manual de 30 pares de la referencia, el detector clasificó bien los 30 (B26). El 81 % de las relaciones de dev y el 96 % de las de test aparecen como mención en el texto; el resto no se puede recuperar leyendo (B26, B34).

## Etapa 5. Reglas v1: ¿cuándo una mención es una relación?

**Qué se hizo.** No toda mención es una modificación: muchas son citas de paso. Sobre el corpus v1 se probaron cinco filtros de evidencia y se evaluaron a nivel de par de normas contra InfoLEG:

| Config | Regla | F1 dev |
|---|---|---|
| A | cualquier mención | 0,682 |
| B | solo menciones en el articulado | 0,647 |
| **C** | articulado y la norma destino no es posterior a la origen | **0,652** |
| D | C y un verbo modificatorio en el artículo | 0,574 |
| E | C y un verbo en la oración | 0,495 |

Se eligió C. Pedir un verbo bajaba mucho el recall, porque InfoLEG registra también remisiones y reglamentaciones (D6).

**Hallazgo (B35).** Al aplicar las reglas congeladas al corpus único, el F1 sobre los pares que no se usaron para diseñarlas cayó a 0,514 en dev y a 0,563 en test. Tres causas:

- **Citas de procedencia.** En «Ley 20.744 (t.o. por Decreto 390/76)», el Decreto 390/76 contaba como otra mención.
- **Citas de paso.** Ganancias e IVA se nombraban sin ser modificadas.
- **Vínculos reales fuera del articulado.** 72 de los 73 pares nuevos que filtraba la regla de zona tenían la mención solo en el VISTO, el CONSIDERANDO o un anexo.

## Etapa 6. Reglas v2: el VISTO cuenta, la procedencia no

**Qué se hizo (B36, D13).** Con los errores de dev y una revisión de 30 falsos positivos se ajustaron tres cosas:

1. **VISTO y CONSIDERANDO por separado.** Los pares citados en el VISTO están en InfoLEG el 80 % de las veces; los citados solo en el CONSIDERANDO, el 24 %.
2. **Citas de procedencia.** Se descarta la mención que sigue a «t.o. por» o a «sustituido por el artículo N del».
3. **Verbos.** «Complementarias» y «reglamentarios» dejan de contar como verbo.

La regla final (F) acepta un par si tiene una mención válida que esté en el VISTO, o en el articulado con número cuando la norma origen es una ley o la oración tiene verbo. Un decreto que solo nombra una norma, sin verbo, casi siempre remite a ella.

**Resultado.** F1 0,733 en dev y 0,828 en test, contra 0,652 y 0,788 de v1. En los pares de test que no son del v1, 0,671 contra 0,563. v1 queda congelado y reproducible.

**Punto de comparación (B37, D14).** Un clasificador de scikit-learn (random forest, validación cruzada agrupada por norma en dev) sobre los mismos candidatos da F1 0,823 en test. Las reglas a mano y el modelo entrenado empatan: con atributos de superficie no hay mucho más que ganar. Lo que queda son remisiones que solo se distinguen de una modificación entendiendo la oración.

Archivos: `src/grafo_legal/extractores/reglas.py` (v1), `reglas_v2.py`, `scripts/03_extraer_reglas.py`, `04_evaluar.py`, `08_clasificador.py`.

## Etapa 7. De «hay un vínculo» a «qué hace»: la salida estándar

**El problema.** Hasta acá el parser decía si dos normas estaban vinculadas, igual que InfoLEG, pero no qué hacía una sobre la otra ni sobre qué artículo. El primer grafo (B38) reflejaba eso: una arista por parser que solo decía «vínculo». No respondía las preguntas para las que se arma el grafo, y además dependía de qué parser la había producido.

**Qué se hizo (B41, D16).** Se definió una salida estándar, una tabla que todos los parsers escriben igual (`src/grafo_legal/salida.py`, `docs/salida_estandar.md`). Una fila dice qué hace un artículo de la norma origen sobre una norma o un artículo destino:

| Tipo | Cuándo | Ejemplo |
|---|---|---|
| SUSTITUYE | reemplaza un texto | «Sustitúyese el artículo 245 de la Ley 20.744 por el siguiente…» |
| INCORPORA | agrega un texto | «Incorpórase como artículo 53 bis a la Ley 23.551…» |
| DEROGA | deja sin efecto | «Derógase la Ley 25.323» |
| REGLAMENTA | reglamenta | «Reglaméntase el artículo 179 de la Ley 20.744» |
| MODIFICA | otros cambios: modifica, prorroga, suspende, exime | «Modifícase el artículo 7° de la Ley 23.546» |
| CITA | la nombra sin cambiarla | «…previstas en el artículo 80 de la Ley 24.013» |

Cada fila lleva la evidencia (fragmento y posición), la fuente (`reglas_v2`, `llm`…) y, si el parser la da, una confianza.

**Cómo la produce el parser de reglas (`scripts/09_relaciones.py`, `extractores/relaciones.py`):**

1. **Filtro.** Toma las menciones de la etapa 6 y descarta las de procedencia, las que apuntan a normas posteriores y las de las notas editoriales de InfoLEG, que no son texto de la norma.
2. **Tipo.** Sale del verbo de la oración en que está la mención («Sustitúyese» da SUSTITUYE, «Derógase» da DEROGA). Sin verbo, o en el VISTO o el CONSIDERANDO, es CITA.
3. **Artículo destino.** Es el «artículo N de la» que precede a la mención en la misma oración. «Artículos 232, 233 y 245» da tres relaciones, y un rango corto («43 a 46») se expande. Si no hay, la relación es con la norma entera.
4. **Agrupación.** Las menciones que coinciden en origen, tipo, destino y artículo destino se agrupan en una relación, con la cantidad de menciones.

**Resultado.** 3.277 relaciones entre 1.037 pares de normas: 2.332 citas, 375 sustituciones, 181 incorporaciones, 176 modificaciones, 155 derogaciones y 58 reglamentaciones. El 71 % de las que no son citas tiene artículo destino.

## Etapa 8. La arquitectura del grafo

**Qué se hizo (B42, D17).** El grafo se arma solo a partir de la salida estándar (`src/grafo_legal/grafo.py`, `scripts/10_armar_grafo.py`). No lee InfoLEG.

```
(:Norma)-[:CONTIENE]->(:Articulo)
(:Articulo)-[:SUSTITUYE | INCORPORA | DEROGA | REGLAMENTA | MODIFICA | CITA]->(:Articulo)
(:Articulo)-[...el mismo tipo...]->(:Norma)
```

**Nodos.**

| Nodo | Cantidad | Qué representa | Propiedades |
|---|---|---|---|
| `Norma` | 340 | una ley, decreto o decreto-ley | `id_norma`, `nombre` («Ley 20744»), `tipo`, `numero`, `fecha`, `anio`, `titulo`, `sumario`, `organismo`, `split`, `tiene_texto` |
| `Articulo` | 8.129 | un segmento de una norma: el encabezado (artículo 0), un artículo o un anexo | `id` («id_norma#orden»), `id_norma`, `numero`, `zona`, `inicio`, `fin`, `texto`, `tiene_texto` |

63 de los artículos no tienen texto. Son artículos destino que el texto nombra, pero que no están en el corpus segmentado (por ejemplo, de una norma sin texto en InfoLEG). Se crean igual, para que la relación tenga a dónde llegar.

**Aristas.**

| Arista | De → a | Cantidad | Propiedades |
|---|---|---|---|
| `CONTIENE` | Norma → Articulo | 8.129 | |
| `SUSTITUYE`, `INCORPORA`, `DEROGA`, `REGLAMENTA`, `MODIFICA`, `CITA` | Articulo → Articulo, o Articulo → Norma | 3.277 (1.684 a un artículo, 1.593 a una norma) | `fuente`, `parte_origen`, `verbo`, `metodo`, `confianza`, `n_menciones`, `inicio`, `fin`, `fragmento` |

**Decisiones de diseño:**

- **El tipo de relación es el tipo de arista.** Así una pregunta se traduce directo a Cypher: «¿qué derogó la Ley 27.802?» es `[:DEROGA]`. Esto pesa para el text-to-Cypher.
- **El origen es siempre un artículo.** Así se sabe qué artículo de la norma hace el cambio. El VISTO y el CONSIDERANDO salen del encabezado (artículo 0).
- **El destino es el más preciso que da el texto:** un artículo si lo nombra, la norma si no.
- **La evidencia va en la arista.** Toda respuesta se justifica con el fragmento de la norma.
- **`fuente` distingue parsers.** Si se cargan el LLM y el híbrido, cada uno tiene sus aristas, y una consulta elige cuál usar. El esquema no cambia.
- **InfoLEG queda afuera.** No es parte de lo que el sistema sabe: es la vara con que se lo mide.

**Infraestructura.** Neo4j 5 corre en un contenedor Docker propio del TP (`neo4j-grafo-legal`, puertos 7475 y 7688), para no pisar otra base de la misma máquina (B40). La carga crea restricciones de unicidad sobre `Norma.id_norma` y `Articulo.id`, un índice por nombre de norma y un índice de texto completo sobre el texto de los artículos. `cargar_y_evaluar_grafo.sh` arma, carga y evalúa con un comando.

## Etapa 9. Evaluación del grafo

**Qué se hizo (B43, D18).** `scripts/11_evaluar_grafo.py` lee las relaciones desde el grafo, de Neo4j o de una copia en memoria armada con el mismo código, y mide cuatro cosas:

1. **Ida y vuelta.** Las relaciones que devuelve el grafo tienen que ser exactamente las cargadas. Resultado: 3.277 de 3.277, idénticas.
2. **Contra InfoLEG.** Las relaciones se proyectan a pares de normas con la regla F y se comparan por split. Resultado: F1 0,733 en dev y 0,828 en test, las mismas métricas que las reglas v2. El grafo no pierde ni agrega nada.
3. **Por tipo.** Los pares con SUSTITUYE o DEROGA están en InfoLEG entre el 90 % y el 100 % de las veces; los que solo tienen citas, alrededor del 63 %. Las citas explican 160 de los 185 falsos positivos.
4. **Por norma.** El grafo recupera el 72 % de las modificatorias de la LCT que registra InfoLEG, con 90 % de precisión; el 87 % de las de la Ley 24.557, con 94 %.

**Lo que InfoLEG no puede medir.** InfoLEG no dice el tipo, así que el tipo se revisó a mano en 36 relaciones, 6 por tipo. El tipo es correcto en 24 (67 %) y el artículo destino en 30 (83 %). MODIFICA es el más débil (1 de 6). Los errores son nominalizaciones o verbos que no actúan tomados como acción («la derogación del artículo 2°», «deberá proponer la reglamentación»), el «texto ordenado» de una cita, y las incorporaciones con la forma «como artículo 53 bis a la Ley».

## Un ejemplo de punta a punta

El Decreto 70/2023 (DNU, del split de test), artículo 70.

**1. Texto (adaptador).** El HTML de InfoLEG se convierte en 243.938 caracteres de texto plano.

**2. Segmento (segmentación).** El texto se corta en 371 segmentos; 369 son artículos. El artículo 70 dice:

> ARTÍCULO 70.- Sustitúyese el artículo 80 de la Ley N° 20.744 (t.o. 1976) y sus modificatorias, por el siguiente: “ARTÍCULO 80.- Entrega de certificados…”

**3. Mención (detección).** El detector encuentra «Ley N° 20.744» por número y la resuelve a la LCT (id 25552). No es una cita de procedencia: el «(t.o. 1976)» viene después y se ignora. Tampoco es posterior al decreto.

**4. Vínculo (regla F).** La mención está en el articulado, con número, y la oración tiene verbo, así que el par Decreto 70 → LCT es un vínculo. InfoLEG lo registra: es un acierto de test.

**5. Relación tipada (salida estándar).** El verbo «Sustitúyese» da SUSTITUYE, y el «artículo 80 de la» que precede a la mención da el artículo destino. La fila queda así:

| fuente | norma_origen | articulo_origen | tipo | norma_destino | articulo_destino | verbo |
|---|---|---|---|---|---|---|
| reglas_v2 | Decreto 70 | 70 | SUSTITUYE | Ley 20744 | 80 | Sustitúyese |

**6. Grafo.** La fila se carga como una arista:

```
(:Norma {nombre:'Decreto 70'})-[:CONTIENE]->(:Articulo {numero:'70'})
    -[:SUSTITUYE {fuente:'reglas_v2', fragmento:'…Sustitúyese el artículo 80…'}]->
(:Articulo {numero:'80'})<-[:CONTIENE]-(:Norma {nombre:'Ley 20744'})
```

**7. Consulta.** «¿Quién cambió el artículo 80 de la LCT?»

```cypher
MATCH (n:Norma)-[:CONTIENE]->(:Articulo)-[r:SUSTITUYE|MODIFICA|INCORPORA|DEROGA]->(:Articulo {id_norma: 25552, numero: '80'})
RETURN n.nombre, n.fecha, type(r), r.fragmento ORDER BY n.fecha
```

**Una limitación que se ve en el ejemplo.** El texto nuevo del artículo 80 viene entre comillas dentro del artículo 70, y vuelve a nombrar la Ley 20.744. Esa segunda mención no tiene verbo, así que queda como una CITA extra del mismo artículo. Detectar el texto citado y no extraer menciones de él es una mejora pendiente.

## Mapa del sistema

| Paso | Script | Módulo | Salida |
|---|---|---|---|
| Corpus | `01_obtener_corpus.py` | | `data/corpus/` |
| Textos | `02_descargar_textos.py` | `fuentes/infoleg.py` | `data/textos/infoleg/` |
| Cobertura | `05_cobertura_textual.py` | | `data/corpus/cobertura_textual_gold.csv` |
| Menciones y reglas | `03_extraer_reglas.py` | `extractores/menciones.py`, `reglas.py`, `reglas_v2.py`, `catalogo.py` | `results/reglas*/evidencias.csv` |
| Evaluación de reglas | `04_evaluar.py` | `evaluacion.py` | `results/reglas*/metricas.json` |
| Dataset | `07_armar_dataset.py` | | `data/dataset/` |
| Clasificador | `08_clasificador.py` | | `results/clasificador/` |
| Relaciones tipadas | `09_relaciones.py` | `extractores/relaciones.py`, `salida.py` | `results/relaciones/` |
| Grafo | `10_armar_grafo.py` | `grafo.py` | `data/grafo/` y Neo4j |
| Evaluación del grafo | `11_evaluar_grafo.py` | `grafo.py` | `results/evaluacion_grafo/` |

Todo se corre con `bash correr_pipeline.sh`, y la carga en Neo4j con `bash cargar_y_evaluar_grafo.sh`. Las salidas son deterministas: dan los mismos hashes en la Mac del equipo y en el entorno de Claude.

## Qué falta

1. **Tipado.** Separar los verbos que actúan de las nominalizaciones y los condicionales, reconocer «como artículo N a la Ley» y no extraer menciones del texto citado. Se diseña sobre dev, y la revisión de tipos se amplía para medirlo.
2. **Parser LLM y parser híbrido.** Que escriban la misma salida estándar y se comparen con la misma evaluación del grafo. Falta elegir el modelo y el acceso.
3. **Text-to-Cypher**, a partir de las consultas de `docs/grafo.md`.
4. **Otra fuente.** Probar el parser sobre el digesto de la UNNOBA cambiando solo el adaptador. Es lo que demuestra que es genérico.
5. **Validación humana** de las cuatro revisiones manuales, con un segundo anotador para el kappa.
