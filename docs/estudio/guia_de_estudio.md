# Guía de estudio para el coloquio: el TP de punta a punta

TP Integrador · Problemática III · Sistemas Inteligentes · UNNOBA. Integrantes: Cidoni, Valentino · Lodeiro, Bruno · Martino, Lucas · Tagliaferro, Juan Pedro.

Esta guía está pensada para estudiar antes del examen oral y para repasar las preguntas. Cada cifra sale del informe de avance, de `results/` o de la bitácora (las referencias B y D apuntan a sus entradas). Si en el coloquio te piden un detalle que no está acá, casi seguro está en la entrada de la bitácora que se cita al lado.

**Cómo usarla.**
1. Leé las secciones 1 a 11 de corrido una vez: cuentan el trabajo en el orden en que se hizo.
2. Memorizá la sección 12 (las cifras clave).
3. Practicá la sección 13 en voz alta: son las preguntas más probables, con una respuesta corta y una larga.

---

## 1. El trabajo en un minuto

Las normas se modifican entre sí, pero esas relaciones están escritas en texto libre («Sustitúyese el artículo 245 de la Ley 20.744…»). El TP construye un sistema que **lee el texto de las normas y reconstruye solo qué norma modifica o complementa a cuál**, y lo guarda en un **grafo en Neo4j donde cada arista conserva el fragmento de texto que la justifica**.

Lo evaluamos con un **experimento controlado**: InfoLEG publica, aparte del texto, bases estructuradas con qué norma modifica a cuál. Esas bases son el *gold*: el sistema nunca las ve y solo se usan para medir.

Comparamos **reglas, modelos y estrategias híbridas** con el mismo protocolo, sobre los mismos 192 pares de prueba:

- las reglas llegan a **F1 0,828**;
- el LLM a **0,841** (y sube mucho el tipo de relación: macro-F1 de 0,672 a **0,883**);
- los híbridos, entre **0,829 y 0,839**;
- la única mejora significativa sobre las reglas es el **híbrido por intersección (+1,0 punto)**.

El hallazgo central: **el problema no está en encontrar la cita (99,6 %), sino en decidir si una cita es una relación**, sobre todo en el VISTO y en los vínculos que el texto ni nombra. Además: el pipeline se transfirió al **digesto de la UNNOBA** (híbrido F1 0,958) y con el grafo se **reconstruyó el texto vigente de la LCT** (95,9 % de los artículos coinciden con InfoLEG).

---

## 2. El problema y lo que pide la consigna

**Problema.** Un cuerpo normativo es una red: las normas se sustituyen, incorporan, derogan, reglamentan y citan. Para saber qué dice hoy una ley hay que conocer esa red, y en muchos repositorios no está estructurada.

**Por qué InfoLEG.** Es la base de normativa nacional del Ministerio de Justicia. Publica:
- el **texto** de cada norma (HTML);
- dos **bases complementarias** (normas modificadas y modificatorias), con licencia CC BY 4.0.

Eso permite ocultar las bases, reconstruir desde el texto y comparar: un experimento controlado con un gold **oficial, grande y externo**.

**Lo que pide la consigna** (Anexo Problemática III):
- un método de **reglas** como referencia y **al menos un enfoque basado en modelos** (aprendizaje automático o modelos de lenguaje), evaluados **sobre el mismo test**;
- una **estrategia híbrida** (recomendada: las reglas detectan candidatos y un modelo resuelve);
- un **grafo dirigido** con **trazabilidad**: cada arista con norma origen, norma destino, tipo si se puede, fragmento, ubicación y método;
- evaluación separada de **detección, normalización y extracción**; P/R/F1; macro-F1 y matriz de confusión si hay tipos;
- **análisis de errores** con sus categorías (norma no detectada, mal normalizada, relación invertida, inexistente, tipo incorrecto, referencia ambigua, destino fuera del corpus);
- **test separado**, idealmente con un corte temporal.

**Preguntas de investigación.**

| PI | Pregunta | Dónde se responde |
|---|---|---|
| PI1 | ¿Qué efectividad tienen reglas, modelos e híbridos? | Tabla de métodos (sec. 7) |
| PI2 | ¿El híbrido mejora a cada enfoque por separado? | Sec. 7 y 8 |
| PI3 | ¿Qué formulaciones producen más errores? | Sec. 8 |
| PI4 | ¿Se transfiere a un cuerpo sin relaciones estructuradas? | Sec. 10 (digesto UNNOBA, preliminar) |
| PI5 | ¿Qué aporta un grafo con evidencia? | Sec. 11 (consolidación de la LCT, preliminar) |

La cursada pedía la PI1 y una primera aproximación a la PI2. Respondimos PI1, PI2 y PI3, y adelantamos PI4 y PI5.

---

## 3. Los datos: qué corpus usamos y por qué

### 3.1 Qué es

| Elemento | Valor |
|---|---|
| Fuente | InfoLEG + bases complementarias, descargadas el 06/11/2026 (SHA-256 en `data/corpus/SNAPSHOT.md`) |
| Catálogo completo | 430.834 normas (es contra lo que se normaliza) |
| Dominio | Derecho laboral |
| Anclas | 5 leyes: 20.744 (LCT), 27.802 (modernización laboral, 2026), 24.013 (empleo), 24.557 (riesgos del trabajo), 23.551 (asociaciones sindicales) |
| Expansión | Un salto en el grafo de InfoLEG; solo leyes, decretos y decretos-ley |
| Normas | **340**, de las cuales **306 tienen texto** (34 sin enlace al texto, casi todas de 1997 o antes) |
| Gold | **775 pares** dirigidos (origen → destino) dentro del corpus |
| Partición | Temporal, corte 31/12/2019 por fecha de la modificatoria: **583 pares dev / 192 test** (43 normas de origen en test) |
| Dataset derivado | `articulos.csv`: 8.066 segmentos · `pares_candidatos.csv`: 1.091 pares candidatos con 22 atributos y su etiqueta |

### 3.2 Por qué ese corpus (decisiones)

- **No solo dos leyes (B04).** La idea inicial era LCT + Ley 27.802. Pero el gold registra relaciones **entre normas**, no entre artículos: la 27.802 cambia decenas de artículos de la LCT y eso es **una sola arista**. Con 1 o 2 aristas las métricas valen 0 o 1, no hay split posible y las reglas quedan ajustadas a un solo redactor. Por eso pasamos a un dominio.
- **Derecho laboral.** Tiene cadenas largas de modificación (la LCT es la ley más modificada del corpus) y la reforma de 2026 como caso central.
- **Un salto de expansión (B08).** Con dos saltos salían **4.115 normas y 12.380 pares**: imposible el análisis manual de errores que exige la consigna. La consigna además permite «un subconjunto acotado de normas» durante la cursada.
- **Se amplió una vez (B18, B24).** Con solo LCT y 27.802 el grafo era una estrella (37 % de las aristas tocaba la LCT). Sumamos Empleo, Riesgos del Trabajo y Asociaciones Sindicales: 775 pares y la concentración bajó al 19 %.
- **Ley 14.250 sin expandir (B07, B30).** Tiene 42.598 relaciones, casi todas resoluciones que homologan convenios. Revisamos 30: ninguna modifica el texto de la ley. Se deja como nodo, sin expandir.
- **Solo leyes y decretos.** Las resoluciones y disposiciones abren otro universo; aparecen recién en la PI4.
- **Congelado (B17, B23, B33).** El portal publica una versión por mes y no guarda las anteriores: si no se congela, el corpus cambia solo. `correr_pipeline.sh` lo regenera y compara byte a byte.
- **Un solo corpus (B33).** Hubo un v1 (183 normas, 402 pares) y un v2; mantener dos obligaba a informar todo dos veces. Quedó uno; el v1 está contenido y `pares_evaluados_en_v1.csv` marca los pares ya vistos.

