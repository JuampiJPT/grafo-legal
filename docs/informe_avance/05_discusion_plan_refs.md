# 7. Discusión, limitaciones y amenazas a la validez

## 7.1 Interpretación de los resultados

**PI1: efectividad de cada enfoque.** Reglas, modelos y LLM llegan a F1 de 0,76 a 0,84 en test. Las reglas a mano y un clasificador entrenado con los mismos atributos empatan (0,828 y 0,823): la curva de aprendizaje muestra que los dos modelos supervisados seguían mejorando con más datos y tienen alta varianza, así que el empate se explica sobre todo por el tamaño del dataset de entrenamiento (801 pares de dev) y no está probado que sea un techo de los atributos (B37, B68). El LLM aporta en dos lugares:

- **el recall**, porque lee la oración y el CONSIDERANDO;
- **el tipo de relación**, con macro-F1 de 0,672 a 0,883.

El parecido entre métodos tan distintos sugiere que **el techo no está en el método sino en la tarea**. Hay dos razones:

- una parte del gold no se puede encontrar leyendo el texto de la modificatoria;
- InfoLEG registra algunas citas del VISTO y otras no, sin un criterio que se lea en el texto.

**¿Cuánto explica el tamaño del corpus?** El corpus es chico: 340 normas, 801 pares para entrenar y 192 de test. Pero el tamaño no afecta a todas las conclusiones por igual:

- **A los modelos supervisados, sí.** Es la causa medible de su empate con las reglas (sección 6.7).
- **A la potencia estadística, sí.** Con 43 normas de test, los intervalos son de unos ±4,5 puntos, y diferencias de 1 o 2 puntos no se pueden afirmar ni descartar (sección 7.2).
- **Al techo de las reglas y del LLM, no.** Ninguno de los dos aprende del corpus. Los limitan propiedades de la tarea: en el 19 % de los pares de dev el destino no aparece nombrado en el texto, y el criterio de InfoLEG para las citas del VISTO no se puede leer en el texto. Un corpus más grande daría intervalos más angostos, pero no movería ese techo.
- **A dónde se pierden los pares, no.** La detección y la normalización casi no pierden pares en dev ni en test, y eso se verificó caso por caso.

**PI2: el híbrido.** El híbrido mejora, pero poco. La intersección de reglas y LLM es la única mejora significativa (+1 punto, por precisión). El híbrido en cascada logra el mismo F1 a un cuarto del costo, y en el digesto es el mejor de todos. Coincide con lo que pide la consigna: las reglas detectan candidatos de forma barata y casi sin errores, y el modelo decide donde las reglas dudan.

**PI3: formulaciones problemáticas.** El análisis caso por caso cambió dónde se puso el esfuerzo. La detección y la normalización casi no pierden pares. Los errores se concentran en:

- las citas sin acción del VISTO;
- las remisiones desde leyes;
- los decretos que aplican una ley sin verbo;
- los vínculos que el texto no nombra.

La lección metodológica es que **sin evaluar por subtarea, el siguiente paso habría sido seguir puliendo el detector**, que ya estaba en el 99,6 %.

**PI4 y PI5, preliminares.** La arquitectura con el adaptador como único punto que depende de la fuente funcionó: el digesto corrió con los mismos extractores. El grafo conserva suficiente información para reconstruir el texto vigente de una ley con 105 modificatorias. Esa es la evidencia más fuerte de que la trazabilidad, con el artículo destino y la evidencia en cada arista, aporta algo que una tabla de pares no tiene.

**Comparación con la literatura.** Nuestras reglas son mucho mejores que las del Reino Unido [11] (0,83 contra 0,35), y el LLM no queda por debajo de las reglas, como sí pasaba allí. Lo atribuimos a dos diferencias:

- **la tarea:** decidir un vínculo entre normas de un catálogo, no detectar cualquier cita en una sentencia;
- **el estilo:** la técnica legislativa argentina es muy regular.

A diferencia del grafo italiano [2, 3], las modificaciones no vienen marcadas y hay que extraerlas del texto. El costo de eso es justamente el F1 de 0,83.

