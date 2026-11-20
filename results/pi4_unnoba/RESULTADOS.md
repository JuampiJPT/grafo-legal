# PI4 · El pipeline sobre el digesto de la UNNOBA (cambiando solo el adaptador)

Script: `scripts/21_pi4_unnoba.py` · Adaptador: `src/grafo_legal/fuentes/unnoba.py` · Gold: `data/corpus_unnoba/gold_pi4.tsv` · Bitácora B57 · Decisión D28.

## Qué se midió

**Muestra.** 70 documentos del digesto (semilla 20261120, `data/corpus_unnoba/muestra_pi4.csv`):

- 7 ordenanzas;
- 48 resoluciones de los temas Reglamentación, Cursadas, Regularidades, Reglamento Trabajo Final e Ingreso;
- 15 documentos al azar del resto («negativos»: se esperaba que tuvieran pocas relaciones).

38 son escaneos y su texto sale de OCR (tesseract, español).

**Gold.** Anotación manual, hecha por Claude y pendiente de validación del equipo. Es un par (documento, norma citada) con una de tres clases:

| Clase | Significa | Pares |
|---|---|---|
| MOD | actúa sobre la norma: modifica, sustituye, deroga, deja sin efecto, ratifica, prorroga, reglamenta, extiende | 19 |
| APLICA | el dispositivo aplica la norma o se dicta en su marco (otorga un beneficio previsto en ella, reglamenta algo que ella prevé) | 26 |
| CITA | antecedente, competencia («Art. 76 del Estatuto») o remisión | 63 |

Se evalúa el **vínculo** (MOD ∪ APLICA, 45 pares), que es lo más parecido al «modifica o complementa» de InfoLEG. También se evalúa MOD por separado (19 pares) y la detección de menciones (los 108 pares).

Nueve pares CITA se agregaron después de la primera corrida: eran menciones reales que la anotación había salteado (lo explica el B57). No cambian el gold de vínculo.

**Qué cambió y qué no.**

- **Cambió el adaptador:** texto del PDF, partes del documento (VISTO, CONSIDERANDO, «RESUELVE:»/«ORDENA:»), menciones y claves `TIPO-EMISOR-NÚMERO-AÑO`. La comparación se hace sin el emisor.
- **No cambió:** las reglas F (v2) y F3 (v3), el verbo, el parser LLM y el híbrido («previa», umbrales 0,5 y 0,15), con sus prompts tal cual.
- **Variante «vocab»:** en los dos prompts se cambiaron solo las frases que enumeran tipos de norma («ley o decreto» → «ley, decreto, resolución u ordenanza»).

## Resultados (vínculo, 45 pares)

| Método | P | R | F1 |
|---|---|---|---|
| Reglas F (v2) = F3 (v3) | 0,695 | 0,911 | 0,788 |
| LLM, prompt de InfoLEG | 0,500 | 0,200 | 0,286 |
| LLM, prompt «vocab» | 0,632 | 0,800 | 0,706 |
| **Híbrido, prompt de InfoLEG** | **0,759** | **0,978** | **0,854** |
| Híbrido, prompt «vocab» | 0,738 | 1,000 | 0,849 |

Bootstrap pareado por documento (2.000 remuestras, IC 95 %):

| Comparación | Diferencia de F1 | IC 95 % |
|---|---|---|
| Híbrido − F3 | +0,066 | [+0,018; +0,137] |
| Híbrido − LLM vocab | +0,148 | [+0,032; +0,303] |
| LLM vocab − F3 | −0,082 | [−0,262; +0,041] |
| LLM vocab − LLM InfoLEG | +0,420 | [+0,210; +0,624] |

**Solo MOD (19 pares):**

| Método | P | R | F1 |
|---|---|---|---|
| Reglas (tipo por verbo ≠ CITA) | 0,833 | 0,526 | 0,645 |
| LLM InfoLEG | 1,000 | 0,316 | 0,480 |
| LLM vocab | 1,000 | 0,684 | 0,813 |

El híbrido no separa MOD de APLICA, así que no tiene esta medida.

**Detección de menciones (108 pares):**

| Detector | P | R | F1 |
|---|---|---|---|
| Detector del adaptador | 0,991 | 0,972 | 0,981 |
| LLM InfoLEG | 0,905 | 0,176 | 0,295 |
| LLM vocab | 0,980 | 0,907 | 0,942 |

**Costo.** 252 pedidos, unos 680.000 tokens de entrada y 70.000 de salida, alrededor de USD 3. Todo queda en la cache: se repite sin costo.

## Qué se pierde al cambiar de corpus, y por qué