### 3.3 Por qué el split es temporal (B09)

- Simula usar el sistema con **normas nuevas**: se diseña con normas hasta 2019 y se prueba con normas de 2020 en adelante.
- Deja en test las **reformas recientes** (DNU 70/2023, Ley 27.742, Ley 27.802).
- Objeción posible: 114 pares cruzan el corte (modificatoria en test, modificada en dev). **No es fuga**: el extractor nunca ve el gold y la norma modificada solo aparece como destino a normalizar.

### 3.4 Qué mide el gold (B27, D6)

InfoLEG registra un vínculo **amplio**. En 21 pares con mención explícita revisados a mano: 7 modificaciones, 9 remisiones, 4 reglamentaciones y 1 texto ordenado. Por eso evaluamos **«modifica o complementa»** y no la modificación estricta. Exigir un verbo modificatorio bajaba el F1 de dev de 0,716 a 0,556.

### 3.5 El techo textual (B26, B51)

No todo el gold se puede encontrar leyendo el texto de la modificatoria. El destino aparece nombrado en el **81 % de los pares de dev** y el **96 % de test**. De los 80 pares sin mención: 36 complementan sin citar, 9 son textos ordenados implícitos («LCT t.o. 1976» vincula al Decreto 390/76), 16 son derogaciones genéricas o de modificatorias, y 2 parecen errores del gold. **Ningún parser textual puede encontrarlos.**

### 3.6 ¿Por qué tan chico? (respuesta para el coloquio)

El tamaño se eligió para **evaluar con rigor y revisar cada error a mano**, como pide la consigna en la cursada. Para **entrenar** modelos resultó chico, y lo medimos con la curva de aprendizaje (sec. 8.6). Las reglas y el LLM no aprenden del corpus, así que su techo no depende del tamaño. InfoLEG tiene más de 37.000 relaciones entre leyes y decretos con texto: ampliar es el primer paso para el final.

---

## 4. El pipeline y el código

### 4.1 La arquitectura (Figura 1 del informe)

Una cadena de componentes independientes. **Solo el adaptador depende de la fuente**, y **el gold entra únicamente en la evaluación**.

```
texto de la norma
  → 1. ADAPTADOR (fuentes/infoleg.py, fuentes/unnoba.py): HTML/PDF → texto limpio → zonas y artículos, con offsets
  → 2. DETECCIÓN (extractores/menciones.py): regex + gazetteer de nombres propios
  → 3. NORMALIZACIÓN (catalogo.py): mención → id de norma (mundo cerrado)
  → 4. EXTRACCIÓN de la relación: reglas | LLM | híbrido (intercambiables)
  → 5. SALIDA ESTÁNDAR (salida.py): una tabla igual para todos los parsers
  → 6. GRAFO (grafo.py): Neo4j con MERGE, idempotente
  → 7. EVALUACIÓN: contra el gold, también leyendo el grafo de vuelta
```

### 4.2 Cada pieza

1. **Adaptador.** Pasa el HTML a texto limpio (saca etiquetas, notas al pie, espacios) y segmenta en **zonas**: encabezado (con VISTO y CONSIDERANDO), articulado (partido en artículos), anexos y notas de InfoLEG. **Cada segmento guarda sus offsets** en el texto limpio: es lo que permite que cada arista apunte a su evidencia exacta. El del digesto hace lo mismo sobre `pdftotext` (y OCR con tesseract en 38 escaneados) y reconoce «RESUELVE:», «ORDENA:».
2. **Detección.** Dos detectores:
   - **expresiones regulares** para menciones por número: «Ley N° 24.557», «Decreto 1694/06», «leyes 23.551 y 25.674», «DNU 70/2023», listas, «(t.o. 1976) y sus modificatorias», decretos-ley;
   - **gazetteer** de nombres propios: «Ley de Contrato de Trabajo», «L.C.T.», «Ley de Ministerios».
3. **Normalización.** Cada mención (tipo, número, año) se busca en el catálogo de 430.834 normas y queda **resuelta, ambigua, fuera del corpus o no encontrada**.
   - **Mundo cerrado (D4):** solo se vincula si el destino está en el corpus. Lo de afuera se registra, no se enlaza. El gold también está limitado al corpus, así que no distorsiona.
   - **Decretos (D5):** los números se repiten cada año. Si la mención trae año, se exige; si no, se resuelve solo si hay una única candidata en el corpus (riesgo documentado). Los decretos-ley se catalogan como Ley.
4. **Decisión de la relación (regla F, sec. 5.1)** y **tipo por verbo** (`relaciones.py`): el verbo de la oración da SUSTITUYE, INCORPORA, DEROGA, REGLAMENTA, MODIFICA o CITA, y el artículo destino si lo dice.
5. **Salida estándar (B41, D16).** Una fila por relación: fuente, norma y artículo de origen, parte (zona), tipo, norma y artículo destino, verbo, método, confianza, n.º de menciones, offsets y fragmento. **Cualquier parser escribe esto**, así sumar un parser o una fuente no cambia ni el grafo ni la evaluación.
6. **Grafo** (sec. 9).
7. **Evaluación** (sec. 6).

### 4.3 Dónde está cada cosa (para cuando te pidan ver código)

| Qué | Archivo |
|---|---|
| Biblioteca (unas 1.900 líneas) | `src/grafo_legal/` |
| Adaptadores | `fuentes/infoleg.py`, `fuentes/unnoba.py` |
| Menciones | `extractores/menciones.py` |
| Reglas v1 / v2 / v3 | `extractores/reglas.py`, `reglas_v2.py`, `reglas_v3.py` |
| Tipo por verbo | `extractores/relaciones.py` |
| Parser LLM | `extractores/llm.py` (prompt en `llm.SISTEMA`) |
| Híbrido en cascada | `extractores/hibrido.py` |
| Catálogo / normalización | `catalogo.py` |
| Salida estándar | `salida.py` |
| Grafo (Neo4j y copia en memoria) | `grafo.py` |
| P/R/F1 | `evaluacion.py` |
| Pipeline completo | scripts numerados `01`–`35`, `correr_pipeline.sh` |
| Tests | `tests/` (19, sin red, con `pytest`) |
| Recorrido para la presentación | `docs/guia_codigo.md` |

