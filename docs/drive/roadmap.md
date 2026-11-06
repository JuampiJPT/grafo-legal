<!-- Copia del documento "Roadmap TP Integrador — Grafo normativo trazable" (https://claude.ai/artifact/Aai3uXH2hrR92fLDmYpvfM, revisión 10). La versión editable es esa; el diagrama de fases embebido solo se ve allí. -->

# Roadmap TP Integrador — Grafo normativo trazable

27/10/2026 · Juan Pedro Tagliaferro

## Propósito

Este roadmap ordena el TP en 8 fases; cada fase produce código, un entregable documental y una sección del informe final en formato LNCS. La regla es simple: ninguna fase se cierra sin su registro escrito, para que la defensa se apoye en decisiones justificadas y no en recuerdos.

El objetivo propio del equipo (grafo en Neo4j consultable con text-to-Cypher) se ubica en las fases 6 y 7, después de que el núcleo evaluable del enunciado (extracción, normalización, evaluación contra InfoLEG) tenga resultados.

## El artículo de Neo4j: qué sirve y qué no

El artículo de Bratanič y Çelik ([Neo4j, 2025](https://neo4j.com/blog/developer/from-legal-documents-to-knowledge-graphs/)) es útil como referencia de arquitectura, pero resuelve un problema distinto al nuestro. Su pipeline parsea contratos en PDF, clasifica el tipo de contrato con un LLM, extrae atributos con un esquema Pydantic y los carga en Neo4j con `MERGE`.

**Qué tomar:**

- La idea de **extracción guiada por esquema**: definir con Pydantic la salida exacta que debe devolver el LLM (norma destino, tipo de relación, fragmento). Es directamente aplicable a nuestro enfoque basado en modelos.
- La **clasificación previa** para elegir qué extraer, análoga a nuestro híbrido: reglas detectan candidatos, el modelo decide.
- El patrón de carga idempotente con `MERGE` en Cypher.
- El argumento de por qué un grafo supera a la búsqueda vectorial en consultas multi-salto: sirve como motivación para la PI5.

**Qué no cubre y nosotros sí debemos hacer:**

- **No evalúa nada.** No hay gold standard, precision, recall ni análisis de errores; en nuestro TP eso es el núcleo.
- **Extrae entidades dentro de un documento** (partes, fechas, ubicaciones), no **relaciones entre documentos**. Nuestro problema central, la normalización de "Ley 24.240" a un identificador único del corpus, no aparece.
- **No guarda trazabilidad**: el grafo final no conserva el fragmento ni la ubicación que sustenta cada dato.
- Depende de servicios pagos (LlamaParse, LlamaExtract, OpenAI). InfoLEG ya ofrece texto en HTML, así que no necesitamos OCR.

Conclusión: se cita en el estado del arte como ejemplo de construcción de grafos jurídicos con LLM, y se toma su patrón de extracción por esquema, pero el diseño experimental lo marca el enunciado.

## Estructura del informe (LNCS)

El informe final sigue la plantilla LNCS de Springer y cada sección se alimenta de una o más fases. Escribir la sección al cerrar su fase evita reconstruir todo al final.

| Sección del paper | Contenido | Se escribe en |
|---|---|---|
| Abstract (70–150 palabras) | Problema, enfoque, resultado principal con su número | Al final |
| 1. Introducción | Contexto, problemática, objetivos, PI1–PI5, contribuciones | Fase 0, se ajusta al final |
| 2. Trabajos relacionados | Legal Knowledge Graphs, EUR-Lex-Triples, Colombo et al. (2024), extracción con LLM, text-to-Cypher | Fase 0 |
| 3. Datos y corpus | Fuente, criterio de selección del subconjunto, estadísticas, gold standard, split | Fases 1 y 2 |
| 4. Metodología | Arquitectura modular, segmentación, detección, normalización, reglas, modelo, híbrido | Fases 2 a 5 |
| 5. Grafo y trazabilidad | Esquema Neo4j, propiedades de evidencia, consultas, text-to-Cypher | Fases 6 y 7 |
| 6. Diseño experimental | Métricas por subtarea, protocolo de evaluación, configuración | Fase 3, antes de medir |
| 7. Resultados | Tablas P/R/F1 por método y subtarea, normalización, text-to-Cypher | Fases 3 a 7 |
| 8. Análisis de errores | Taxonomía del enunciado con conteos y ejemplos reales | Fase 8 |
| 9. Discusión y limitaciones | Respuesta a PI1, primera aproximación a PI2, PI5, amenazas a la validez | Fase 8 |
| 10. Conclusiones y trabajo futuro | PI3, PI4 (digesto UNNOBA), ampliación del corpus | Fase 8 |
| Referencias | Formato LNCS numerado entre corchetes | Continuo |

## Fases del roadmap

Cada fase lista qué se hace, qué se documenta y su criterio de cierre. Un criterio de cierre es verificable: un archivo, un número o una decisión escrita.

*(Diagrama embebido en el original: 9 fases en 3 bloques.)* Los bloques A y B cubren el alcance mínimo de la cursada; el bloque C suma el objetivo propio del equipo (resaltado) y el cierre.

### F0 · Alcance y estado del arte

- **Hacer:** leer las referencias sugeridas (EUR-Lex-Triples, Colombo et al. 2024, dataset InfoLEG) y el artículo de Neo4j; fijar el tipo de relación a extraer ("modifica o complementa") y el tamaño objetivo del corpus.
- **Documentar:** una ficha de lectura por referencia (problema, datos, método, métricas, qué tomamos); documento de alcance con lo que entra y lo que queda para el final.
- **Cierre:** alcance escrito y aprobado por el equipo; borrador de Introducción y Trabajos relacionados.

### F1 · Corpus y gold standard

- **Hacer:** descargar la base InfoLEG y las bases de normas modificadas/modificatorias; definir el criterio del subconjunto (tema, período o tipo de norma); descargar los textos; armar los pares gold (modificatoria → modificada) restringidos al subconjunto; definir el split dev/test, idealmente temporal.
- **Documentar:** ficha del corpus (fuente, fecha de descarga, licencia CC BY 4.0, criterio, cantidad de normas y pares, distribución por tipo y año); cómo se construyó el gold y sus limitaciones (relaciones sin texto disponible, destinos fuera del corpus).
- **Cierre:** script que reproduce el corpus desde cero; **test congelado** (lista de IDs versionada, no se mira durante el desarrollo).

### F2 · Segmentación, detección y normalización

- **Hacer:** limpiar HTML, segmentar en artículos; detectar menciones ("Ley N° 24.240", "Decreto 1759/72", "la ley citada"); normalizar a un ID canónico (por ejemplo `ley-24240`) y vincularlo al corpus.
- **Documentar:** especificación del formato de ID; catálogo de variantes de escritura encontradas; casos no resueltos y por qué.
- **Cierre:** exactitud de vinculación y porcentaje de referencias no resueltas medidos en dev, sobre una muestra revisada a mano.

### F3 · Baseline basado en reglas y protocolo de evaluación

- **Hacer:** patrones regex para verbos de modificación ("Modifícase", "Sustitúyese", "Incorpórase", "Derógase"); evaluador automático que compara aristas extraídas contra el gold.
- **Documentar:** tabla de patrones (patrón, ejemplo real, relación que produce); protocolo de evaluación escrito **antes** de medir (unidad de evaluación, qué cuenta como acierto, tratamiento de duplicados).
- **Cierre:** P/R/F1 del baseline en test, reportado una sola vez.

### F4 · Enfoque basado en modelos

- **Hacer:** LLM con salida estructurada (esquema Pydantic: norma destino, tipo de relación, fragmento, confianza), zero-shot y few-shot; alternativa o complemento: clasificador BERT en español sobre pares (fragmento, mención).
- **Documentar:** modelo, versión, temperatura, prompt versionado, ejemplos few-shot, costo y tiempo por documento.
- **Cierre:** P/R/F1 sobre el mismo test que F3.

### F5 · Estrategia híbrida (primera aproximación a PI2)

- **Hacer:** las reglas proponen candidatos de alta cobertura; el modelo confirma, descarta o clasifica.
- **Documentar:** criterio de derivación al modelo; comparación de las tres estrategias en una tabla única.
- **Cierre:** tabla comparativa reglas vs. modelo vs. híbrido, con la diferencia explicada.

### F6 · Grafo en Neo4j con trazabilidad

- **Hacer:** cargar normas, artículos y aristas con propiedades de evidencia (fragmento, artículo, offsets, método, confianza); cargar el gold como relación separada (`GOLD_MODIFICA`) solo para evaluación.
- **Documentar:** diagrama del esquema; diccionario de propiedades; consultas Cypher de validación (aciertos, falsos positivos, falsos negativos).
- **Cierre:** las cifras de F3–F5 reproducidas con Cypher; toda arista navegable hasta su fragmento.

### F7 · Consulta en lenguaje natural (text-to-Cypher)

- **Hacer:** LLM que recibe el esquema y ejemplos pregunta→Cypher; usuario de solo lectura; validación con `EXPLAIN` antes de ejecutar.
- **Documentar:** banco de 30–50 preguntas con su Cypher y resultado esperado, separado en dev/test; prompt versionado.
- **Cierre:** *execution accuracy* medida en el banco de test; ejemplos de respuesta con evidencia textual para la PI5.

### F8 · Análisis de errores, informe y defensa

- **Hacer:** clasificar cada falso positivo y falso negativo con la taxonomía del enunciado (no detectada, mal normalizada, invertida, inexistente, tipo incorrecto, ambigua, destino ausente).
- **Documentar:** tabla de errores por categoría y método, con ejemplos reales; Discusión, Limitaciones y Conclusiones; abstract.
- **Cierre:** paper LNCS completo, demo funcionando y un ensayo de defensa cronometrado.

## Registro de decisiones y bitácora

En una defensa la pregunta más frecuente es "¿por qué hicieron esto así?". Cada decisión no obvia se registra en el momento con este formato breve (un ADR por decisión):

| ID | Decisión | Alternativas consideradas | Motivo | Fase |
|---|---|---|---|---|
| D01 | Extraer solo "modifica o complementa" en la cursada | Tipos específicos (deroga, sustituye, reglamenta) | Alcance mínimo del enunciado; tipos finos requieren anotación manual | F0 |
| D02 | Neo4j como base del grafo | NetworkX, RDF/SPARQL | Cypher, visualización y soporte para text-to-Cypher | F0 |
| D03 | | | | |

Además, una **bitácora semanal** de pocas líneas: qué se hizo, qué número cambió, qué falló. Sirve para reconstruir la evolución de los resultados y para la sección de limitaciones.

## Repositorio y reproducibilidad

El enunciado pide entregar corpus, procedimiento, conjunto de evaluación, métricas y evidencia, no solo el grafo. Una estructura de repositorio que refleje los módulos del pipeline lo hace visible:

```
tp-grafo-normativo/
  data/          raw/ (descargas), processed/, gold/, splits/
  src/           source_adapter/, segmentation/, detection/,
                 normalization/, extraction/ (rules, llm, hybrid),
                 graph/ (carga Neo4j), text2cypher/
  eval/          evaluador, banco de preguntas, resultados por corrida
  docs/          fichas de lectura, decisiones (ADR), bitácora
  paper/         informe LNCS
  notebooks/     exploración (no forma parte del pipeline)
```

- Cada corrida de evaluación guarda: commit, fecha, método, configuración y métricas en un archivo de resultados.
- Semillas fijas y versiones de librerías y modelos anotadas.
- Neo4j levantado con Docker Compose, para que cualquiera reproduzca el grafo con un comando.
- El adaptador de fuente aísla todo lo específico de InfoLEG, de modo que la PI4 (digesto universitario) solo requiera un adaptador nuevo.

## Preparación de la defensa

La defensa tiene que poder responder cada pregunta de investigación con un número o una evidencia concreta. Preguntas que conviene tener preparadas:

- ¿Cómo garantizan que el extractor no vio el gold? (respuesta: test congelado en F1 y protocolo escrito en F3)
- ¿Qué tan representativo es el subconjunto del corpus? (ficha del corpus)
- ¿En qué casos las reglas alcanzan y en cuáles el modelo aporta? (tabla F5 + errores F8)
- ¿Por qué un LLM y no un modelo entrenado, o al revés? (registro de decisiones)
- ¿Qué pasa con referencias implícitas como "la ley citada"? (catálogo F2)
- ¿Qué ventaja concreta da el grafo frente a una tabla de pares? (consultas multi-salto y evidencia, PI5)
- ¿Qué tan confiable es el text-to-Cypher? (accuracy F7 y casos fallidos)

Para la demo: una pregunta en lenguaje natural, el Cypher generado, el resultado en el grafo y el fragmento del artículo que sustenta la arista.