1. **El vocabulario de los prompts es parte del adaptador.** Con el prompt de InfoLEG, el LLM solo reporta leyes y decretos: encuentra 19 de las 108 menciones. Las resoluciones y ordenanzas, que son casi todo el digesto, quedan afuera. Con cambiar tres frases del prompt pasa a 98 de 108. El parser LLM no se transfiere solo: lo que cambia con la fuente incluye los tipos de norma que nombra el prompt. Al híbrido no le pasa porque sus candidatos vienen del detector del adaptador, y el LLM solo los juzga.
2. **El léxico de verbos de las reglas es el de InfoLEG.** InfoLEG escribe la fórmula impersonal («Sustitúyese», «Derógase»). La UNNOBA usa el infinitivo: «Ratificar», «Dejar sin efecto», «Extender la aplicación», «Otorgar». `VERBOS` no tiene «ratificar» ni el infinitivo de «dejar sin efecto», así que 9 de los 19 MOD quedan sin verbo:
   - las 6 ratificaciones de resoluciones del Rector;
   - «Dejar sin efecto la Res. (CD.ET) 64/2013»;
   - «Extender la aplicación de la Res. 44/2008»;
   - la revisión de la Res. 633/2013.

   El vínculo no se pierde, porque la regla F acepta todo el VISTO y el articulado. Lo que se pierde es el tipo, y con él la zona «segura» del híbrido: solo 9 pares caen en esa zona y 97 en la gris.
3. **Las reglas F y F3 dan lo mismo.** Lo que agrega la v3 (alias con verbo en el articulado, «Valor Agregado», procedencia) no aparece en este corpus.
4. **Casi todos los falsos positivos son una sola duda de criterio.** Ocho resoluciones de inscripción (docs 33 a 40) dicen que los aspirantes «no incluidos en la Resolución Ministerial N° 1523/90 quedan comprendidos…» y traen el modelo de constancia «en el marco del art. 7° de la Ley de Migraciones N° 25.871». La anotación las marcó como CITA, una remisión. Son 14 de los 18 falsos positivos de las reglas y 14 de los 14 del híbrido.
   - El LLM del híbrido les da probabilidades de 0,1 a 0,55, pero la política «previa» solo descarta un par que F3 acepta si la probabilidad es menor que 0,15. Así que gana la regla.
   - **Sensibilidad.** Si esas remisiones se anotan como APLICA, F3 sube a F1 0,915 y el híbrido a 0,957. La política «cascada» (el LLM decide la zona gris con umbral 0,5) da 0,944 con el gold actual y 0,854 con el alternativo. El orden de los métodos depende de esa decisión. Lo que no cambia con ella: el híbrido queda primero y el LLM con el prompt de InfoLEG, último (`analisis_sensibilidad.json`).
5. **Falsos negativos.** Las reglas pierden 4 pares. En los cuatro, la norma solo aparece en el CONSIDERANDO:
   - **doc 7:** el articulado la nombra, pero el OCR leyó «Res.olución (CS) 531/2012» y el detector no la reconoce;
   - **doc 50:** el dispositivo revisa un beneficio sin volver a nombrar la Res. 531/2012;
   - **doc 15:** ratifica una resolución del Rector que modificaba la Ordenanza 14/2009, así que el efecto es indirecto;
   - **doc 17:** la Ordenanza 40/2014 reemplaza el procedimiento de la Ordenanza 12/2009 sin nombrarla en el articulado.

   El híbrido recupera 3, porque el LLM ve en el fragmento del CONSIDERANDO de qué norma se trata. Pierde el doc 50, con probabilidad 0,45.
6. **Lo que el OCR rompe, poco.** El detector corrige la barra leída como «1» («53112012» → 531/2012). A nivel de par pierde 3:
   - «N° '1523/90», con un apóstrofo del OCR;
   - «Estatnto», por «Estatuto»;
   - la «resolución ET 313/2016» del doc 10, que es la Resolución (CD.ET) 313/2016 y cita la resolución ad referéndum de la Directora con el mismo número. Como las claves se comparan sin emisor, el filtro de autocita la descarta. Es el costo de comparar sin emisor.

   Además, a nivel de mención, el OCR rompe «Res.olución» (doc 7, punto 5). El único falso positivo es el Estatuto del doc 15, que la anotación probablemente salteó. No se corrigió, para no seguir ajustando el gold después de ver los resultados.

## Límites

- La muestra es chica: 70 documentos y 45 pares de vínculo. Los intervalos son anchos.
- **Hay un solo anotador**, que además escribió el adaptador. El vocabulario del detector se escribió leyendo los mismos documentos que se anotaron. No hay separación dev/test como en InfoLEG, así que la detección (0,98) es optimista. Las reglas y los prompts, en cambio, no se tocaron para este corpus.
- El gold es de Claude y el equipo tiene que validarlo, sobre todo la clase de las remisiones (punto 4).

## Archivos

- `evidencias.csv`: una fila por mención, con parte, artículo, verbo y clave.
- `relaciones_llm.csv`, `relaciones_llm_vocab.csv`, `relaciones_hibrido.csv`, `relaciones_hibrido_vocab.csv`: las salidas de cada método.
- `metricas.json`: todas las métricas, por estrato de la muestra y el bootstrap.
- `errores.csv`: los falsos positivos y negativos de cada método.
- `analisis_sensibilidad.json`: el gold alternativo y la política «cascada».
- `cache_llm/`, `cache_hibrido/`: las respuestas del modelo. No van a git: pueden traer nombres de las resoluciones.