Scripts más citados: `08` clasificador · `09` relaciones · `10` armar grafo · `11` evaluar grafo · `12` subtareas · `13` TF-IDF · `14/15` LLM · `16` tipos · `17` tabla final con intervalos · `18` explicar errores · `20` híbrido en cascada · `21/22` digesto · `23–25` consolidado · `30` cargar todo en Neo4j · `32` curva de aprendizaje · `33/34` grafos de los clasificadores · `35` consultas de la demo.

**Stack:** Python 3.10+, pandas, scikit-learn, numpy/scipy (bootstrap), SDK `anthropic`, Neo4j 5 en Docker (puertos 7475 y 7688) con el driver `neo4j`, networkx para la copia en memoria, pdftotext y tesseract, matplotlib, pytest, git/GitHub.

---

## 5. Los métodos

### 5.1 Reglas (método de referencia)

| Versión | Qué hace | F1 dev | F1 test |
|---|---|---|---|
| v1 (config. C) | Solo menciones del articulado, no posteriores al origen | 0,652 | 0,788 |
| **v2 (config. F) — referencia** | Ver abajo | **0,733** | **0,828** |
| v3 (experimento) | v2 + lee el año escrito como fecha | 0,750 | 0,826 |

**Regla F (v2), en una frase:** se acepta el par si hay una mención **no posterior al origen**, que **no sea una cita de procedencia** («t.o. por Decreto 390/76», «sustituido por el art. 2° del Decreto…»), y que esté **en el VISTO**, o **en el articulado, con número, cuando el origen es una ley o la oración tiene un verbo modificatorio**. «Complementarias» y «reglamentarios» no cuentan como verbos.

**Cómo se diseñó (B36):** solo sobre dev, mirando errores y 30 falsos positivos revisados a mano (16 remisiones en el articulado, 9 normas de listas largas del VISTO, 2 procedencias, 3 modificaciones reales que InfoLEG no registra). El dato clave de dev: **el 80 % de los pares citados en el VISTO está en el gold, contra el 24 % de los que solo están en el CONSIDERANDO**; en el articulado, un decreto que nombra una norma sin verbo casi siempre remite (solo el 19 % está en el gold).

**Alternativas descartadas:** limitar el VISTO a listas cortas (bajaba más el recall que lo que subía la precisión); un filtro de procedencia que incluía «aprobado por» (atrapaba «Régimen de Contrato de Trabajo aprobado por la Ley 20.744», que sí está en el gold).

**Por qué la v2 sigue siendo la referencia y no la v3:** la v2 se congeló primero y se evaluó una sola vez. La v3 se diseñó **después de ver los errores de test de la v2**, así que se informa como experimento. Además empata (0,826 contra 0,828).

### 5.2 Clasificador de superficie: random forest (B37, D14)

- **Qué es:** un clasificador de pares. Para cada par candidato (la norma A menciona a la B) decide si es una relación.
- **Atributos (22):** menciones por zona (articulado, VISTO, CONSIDERANDO, anexo, notas), menciones de procedencia, verbo en el artículo o en la oración, fracción de artículos que nombran al destino, posición de la primera mención, largo del texto, diferencia de años, tipos de norma, mención solo por nombre propio, si el destino es una ancla.
- **Cómo se eligió:** se compararon **regresión logística, random forest y gradient boosting** con **validación cruzada de 5 particiones en dev, agrupada por norma de origen** (para que los pares de una misma norma no queden repartidos entre entrenamiento y validación: si no, el modelo «reconocería» la norma y el resultado saldría inflado). Ganó el random forest con **umbral 0,45**.
- **Cómo funciona:** 400 árboles de decisión; cada uno ve una muestra distinta de pares y, en cada pregunta, solo algunos atributos. La probabilidad es el promedio de los árboles. Los atributos que más pesan: posición de la primera mención, fracción de artículos que nombran al destino, largo del texto y diferencia de años.
- **Resultado:** F1 **0,823** en test, empatado con las reglas (0,828).
- **Por qué este modelo:** con 800 ejemplos y unos 20 atributos numéricos es el estándar más fuerte para datos tabulares, robusto, sin escalar, y da importancia de atributos.

### 5.3 Modelo contextual: TF-IDF + regresión logística (B46, D20)

- **Por qué:** la consigna pide un modelo que clasifique «a partir del contexto textual», y el random forest no lee el texto. Es el modelo **más simple que lee el texto**, interpretable (se ven los pesos de cada palabra) y funciona con pocos datos. Un BERT afinado necesita más ejemplos y GPU: queda como trabajo futuro.
- **Cómo:** de cada mención toma 150 caracteres a cada lado; **reemplaza la norma mencionada por la palabra DESTINO** y los dígitos por `#`, y agrega la zona. Así aprende la forma de la frase y no el número de una ley. TF-IDF de unigramas y bigramas (unas 10.800 columnas) + regresión logística.
- **Pesos que aprendió:** a favor, técnica legislativa («parte_articulado articulo», «la destino», «siguiente»); en contra, remisiones («alcance», «caso», «contrato de»), «reemplazado por», «derogado», «concordantes». También aprendió cosas sin sentido, como «bs as» (de «Bs. As.», la línea de la fecha): **memoriza**.
- **Variantes:** solo texto (C = 10, umbral 0,40) → **0,761**; texto + atributos de superficie (C = 30, umbral 0,20) → **0,783**. Las dos son **significativamente peores que las reglas**.
- **Como ayudante (híbrido reglas + TF-IDF):** las reglas deciden los casos claros (grupo «seguro_si»: articulado con verbo) y el modelo solo la **zona gris** → **0,839**, recall de 0,875 a 0,906. No significativo.

### 5.4 Parser LLM (B48, B53, B54, D22, D26)

**Qué modelo y por qué.** `claude-sonnet-5-5` por la API de Anthropic.
- No había LLM local disponible en el entorno (no estaba Ollama y Hugging Face estaba bloqueado por la red); la API de Anthropic sí era accesible.
- Sonnet es el equilibrio calidad/costo para leer texto jurídico largo y devolver JSON estructurado; Haiku sería unas 20 veces más barato y queda para comparar en el plan (comparar modelos es un experimento pendiente).

**Cómo se usa (`extractores/llm.py`):**
1. **Prefiltro sin LLM:** solo se mandan los segmentos del encabezado y del articulado que contienen una palabra que puede introducir una norma (ley, decreto, DNU, código, régimen, estatuto). Las notas y los anexos no van.
2. **Lotes** de hasta 12.000 caracteres, con el id de cada segmento (`[S12] Artículo 11`), para que el modelo diga de dónde sale cada relación. 590 pedidos para las 306 normas.
3. **Prompt:** definición de los 6 tipos con ejemplos de técnica legislativa argentina. Devuelve un **JSON** por relación: segmento, **cita textual exacta**, tipo/número/año del destino, artículo destino, tipo y verbo.
4. **Verificación de la cita (anti-alucinación):** la cita se busca **literal** en el texto. Si está, se guardan sus offsets (la relación queda trazable igual que en las reglas). Si no está, se descarta y se cuenta. **Alucinación: 8 citas de 7.688 (0,1 %)**.
5. **Normalización con el mismo catálogo que las reglas:** así la comparación mide solo la **lectura** del texto, no la normalización.
6. **Caché** por huella SHA-256 del pedido (modelo + versión del prompt + texto), **en el repositorio**: volver a correr no llama a la API y da exactamente lo mismo, sin clave y sin costo.
- **Temperatura:** la API de los modelos 5.5 ya no acepta el parámetro (B53); la reproducibilidad viene de la caché.
- **El LLM nunca ve el gold.**
- **Costo real:** USD 14 para todo el corpus.
- **Proyección a pares (D26):** se probaron 4 en dev y se eligió aplicar la **regla F a las relaciones del LLM**, con la misma restricción temporal.