## 7.2 Limitaciones de datos y método

1. **El gold mide un vínculo amplio y tiene ruido.** «Modifica o complementa» incluye remisiones y textos ordenados. En 3 de 30 falsos positivos revisados, el vínculo es real y no está en InfoLEG (B36). El F1 contra InfoLEG subestima un poco la calidad real y mezcla dos tareas distintas.
2. **Tamaño de test.** Son 192 pares de 43 normas de origen. Los intervalos de confianza tienen unos ±4,5 puntos, y diferencias de 1 o 2 puntos no se pueden afirmar.
3. **Anotaciones de una sola persona, y no humana.** Las revisiones manuales (tipos, cobertura, falsos positivos, menciones) y el gold de la PI4 los hizo Claude. No hay acuerdo entre anotadores (kappa) ni validación del equipo. Es la limitación más importante para la PI3 y la PI4.
4. **Mundo cerrado.** Solo se vincula lo que está en el corpus. El 48 % de las menciones nombra normas reales fuera de él. La regla F acierta contra la base completa de InfoLEG el 62 % de las veces en test (B45), pero eso no se evaluó como tarea principal.
5. **Un solo dominio y dos tipos de norma.** Laboral; leyes y decretos. Las resoluciones y disposiciones solo aparecen en la PI4.
6. **El LLM es un servicio externo.** El modelo puede cambiar o dejar de estar disponible. La caché fija los resultados del trabajo, pero no garantiza que una corrida futura dé lo mismo (`docs/reproducibilidad.md`).
7. **El diseño de la v3 y del híbrido en cascada** fue posterior a ver los errores de test de la v2. Por eso se informan como experimentos, y la v2 sigue siendo la referencia.
8. **La PI4 es chica.** 70 documentos y 61 pares de vínculo; 38 documentos con OCR, que no es reproducible byte a byte.
9. **El consolidado no es texto oficial.** No modela vigencias diferidas, suspensiones judiciales, vetos ni derogaciones de normas modificatorias.

## 7.3 Amenazas a la validez

- **Validez interna.**
  - **Fuga de información de test.** Se mitigó congelando cada versión antes de evaluarla y evaluando una sola vez. La amenaza que queda es que los autores conocen el dominio y vieron errores de test de la v2 antes de diseñar la v3.
  - **Sesgo de selección del corpus.** El corpus se construye a partir del propio gold (expansión de las anclas), así que solo contiene normas que InfoLEG ya vinculó (B15). Una muestra independiente del gold está en el plan de maduración.
- **Validez de constructo.** El gold de InfoLEG no es «la verdad», sino lo que el Ministerio registró. Medir contra él premia imitar su criterio editorial, por ejemplo qué citas del VISTO registra.
- **Validez externa.** Los resultados no deberían generalizarse a:
  - otros dominios, como el tributario, donde las remisiones a leyes de impuestos serían mucho más frecuentes;
  - normas de otras épocas, con estilos de cita distintos (los decretos sin año);
  - fuentes con otra estructura de documento, sin VISTO o CONSIDERANDO;
  - otros modelos de lenguaje o versiones del prompt;
  - el texto extraído de PDF con OCR de baja calidad.
- **Validez de conclusión.** Muchas comparaciones (11 métodos) sobre el mismo test aumentan la chance de encontrar una diferencia «significativa» por azar. La mejora del híbrido por intersección (+1 punto) se tiene que confirmar sobre otra muestra.

# 8. Plan de maduración

## 8.1 Experimentos pendientes

