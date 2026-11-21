---
title: "Extracción de relaciones entre normas y construcción de un grafo normativo trazable"
subtitle: "Informe de avance y bitácora de investigación — TP Integrador, Problemática III"
author: "Sistemas Inteligentes · Ingeniería en Informática · UNNOBA · Integrantes: [completar]"
date: "Noviembre de 2026"
lang: es
---

# Resumen

Este informe documenta el estado del Trabajo Práctico Integrador de la Problemática III al cierre de la cursada. El objetivo es reconstruir automáticamente, a partir del texto de las normas, las relaciones «modifica o complementa» que InfoLEG publica como datos estructurados, y representarlas en un grafo en el que cada arista conserva su evidencia textual.

Se armó un corpus reproducible del dominio laboral argentino: 340 normas, 306 con texto, y 775 pares del gold, separados en el tiempo en desarrollo (583 pares) y prueba (192 pares). Sobre él se compararon tres enfoques con el mismo protocolo:

- un parser de reglas (expresiones regulares y zonas del documento);
- modelos (un clasificador con atributos de superficie, un modelo TF-IDF y un parser con un modelo de lenguaje grande, LLM);
- estrategias híbridas.

En prueba, las reglas alcanzan F1 = 0,828, el LLM 0,841 y los híbridos entre 0,829 y 0,839. La única mejora estadísticamente significativa sobre las reglas es el híbrido por intersección: +1,0 punto, con un intervalo de confianza del 95 % de +0,2 a +2,5. El LLM mejora sobre todo el tipo de relación: macro-F1 de 0,672 a 0,883.

El análisis por subtareas muestra que la detección y la normalización casi no pierden pares. El límite está en decidir si una cita es un vínculo, en especial las citas del VISTO, y en los vínculos que el texto no nombra.

Además se adelantaron dos extensiones previstas para el examen final:

- **Transferencia (PI4).** El pipeline se aplicó a 70 documentos del digesto de la UNNOBA cambiando solo el adaptador. El híbrido alcanza F1 = 0,958.
- **Consolidación.** A partir del grafo se reconstruyó el texto vigente de la Ley de Contrato de Trabajo, que coincide con el de InfoLEG en el 95,9 % de los artículos.

**Palabras clave:** extracción de relaciones jurídicas · grafos de conocimiento normativo · InfoLEG · modelos de lenguaje · trazabilidad · Neo4j.

# 1. Introducción

## 1.1 Descripción del problema

Un cuerpo normativo es una red: las normas se modifican, sustituyen, derogan, reglamentan y citan entre sí. Para saber qué dice hoy una ley, o qué pasa si se deroga un decreto, hay que conocer esa red. En muchos repositorios los vínculos no están estructurados y solo se pueden inferir del lenguaje de las propias normas: «Sustitúyese el artículo 245 de la Ley N° 20.744 (t.o. 1976) por el siguiente…», «Derógase el Decreto N° 467/88», «VISTO la Ley N° 24.013…».

InfoLEG, la base de normativa nacional del Ministerio de Justicia, permite plantear un **experimento controlado**. Publica el texto de las normas y, por separado, bases complementarias de normas modificadas y modificatorias [1]. El sistema reconstruye las relaciones solo a partir del texto, y las bases estructuradas se usan únicamente como patrón de referencia (gold standard) para evaluar.

## 1.2 Relevancia

- **Práctica.** Un grafo de relaciones con evidencia permite responder preguntas que hoy exigen leer decenas de normas: qué artículos de la LCT cambió una ley, qué normas reglamenta un decreto, cuál es el texto vigente de un artículo.
- **Transferencia.** Muchos cuerpos normativos no tienen sus relaciones estructuradas, por ejemplo los digestos universitarios, municipales o provinciales. Un extractor validado sobre InfoLEG sería útil justamente donde no hay gold.
- **Investigación.** No conocemos un corpus en español rioplatense para extracción de relaciones entre normas evaluado contra un gold oficial. La literatura sobre grafos normativos parte de fuentes ya marcadas, como Akoma Ntoso en Italia [2, 3] o los triples anotados de EUR-Lex [4], y no del texto libre (sección 2).

## 1.3 Alcance y restricciones