**Resultado:** F1 **0,841**, **recall 0,938** (el más alto), precisión 0,763. Recupera 12 de los 24 pares que pierden las reglas (decretos sin verbo, CONSIDERANDO, nombres propios), pero agrega falsos positivos del VISTO. Su gran aporte es el **tipo de relación: macro-F1 ponderada 0,883** contra 0,672 de las reglas.

### 5.5 Híbridos

| Híbrido | Cómo combina | F1 test | Comentario |
|---|---|---|---|
| Reglas ∩ LLM | Par aceptado por los dos | **0,838** | **Única mejora significativa:** +1,0 [+0,2; +2,5]. Sube la precisión a 0,804 sin perder recall |
| Reglas ∪ LLM | Aceptado por cualquiera | 0,831 | Más recall, menos precisión |
| Reglas + TF-IDF | Reglas en lo claro, TF-IDF en la zona gris | 0,839 | +1,1, no significativo |
| **Cascada** (B55, D27) | Un solo parser: reglas filtran, LLM juzga | 0,829 | **El mejor en dev (0,758)**, recall 0,911, **un cuarto del costo** (USD 3,6) |

**El híbrido en cascada, paso a paso:**
1. Las **reglas v3** (mejor normalización) generan un **candidato por par**, con todas sus menciones.
2. Se separan en tres zonas: **DESCARTE** (menciones posteriores o solo en anexos/notas), **SEGURO** (articulado + verbo + sin procedencia; en dev el 91 % está en el gold), **GRIS** (el resto).
3. El LLM juzga solo SEGUROS (para ponerles tipo) y GRISES (para decidir), con la mención marcada entre ⟦ ⟧ y los fragmentos donde aparece. Devuelve probabilidad, tipo, artículo destino, cita y motivo.
4. **Decisión con la política «previa»:** en la zona gris, la regla F3 opina primero y el LLM la corrige solo con confianza: si F3 acepta, se descarta solo si el LLM da < 0,15; si F3 rechaza, se acepta solo si da ≥ 0,5.
5. Se verifica la cita; si no está, queda lo que decía la regla.

**Por qué así:** el LLM **no inventa destinos** (solo juzga normas que el texto nombra y el catálogo resolvió), responde una **pregunta cerrada** con la evidencia justa, cada decisión queda trazable (`candidatos.csv`) y lee unos 1.000 fragmentos en lugar de 306 normas. Las tasas de base (VISTO ~80 %, CONSIDERANDO ~25 %) van en el prompt porque sin ellas trataba el VISTO como simple antecedente. Un primer prompt estricto bajaba el F1 a 0,52: aceptaba 64 de 544 grises.

**Por qué no gana más en test:** en el VISTO el LLM no es más preciso que la regla. Separar la norma que se reglamenta de la que solo se cita depende de un criterio que InfoLEG no publica.

---

## 6. Cómo evaluamos

**Principios del protocolo:**
1. **El gold nunca es entrada de un extractor (D7).** Solo lo leen los scripts de evaluación y, para entrenar, los modelos supervisados sobre dev.
2. **Todo se diseña sobre dev**; cada versión congelada se evalúa en test **una sola vez** (B16).
3. **Todos los métodos sobre los mismos 192 pares**, con la misma proyección y la misma restricción temporal (`17_comparar_metodos.py`).
4. **Cada error explicado caso por caso** (`18_explicar_errores.py`).
5. **Todo reproducible** con scripts y caché.

**Métricas:**

| Qué | Métrica |
|---|---|
| Extracción | P, R, F1 a nivel de par dirigido (origen, destino) contra el gold |
| Detección | % de pares del gold cuyo destino se detecta en el texto |
| Normalización | Exactitud de vinculación (verificable con la fecha del texto, y estimada) y % no resuelto (separando fuera del corpus) |
| Tipo | Matriz de confusión, F1 por tipo y macro-F1 sobre **78 casos** revisados a mano (13 por tipo), también **ponderada** por la frecuencia real de cada tipo |
| Incertidumbre | **IC 95 % por bootstrap pareado, remuestreando normas de origen** (43 normas, 2.000 réplicas, semilla fija). Significativo si el intervalo no contiene 0 |
| Grafo | **Ida y vuelta** (lo que se lee de Neo4j = lo que se cargó) y F1 leyendo desde el grafo |
| Consolidado | Similitud por artículo (difflib sobre texto normalizado) contra el texto actualizado de InfoLEG |

**¿Por qué bootstrap por norma y no por par?** Los pares de una misma norma no son independientes (si una norma está mal leída, fallan todos sus pares). Remuestrear pares subestimaría la varianza.

**¿Por qué ponderar la macro-F1 de tipos?** La muestra está estratificada (13 por tipo) pero en la población CITA es mucho más frecuente que REGLAMENTA. Sin ponderar, cada tipo pesa igual aunque en la realidad no.

**Verificación del software:** 19 tests automáticos sin red (detección, catálogo, zonas, reglas, tipos, ida y vuelta del grafo, LLM con respuestas simuladas, TF-IDF, v3, híbrido, adaptador del digesto); corpus regenerado idéntico byte a byte; textos por SHA-256; catálogo y muestra del digesto con `--verificar`.

---

## 7. Resultados (PI1 y PI2)

**Tabla 1. F1 en test con IC 95 % y diferencia con las reglas v2.**

| Método | P | R | F1 dev | F1 test [IC 95 %] | Δ con reglas v2 |
|---|---|---|---|---|---|
| Reglas v1 | 0,732 | 0,854 | 0,652 | 0,788 | — |
| **Reglas v2 (referencia)** | 0,785 | 0,875 | 0,733 | **0,828** [0,783; 0,875] | — |
| Reglas v3 | 0,779 | 0,880 | 0,750 | 0,826 | −0,1 [−1,9; +1,3] |
| Random forest | 0,799 | 0,849 | 0,728 (CV) | 0,823 | −0,4 [−3,5; +2,5] |
| TF-IDF (contexto) | 0,697 | 0,839 | — | 0,761 | **−6,6** [−13,6; −1,5] |
| TF-IDF + superficie | 0,760 | 0,807 | 0,751 (CV) | 0,783 | **−4,5** [−8,6; −0,7] |
| Reglas + TF-IDF | 0,780 | 0,906 | 0,749 (CV) | 0,839 | +1,1 [−2,2; +4,0] |
| **LLM** | 0,763 | **0,938** | 0,741 | **0,841** | +1,3 [−1,9; +4,0] |
| Reglas ∪ LLM | 0,747 | 0,938 | — | 0,831 | +0,4 [−2,7; +3,0] |
| **Reglas ∩ LLM** | **0,804** | 0,875 | 0,735 | 0,838 | **+1,0 [+0,2; +2,5]** |
| Cascada | 0,761 | 0,911 | **0,758** | 0,829 | +0,2 [−3,4; +3,2] |