1. **Validación humana y acuerdo entre anotadores.** El equipo valida las revisiones manuales y el gold de la PI4. Un segundo anotador repite una parte de cada uno, y se calcula el kappa de Cohen (B58).
2. **Gold de tipos más grande y doble anotación.** Ampliar los 78 casos de tipos, con la guía de anotación escrita.
3. **Muestra independiente del gold** (B15). Normas del dominio que no vienen de la expansión de InfoLEG, para medir la precisión sin el sesgo de selección.
4. **Comparar modelos de lenguaje:** Sonnet, Haiku y un modelo abierto. Medir costo y desempeño, y su sensibilidad al prompt.
5. **Reglas v4,** diseñadas sobre dev: los ajustes identificados en B52 y B57, como «creado por», «inclúyense», los verbos en infinitivo y la condición del verbo antes de la mención.
6. **Ampliar la PI4.** Más documentos del digesto y otro digesto (provincial o municipal), con anotación humana.
7. **Text-to-Cypher (F7).** Un banco de preguntas en lenguaje natural con su consulta esperada, evaluado por *execution accuracy*.
8. **Análisis temporal y consultas sobre el grafo.** Cadenas de modificación, normas más modificadas y vigencia.
9. **Ampliar el corpus de entrenamiento y revisar las pruebas de los modelos supervisados** (B68). La curva de aprendizaje sigue subiendo con los 801 pares de dev. Queda abierta la posibilidad de sumar normas de InfoLEG, repetir la curva con el doble y con 10 veces más datos, y ver si los modelos superan a las reglas o si se aplanan antes.

## 8.2 Mejoras

- **El VISTO como señal graduada,** que distinga la lista de antecedentes de la norma que se reglamenta o modifica. Es el principal punto de falsos positivos.
- **El consolidado:** modelar la derogación de modificatorias y las vigencias diferidas, y aflojar la verificación literal para los cambios parciales.
- **La descarga y el OCR del digesto:** guardar los HTML de las secciones y escribir el script que reconstruye el catálogo desde ellos.
- **Embeddings en el grafo,** si suman a las consultas (B38).

## 8.3 Información adicional necesaria

Hay que consultar con la cátedra:

- si se acepta la supervisión distante;
- si se evalúa también la modificación estricta y la clasificación fina (B02, B14, B27);
- la extensión esperada del artículo final.

También hace falta tiempo del equipo para las anotaciones humanas.

## 8.4 Actividades previstas antes del examen final

| Actividad | Producto |
|---|---|
| Validación humana y segundo anotador | Kappa de Cohen para tipos, cobertura y gold de la PI4 |
| Muestra independiente y reglas v4 | Precisión sin sesgo de selección. Nueva tabla de métodos |
| Comparación de modelos de lenguaje | Costo y desempeño por modelo |
| PI4 ampliada | Transferencia con gold humano y con más documentos |
| Text-to-Cypher | Demo y evaluación sobre el grafo |
| Artículo científico (formato LNCS) | Redacción a partir de este informe y de `docs/conclusiones.md` |

# 9. Referencias bibliográficas

