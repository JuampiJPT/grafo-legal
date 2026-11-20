# PI4 · El pipeline sobre el digesto de la UNNOBA (cambiando solo el adaptador)

Script: `scripts/21_pi4_unnoba.py`. Adaptador: `src/grafo_legal/fuentes/unnoba.py`. Gold: `data/corpus_unnoba/gold_pi4.tsv` (revisión 2, `docs/pi4_revision_gold.md`). Bitácora B57 y B58. Decisión D28.

## Qué se midió

**Muestra.** 70 documentos del digesto (semilla 20261120, `data/corpus_unnoba/muestra_pi4.csv`):
- 7 ordenanzas;
- 48 resoluciones de los temas Reglamentación, Cursadas, Regularidades, Reglamento Trabajo Final e Ingreso;
- 15 al azar.

38 son escaneos y su texto sale de OCR (tesseract, español).

**Gold.** Es una anotación manual hecha por Claude, en dos revisiones (B57 y B58). Cada par (documento, norma citada) tiene una de tres clases:

| Clase | Significa | Pares |
|---|---|---|
| MOD | actúa sobre la norma: modifica, sustituye, deroga, deja sin efecto, ratifica, prorroga, reglamenta, extiende | 20 |
| APLICA | el articulado la aplica: la usa para definir a quién alcanza o cómo se hace algo, otorga algo previsto en ella, o se dicta en su marco | 41 |
| CITA | antecedente, competencia («Art. 76 del Estatuto»), mención incidental, formulario o sello | 48 |

Se evalúa el **vínculo**, MOD ∪ APLICA (61 pares), que es lo más parecido al «modifica o complementa» de InfoLEG. También se evalúa MOD solo (20 pares) y la detección de menciones (los 109 pares).

**Qué cambió y qué no.**
- **Cambió el adaptador:** el texto del PDF, las partes del documento, las menciones y las claves `TIPO-EMISOR-NÚMERO-AÑO`. Las claves se comparan sin el emisor.
- **No cambió:** las reglas F (v2) y F3 (v3), el verbo, el parser LLM y el híbrido («previa», umbrales 0,5 y 0,15), con sus prompts tal cual.
- **Variante «vocab»:** en los dos prompts se cambiaron solo las frases que enumeran tipos de norma.

## Resultados (vínculo, 61 pares)

| Método | P | R | F1 |
|---|---|---|---|
| Reglas F (v2) = F3 (v3) | 0,932 | 0,902 | 0,917 |
| LLM, prompt de InfoLEG | 0,889 | 0,262 | 0,405 |
| LLM, prompt «vocab» | 0,895 | 0,836 | 0,864 |
| **Híbrido, prompt de InfoLEG** | **0,983** | **0,934** | **0,958** |
| Híbrido, prompt «vocab» | 0,967 | 0,967 | 0,967 |

Bootstrap pareado por documento (2.000 remuestras, IC 95 %):

| Comparación | Diferencia de F1 | IC 95 % |
|---|---|---|
| Híbrido − F3 | +0,041 | [−0,002; +0,101] |
| Híbrido − LLM vocab | +0,094 | [−0,003; +0,230] |
| LLM vocab − F3 | −0,053 | [−0,200; +0,048] |
| LLM vocab − LLM InfoLEG | +0,459 | [+0,303; +0,617] |

El híbrido es el mejor, pero con 70 documentos la diferencia con las reglas no llega a ser significativa: el intervalo toca el cero. La única diferencia clara es la del vocabulario del prompt del LLM.

**Solo MOD (20 pares):**

| Método | P | R | F1 |
|---|---|---|---|
| Reglas (tipo por verbo ≠ CITA) | 0,833 | 0,500 | 0,625 |
| LLM InfoLEG | 1,000 | 0,300 | 0,462 |
| LLM vocab | 1,000 | 0,650 | 0,788 |

El híbrido no separa MOD de APLICA, así que no tiene esta medida.

**Detección de menciones (109 pares):**

| Detector | P | R | F1 |
|---|---|---|---|
| Detector del adaptador | 1,000 | 0,972 | 0,986 |
| LLM InfoLEG | 0,905 | 0,174 | 0,292 |
| LLM vocab | 0,990 | 0,908 | 0,947 |

**Costo.** 252 pedidos, alrededor de 680.000 tokens de entrada y 70.000 de salida, unos USD 3. Todo queda en la cache: se repite sin costo.

## Sensibilidad al gold

La revisión 2 cambió 16 pares: 14 remisiones, una exigencia de formato y una ratificación implícita (B58). Las 16 son pares que antes eran CITA y ahora son vínculo, y los métodos ya los predecían. Así que la revisión **sube todos los números**. Para que se vea cuánto, `metricas.json` (`sensibilidad_gold_revision_1`) guarda también los resultados con el gold de la revisión 1:

| Método | F1 con la revisión 1 | F1 con la revisión 2 |
|---|---|---|
| Reglas F3 | 0,788 | 0,917 |
| LLM InfoLEG | 0,286 | 0,405 |
| LLM vocab | 0,706 | 0,864 |
| Híbrido | 0,854 | 0,958 |
| Híbrido, política «cascada» | 0,944 | 0,838 |

**Lo que no cambia con el criterio:**
- el híbrido con su política congelada («previa») queda primero;
- el LLM con el prompt de InfoLEG queda último;
- el vocabulario del prompt pesa más que cualquier otra cosa.