**Cómo leerla:**
- **Todo queda entre 0,76 y 0,84.** Las reglas bien diseñadas ya son competitivas.
- **Diferencias significativas, solo tres:** los dos TF-IDF solos son **peores** y la intersección reglas ∩ LLM es **mejor** (+1 punto, por precisión).
- **El LLM tiene el mayor recall** (0,938) y es el mejor en el **tipo** de relación.
- **La cascada** es la mejor en dev, empata en test y cuesta un cuarto.
- **Generalización:** sobre los 65 pares de test nunca vistos en el corpus v1, la v1 da 0,563 y la v2 0,671 (las reglas generalizan peor a lo nuevo).

**Respuesta a la PI1:** reglas, modelos y LLM llegan a 0,76–0,84; las reglas empatan con un modelo entrenado, y el LLM aporta en recall y sobre todo en tipo. **Respuesta a la PI2:** el híbrido mejora, pero poco: la intersección es la única mejora significativa; la cascada logra lo mismo más barato y en el digesto es la mejor.

---

## 8. Por qué se dieron esos resultados (análisis)

### 8.1 Dónde se pierden los pares (subtareas, B45)

- **Detección:** 99,6 % de los destinos nombrados en dev, 100 % en test.
- **Normalización:** exactitud estimada 99,1 % (99,4 % en test). El 48 % de las menciones nombra normas fuera del corpus (mundo cerrado).
- **Extracción:** condicionado a ser candidato, recall 0,908 y precisión 0,785 en test.
- **Los 24 pares de test que se pierden:** 16 los descarta la regla, 7 no nombran a su destino, 1 no se normaliza.

**Conclusión:** mejorar el detector o el catálogo no mueve el F1. Lo confirma la v3, que arregla la normalización y empata. **El cuello de botella es decidir si una cita es un vínculo.** Sin evaluar por subtarea, el siguiente paso habría sido seguir puliendo un detector que ya estaba en 99,6 %.

### 8.2 Errores de test, caso por caso (reglas v2: 46 FP y 24 FN)

| Categoría de la consigna | Causas | FP | FN |
|---|---|---|---|
| Relación inexistente | Cita del VISTO (24), remisión desde una ley (14), verbo que no actúa (3), procedencia (1), error del texto (1) | 43 | — |
| Mal normalizada / ambigua | Otro decreto con el mismo número (1), decreto sin año resuelto por mundo cerrado (2) | 3 | — |
| No detectada como vínculo | CONSIDERANDO + decreto sin verbo (6), decreto sin verbo en el articulado (4), solo CONSIDERANDO (3), solo nombre propio (2), solo procedencia (1) | — | 16 |
| Destino no nombrado | Texto ordenado implícito (5), no verificable (2) | — | 7 |
| Mal normalizada | Año escrito como fecha (1) | — | 1 |
| Relación invertida | No se observó: la dirección sale de qué norma contiene el texto | 0 | 0 |

### 8.3 Formulaciones que más errores producen (PI3)

1. **Citas del VISTO que solo mencionan la norma:** 52 % de los falsos positivos de test. **El VISTO es a la vez la mejor señal (80 % de acierto en dev) y la principal fuente de error.** InfoLEG registra algunas citas del VISTO y otras no, sin un criterio que se lea en el texto.
2. **Remisiones desde leyes** («las contribuciones previstas en la Ley 23.660»): parecen modificaciones y no lo son.
3. **Decretos que aplican una ley sin verbo** o solo la nombran en el CONSIDERANDO: InfoLEG los registra como «complementa».
4. **Vínculos que el texto no nombra:** textos ordenados implícitos, derogaciones genéricas, modificatorias de la citada (80 pares entre dev y test).
5. **El año escrito como fecha** («Decreto 467 del 14 de abril de 1988») y los decretos sin año, en la normalización: dejaba ambiguas 360 de 580 menciones y vinculaba mal 31. La v3 lo corrige (vinculaciones erróneas verificables: 31 → 0).

### 8.4 Por qué métodos tan distintos dan lo mismo

**El techo no está en el método sino en la tarea:**
- una parte del gold no se puede encontrar leyendo el texto (19 % de dev);
- el criterio de InfoLEG para el VISTO no es legible en el texto;
- el gold mide un vínculo amplio y tiene ruido (3 de 30 FP revisados eran relaciones reales que InfoLEG no registró).

### 8.5 Tipo de relación (78 casos, B47)

| Método | Macro-F1 ponderada | Exactitud ponderada |
|---|---|---|
| Reglas v2 (tipo por verbo) | 0,672 | 0,754 |
| Reglas v3 | 0,703 | 0,755 |
| **LLM** | **0,883** | **0,849** |
| Cascada | 0,763 | 0,646 |

- **Error dominante de las reglas: una cita tomada como acción** (21 de 25 errores): nominalizaciones («la derogación del artículo 2°» → DEROGA) y verbos que no actúan («deberá proponer la reglamentación» → REGLAMENTA). MODIFICA: solo 4 de 13 bien.
- **El LLM lee la oración** y distingue cita de acción.
- **La cascada** baja la exactitud porque, cuando acepta un par por el VISTO, le pone MODIFICA («complementa») y en la revisión eran CITA.

### 8.6 ¿Los modelos empatan por pocos datos? Curva de aprendizaje (B68)

Se entrenaron el random forest y los TF-IDF con el 10 %, 20 %, 30 %, 50 %, 70 % y 100 % de las normas de origen de dev, con la misma validación cruzada agrupada y 5 sorteos por fracción, hiperparámetros fijos y **sin usar test**.

| Modelo | 61 pares | 316 pares | 641 (todo dev) | F1 en entrenamiento |
|---|---|---|---|---|
| Random forest | 0,727 | 0,774 | 0,814 | 0,936 |
| TF-IDF + atributos | 0,735 | 0,809 | 0,831 | 0,986 |
| TF-IDF solo | 0,731 | 0,782 | 0,800 | 0,992 |
| Regla F (no aprende) | 0,812 | 0,812 | 0,812 | — |

- **Las curvas no se aplanan:** ganan ~**2 puntos de F1 cada vez que se duplican los datos** y recién con todo dev alcanzan a las reglas.
- **Alta varianza / memorizan:** brecha entrenamiento–validación de 0,12 a 0,19 (ej.: «bs as»).
- **Las etiquetas no explican el empate:** solo 5 posibles omisiones del gold en dev.
- **Conclusión honesta:** con 801 pares, la limitación medible es la **cantidad de datos**; no está probado que la representación alcance (con más datos podrían aplanarse antes de superar a las reglas). Usamos ~1,5 % de las normas modificatorias que InfoLEG permite etiquetar.

**¿Qué conclusiones dependen del tamaño del corpus?**
- **Sí:** el empate de los modelos supervisados y la baja potencia del test (±4,5 puntos).
- **No:** el techo de las reglas y del LLM (no aprenden del corpus) y el diagnóstico de que se pierde al decidir y no al detectar.