1. Ministerio de Justicia de la Nación Argentina. Base InfoLEG de Normativa Nacional y bases complementarias de normas modificadas y modificatorias. Portal de Datos Abiertos de la Justicia Argentina, licencia CC BY 4.0. http://datos.jus.gob.ar/dataset/base-de-datos-legislativos-infoleg (descarga del 06/11/2026).
2. Colombo, A., Bernasconi, A., Ceri, S.: Modelling Legislative Systems into Property Graphs to Enable Advanced Pattern Detection. arXiv:2406.14935 (2024). Dataset: Italian Legislative Property Graph, Zenodo, doi:10.5281/zenodo.11210265.
3. Colombo, A., Bernasconi, A., Ceri, S.: An LLM-assisted ETL pipeline to build a high-quality knowledge graph of the Italian legislation. Information Processing & Management 62, 104082 (2025). doi:10.1016/j.ipm.2025.104082.
4. Bendahman, N., Pinel-Sauvagnat, K., Hubert, G., Billami, M.B.: EUR-Lex-Triples: A Legal Relation Extraction Dataset from European Legislation. En: Linking Theory and Practice of Digital Libraries (TPDL 2025). LNCS, pp. 433–451. Springer (2025). doi:10.1007/978-3-032-05409-8_25.
5. de Maat, E., Winkels, R., van Engers, T.: Automated Detection of Reference Structures in Law. En: Legal Knowledge and Information Systems (JURIX 2006). Frontiers in Artificial Intelligence and Applications 152, pp. 41–50. IOS Press (2006).
6. Martínez-González, M., de la Fuente, P., Vicente, D.-J.: Reference Extraction and Resolution for Legal Texts. En: Pattern Recognition and Machine Intelligence (PReMI 2005). LNCS 3776. Springer (2005).
7. Adedjouma, M., Sabetzadeh, M., Briand, L.: Automated Detection and Resolution of Legal Cross References: Approach and a Study of Luxembourg's Legislation. En: IEEE 22nd International Requirements Engineering Conference (RE 2014), pp. 63–72 (2014).
8. Sleimi, A., Sannier, N., Sabetzadeh, M., Briand, L., Ceci, M., Dann, J.: An Automated Framework for the Extraction of Semantic Legal Metadata from Legal Texts. Empirical Software Engineering 26(3), 43 (2021).
9. Coupette, C., Beckedorf, J., Hartung, D., Bommarito, M., Katz, D.M.: Measuring Law Over Time: A Network Analytical Framework with an Application to Statutes and Regulations in the United States and Germany. arXiv:2101.11284 (2021).
10. Cardellino, F., Cardellino, C., Haag, K., Soto, A., Teruel, M., Alonso Alemany, L., Villata, S.: Mejora del acceso a Infoleg mediante técnicas de procesamiento automático del lenguaje. En: Simposio Argentino de Informática y Derecho (SID), 47 JAIIO (2018).
11. Sargeant, H., Östling, A., Magnusson, M.: Detecting Legal Citations in United Kingdom Court Judgments. En: Proceedings of EMNLP 2025, pp. 26810–26836. ACL (2025).
12. Bratanič, T., Çelik, T.: From Legal Documents to Knowledge Graphs. Neo4j Developer Blog (2025). https://neo4j.com/blog/developer/from-legal-documents-to-knowledge-graphs/
13. Silber, G.-A.: Towards an Automatic Consolidation of French Law. arXiv:2301.06469 (2023).
14. Etcheverry, M., Real, T., Chavallard, P.: Algorithm for Automatic Legislative Text Consolidation. En: Proceedings of the Natural Legal Language Processing Workshop (NLLP 2024), pp. 166–175. ACL (2024).
15. Prior, M., Hof, A., Wais, N., Grabmair, M.: Risks and Limits of Automatic Consolidation of Statutes. En: Proceedings of the Natural Legal Language Processing Workshop (NLLP 2025), pp. 396–407. ACL (2025).
16. Efron, B., Tibshirani, R.J.: An Introduction to the Bootstrap. Chapman & Hall/CRC (1993).

# Anexo A. Repositorio e implementación

- **Repositorio:** https://github.com/JuampiJPT/grafo-legal
- **Instalación, ejecución y configuración:** `README.md`
- **Estructura:** `docs/estructura_repositorio.md`
- **Qué se repite exacto y qué no:** `docs/reproducibilidad.md`
- **Conclusiones y cómo se llegó a cada una:** `docs/conclusiones.md`
- **Las figuras de este informe** se regeneran con `python scripts/31_figuras_informe.py`.

# Anexo B. Bitácora de investigación

La bitácora registra, con fecha, cada decisión, dificultad, hallazgo y cuestionamiento del trabajo, con su contexto, las alternativas y cómo quedó. Las entradas no se borran: si una decisión cambia, se agrega otra que la reemplaza. A continuación se transcriben las entradas de la investigación, de B01 a B64 y B68. Cuando un punto que había quedado abierto se resolvió después, la entrada lo indica con una nota de *Seguimiento*. Lo que sigue pendiente está resumido en el plan de maduración (sección 8). En esta transcripción se omiten tres cosas: el estado de cada entrada, la lista interna de tareas y las entradas sobre el video explicativo y la preparación de la entrega (presentación y revisión final de este informe). La versión completa es «00 - Bitácora del TP», en la carpeta del Drive, y la copia está en `docs/drive/00_bitacora.md`.