- **Relación.** Se evalúa la relación general «modifica o complementa», que es la que registra InfoLEG (B02). Los tipos específicos (sustituye, incorpora, deroga, reglamenta, modifica y cita) se extraen igual y se evalúan sobre una muestra revisada a mano de 78 casos.
- **Dominio.** El derecho laboral: cinco leyes ancla (20.744 LCT, 27.802, 24.013, 24.557 y 23.551), expandidas un salto en el gráfico de relaciones de InfoLEG (B04, B08). Solo leyes, decretos y decretos-ley. Dos nodos quedan sin expandir: la Ley 14.250 y la Ley 27.742 (B07).
- **Mundo cerrado.** Una mención se vincula solo si su destino está en el corpus. Fuera del corpus se registra, pero no se enlaza (D4).
- **Fuente de verdad.** El gold nunca es entrada de un extractor (D7).
- **Restricciones operativas.**
  - El portal de datos publica una versión nueva por mes y no guarda las anteriores, así que el corpus se congeló (B17, B23).
  - El digesto de la UNNOBA prohíbe el acceso automático: los PDF se bajaron a mano (B56).
  - El LLM tiene costo (USD 14 por el corpus completo) y no es determinista, así que toda respuesta se guarda en una caché.

## 1.4 Preguntas de investigación

La pregunta principal es la **PI1**: ¿qué efectividad alcanzan distintos enfoques —reglas, modelos y estrategias híbridas— para identificar automáticamente relaciones dirigidas entre normas a partir de su texto?

Las preguntas complementarias son:

- **PI2.** ¿Una estrategia híbrida, con reglas que detectan candidatos y un modelo que resuelve la relación, mejora respecto de cada enfoque por separado?
- **PI3.** ¿Qué formulaciones normativas producen más errores en la identificación, la normalización y la clasificación?
- **PI4.** ¿Qué capacidad de transferencia tiene el extractor, con modificaciones mínimas, sobre un cuerpo normativo sin relaciones estructuradas?
- **PI5.** ¿Qué ventajas aporta un grafo que conserva la evidencia textual y la procedencia de cada vínculo?

La consigna pide abordar la PI1 durante la cursada y una primera aproximación a la PI2. Este informe responde la PI1, la PI2 y la PI3. También presenta resultados preliminares de la PI4 y la PI5, que estaban reservadas para la etapa de maduración.

# 2. Antecedentes

## 2.1 Detección y resolución de referencias normativas

La detección de referencias en textos legales es un problema clásico de extracción de información. Casi siempre se resuelve con gramáticas o expresiones regulares, porque las citas siguen patrones de técnica legislativa.

- **de Maat, Winkels y van Engers** [5] detectan estructuras de referencia en leyes neerlandesas con un parser basado en patrones.
- **Martínez-González, de la Fuente y Vicente** [6] separan tres subprocesos: detectar la cadena, resolverla a un documento o fragmento, y almacenarla. Es la misma división en detección, normalización y vinculación que pide la consigna.
- **Adedjouma, Sabetzadeh y Briand** [7] trabajan sobre la legislación de Luxemburgo y separan la detección de las referencias cruzadas de su resolución. **Sleimi et al.** [8] extienden la línea a la extracción de metadatos semánticos con reglas sobre análisis sintáctico, con precisiones de 82 % a 97 %.
- **Coupette et al.** [9] extraen las referencias de los códigos de EE.UU. y Alemania con expresiones regulares para analizar la red legislativa. Advierten que no reconocen las referencias por el nombre popular de la ley, que es uno de los problemas que encontramos (sección 6.4).

En Argentina, **Cardellino et al.** [10] trabajaron sobre InfoLEG. Detectaron entidades —sobre todo normas— con un enfoque híbrido: reglas de expresiones regulares para los casos no ambiguos y un clasificador entrenado sobre ese etiquetado o sobre una anotación manual. Su objetivo era enlazar referencias, no extraer ni evaluar relaciones entre normas.

La comparación más reciente entre paradigmas es la de **Sargeant, Östling y Magnusson** [11], sobre citas en sentencias del Reino Unido, con 190 sentencias anotadas:

| Paradigma | Macro-F1 |
|---|---|
| Encoders afinados (ModernBERT) | 93,3 % |
| GPT-4.1 | 76,6 % |
| Mejor línea de base con expresiones regulares | 35,4 % |

Ese resultado muestra que el desempeño relativo de las reglas depende mucho de cuán regular sea el estilo de cita de la fuente.

## 2.2 Extracción de relaciones jurídicas y grafos normativos