### 8.7 Comparación con la literatura

- **Sargeant et al. (Reino Unido, sentencias):** reglas 35 %, GPT-4.1 77 %, encoders 93 %. Nuestras reglas llegan a 0,83 y el LLM no queda abajo. Diferencias: la **tarea** (decidir un vínculo entre normas de un catálogo, no detectar cualquier cita) y el **estilo** (la técnica legislativa argentina es muy regular).
- **Colombo et al. (Italia):** grafo de la legislación en Neo4j, pero las modificaciones vienen **marcadas** (Akoma Ntoso). Nosotros las extraemos del texto libre: el costo es justamente el F1 de 0,83.
- **Cardellino et al. (InfoLEG):** detección de entidades (normas) con regex + clasificador, sin extraer ni evaluar relaciones.
- **Bendahman et al. (EUR-Lex):** modelos afinados 0,80, LLM sin entrenar 0,27–0,47 en triples.
- **Prior et al. (consolidación con LLM):** la coincidencia exacta cae al 20,5 % en cadenas largas → la consolidación con LLM necesita verificación (por eso la nuestra verifica literal).

---

## 9. El grafo (PI5)

**Modelo:**
```
(:Norma)-[:CONTIENE]->(:Articulo)
(:Articulo)-[:SUSTITUYE|INCORPORA|DEROGA|REGLAMENTA|MODIFICA|CITA {fuente, verbo, metodo, confianza, parte_origen, inicio, fin, fragmento}]->(:Articulo | :Norma)
```

**Decisiones (B38 → B42, D17):**
- **El origen siempre es un artículo**; el VISTO y el CONSIDERANDO salen del encabezado (artículo 0).
- **El destino es un artículo** si el texto dice cuál («Sustitúyese el artículo 245…»), y la **norma entera** si no.
- **La relación es una arista tipada, no un nodo:** «¿qué derogó la Ley 27.802?» se escribe directo con `[:DEROGA]`.
- **Cada arista lleva su evidencia** (fragmento y offsets) y su **procedencia** (`fuente`, `metodo`, `verbo`, `confianza`).
- **Varias fuentes conviven sin pisarse:** cada parser tiene sus aristas sobre los mismos nodos; se comparan dos lecturas del mismo artículo con una consulta. Carga con `MERGE` por fuente, idempotente, **sin `--borrar`**.
- **InfoLEG no está en el grafo:** el grafo es solo lo que extrajeron los parsers; InfoLEG se usa para medirlo. (El primer modelo, B38, tenía aristas «hay vínculo» por parser y el gold adentro; servía para comparar pero no respondía qué hace una norma sobre otra.)
- **Por qué Neo4j:** grafo de propiedades (aristas con atributos, ideal para la evidencia), Cypher legible, índice de texto completo y es el mismo enfoque del grafo italiano de la literatura. Contenedor propio (7475/7688) para no pisar otra base de la Mac.

**Qué hay cargado hoy:** 444 normas (340 de InfoLEG + 104 del digesto) y 8.545 artículos. Siete fuentes de InfoLEG: cuatro extractores (`reglas_v2` 3.277 aristas, `reglas_v3` 3.149, `llm` 3.247, `hibrido` 3.147) y tres clasificadores (`random_forest` 3.283, `tfidf` 3.280, `hibrido_tfidf` 3.273, B73), más tres del digesto (`unnoba_*`).

**Los clasificadores en el grafo (B73):** como solo dicen sí/no por par, su grafo usa la evidencia de las menciones del detector; par aceptado → conserva el tipo de la regla (o MODIFICA si todas eran CITA); rechazado → todo CITA; la arista lleva la probabilidad del modelo. Cubren el corpus entero (los 1.091 candidatos son todos los pares que el detector encuentra en las 306 normas).

**Verificación del grafo:** ida y vuelta **idéntica** en las 7 fuentes; F1 leído desde Neo4j = F1 de los CSV (reglas v2: 0,828).

---

## 10. Transferencia al digesto de la UNNOBA (PI4, preliminar)

- **Corpus:** 912 PDF distintos, bajados **a mano** (el robots.txt prohíbe el acceso automático, B56). Muestra estratificada de **70 documentos** con semilla fija (7 ordenanzas, 48 de reglamentos, 15 al azar), 38 con OCR.
- **Gold:** anotado por Claude en tres clases (MOD, APLICA, CITA), dos revisiones; **109 pares**, 61 de vínculo (MOD ∪ APLICA). **Falta validación humana y segundo anotador.**
- **Qué se cambió:** **solo el adaptador** (`fuentes/unnoba.py`). Ninguna regla, umbral ni código de los extractores.

| Método | P | R | F1 |
|---|---|---|---|
| Reglas | 0,932 | 0,902 | 0,917 |
| LLM, prompt de InfoLEG | 0,889 | 0,262 | **0,405** |
| LLM, prompt con vocabulario del digesto | 0,895 | 0,836 | 0,864 |
| **Híbrido, prompt de InfoLEG** | **0,983** | **0,934** | **0,958** |

- **La detección se transfiere casi perfecta:** F1 0,986 sobre los 109 pares.
- **El híbrido es el mejor**, pero no significativamente con 70 documentos.
- **La lección:** el prompt de InfoLEG solo habla de leyes y decretos, y el LLM **ignoraba las resoluciones**. Con **tres frases** nuevas sube **46 puntos**. Los verbos también dependen de la fuente («ratificar», «dejar sin efecto» no estaban en el léxico).
- **Conclusión:** la transferencia funciona **si el vocabulario de la fuente es parte del adaptador** (D28).

---

## 11. Reconstrucción del texto vigente de la LCT (PI5, preliminar, B60–B61)

**Idea:** si el grafo tiene información suficiente, debería alcanzar para armar el texto vigente de una ley. Es la prueba más fuerte de que la trazabilidad (artículo destino + evidencia) aporta algo que una tabla de pares no tiene.

**Qué ley:** la de más profundidad. Con la fuente del híbrido, la LCT tiene **105 normas modificatorias, 107 artículos afectados** y una cadena de **16 saltos** (ranking de B61, que cuenta cualquier arista que no sea CITA). La siguen la Ley 24.013 (81 normas) y la 24.241 (62).

**Pasos:**
1. **Manifiesto desde Neo4j:** 943 relaciones de 107 normas (sumando 4 fuentes).
2. **Texto base:** no el original de 1974 sino el **t.o. del Decreto 390/76**, porque desde 1976 todas las modificaciones citan esa numeración (la indemnización es el art. 245 del t.o.).
3. **Operaciones:** el LLM lee cada artículo modificatorio (235 de 100 normas) con las pistas del grafo y devuelve operación y texto nuevo **literal**. 73 no hacen cambios textuales (son «complementa»). 172 operaciones: 120 SUSTITUYE, 23 MODIFICA_PARCIAL, 16 INCORPORA, 13 DEROGA; **168 verificadas**.
4. **Aplicación en orden cronológico:** SUSTITUYE/INCORPORA/DEROGA sin LLM; los cambios parciales los reescribe el LLM y se aceptan solo si ≥ 90 % de los 4-gramas está en el texto anterior o en la modificatoria. 8 operaciones no se aplicaron, cada una con motivo.
5. **Comparación** artículo por artículo con el texto actualizado de InfoLEG (solo para medir).