**Lo que sí depende del criterio** es cuál política del híbrido conviene:
- «cascada» deja que el LLM decida solo y es más estricta: con el criterio viejo se descartan las remisiones.
- «previa», la congelada en InfoLEG, deja que la regla gane en la duda. Con el criterio nuevo esas remisiones son vínculos, y por eso «previa» rinde más.

## Qué se pierde al cambiar de corpus, y por qué

1. **El vocabulario de los prompts es parte del adaptador.**
   - Con el prompt de InfoLEG, el LLM solo reporta leyes y decretos: encuentra 19 de las 109 menciones. Las resoluciones y ordenanzas, que son casi todo el digesto, quedan afuera.
   - Con tres frases cambiadas pasa a 99 de 109.
   - El parser LLM no se transfiere solo: el prompt nombra los tipos de norma de la fuente, y eso hay que cambiarlo junto con el adaptador.
   - El híbrido no tiene este problema, porque sus candidatos vienen del detector del adaptador y el LLM solo los juzga.
2. **El léxico de verbos de las reglas es el de InfoLEG.**
   - InfoLEG escribe la fórmula impersonal («Sustitúyese», «Derógase»). La UNNOBA usa el infinitivo: «Ratificar», «Dejar sin efecto», «Extender la aplicación».
   - `VERBOS` no tiene «ratificar» ni el infinitivo de «dejar sin efecto». Por eso 10 de los 20 MOD quedan sin verbo: las 6 ratificaciones, «Dejar sin efecto la Res. (CD.ET) 64/2013», «Extender la aplicación…», la revisión de la Res. 633/2013 y la ratificación implícita del doc 10.
   - El vínculo no se pierde, porque la regla F acepta el VISTO y el articulado. Lo que se pierde es el tipo, y con él la zona «segura» del híbrido: solo 9 pares caen ahí y 97 en la gris.
3. **Las reglas F y F3 dan lo mismo.** Lo que agrega la v3 (alias con verbo en el articulado, «Valor Agregado», procedencia) no aparece en este corpus.
4. **Falsos positivos.** Quedan pocos: 4 de las reglas, 1 del híbrido y 6 del LLM vocab.
   - Las reglas aceptan cualquier mención del articulado o del VISTO aunque sea incidental:
     - una bibliografía que cita la Ley 13.016 (doc 12);
     - un sello de «copia fiel» con la Res. (CS) 1/2001 (doc 17);
     - el Plan Estratégico citado en la propuesta de una carrera (doc 2);
     - la Res. 556/98, nombrada en el VISTO solo para describir un decreto (doc 21).
   - El híbrido descarta tres de esos cuatro, porque el LLM ve que la mención es incidental.
   - El LLM vocab marca, además, el Estatuto cuando aparece en el articulado como fuente de la competencia («conforme el Art. 76 inc. 32 del Estatuto»).
5. **Falsos negativos.**
   - **Reglas (6):**
     - doc 7: el OCR leyó «Res.olución (CS) 531/2012» y el articulado no se detecta;
     - doc 50: el dispositivo revisa un beneficio sin volver a nombrar la Res. 531/2012;
     - doc 15: ratifica una resolución que modificaba la Ordenanza 14/2009, así que el efecto es indirecto;
     - doc 17: la Ordenanza 40/2014 reemplaza el procedimiento de la Ordenanza 12/2009 sin nombrarla en el articulado;
     - doc 10 y doc 36: dos menciones que el detector pierde (punto 6).
   - **Híbrido (4):**
     - recupera los docs 7, 15 y 17, porque el LLM ve en el fragmento del CONSIDERANDO de qué norma se trata;
     - pierde el doc 50 (probabilidad 0,45) y las dos menciones que no se detectan;
     - pierde la Res. Ministerial 1523/90 del doc 34, porque el LLM le dio 0,10 y la política «previa» la descarta por debajo de 0,15.
6. **Detección.**
   - El detector corrige la barra que el OCR lee como «1» («53112012» → 531/2012).
   - Pierde 3 pares:
     - «N° '1523/90», con un apóstrofo del OCR;
     - «Estatnto»;
     - la «resolución ET 313/2016» del doc 10. Es la resolución ad referéndum de la Directora y tiene el mismo número que la propia (CD.ET 313/2016). Como las claves se comparan sin emisor, el filtro de autocita la descarta.
   - Además, a nivel de mención, se pierde «Res.olución» (doc 7).

## Límites

- **La muestra es chica:** 70 documentos y 61 pares de vínculo, así que los intervalos son anchos.
- **Hay un solo anotador**, que además escribió el adaptador y vio los resultados antes de la revisión 2. La revisión aplica las definiciones de clase escritas antes de correr nada y deja cada cambio escrito con su motivo (`docs/pi4_revision_gold.md`). Aun así, todos los cambios fueron hacia lo que los métodos predecían. Por eso se informan las dos versiones.
- **El detector se escribió leyendo los mismos documentos.** No hay separación dev/test como en InfoLEG, así que la detección (0,986) es optimista. Las reglas y los prompts no se tocaron.

## Archivos

- `evidencias.csv`: una fila por mención, con parte, artículo, verbo y clave.
- `relaciones_llm.csv`, `relaciones_llm_vocab.csv`, `relaciones_hibrido.csv`, `relaciones_hibrido_vocab.csv`: las salidas de cada método.
- `metricas.json`: todas las métricas, por estrato de la muestra, el bootstrap, la política «cascada» y la sensibilidad al gold de la revisión 1.
- `errores.csv`: los falsos positivos y negativos de cada método.
- `gold_normalizado.csv`: el gold con las claves de comparación.
- `cache_llm/` y `cache_hibrido/`: no van a git, porque pueden traer nombres.