- **Grafo de la legislación italiana.** **Colombo, Bernasconi y Ceri** [2] modelan la legislación como un grafo de propiedades en Neo4j. Las leyes y sus artículos son nodos, y las citas, modificaciones y derogaciones son aristas con propiedades. En un trabajo posterior [3] completan el grafo con modelos de lenguaje afinados (BERT y Mistral-7B) y reportan que capta el 98 % de las derogaciones. Las relaciones de modificación y derogación salen de la **marcación Akoma Ntoso** que publica el portal oficial (por ejemplo, las etiquetas `activeModification` y `textualMod`), no del texto libre. Los LLM se usan para asignar dominios, generar títulos y extraer temas.
- **EUR-Lex-Triples.** **Bendahman et al.** [4] publican un dataset de 1.504 documentos de la legislación europea anotados con triples. Comparan líneas de base: los modelos afinados son los mejores (Rebel-Large F1 = 0,80; Mistral-7B afinado 0,75), y el uso del LLM sin entrenar es mucho peor (0,27 a 0,47 en zero-shot o con ejemplos).
- **Grafos con LLM, desde la industria.** **Bratanič y Çelik** [12] construyen grafos de contratos con LLM y extracción guiada por esquema. De ese trabajo se tomó la salida en un esquema estructurado y la carga idempotente con `MERGE` (B03). No evalúan contra un gold ni conservan la evidencia, y extraen entidades dentro de un documento, no relaciones entre documentos.

## 2.3 Consolidación automática de textos

Aplicar las modificaciones para obtener el texto vigente es una tarea vecina, que usamos para evaluar el grafo (sección 6.6).

- **Silber** [13] automatiza el 93 % de las operaciones de consolidación del derecho francés con un lenguaje de dominio específico.
- **Etcheverry, Real y Chavallard** [14] usan un modelo generativo afinado y logran más del 63 % de éxito en un proyecto de ley difícil.
- **Prior et al.** [15] advierten que con LLM la similitud textual es alta (93 % a 99 %), pero la coincidencia exacta cae al 50,3 % en un paso y al 20,5 % en cadenas de varias modificaciones. Por eso concluyen que la salida tiene que tratarse como borrador sujeto a verificación humana.

## 2.4 Métodos, datos y métricas de la literatura

| Trabajo | Datos | Método | Métrica |
|---|---|---|---|
| de Maat et al. [5] | Leyes neerlandesas | Patrones | Precisión y recall de detección |
| Sleimi et al. [8] | Legislación de Luxemburgo (metadatos semánticos) | Reglas + análisis sintáctico | P = 82–97 %, R = 92–95 % |
| Cardellino et al. [10] | InfoLEG (11 documentos anotados) | Regex + clasificador NER | P, cobertura, F |
| Sargeant et al. [11] | 190 sentencias del Reino Unido | Regex / encoders / GPT-4.1 | Macro-F1 |
| Colombo et al. [2, 3] | Normattiva (Akoma Ntoso) | Mapeo de la marcación + LLM afinados para completar | Exactitud, consistencia y completitud del grafo |
| Bendahman et al. [4] | EUR-Lex (1.504 documentos) | REBEL, BERT y LLM | P, R, F1 de triples |
| Prior et al. [15] | 908 pares modificación–ley (Alemania) | LLM | Similitud y coincidencia exacta |

## 2.5 Limitaciones identificadas y oportunidad

1. **Fuentes ya marcadas.** Los grafos normativos más completos [2, 3] parten de fuentes que ya marcan la modificación. Donde no hay esa marcación, como en InfoLEG (en su texto) o en un digesto universitario, el problema es extraer las relaciones del texto libre.
2. **Falta de gold.** Los trabajos de detección de referencias evalúan con anotaciones propias, chicas. Las bases complementarias de InfoLEG permiten evaluar contra un **gold oficial, grande y externo**, aunque mide un vínculo más amplio que la modificación (sección 3.1).
3. **Comparaciones parciales entre paradigmas.** Los trabajos comparan reglas y modelos en la detección de citas [11] o en la extracción de triples [4], pero no en la **decisión de si una cita es una relación** entre normas, ni evaluando cada subtarea por separado.
4. **Trazabilidad.** Pocos trabajos conservan, en cada arista, el fragmento y el método que la produjeron. Sin eso, no se puede auditar el grafo ni usarlo como fuente de respuestas justificadas.
5. **Español rioplatense.** No encontramos un corpus para esta tarea en el español normativo argentino.

La **oportunidad** del trabajo combina:

- un corpus argentino con gold oficial;
- un protocolo reproducible que separa detección, normalización y extracción;
- tres enfoques comparados con el mismo protocolo;
- un grafo trazable;
- una primera evaluación de transferencia a un digesto sin relaciones estructuradas.