**Resultados:**
- **281 de 293 artículos (95,9 %)** idénticos, casi idénticos o derogados en los dos.
- De los **103 artículos que cambian**, coinciden **94 (91 %)**.
- Cadenas largas bien: el **art. 245** pasa por las Leyes 23.697, 24.013, 25.877, el DNU 70/2023 y la Ley 27.802; el **art. 92 bis** tiene seis versiones.
- **6 errores reales, ninguno de la consolidación:** 4 artículos porque **ningún parser vinculó la Ley 24.522 con la LCT** (recall del grafo); 1 sustitución descartada por la **verificación literal** (art. 2); 1 **derogación de una norma modificatoria** que el método no modela (art. 147).
- Costo: USD 2,4.

**Límites:** no es texto oficial; no modela vigencias diferidas, suspensiones judiciales (el capítulo laboral del DNU 70/2023), vetos ni derogaciones de modificatorias.

---

## 12. Cifras clave para memorizar

| Qué | Cifra |
|---|---|
| Corpus | 340 normas, 306 con texto, 775 pares (583 dev / 192 test), 43 normas de origen en test |
| Catálogo | 430.834 normas |
| Dataset | 8.066 segmentos, 1.091 pares candidatos |
| Techo textual | destino nombrado en 81 % (dev) y 96 % (test) |
| VISTO vs CONSIDERANDO | 80 % vs 24 % en el gold (dev) |
| Reglas v2 | F1 0,828 (P 0,785, R 0,875) |
| Random forest | 0,823 |
| TF-IDF solo / + superficie / híbrido | 0,761 / 0,783 / 0,839 |
| LLM | 0,841 (R 0,938), tipo 0,883 |
| Reglas ∩ LLM | 0,838, **+1,0 [+0,2; +2,5]** (única significativa) |
| Cascada | dev 0,758 (la mejor), test 0,829, USD 3,6 |
| Detección / normalización | 99,6 % / 99,1 % |
| Pares de test perdidos | 24: 16 regla, 7 sin mención, 1 normalización |
| Errores de test | 46 FP (24 del VISTO) y 24 FN |
| Tipo, reglas | macro-F1 ponderada 0,672; 21 de 25 errores = cita tomada como acción |
| Alucinación LLM | 0,1 % (8 citas) |
| Costos | LLM USD 14 · cascada USD 3,6 · consolidado USD 2,4 |
| Curva de aprendizaje | +2 puntos por duplicar datos; F1 entrenamiento 0,94–0,99 |
| IC de test | ±4,5 puntos |
| PI4 | híbrido 0,958 · reglas 0,917 · LLM 0,405 → 0,864 con vocabulario |
| Consolidado | 95,9 % de los artículos; 91 % de los que cambian; 6 errores reales |
| Grafo | 444 normas, 8.545 artículos, 7 fuentes InfoLEG + 3 digesto |
| Tests | 19 de 19 |

---

## 13. Preguntas probables y cómo contestarlas

**Sobre el planteo**

**1. ¿Por qué no usaron directamente las bases de InfoLEG para armar el grafo?**
Porque el objetivo es extraer relaciones del **texto**, para poder usarlo donde no hay bases estructuradas (como el digesto). InfoLEG nos da un experimento controlado: lo ocultamos y lo usamos solo para medir. Si lo usáramos como entrada, no estaríamos evaluando nada.

**2. ¿El gold de InfoLEG es «la verdad»?**
No. Es lo que el Ministerio registró, y mide un vínculo amplio («modifica o complementa»: incluye remisiones y reglamentaciones). Tiene ruido: en 3 de 30 FP revisados, el vínculo era real y no estaba registrado. Medir contra él premia imitar su criterio editorial (por ejemplo, qué citas del VISTO registra). Es una amenaza a la validez de constructo que declaramos.

**3. ¿Por qué evalúan «modifica o complementa» y no «modifica» a secas?**
Porque es lo que mide el gold. Exigir un verbo modificatorio bajaba el F1 de dev de 0,716 a 0,556, porque el gold tiene remisiones y reglamentaciones. Los tipos finos se evalúan aparte, sobre 78 casos revisados.

**Sobre los datos**

**4. ¿Por qué derecho laboral y por qué tan pocas normas?**
Laboral porque tiene cadenas largas (la LCT es la ley más modificada) y la reforma de 2026. El tamaño: con un salto de expansión son 340 normas; con dos, 4.115 y 12.380 pares, imposible revisar errores a mano, que la consigna exige. La consigna permite un subconjunto acotado en la cursada. Para entrenar resultó chico y lo medimos.

**5. ¿Por qué un split temporal y no aleatorio?**
Para simular normas nuevas y dejar en test las reformas recientes. Un split aleatorio mezclaría normas de la misma época y estilo, y sobreestimaría.

**6. ¿No hay fuga si una norma modificada está en dev y su modificatoria en test?**
No: el extractor nunca ve el gold, y la modificada solo aparece como destino a normalizar.

**7. ¿Qué es el mundo cerrado y no les infla los resultados?**
Solo se vincula un destino que está en el corpus. El gold también está limitado al corpus, así que se mide sobre el mismo universo. El costo es que el 48 % de las menciones (normas reales afuera) no se enlaza; contra la base completa, la regla acierta el 62 % de las veces en test.

**Sobre los métodos**

**8. ¿Por qué esos modelos (random forest y TF-IDF)?**
El random forest es el estándar más fuerte para pocos datos tabulares; lo elegimos comparando tres con validación cruzada agrupada. El TF-IDF es el modelo más simple que lee el texto, que es lo que pide la consigna, y es interpretable. Un BERT necesita más datos y GPU: es trabajo futuro.

**9. ¿Para qué sirven si empatan con las reglas?**
Responden la PI1 del lado del aprendizaje y muestran algo importante: el empate se explica por falta de datos (curva de aprendizaje), no porque aprender no sirva. El TF-IDF probó el híbrido que recomienda la consigna (reglas detectan, modelo decide la zona gris). Y ahora también tienen su grafo en Neo4j.

**10. ¿Qué diferencia hay entre un clasificador y un extractor?**
El extractor (reglas, LLM) produce la relación completa: artículo de origen, destino, tipo y evidencia. El clasificador decide si un par candidato es una relación. En el pipeline trabaja en el paso de decisión; su grafo usa las menciones del detector como evidencia.

**11. ¿Por qué Claude y por qué Sonnet?**
No había LLM local disponible (sin Ollama, Hugging Face bloqueado), y la API de Anthropic sí. Sonnet equilibra calidad y costo para leer texto jurídico largo y devolver JSON. Comparar con Haiku y un modelo abierto está en el plan.

**12. ¿Cómo evitan que el LLM invente relaciones?**
Tiene que devolver la **cita textual**, y la buscamos literal en el texto: si no está, se descarta. Alucinación del 0,1 %. Además normaliza con el mismo catálogo que las reglas, y en la cascada solo juzga normas que el texto nombra.

**13. ¿Cómo garantizan reproducibilidad si el LLM no es determinista?**
Cada respuesta se guarda en una caché indexada por la huella SHA-256 del pedido, y la caché está en el repo: volver a correr da lo mismo, sin clave y sin costo. Lo que no es reproducible (una corrida nueva sin caché) está documentado.

**14. ¿Por qué no fijaron temperatura 0?**
La API de los modelos 5.5 ya no acepta el parámetro. La reproducibilidad viene de la caché.

**15. ¿Qué es el híbrido en cascada y por qué no ganó?**
Las reglas detectan, normalizan y separan en zonas; el LLM juzga solo la zona gris y pone el tipo en la segura. Es el mejor en dev y cuesta un cuarto. En test empata porque en el VISTO el LLM no es más preciso que la regla: el criterio de InfoLEG no está en el texto.

**16. ¿Por qué la intersección es la única mejora significativa?**
Porque sube la precisión (0,785 → 0,804) sin perder recall: el LLM filtra falsos positivos de las reglas y las reglas filtran los del LLM. Es +1 punto con IC [+0,2; +2,5]. Con 11 comparaciones sobre el mismo test, igual hay que confirmarlo en otra muestra.

**Sobre la evaluación**

**17. ¿Por qué bootstrap por norma?**
Los pares de una norma no son independientes. Remuestrear normas da intervalos honestos.

**18. ¿Cómo saben que no sobreajustaron al test?**
Todo se diseñó en dev; cada versión congelada se evaluó en test una sola vez. La v3 y la cascada se diseñaron después de ver errores de test de la v2: por eso son experimentos y la v2 es la referencia.

**19. ¿Por qué evaluar por subtareas?**
Porque cambió dónde pusimos el esfuerzo: la detección ya estaba en 99,6 % y la normalización en 99,1 %; todo se pierde al decidir. Sin eso, habríamos seguido puliendo el detector.

**20. ¿Quién anotó los 78 tipos y el gold del digesto?**
Claude, con revisión documentada. Es la limitación más importante: no hay validación humana ni kappa. Está primera en el plan.

**Sobre los resultados**

**21. ¿Por qué el VISTO es problemático?**
Es la mejor señal (80 % de acierto en dev) y la principal fuente de error (52 % de los FP de test). El VISTO lista antecedentes: InfoLEG registra algunos y otros no, sin un criterio legible en el texto.

**22. ¿Hubo relaciones invertidas?**
No: la dirección sale de qué norma contiene el texto (la que habla es la de origen).

**23. ¿Las conclusiones se deben a que el corpus es chico?**
En parte. El empate de los modelos supervisados y la poca potencia estadística, sí. El techo de las reglas y el LLM, no (no aprenden del corpus). Tampoco el diagnóstico de dónde se pierde.

**24. ¿Qué harían para mejorar?**
Ampliar el corpus y repetir la curva; validación humana y kappa; muestra independiente del gold; tratar el VISTO como señal graduada; reglas v4 diseñadas en dev; comparar modelos de lenguaje; text-to-Cypher.

**Sobre el grafo y la reconstrucción**

**25. ¿Por qué el artículo es nodo y la relación arista?**
Porque las modificaciones operan sobre artículos y así una pregunta como «quién cambió el art. 245» es un patrón directo. La relación como arista tipada simplifica Cypher; la evidencia va en sus propiedades.

**26. ¿Cómo comprobaron que el grafo está bien cargado?**
Ida y vuelta: leemos de Neo4j y debe ser exactamente lo cargado (idéntico en las 7 fuentes). Y repetimos la evaluación contra InfoLEG leyendo desde Neo4j: da el mismo F1.

**27. ¿Por qué la reconstrucción de la LCT usa el Decreto 390/76?**
Porque desde 1976 todas las modificaciones citan la numeración del texto ordenado. El texto de 1974 tiene otra numeración.

**28. ¿Los errores del consolidado son del grafo o de la consolidación?**
De los 6 reales, 4 son recall del grafo (la Ley 24.522 no se vinculó), 1 la verificación literal y 1 una derogación de una modificatoria que no modelamos. La consolidación no agrega errores donde el grafo está completo.

**29. ¿El consolidado sirve como texto oficial?**
No: no modela vigencias diferidas, suspensiones judiciales ni vetos. Sirve para mostrar que el grafo tiene información suficiente y medir cuánto se pierde en cada paso.

**30. ¿Por qué con el digesto el LLM daba 0,405?**
Su prompt hablaba solo de leyes y decretos y no consideraba resoluciones ni ordenanzas. Con tres frases de vocabulario subió a 0,864. Por eso concluimos que el vocabulario de la fuente es parte del adaptador.

---

## 14. Limitaciones que conviene decir antes de que las pregunten

1. El gold mide un vínculo amplio y tiene ruido.
2. Test chico: 192 pares, 43 normas, IC de ±4,5 puntos.
3. Las anotaciones manuales y el gold del digesto los hizo Claude: falta validación humana y kappa.
4. Mundo cerrado: 48 % de las menciones fuera del corpus.
5. Un dominio, dos tipos de norma.
6. El LLM es un servicio externo (la caché fija los resultados, no el futuro).
7. La v3 y la cascada se diseñaron después de ver test: son experimentos.
8. La PI4 es chica (70 documentos, OCR no reproducible byte a byte).
9. El consolidado no es texto oficial.
10. **Sesgo de selección:** el corpus sale de expandir el propio gold, así que solo tiene normas que InfoLEG ya vinculó. La muestra independiente está en el plan.
11. **Muchas comparaciones** sobre el mismo test: la mejora de la intersección hay que confirmarla.

---

## 15. Glosario rápido

- **Gold standard:** las relaciones de referencia contra las que se mide (bases complementarias de InfoLEG).
- **Par dirigido:** (norma origen, norma destino); la unidad de evaluación.
- **VISTO / CONSIDERANDO:** partes del encabezado de una norma: antecedentes normativos / fundamentos.
- **Articulado:** la parte dispositiva, los artículos.
- **Cita de procedencia:** mención que indica de dónde viene un texto («t.o. por Decreto 390/76»), no una modificación.
- **Texto ordenado (t.o.):** versión reordenada de una ley con sus modificaciones; cambia la numeración.
- **Mundo cerrado:** solo se vincula lo que está en el corpus.
- **Regla F:** la regla de decisión de las reglas v2 (sec. 5.1).
- **Zona gris:** candidatos donde la regla duda; ahí decide el modelo en los híbridos.
- **Bootstrap pareado:** remuestrear normas de test con reemplazo y recalcular la diferencia entre dos métodos sobre las mismas muestras.
- **Macro-F1 ponderada:** promedio de F1 por tipo, ponderado por la frecuencia de cada tipo en la población.
- **Ida y vuelta:** cargar el grafo y leerlo de vuelta para verificar que no cambió nada.
- **Caché por huella:** guardar la respuesta del LLM con una clave SHA-256 del pedido exacto.
- **Consolidación:** aplicar las modificaciones a una ley para obtener su texto vigente.
