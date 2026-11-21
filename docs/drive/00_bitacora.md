<!-- Copia del Google Doc "00 - Bitácora del TP" (id 1kXhR_wDGRq8TsD8jtcxX6sSWMZPaRJS9fggNjLIReCY, revision AHj4eMSPpiaF). La version editable es la del Drive; esta copia se regenera con tools/gdoc_a_md.py. -->

# Bitácora del TP Integrador

*Sistemas Inteligentes (UNNOBA). Problemática III: extracción de relaciones entre normas y grafo normativo trazable. Iniciada el 27/10/2026, última entrada el 21/11/2026.*

## Cómo usar esta bitácora

Cada entrada registra una decisión, una dificultad, un hallazgo o un cuestionamiento, con su contexto, las alternativas consideradas y cómo quedó. Las entradas no se borran: si una decisión cambia, se agrega una entrada nueva que la reemplaza y se cita la anterior. Así el informe final puede reconstruir por qué el sistema quedó como quedó, y las secciones de Metodología, Limitaciones y Amenazas a la validez salen de acá.

Tipos de entrada: **Decisión** (se eligió un camino), **Dificultad** (algo trabó el trabajo), **Hallazgo** (algo que aprendimos de los datos) y **Cuestionamiento** (una pregunta metodológica que alguien puede hacernos en la defensa). Estado: abierta o cerrada.

## Índice de entradas

| ID | Fecha | Tipo | Tema | Estado |
|---|---|---|---|---|
| B01 | 27/10 | Decisión | El grafo y el text-to-Cypher se subordinan al núcleo evaluable | Cerrada |
| B02 | 27/10 | Decisión | Relación general "modifica o complementa" | Abierta |
| B03 | 27/10 | Cuestionamiento | Qué tomar del artículo de Neo4j y LlamaIndex | Cerrada |
| B04 | 27/10 | Decisión | Dominio laboral en lugar de solo dos leyes | Cerrada |
| B05 | 27/10 | Dificultad | Portal bloqueado desde el entorno de trabajo | Cerrada |
| B06 | 27/10 | Hallazgo | Estructura real de las bases complementarias | Cerrada |
| B07 | 27/10 | Decisión | No expandir la Ley 14.250 | Cerrada |
| B08 | 27/10 | Decisión | Solo leyes y decretos, un salto de expansión | Cerrada |
| B09 | 27/10 | Decisión | Split temporal con corte en 2019 | Cerrada |
| B10 | 27/10 | Hallazgo | Normas sin texto y techo de recall | Cerrada |
| B11 | 28/10 | Cuestionamiento | ¿Hace falta Cloudflare para obtener los textos? | Cerrada |
| B12 | 28/10 | Hallazgo | Cobertura textual del gold | Abierta |
| B13 | 28/10 | Dificultad | Guardar los textos fuera del navegador | Cerrada |
| B14 | 28/10 | Cuestionamiento | ¿Esto ya es un dataset? ¿Con qué librerías? | Abierta |
| B15 | 28/10 | Cuestionamiento | Sesgo de selección del corpus | Abierta |
| B16 | 28/10 | Decisión | El test no se usa para diseñar reglas ni prompts | Cerrada |
| B17 | 02/11 | Hallazgo | El portal se actualizó y los hashes cambiaron | Cerrada |
| B18 | 02/11 | Hallazgo | Profundidad del grafo laboral frente a otros dominios | Cerrada |
| B19 | 02/11 | Dificultad | El digesto de la UNNOBA bloquea el acceso automático | Abierta |
| B20 | 02/11 | Decisión | Tres parsers: regex/AST, LLM puro e híbrido | Cerrada |
| B21 | 02/11 | Cuestionamiento | Qué significa profundidad del grafo | Abierta |
| B22 | 02/11 | Hallazgo | Acceso al digesto y formato de los documentos | Cerrada |
| B23 | 06/11 | Decisión | Se congela el snapshot del 30/09 y el pipeline oficial pasa a los scripts | Cerrada |
| B24 | 06/11 | Decisión | Corpus v2 laboral ampliado | Cerrada |
| B25 | 06/11 | Decisión | Repositorio git del TP | Cerrada |
| B26 | 06/11 | Hallazgo | La cobertura textual, reproducida con el detector de menciones | Abierta |
| B27 | 06/11 | Hallazgo | El gold mezcla modificaciones con remisiones | Abierta |
| B28 | 06/11 | Hallazgo | Primer resultado del parser de reglas | Abierta |
| B29 | 06/11 | Hallazgo | Primera corrida del pipeline oficial | Cerrada |
| B30 | 06/11 | Hallazgo | La muestra de la Ley 14.250 confirma la exclusión | Abierta |
| B31 | 06/11 | Dificultad | Permisos y límite de pedidos al correr el pipeline | Cerrada |
| B32 | 06/11 | Decisión | La documentación se mantiene en el Drive y en el repositorio | Cerrada |
| B33 | 09/11 | Decisión | Un solo corpus | Cerrada |
| B34 | 09/11 | Decisión | Dataset en CSV con pandas | Cerrada |
| B35 | 09/11 | Hallazgo | Las reglas v1 no generalizan bien a los pares nuevos | Abierta |
| B36 | 09/11 | Decisión | Reglas v2: el VISTO cuenta, las citas de procedencia no | Cerrada |
| B37 | 09/11 | Hallazgo | Un clasificador entrenado empata con las reglas | Cerrada |
| B38 | 09/11 | Decisión | Modelo del grafo: InfoLEG y lo extraído por separado | Abierta |
| B39 | 09/11 | Dificultad | Sin acceso de escritura a GitHub desde la sesión de Claude | Cerrada |
| B40 | 09/11 | Decisión | Contenedor Neo4j propio del TP | Cerrada |
| B41 | 09/11 | Decisión | Una salida estándar para cualquier parser y cualquier documento normativo | Cerrada |
| B42 | 09/11 | Decisión | El grafo representa lo que hace cada norma; InfoLEG queda afuera | Cerrada |
| B43 | 09/11 | Hallazgo | El grafo devuelve lo que se le cargó; contra InfoLEG, las citas son el problema | Abierta |
| B44 | 09/11 | Decisión | Documento del parser y del grafo, contado paso a paso | Cerrada |
| B45 | 16/11 | Hallazgo | Evaluación por subtareas: la detección y la normalización no pierden pares | Abierta |
| B46 | 16/11 | Hallazgo | El modelo con contexto textual, solo, no supera a las reglas; en un híbrido, ayuda en la zona gris | Cerrada |
| B47 | 16/11 | Hallazgo | Tipo de relación sobre 78 casos: macro-F1 0,672; el error dominante es una cita tomada como acción | Abierta |
| B48 | 16/11 | Decisión | Parser LLM con verificación de la cita, caché reproducible y grafo aparte | Abierta |
| B49 | 16/11 | Decisión | Tabla final con intervalos de confianza por bootstrap | Cerrada |
| B50 | 16/11 | Decisión | Código comentado y guía de lectura para la presentación | Cerrada |
| B51 | 16/11 | Hallazgo | Cada error explicado; corrige la clasificación de B45 | Cerrada |
| B52 | 16/11 | Hallazgo | Reglas v3: corrigen la normalización, empatan en test | Abierta |
| B53 | 16/11 | Dificultad | La API no respondía desde el entorno de la Mac; se saca la temperatura | Cerrada |
| B54 | 16/11 | Hallazgo | El parser LLM sube el recall y el tipado; la intersección con las reglas es la única mejora significativa | Abierta |
| B55 | 18/11 | Decisión | Parser híbrido en cascada: las reglas filtran y el LLM decide la zona gris | Cerrada |
| B56 | 20/11 | Dificultad | Descarga del digesto de la UNNOBA para la PI4 | Cerrada |
| B57 | 20/11 | Hallazgo | PI4: el pipeline se transfiere al digesto de la UNNOBA si el adaptador lleva el vocabulario de la fuente | Cerrada |
| B58 | 20/11 | Decisión | Revisión del gold de la PI4: las remisiones que definen a quién alcanza la resolución son APLICA | Abierta |
| B59 | 20/11 | Decisión | Grafos del digesto de la UNNOBA, con el mismo modelo y código que los de InfoLEG | Cerrada |
| B60 | 20/11 | Hallazgo | Evaluación de los grafos leyéndolos desde Neo4j: ida y vuelta idéntica en las cuatro fuentes | Cerrada |
| B61 | 20/11 | Hallazgo | Texto consolidado de la LCT desde el grafo: coincide con InfoLEG en el 96 % de los artículos (91 % de los que cambian) | Abierta |
| B62 | 20/11 | Decisión | Todo lo que se hizo a mano en la sesión queda como script en el repositorio | Cerrada |
| B63 | 21/11 | Decisión | Tres documentos de cierre: reproducibilidad, estructura del repositorio y conclusiones | Cerrada |

## Entradas

### B01 · 27/10/2026 · Decisión · El grafo y el text-to-Cypher se subordinan al núcleo evaluable

**Contexto.** El objetivo propio del equipo es un grafo en Neo4j consultable en lenguaje natural mediante text-to-Cypher. El enunciado, en cambio, evalúa la extracción de relaciones desde el texto y su comparación contra InfoLEG.

**Decisión.** El grafo y la consulta en lenguaje natural van en las fases 6 y 7 del roadmap, después de tener corpus, gold, baseline de reglas, enfoque con modelos y métricas. El grafo se usa además como herramienta de evaluación: el gold se carga como una relación separada y los aciertos y errores se calculan con Cypher.

**Por qué.** Un grafo vistoso sin métricas no cumple el alcance mínimo de la cursada. Con las métricas hechas, el text-to-Cypher responde la PI5.

### B02 · 27/10/2026 · Decisión · Relación general "modifica o complementa"

**Contexto.** InfoLEG agrupa en una sola relación vínculos distintos: modificación, sustitución, derogación, reglamentación, prórroga y complementación.

**Decisión.** En la cursada se extrae solo la relación general, como permite el enunciado. Los tipos finos quedan para la etapa de maduración, porque requieren anotación manual.

**Abierto.** Hay que confirmar con el equipo y la cátedra si se intenta igual una clasificación fina como resultado exploratorio. El verbo de la oración (sustitúyese, derógase, reglaméntase) ya da una primera aproximación gratis.

### B03 · 27/10/2026 · Cuestionamiento · Qué tomar del artículo de Neo4j y LlamaIndex

**Pregunta.** ¿Sirve como base el artículo "From legal documents to knowledge graphs" (Bratanič y Çelik, Neo4j, 2025)?

**Respuesta.** Se toma la extracción guiada por esquema (Pydantic) para el enfoque con LLM, la clasificación previa del documento y la carga idempotente con MERGE. No se toma su diseño experimental: no evalúa contra un gold, extrae entidades dentro de un contrato y no relaciones entre documentos, y no conserva la evidencia textual. Se cita en Trabajos relacionados como ejemplo de construcción de grafos jurídicos con LLM.

### B04 · 27/10/2026 · Decisión · Dominio laboral en lugar de solo dos leyes

**Propuesta inicial.** Usar como corpus solo la Ley 27.802 de Modernización Laboral y la Ley 20.744 de Contrato de Trabajo.

**Problema.** El gold de InfoLEG registra relaciones entre normas, no entre artículos. Aunque la 27.802 modifica decenas de artículos de la LCT, eso es una sola arista. Con una o dos aristas las métricas valen 0 o 1, no hay split posible y las reglas quedan ajustadas a un solo redactor.

**Decisión.** Se usa el derecho laboral como dominio y la reforma de 2026 como caso central de la demo.

### B05 · 27/10/2026 · Dificultad · Portal bloqueado desde el entorno de trabajo

**Qué pasó.** El entorno de procesamiento no podía acceder a datos.jus.gob.ar ni a infoleg.gob.ar. El repositorio de GitHub del dataset tiene solo la documentación de columnas, no los datos.

**Cómo se resolvió.** Las bases se descargaron y procesaron con JavaScript en el navegador de la máquina local. El script *01_obtener_corpus.py* implementa el mismo criterio con pandas, pero solo se probó con datos sintéticos.

**Consecuencia para la defensa.** El pipeline oficial tiene que ser el de Python. Falta correr los scripts sobre los datos reales en una máquina del equipo. Ver B17: por la actualización del portal ya no van a dar exactamente los mismos números.

### B06 · 27/10/2026 · Hallazgo · Estructura real de las bases complementarias

Al cruzar las tres bases se verificó que:

- la base de normas modificadas y la de modificatorias contienen exactamente los mismos 375.808 pares únicos;
- las columnas descriptivas (tipo, número, fecha, título) describen a la otra norma del par, no a la que nombra el archivo;
- la base de modificatorias tiene 3.355 filas duplicadas;
- todos los identificadores existen en la base normativa.

**Uso.** Basta una de las dos bases para el gold. Este detalle de las columnas es fácil de malinterpretar y conviene contarlo en la sección de Datos.

### B07 · 27/10/2026 · Decisión · No expandir la Ley 14.250

**Contexto.** La Ley 14.250 de Convenios Colectivos tiene 42.598 relaciones en InfoLEG, casi todas resoluciones (28.935) y disposiciones (13.620) de la Secretaría de Trabajo que homologan convenios.

**Decisión.** Se incluye como nodo pero no se expande.

**Cuestionamiento abierto.** Asumimos que esas resoluciones no expresan la relación con un verbo de modificación, pero no lo verificamos. Hay que leer una muestra de 10 a 20 resoluciones antes de defender esta exclusión.

### B08 · 27/10/2026 · Decisión · Solo leyes y decretos, un salto de expansión

**Decisión.** El corpus incluye leyes, decretos y decretos-ley a un salto de las semillas (LCT y Ley 27.802).

**Alternativas.** Expandir también la Ley 27.742 daba 251 normas y 643 pares. Expandir dos saltos daba 4.115 normas y 12.380 pares, lo que impide el análisis manual de errores. Ver B18 para la revisión de esta decisión.

### B09 · 27/10/2026 · Decisión · Split temporal con corte en 2019

**Decisión.** Las normas publicadas hasta el 31/12/2019 son de desarrollo y las posteriores son de test. En el gold, el split lo fija la norma modificatoria, porque es la que lee el extractor. Resultado: 275 pares de desarrollo y 127 de test.

**Por qué temporal y no aleatorio.** Mide si lo diseñado con normas viejas funciona con normas que no se vieron, y deja en test las reformas recientes (DNU 70/2023, Ley 27.742 y Ley 27.802).

**Posible objeción.** 114 pares cruzan el corte (modificatoria en test, modificada en desarrollo). No es una fuga: el extractor nunca recibe el gold y la norma modificada solo aparece como destino a normalizar.

### B10 · 27/10/2026 · Hallazgo · Normas sin texto y techo de recall

Quince normas del corpus no tienen link al texto en InfoLEG, todas anteriores a 1994. Esto deja 9 pares del gold cuya norma modificatoria no se puede leer. Esos pares son irrecuperables para cualquier extractor y se reportan como un techo conocido del recall.

### B11 · 28/10/2026 · Cuestionamiento · ¿Hace falta Cloudflare para obtener los textos?

**Pregunta.** ¿Conviene usar la Browser Rendering API de Cloudflare (endpoints /content, /markdown y /crawl) para el scraping?

**Respuesta.** Para InfoLEG no. Es HTML estático servido por Apache, sin protección contra bots, sin robots.txt y sin JavaScript necesario. Se descargó con pedidos simples, uno por segundo. Además, según su documentación, la API de Cloudflare se identifica como bot, respeta robots.txt y no puede evitar captchas ni detección de bots, así que tampoco sirve para destrabar un sitio protegido. Ver B19 para el caso del digesto.

### B12 · 28/10/2026 · Hallazgo · Cobertura textual del gold

**Qué se midió.** En cada relación del gold se buscó si el texto de la norma modificatoria menciona a la modificada. De las 393 relaciones con texto, el 81,9 % menciona el número de la norma destino, el 5,1 % solo su nombre ("Ley de Contrato de Trabajo") y el 13,0 % no tiene mención detectable. En test la mención por número llega al 92,9 %.

**Interpretación.** El 13 % sin mención son vínculos que InfoLEG registró con criterio documental. Ese es el techo realista del recall de cualquier extractor que lea solo el texto, y conviene reportarlo así.

**Abierto.** La clasificación salió de una búsqueda automática sin revisar. Hay que verificar a mano unos 30 casos antes de citar los porcentajes en el informe.

### B13 · 28/10/2026 · Dificultad · Guardar los textos fuera del navegador

**Qué pasó.** Los 168 HTML descargados quedaron en la memoria del navegador integrado. Eran demasiado grandes para subirlos al Drive por las herramientas disponibles, y el navegador solo podía guardar en la carpeta Descargas.

**Cómo se resolvió.** Se generó un zip en el navegador y el equipo lo movió a *Documentos/grafo legal*. El 02/11 se verificó que los 168 archivos coinciden con los hashes del manifiesto.

**Lección.** Conviene trabajar desde el principio en una carpeta local del proyecto y sincronizarla, en lugar de depender de la memoria del navegador.

### B14 · 28/10/2026 · Cuestionamiento · ¿Esto ya es un dataset? ¿Con qué librerías?

**Respuesta.** Todavía no del todo. Tenemos una tabla de metadatos (nodos), un conjunto de evaluación (gold) y los textos crudos. El dataset para el enfoque con modelos se arma después de segmentar en artículos y detectar referencias: una fila por candidato (artículo, mención, destino normalizado) y una etiqueta según el gold, solo en desarrollo.

**Librerías.** Los CSV actuales se generaron en JavaScript (ver B05). Los scripts oficiales usan pandas y requests. Falta alinearlos con las librerías que se ven en la materia.

**A consultar con la cátedra.** Entrenar o elegir ejemplos few-shot con etiquetas derivadas de InfoLEG es supervisión distante. Es una práctica estándar, pero hay que justificarla frente a la consigna de que el gold no sea entrada del extractor.

### B15 · 28/10/2026 · Cuestionamiento · Sesgo de selección del corpus

**Problema.** El corpus se eligió usando las relaciones de InfoLEG. No hay fuga hacia el extractor, pero todas las normas del corpus tienen relaciones conocidas, y eso puede inflar la precision respecto de un uso real.

**Propuesta.** Agregar una muestra elegida sin mirar el gold, por ejemplo todas las leyes y decretos con "TRABAJO" en el título entre 2015 y 2020, y comparar las métricas. Si no da el tiempo, declararlo como amenaza a la validez.

### B16 · 28/10/2026 · Decisión · El test no se usa para diseñar reglas ni prompts

Los patrones de regex, los ejemplos few-shot y los umbrales del híbrido se sacan solo de desarrollo. La tabla de cobertura incluye test, pero solo con fines descriptivos. El test se evalúa una vez por enfoque, con la configuración final.

### B17 · 02/11/2026 · Hallazgo · El portal se actualizó y los hashes cambiaron

**Qué pasó.** Al volver a descargar las bases, el portal informaba datos actualizados al 31/10/2026 (antes, 30/09/2026). Los hashes ya no coinciden. Con el mismo criterio el corpus pasaría de 183 a 185 normas y el gold de 402 a 406 pares, por dos decretos nuevos: el 1203/2026 y el 1228/2026, este último modificatorio del Decreto 408/2026.

**Por qué importa.** La regeneración desde el portal ya no reproduce los números del documento 01. Los zip originales del 27/10 no se guardaron.

**Propuesta de decisión.** Congelar como versión oficial del TP el snapshot de datos al 30/09/2026, es decir los CSV que están en el Drive. El script reproduce el procedimiento, no el snapshot. A partir de ahora, guardar también los zip crudos de cada descarga.

**Abierto.** Decidir si se congela o se actualiza a la versión del 31/10. Congelar es más simple y defendible.

### B18 · 02/11/2026 · Hallazgo · Profundidad del grafo laboral frente a otros dominios

**Pregunta.** ¿El dominio laboral da un grafo con suficiente profundidad o conviene buscar otro?

**Resultado.** El laboral alcanza para la cursada, pero tiene forma de estrella: el 37 % de las aristas toca a la LCT. Ampliarlo con la Ley de Empleo, la de Riesgos del Trabajo y la de Asociaciones Sindicales casi duplica el gold (775 pares, 192 en test) y baja esa concentración al 19 %. El tributario es el candidato natural para una prueba en otro dominio. El detalle está en el documento 02.

**Abierto.** Decidir si se adopta el corpus laboral ampliado. Si se adopta, entra como una nueva versión del corpus y se rehacen el split y la cobertura.

### B19 · 02/11/2026 · Dificultad · El digesto de la UNNOBA bloquea el acceso automático

**Qué se encontró.** digesto.unnoba.edu.ar está detrás de Cloudflare, muestra un captcha ("Verifique que es un ser humano") al navegar sus listados y su robots.txt prohíbe todo rastreo automático (Disallow: /). Los documentos se publican en PDF.

**Decisión.** No se scrapea el digesto ni se intenta saltear el captcha. La API de Cloudflare tampoco sirve, porque respeta robots.txt. Las vías válidas son dos: pedir a la UNNOBA una copia de un conjunto de resoluciones para uso académico, o descargar a mano una muestra chica como cualquier usuario. El enunciado pide justamente un corpus pequeño anotado manualmente.

**Abierto.** Elegir la vía y el tamaño de la muestra. Ver B22: con la sesión de un integrante del equipo se accede sin captcha, y los PDF recientes tienen texto.

### B20 · 02/11/2026 · Decisión · Tres parsers: regex/AST, LLM puro e híbrido

**Decisión.** Se implementan tres extractores que comparten la misma interfaz de entrada (artículos segmentados) y de salida (aristas con origen, destino normalizado, tipo, fragmento, ubicación y método):

- **Regex/AST:** el documento se parsea a un árbol (norma, artículo, inciso) y las citas se reconocen con una gramática de referencias normativas.
- **LLM puro:** el modelo recibe el artículo y devuelve las relaciones en un esquema estructurado, sin candidatos previos.
- **Híbrido:** regex/AST propone candidatos con alta cobertura y el LLM los confirma, clasifica y resuelve las referencias implícitas.

**Por qué.** Responde directamente PI1 (efectividad de cada enfoque) y PI2 (si el híbrido mejora). Con la misma interfaz, los tres se evalúan sobre los mismos conjuntos y se pueden aplicar sin cambios al digesto (PI4). El diseño completo está en el documento 02.

### B21 · 02/11/2026 · Cuestionamiento · Qué significa profundidad del grafo

**Aclaración.** Para el equipo, la profundidad es la cantidad de relaciones de un nodo particular (su grado), no la longitud de las cadenas de modificaciones. El análisis de B18 medía la estructura del grafo; se agregó la sección 9 del documento 02 con esta definición.

**Resultado.** La LCT tiene 130 modificatorias que son leyes o decretos (267 si se cuentan resoluciones y otros actos) y ocupa el puesto 29 entre 34.026 normas: ya es uno de los nodos más profundos de InfoLEG. En el resto del corpus la mediana es de 2 relaciones por norma.

**Decisión propuesta.** Mantener la LCT como nodo central. Si se quiere un segundo nodo de alto grado, evaluar la Ley 24.241 (SIPA, 341 modificatorias) o el subdominio de empleo público (Ley 24.185 y Decretos 214/2006 y 2098/2008), verificando antes que sus modificatorias no sean homologaciones repetitivas.

### B22 · 02/11/2026 · Hallazgo · Acceso al digesto con la sesión del equipo y formato de los documentos

**Qué pasó.** Con el Chrome de un integrante del equipo, ya verificado por Cloudflare, el digesto se navega sin captcha. Se abrieron solo tres páginas y dos documentos, sin descargas masivas, para respetar el robots.txt.

**Hallazgos.** La sección de reglamentaciones vigentes organiza las ordenanzas por tema y muestra un resumen de cada una, donde ya aparecen relaciones entre ordenanzas. Las citas tienen otra forma que en InfoLEG ("Ordenanza HCS Nº 035/12", "Ordenanza (CS) Nro. 23/09"). La ordenanza de 2012 revisada es un PDF con texto; la de 2007 parece escaneada.

**Consecuencia.** La muestra para la PI4 se puede armar a mano por tema, por ejemplo el Reglamento General de Alumnos y sus modificaciones. El adaptador necesita extraer texto de PDF y, para los documentos antiguos, OCR.

### B23 · 06/11/2026 · Decisión · Se congela el snapshot del 30/09 y el pipeline oficial pasa a los scripts

**Contexto.** B17 dejó abierta la elección entre congelar el snapshot del 30/09 o actualizar al del 31/10, que da 185 normas y 406 pares. B05 dejaba pendiente que el pipeline oficial fuera el de Python.

**Decisión.** El corpus v1 queda congelado en el snapshot del 30/09. Los CSV y sus hashes están en el repositorio, en data/corpus_v1/SNAPSHOT.md. Los datos nuevos se generan solo con los scripts, corridos con correr_pipeline.sh en una máquina con red. El script 01 se niega a escribir sobre data/corpus_v1; con los datos actuales regenera el v1 en una carpeta de verificación para poder comparar.

**Dificultad.** El shell que usa Claude sobre la Mac del equipo tampoco tiene salida a datos.jus.gob.ar ni a InfoLEG (el proxy responde 403). La corrida con red la tiene que hacer un integrante del equipo desde su terminal.

### B24 · 06/11/2026 · Decisión · Corpus v2 laboral ampliado

**Decisión.** Se adopta lo propuesto en B18: un corpus v2 que suma como semillas la Ley 24.013, la Ley 24.557 y la Ley 23.551. El v1 sigue siendo el corpus sobre el que se diseñan las reglas. El v2 sirve como test más grande y para medir cuánto cae el F1 con las reglas congeladas.

**Por qué.** El test de v1 tiene 127 pares y el 54 % sale de tres normas: la Ley 27.802 (38), el DNU 70/2023 (17) y la Ley 27.742 (13). Se descartó sumar un segundo nodo grande fuera del laboral, como el SIPA o el empleo público (B21). La prueba en otro dominio queda para el corpus tributario y para el digesto.

**Pendiente.** Los números definitivos de v2 salen de la corrida con red. Las cifras de B18 (340 normas y 775 pares) son del análisis hecho en el navegador.

### B25 · 06/11/2026 · Decisión · Repositorio git del TP

**Qué.** El trabajo reproducible quedó en el repositorio grafo-legal (github.com/JuampiJPT/grafo-legal): los datos del corpus v1, los 168 textos con su manifiesto, los scripts 01 a 06, el paquete src/grafo_legal, los resultados y tests que corren sin red. Los zip crudos del portal quedan fuera de git, en data/raw, y se identifican por su hash en procedencia.json. La copia duplicada de los textos en la carpeta local se borró después de verificar que los 168 archivos coincidían byte a byte.

**Dificultad.** La sesión de trabajo no tiene la cuenta de GitHub vinculada, así que el primer push lo hace el equipo.

### B26 · 06/11/2026 · Hallazgo · La cobertura textual, reproducida con el detector de menciones

**Qué se hizo.** La clasificación de B12 se rehízo con el detector de menciones del parser (script 05). La primera versión del detector perdía 30 menciones reales. Faltaban estos patrones: las abreviaturas «núm.» y «N.°» y el error de OCR «NQ»; los nombres intercalados, como «Ley de Contrato de Trabajo Nº 20.744»; las listas con «(t.o. 1976) y sus modificatorias» entre ítems; los decretos-leyes de facto que InfoLEG cataloga como Ley, como «Decreto-Ley 17.258/67»; y la errata «pordecreto».

**Resultado.** La nueva clasificación coincide con la del navegador en 401 de 402 pares: 322 citan por número, 21 solo por nombre, 50 no mencionan a la norma y 9 no tienen texto. La diferencia es un acierto del script: la Ley 23.947 cita la «Ley de Contrato de Trabajo» sin número.

**Revisión manual.** En una muestra de 30 pares estratificada por categoría, con semilla fija, las 30 categorías resultaron correctas. La primera pasada la hizo Claude. Falta que la valide un integrante del equipo y que un segundo anotador repita parte de la muestra para calcular el kappa.

### B27 · 06/11/2026 · Hallazgo · El gold mezcla modificaciones con remisiones

**Qué se encontró.** De los 21 pares de la revisión que tienen mención explícita, 7 son modificaciones, 4 reglamentaciones, 1 texto ordenado y 9 remisiones o complementos («se regirá por la ley de contrato de trabajo», «conforme a los artículos 64 y 65»). En 7 de los 21 la única mención está en el VISTO o el CONSIDERANDO. De los 9 pares sin mención: 3 complementan por materia, 2 se explican por un texto ordenado, 1 es una modificación transitiva, 1 una derogación tácita y 2 no se explican con el texto publicado. En los casos de texto ordenado, el gold enlaza el decreto que aprobó el t.o. aunque el texto cite la ley solo por su nombre.

**Consecuencia.** Los datos confirman B02: el gold mide un vínculo amplio. Exigir un verbo modificatorio deja afuera muchos aciertos reales (el F1 de dev baja de 0,716 a 0,556). En el informe hay que separar dos tareas: recuperar el vínculo de InfoLEG, que es lo que mide el gold, y tipar la relación, que requiere anotación manual.

**A consultar con la cátedra.** Si se reporta solo la tarea amplia o también la estricta, sobre una muestra anotada a mano.

### B28 · 06/11/2026 · Hallazgo · Primer resultado del parser de reglas

**Qué se evaluó.** Cinco configuraciones sobre la misma salida del parser, medidas a nivel de par: todas las menciones; solo las del articulado; articulado con filtro temporal; y esta última exigiendo además un verbo modificatorio en el artículo o en la oración. Sobre dev hubo dos iteraciones de reglas. Después se congelaron y test se evaluó una sola vez.

**Resultado.** La mejor configuración es la del articulado con filtro temporal: P 0,692, R 0,742 y F1 0,716 en dev; P 0,784, R 0,913 y F1 0,844 en test. Con verbo en la oración, la precisión de dev sube a 0,844 pero el recall cae a 0,414.

**Lectura.** Test da mejor que dev por cómo quedó compuesto el split (B24), no por las reglas. La mayoría de los falsos positivos son citas que InfoLEG no registró como vínculo. Antes de dar por cerrada la precisión hay que revisar a mano 30 de ellos.

### B29 · 06/11/2026 · Hallazgo · Primera corrida del pipeline oficial

**Qué se corrió.** correr_pipeline.sh en la Mac de un integrante del equipo, con red, sobre el snapshot de InfoLEG del 06/11/2026.

**Resultado.** El corpus v2 quedó con 340 normas (306 con texto) y 775 pares: 583 en dev y 192 en test. La LCT toca el 19,5 % de los pares, y las tres normas que más aportan al test pasan de explicar el 54 % al 36 %. El v1 regenerado coincide con el congelado en sus 183 normas y 402 pares, y solo agrega los Decretos 1203/2026 y 1228/2026 con sus 4 relaciones, los mismos que se habían anticipado en B17. Las métricas del parser de reglas sobre el v1 son idénticas a las calculadas antes.

**Consecuencia.** El pipeline de scripts reproduce lo hecho en el navegador. Queda cerrado lo pendiente de B05.

### B30 · 06/11/2026 · Hallazgo · La muestra de la Ley 14.250 confirma la exclusión

**Qué se encontró.** InfoLEG registra 42.860 modificatorias de la Ley 14.250: 28.935 resoluciones, 13.882 disposiciones, 22 decretos, 11 laudos, 6 leyes y otros 4 actos. En una muestra de 30 normas que no son leyes ni decretos, ninguna modifica el texto de la ley: 19 homologan o registran convenios, 8 fijan el tope indemnizatorio de un acuerdo ya homologado y 3 aplican un convenio o no tienen relación visible.

**Decisión.** Se mantiene lo decidido en B07. Si se expandiera la 14.250 con el mismo filtro por tipo de norma, entrarían a lo sumo 16 normas nuevas: son 28 leyes y decretos y 12 ya están en el v2.

**Observación.** Entre las modificatorias hay una circular del BCRA sobre regímenes informativos y dos decretos secretos de 2015 rotulados «Detención». Sirven como ejemplos de ruido en el gold para la sección de amenazas a la validez.

**Pendiente.** La anotación es una primera pasada de Claude; falta la validación humana.

### B31 · 06/11/2026 · Dificultad · Permisos y límite de pedidos al correr el pipeline

**Qué pasó.** La corrida tuvo dos problemas. Los archivos que Claude había creado en la carpeta local no se podían sobrescribir desde la terminal del usuario, y el script 02 falló al guardar el manifiesto después de bajar 138 textos. Al volver a correrlo, InfoLEG respondió 404 a pedidos que minutos antes habían funcionado, probablemente por un límite de pedidos.

**Cómo se resolvió.** Los scripts ahora escriben en un archivo temporal y lo renombran, lo que solo requiere permiso sobre la carpeta. El script 02 ya no vuelve a pedir un texto que está en disco: arma la fila del manifiesto desde el archivo. La tercera corrida no le hizo ningún pedido a InfoLEG.

**Lección.** Toda descarga masiva tiene que poder retomarse sin repetir pedidos, y su progreso tiene que verse mientras corre.

### B32 · 06/11/2026 · Decisión · La documentación se mantiene en el Drive y en el repositorio

**Decisión.** Todo documento del TP se guarda en los dos lugares, y toda decisión, dificultad o hallazgo se registra en esta bitácora. Los documentos del Drive (esta bitácora y los informes 01 a 05) tienen una copia en Markdown en docs/drive/ del repositorio, regenerada con tools/gdoc_a_md.py. La documentación del repositorio (README, decisiones, resultados y revisión manual) está copiada en el documento 03 del Drive, y el estado general en el documento 04 y en docs/ESTADO.md. El roadmap tiene una copia en el documento 05.

**Por qué.** El equipo y la cátedra consultan el Drive, y el repositorio es la fuente reproducible. Con las dos copias, quien lee el informe encuentra cada dato en cualquiera de los dos lugares.

**Regla de edición.** La versión editable de cada documento es la del lugar donde se creó: los informes y la bitácora en el Drive, la documentación técnica en el repositorio. La copia del otro lado se actualiza en la misma sesión en que cambia el original.

### B33 · 09/11/2026 · Decisión · Un solo corpus

**Contexto.** Hasta ahora había dos corpus: el v1 (183 normas, 402 pares, snapshot del 30/09), sobre el que se diseñaron las reglas, y el v2 ampliado (340 normas, 775 pares, snapshot del 06/11), pensado como prueba más grande (B23, B24). Mantener los dos obligaba a reportar cada resultado dos veces.

**Decisión.** El TP usa un único corpus: el ampliado, congelado en el snapshot del 06/11 (data/corpus en el repositorio). El v1 está contenido en él con el mismo split. Sus 402 pares quedan marcados en pares_evaluados_en_v1.csv para reportar también las métricas sin ellos. El v1 queda en el historial de git y en el documento 01.

**Protocolo.** Las reglas v1, congeladas, se evaluaron una vez sobre el corpus único (B35). La iteración siguiente se diseña solo sobre el dev del corpus único (583 pares, 308 de ellos nunca usados) y el test (192 pares) se evalúa una sola vez con las reglas v2 congeladas. Los tres parsers se comparan sobre ese mismo test.

**Verificación.** correr_pipeline.sh regenera el corpus con los zips guardados y comprueba que sea idéntico al congelado. Se verificó en la Mac del equipo y en el entorno de Claude, con versiones distintas de pandas: el corpus, las evidencias y el dataset dan los mismos hashes.

### B34 · 09/11/2026 · Decisión · Dataset en CSV con pandas

**Qué se armó.** El script 07 genera dos tablas. articulos.csv tiene una fila por segmento de cada norma (8.066 segmentos de 306 normas, 7,8 millones de caracteres), con zona, número de artículo, offsets y texto limpio: es la entrada de los parsers LLM e híbrido. pares_candidatos.csv tiene una fila por par que propone el detector de menciones (1.091 pares: 801 de dev y 290 de test), con 17 atributos y la etiqueta en_gold: es la matriz para un clasificador con scikit-learn. Los candidatos cubren el 81 % del gold de dev y el 96 % del de test.

**Formato.** CSV, porque se lee con pandas y se abre en cualquier herramienta. No se usa .npy: guarda arreglos numéricos sin nombres de columna, y la mitad del dataset es texto o categorías. La matriz numérica se arma en memoria con pandas cuando hace falta. Parquet quedó descartado porque pyarrow no se pudo instalar en el entorno de trabajo.

**Librerías.** pandas y numpy arman el corpus y el dataset; scikit-learn se suma para el clasificador y para verificar las métricas. El parser de reglas usa solo la biblioteca estándar de Python, para que sus reglas se lean sin capas intermedias.

**Cuidados.** Ningún atributo usa el gold ni los conteos de InfoLEG, que saldrían de las mismas relaciones. La etiqueta de test solo se usa para la evaluación final. Las etiquetas son supervisión distante (B14, B27). La ficha completa está en docs/dataset.md y en el documento 03.

### B35 · 09/11/2026 · Hallazgo · Las reglas v1 no generalizan bien a los pares nuevos

**Resultado.** Sobre el corpus único, la configuración C da F1 0,652 en dev y 0,788 en test. Sobre los pares que no se usaron para diseñarla baja a 0,514 en dev (308 pares) y 0,563 en test (65 pares), contra 0,716 y 0,844 en el v1. Caen la precisión, que queda alrededor de 0,46, y el recall.

**Causas observadas.** De los 201 falsos positivos nuevos de dev, solo 27 apuntan a las semillas agregadas. Los destinos más frecuentes son la LCT, Ganancias, la Ley 24.557, el Decreto 390/76 e IVA. El Decreto 390/76 aparece porque las normas citan la LCT como «Ley 20.744 (t.o. por Decreto 390/76)» y el detector lo cuenta como otra mención. De los 73 pares nuevos que filtra la regla de zona, 72 tienen la mención solo en el VISTO, el CONSIDERANDO o un anexo. En el corpus único, la configuración sin filtro de zona supera a la C en dev (0,682 contra 0,652).

**Consecuencia.** Para el informe, es una medida directa de cuánto se ajustaron las reglas al corpus donde se diseñaron. Para el trabajo, define la iteración v2: tratar el texto ordenado como parte de la cita, revisar la regla de zona y revisar a mano 30 falsos positivos.

### B36 · 09/11/2026 · Decisión · Reglas v2: el VISTO cuenta, las citas de procedencia no

**Cómo se diseñó.** Se usó solo el dev del corpus único. Se cruzaron los pares por dónde aparece la mención y se revisaron a mano 30 falsos positivos (docs/revision_manual/revision_fp_dev_30.csv): 16 son remisiones en el articulado («las contribuciones previstas en la ley 23.660»), 9 son normas de listas largas del VISTO, 2 son citas de procedencia y 3 parecen modificaciones reales que InfoLEG no registra.

**Qué se encontró en dev.** Separar el encabezado en VISTO y CONSIDERANDO cambia todo. Los pares citados en el VISTO están en el gold el 80 % de las veces; los que solo aparecen en el CONSIDERANDO, el 24 %. En el articulado, un decreto que nombra una norma sin verbo modificatorio casi siempre remite a ella: de esos pares, solo el 19 % está en el gold.

**Regla v2 (configuración F).** Se predice el par si hay una mención no posterior al origen, que no sea una cita de procedencia, y que esté en el VISTO o en el articulado, con número, cuando el origen es una ley o la oración tiene un verbo. Se descartan las citas de procedencia («t.o. por Decreto 390/76», «sustituido por el artículo 2° del Decreto 1278/00»). «Complementarias» y «reglamentarios» dejan de contar como verbos.

**Alternativas descartadas.** Limitar el VISTO a listas cortas bajaba el recall más de lo que subía la precisión. Una primera versión del filtro de procedencia, que incluía «aprobado por», atrapaba menciones que sí están en el gold, como «Régimen de Contrato de Trabajo aprobado por la Ley 20.744», y se acotó.

**Resultado.** Con las reglas congeladas, test se evaluó una vez: F1 0,828, contra 0,788 de v1. En dev, 0,733 contra 0,652. En los 65 pares de test que no son del v1, 0,671 contra 0,563. Sin la condición del VISTO, el F1 de test cae a 0,645. v1 sigue congelado y se regenera idéntico.

**Lo que queda.** Los falsos positivos que siguen son, sobre todo, remisiones. Distinguir «conforme a la ley X» de «sustitúyese el artículo de la ley X» pide entender la oración, y esa es la tarea del parser LLM.

### B37 · 09/11/2026 · Hallazgo · Un clasificador entrenado empata con las reglas

**Qué se hizo.** El script 08 entrena tres modelos de scikit-learn (regresión logística, random forest y gradient boosting) sobre pares_candidatos.csv. El dataset ahora tiene 20 atributos, porque se sumaron las menciones en el VISTO y el CONSIDERANDO y las citas de procedencia. El modelo y el umbral se eligen con validación cruzada de 5 particiones en dev, agrupada por norma origen para que los pares de una misma norma no queden repartidos entre entrenamiento y validación. Test se evalúa una vez.

**Resultado.** Ganó el random forest, con umbral 0,45: F1 0,728 en la validación cruzada de dev y 0,823 en test, contra 0,828 de las reglas v2. En los 65 pares de test que no son del v1 da 0,683. Los atributos que más pesan son la posición de la primera mención, la fracción de artículos que nombran al destino, el largo del texto y la diferencia de años.

**Lectura.** Con atributos de superficie, un modelo entrenado no encuentra mucho más que las reglas escritas a mano. Para el informe es un buen argumento: las reglas no son una línea de base débil, y la mejora que se busque con el LLM tiene que venir de leer el texto. Además, varios atributos describen la norma más que la mención, y pueden no transferirse a otro dominio (E2, E3).

**Nota de protocolo.** El script se corrió más de una vez con test incluido. Una corrida fue para guardar en dev las probabilidades de la validación cruzada en lugar de las del modelo final, que habrían inflado la precisión en el grafo. Otra fue para verificar que el pipeline es determinista. El modelo, el umbral y el resultado de test no cambiaron.

### B38 · 09/11/2026 · Decisión · Modelo del grafo: InfoLEG y lo extraído por separado

**Modelo.** Nodos Norma (340) y Articulo (8.066, con su texto). Las relaciones son:

- RELACION_INFOLEG (775): el gold.
- RELACION_EXTRAIDA: una arista por par y por parser. Hay 771 de reglas v2, 804 de reglas v1 y 733 del clasificador.
- MENCIONA (4.430): va de un artículo a la norma que cita, con offsets, fragmento, verbo y si la regla v2 la cuenta.

**Por qué así.** Si lo de InfoLEG y lo extraído compartieran tipo de relación, una consulta podría mezclarlos sin decirlo. Con una arista por parser, comparar parsers es una sola consulta, y el LLM y el híbrido se agregan sin cambiar el modelo. Las menciones salen de un artículo que lleva el texto, así cada arista de las reglas se rastrea hasta su fragmento. Un test comprueba que las aristas de reglas v2 coinciden exactamente con los pares que tienen una mención que cuenta.

**Qué hay.** El script 09 arma los CSV en data/grafo y, con una conexión, los carga en Neo4j con restricciones de unicidad y un índice de texto completo sobre los artículos. docs/grafo.md tiene cinco consultas de ejemplo, con su pregunta en lenguaje natural, para empezar el text-to-Cypher.

**Dificultad.** Desde el entorno de Claude no se pudo descargar Neo4j. Los CSV y la trazabilidad están verificados, y dos consultas se probaron sobre una copia del grafo en memoria (networkx y grand-cypher). El Cypher de carga se corre por primera vez en la máquina del equipo.

**Abierto.** El grafo no tiene embeddings. Si el text-to-Cypher se complementa con recuperación semántica, van en los artículos, con un índice vectorial de Neo4j, pero antes hay que elegir el modelo de embeddings.

### B39 · 09/11/2026 · Dificultad · Sin acceso de escritura a GitHub desde la sesión de Claude

El repositorio usa SSH (git@github.com:JuampiJPT/grafo-legal.git), y desde la sesión de Claude no hay salida por SSH ni una cuenta de GitHub vinculada. Los commits quedan en el repositorio local de la Mac y el push lo hace el equipo. Para que Claude pueda subir cambios hay que vincular GitHub en la configuración de claude.ai.

### B40 · 09/11/2026 · Decisión · Contenedor Neo4j propio del TP

El grafo se carga en un contenedor Docker propio (neo4j-grafo-legal), con los puertos 7475 para el navegador y 7688 para Bolt y un volumen propio. En la Mac del equipo ya corre otro Neo4j que se usa para otros trabajos, y la carga con --borrar elimina los nodos Norma y Articulo: en un contenedor separado no puede tocar esa base. Los comandos están en docs/grafo.md.

### B41 · 09/11/2026 · Decisión · Una salida estándar para cualquier parser y cualquier documento normativo

**Objetivo.** El parser tiene que servir para cualquier documento normativo argentino: leyes y decretos de InfoLEG, resoluciones del digesto de la UNNOBA, normas provinciales. Todos tienen VISTO, CONSIDERANDO y artículos, y usan los mismos verbos («Sustitúyese», «Derógase»). Lo único que cambia de una fuente a otra es cómo se pasa el documento a texto.

**Decisión.** Todos los parsers (reglas, LLM, híbrido) escriben la misma tabla de relaciones (docs/salida_estandar.md). Una fila dice qué hace un artículo de la norma origen sobre una norma o un artículo destino, con uno de seis tipos: SUSTITUYE, INCORPORA, DEROGA, REGLAMENTA, MODIFICA o CITA. Cada fila lleva su evidencia (fragmento y posición), la fuente que la produjo y, si el parser la da, una confianza.

**Cómo la produce el parser de reglas v2.** El tipo sale del verbo de la oración; sin verbo, o en el VISTO o el CONSIDERANDO, es una CITA. El artículo destino sale del «artículo N de la» que precede a la mención. Se descartan las menciones de las notas editoriales de InfoLEG, que no son texto de la norma. Resultado: 3.277 relaciones (2.332 citas, 375 sustituciones, 181 incorporaciones, 176 modificaciones, 155 derogaciones y 58 reglamentaciones). El 71 % de las que no son citas tiene artículo destino.

### B42 · 09/11/2026 · Decisión · El grafo representa lo que hace cada norma; InfoLEG queda afuera

**Problema.** El grafo anterior (B38) servía para comparar parsers contra InfoLEG: tenía una arista por parser que solo decía «hay un vínculo». No respondía qué hace una norma sobre otra, ni sobre qué artículo. Para el objetivo del TP (consultar el grafo en lenguaje natural) no servía.

**Decisión.** El grafo se arma solo con la salida estándar. Tiene (:Norma)-[:CONTIENE]->(:Articulo) y aristas tipadas de un artículo a otro artículo, o a la norma entera si el texto no dice cuál. Ejemplo: (art. 70 del Decreto 70/2023)-[:SUSTITUYE]->(art. 80 de la Ley 20.744). La evidencia va en la arista. InfoLEG no forma parte del grafo: se usa como referencia para evaluarlo.

**Qué responde ahora.** Preguntas como «¿qué artículos de la LCT sustituyó la Ley 27.802?» (52 artículos), «¿quién cambió por última vez el artículo 245 de la LCT?» (la Ley 27.802) o «¿qué decretos reglamentan la Ley de Riesgos del Trabajo?». Las consultas están en docs/grafo.md.

### B43 · 09/11/2026 · Hallazgo · El grafo devuelve lo que se le cargó; contra InfoLEG, las citas son el problema

**Cómo se evalúa.** El script 11 lee las relaciones desde el grafo, no desde los archivos del parser. Puede leerlas del Neo4j del equipo o de una copia en memoria armada con el mismo código.

**Ida y vuelta.** El grafo devuelve exactamente las 3.277 relaciones cargadas, con el mismo tipo y el mismo artículo destino.

**Contra InfoLEG.** Las relaciones se proyectan a pares de normas con la regla F de las reglas v2 y dan las mismas métricas: F1 0,733 en dev y 0,828 en test. Contar cualquier relación sube el recall de test a 0,958, pero baja la precisión a 0,669. Por tipo, los pares con SUSTITUYE o DEROGA están en InfoLEG entre el 90 % y el 100 % de las veces; los que solo tienen citas, alrededor del 63 %, y explican 160 de los 185 falsos positivos. Por semilla, el grafo recupera el 72 % de las modificatorias de la LCT, con 90 % de precisión.

**El tipo.** InfoLEG no dice si una norma sustituye, deroga o cita, así que el tipo se revisó a mano en 36 relaciones, 6 por tipo. El tipo es correcto en 24 (67 %) y el artículo destino en 30 (83 %). MODIFICA es el más débil, con 1 de 6. Los errores son nominalizaciones o verbos que no actúan tomados como acción («la derogación del artículo 2°», «deberá proponer la reglamentación»), el «texto ordenado» de una cita, y las incorporaciones con la forma «como artículo 53 bis a la Ley».

**Consecuencia.** El tipado por verbo es la parte que más hay que mejorar. Es la próxima iteración de las reglas, sobre dev, y es donde se espera que aporte el parser LLM. La revisión es una primera pasada de Claude, pendiente de validación humana.

### B44 · 09/11/2026 · Decisión · Documento del parser y del grafo, contado paso a paso

**Qué se hizo.** Se escribió un documento que cuenta cómo se construyó el sistema, en el orden en que se hizo. Está en el Drive como «06 - Parser y grafo: arquitectura y construcción paso a paso» y en el repositorio como docs/arquitectura_parser_y_grafo.md. Las etapas son nueve:

- corpus y referencia;
- textos y adaptador;
- segmentación;
- detección de menciones;
- reglas v1 y el hallazgo de que no generalizan;
- reglas v2 y el clasificador de referencia;
- salida estándar con relaciones tipadas;
- arquitectura del grafo;
- evaluación del grafo.

**Por qué.** La bitácora registra cada decisión por separado. Para el informe y la defensa hace falta además una explicación continua del parser y del grafo. El documento sigue un artículo real de punta a punta (artículo 70 del Decreto 70/2023, que sustituye el artículo 80 de la LCT), desde el HTML hasta la consulta Cypher que lo devuelve, e incluye el mapa de scripts y módulos.

**Limitación detectada al escribirlo.** Cuando una norma sustituye un artículo, el texto nuevo entre comillas queda dentro del artículo que sustituye. Las menciones de ese texto citado generan citas extra del mismo artículo. Queda como mejora del tipado.

### B45 · 16/11/2026 · Hallazgo · Evaluación por subtareas: la detección y la normalización no pierden pares

**Qué pide la consigna.** Evaluar por separado la detección de referencias, la normalización (con la exactitud de vinculación y la proporción de referencias no resueltas) y la extracción de relaciones, y clasificar los errores en norma no detectada, mal normalizada, relación invertida, relación inexistente, tipo incorrecto, referencia ambigua y destino ausente del corpus.

**Cómo se mide.** Con el script 12 (`results/subtareas/RESULTADOS.md`).

- **Detección.** Se compara con una búsqueda laxa del número de la norma destino («20.744» o «20744»), independiente del detector, y con una muestra de 60 menciones revisadas a mano.
- **Normalización.** Cada mención se resuelve contra el catálogo del corpus y contra el catálogo completo de InfoLEG (106.466 leyes, decretos y decretos-leyes).
- **Extracción.** Se mide de punta a punta y condicional a los pares candidatos.

**Resultados.**

- **Detección.** Recall 1,00 en dev y en test: cuando el número de la norma destino está en el texto, el detector lo encuentra. Precisión 0,97 en la muestra; los 2 casos dudosos son nombres de tributos tomados como alias de la ley.
- **Normalización.** El 55,6 % de las 8.062 menciones por número no se resuelve, pero casi todas (48,0 %) son normas reales fuera del corpus. Otro 7,2 % son decretos citados sin año que en InfoLEG tienen varias candidatas. La exactitud de vinculación verificable es 95,9 %. El 4,1 % restante son decretos sin año que se resuelven solo porque el corpus tiene uno con ese número: es la cota de error de la decisión de mundo cerrado.
- **Extracción.** En test, F1 0,828 de punta a punta y 0,842 condicional a los candidatos. La regla recupera el 91 % de los pares que ya pasaron los pasos anteriores.

**Embudo de test.** Hay 192 pares; 185 nombran a su destino en el texto; los 185 se detectan y se normalizan bien; 168 los extrae la regla. De los 24 que se pierden, 7 no tienen mención y 17 los descarta la regla.

**Taxonomía de test.**

- Falsos negativos: 17 relaciones descartadas por la regla y 7 sin mención explícita. No hay normas no detectadas ni mal normalizadas.
- Falsos positivos: 38 relaciones inexistentes (citas que InfoLEG no registra) y 8 referencias ambiguas. No hay relaciones invertidas: las elimina la restricción temporal.
- Destino ausente del corpus: 203 pares que la regla extraería si el destino estuviera en el catálogo. Contra la base complementaria completa de InfoLEG, el 62 % de ellos son vínculos registrados (54 % en dev). El parser generaliza fuera del corpus, con unos 20 puntos menos de precisión.

### B46 · 16/11/2026 · Hallazgo · El modelo con contexto textual, solo, no supera a las reglas; en un híbrido, ayuda en la zona gris

**Qué faltaba.** La consigna pide un método basado en modelos «a partir del contexto textual». El clasificador de B37 usaba solo atributos de superficie.

**Qué se hizo.** El script 13 (`results/modelo_contextual/RESULTADOS.md`).

- **Texto del par.** Por cada par candidato se juntan los fragmentos de sus menciones. La mención del destino se reemplaza por `DESTINO`, los dígitos por `#`, y adelante va la parte del documento.
- **Modelo.** TF-IDF de unigramas y bigramas con regresión logística, con y sin los atributos de superficie. Mismo protocolo que B37: validación cruzada agrupada en dev para elegir C y umbral, y test una vez.
- **Híbrido.** Las reglas deciden los casos seguros (VISTO, o articulado con verbo: el 82 % está en el gold) y los descartes seguros (9 %). El modelo decide la zona gris (articulado sin verbo, solo CONSIDERANDO, solo alias: 40 % en el gold).

**Resultados en test.**

| Método | F1 |
|---|---|
| Solo texto | 0,761 |
| Texto + superficie | 0,783 |
| Reglas v2 | 0,828 |
| Híbrido con el modelo de texto + superficie | 0,839 (P 0,780, R 0,906) |

**Lectura.** Con 801 pares de entrenamiento, el TF-IDF aprende rasgos del período de dev que no transfieren a las normas de 2020 en adelante. Donde ayuda es en la zona gris: sube el recall de 0,875 a 0,906 sin perder precisión. Los n-gramas con más peso a favor son técnica legislativa («parte_articulado articulo», «la destino», «siguiente»); en contra, remisiones de contenido («alcance», «caso», «contrato de»).

### B47 · 16/11/2026 · Hallazgo · Tipo de relación sobre 78 casos: macro-F1 0,672; el error dominante es una cita tomada como acción

**Qué se hizo.** La revisión de tipos de B43 se amplió de 36 a 78 casos, 13 por tipo predicho (`docs/revision_manual/revision_tipos_78.csv`). Con el script 16 (`results/tipos/RESULTADOS.md`) se calculan la matriz de confusión de la muestra y las métricas de la población, ponderando cada caso por la inversa de su probabilidad de muestreo.

**Resultados.**

- En la muestra, el tipo es correcto en 53 de 78 casos y el artículo destino en 67 de 78.
- En la población, la exactitud es 0,754 y la macro-F1 0,672.
- Por tipo: `SUSTITUYE` tiene F1 0,94 y `MODIFICA` 0,18.

**Errores.** 21 de los 25 errores son citas tomadas como acción. Hay errores nuevos: «Impuesto al Valor **Agregado**» leído como verbo de incorporación (4 de 7 casos nuevos de `INCORPORA`), y el «Artículo 1°» de la propia norma tomado como artículo destino en «Apruébase la reglamentación de la Ley …».

**Decisión.** Los errores se documentan y no se corrigen sobre esta muestra: corregirlos mirando los casos que después se usan para medir inflaría el resultado. La revisión es de Claude y está pendiente de validación humana y de un segundo anotador para el kappa.

### B48 · 16/11/2026 · Decisión · Parser LLM con verificación de la cita, caché reproducible y grafo aparte

**Diseño** (`docs/parser_llm.md`, `src/grafo_legal/extractores/llm.py`).

- **Contrato.** El parser LLM cumple el mismo que el de reglas: segmentos del adaptador como entrada, salida estándar como salida.
- **Entrada.** Un prefiltro sin LLM manda solo los segmentos del encabezado y del articulado que nombran alguna norma. Van en lotes de hasta 12.000 caracteres, con el identificador de cada artículo.
- **Respuesta.** El modelo (`claude-sonnet-5-5`, temperatura 0) recibe la definición de los seis tipos y devuelve un JSON por relación, con la cita textual.
- **Verificación.** La cita se busca en el texto: si no está, la relación se descarta y se cuenta como alucinación. Si está, se guardan sus offsets, y la relación queda trazable igual que en las reglas.
- **Normalización.** Con el mismo catálogo que las reglas, así la comparación mide solo la lectura del texto.
- **Reproducibilidad.** Cada respuesta se guarda en una caché versionada, indexada por la huella del pedido. Volver a correr no llama a la API.

**Grafo aparte.** El grafo del LLM va a `data/grafo_llm/`, y el de las reglas no se toca. En Neo4j se carga sin `--borrar`: sus aristas llevan `fuente = 'llm'` y conviven con las de `reglas_v2` sobre los mismos nodos. Así se pueden comparar las dos lecturas de un mismo artículo.

**Costo.** Son 590 pedidos y unos 1,8 millones de tokens de entrada: unos USD 8 con Sonnet 5.5, menos de USD 0,50 con Haiku 5.5.

**Estado.** El código está probado con respuestas simuladas, pero no se corrió: falta la clave de la API. No hay LLM local (no está Ollama y Hugging Face está bloqueado por la red); la API de Anthropic sí es accesible.

### B49 · 16/11/2026 · Decisión · Tabla final con intervalos de confianza por bootstrap

**Qué se hizo.** El script 17 (`results/comparacion/`) pone todos los métodos sobre el mismo test, con intervalos del 95 % por bootstrap pareado sobre normas origen (2.000 réplicas). Se remuestrean normas porque los pares de una misma norma no son independientes.

**Resultado.**

- Contra las reglas v2 (0,828), el híbrido gana 1,1 puntos, con intervalo de −2,2 a +4,0, y el clasificador de superficie pierde 0,4, con intervalo de −3,5 a +2,5. Ninguna de las dos diferencias es significativa.
- Los modelos contextuales solos sí son significativamente peores: solo texto, −6,6 puntos [−13,6; −1,5]; texto y superficie, −4,5 [−8,6; −0,7].
- Con 192 pares de test, solo se distinguen diferencias de unos 4 puntos o más.

### B50 · 16/11/2026 · Decisión · Código comentado y guía de lectura para la presentación

**Qué se hizo.** Se agregaron comentarios que explican cada paso del pipeline en el adaptador, el detector, el catálogo, las reglas, el tipado y el grafo:

- cada expresión regular, pieza por pieza;
- por qué se toma cada decisión;
- un ejemplo real en cada función.

Los comentarios no cambian el comportamiento: se volvió a correr el pipeline y las evidencias, las relaciones, el dataset y el grafo dieron idénticos byte a byte. La huella de `reglas_v2.py` cambió solo por los comentarios.

**Documentos nuevos.** `docs/guia_codigo.md` recorre el código en el orden en que viaja un documento, con el artículo 70 del Decreto 70/2023 como ejemplo. `docs/comparacion_con_el_gold.md` explica cómo se compara con el gold y es la base de la sección «Diseño experimental» del artículo. Los dos, junto con el parser LLM y los resultados nuevos, están en el Drive como «07 - Evaluación completa, parser LLM y guía del código».

### B51 · 16/11/2026 · Hallazgo · Cada error explicado; corrige la clasificación de B45

**Qué se hizo.** Cada falso negativo y cada falso positivo del parser de reglas v2 tiene ahora una causa concreta, una explicación y la evidencia del texto que la muestra (script 18, `results/errores_explicados/`). Son 304 errores de dev y 70 de test.

- **Descartados por la regla:** la causa sale automáticamente de las evidencias del par.
- **Sin mención:** se asignó con reglas y, para 57 pares, con una revisión manual de Claude pendiente de validación.
- **Falsos positivos:** la causa sale de por qué pasó la regla F, con 8 casos corregidos a mano.

**Corrección de B45.** Explicar los casos uno por uno mostró dos errores que B45 no había visto:

1. **El año escrito como fecha.** «Decreto N° 467 del 14 de abril de 1988»: el detector solo lee el año en la forma «467/88». Cuando el corpus tiene más de un decreto con ese número, la mención queda sin resolver; cuando tiene uno solo, se vincula a ese aunque sea de otro año.
   - De las 580 menciones ambiguas, 360 tienen el año en la fecha.
   - De las 147 resueltas por mundo cerrado, la fecha permite verificar 117: 86 están bien y 31 son otro decreto con el mismo número.
   - La exactitud de vinculación estimada pasa a 99,1 %.
   - Se pierden por esto 10 pares del gold (9 en dev, 1 en test) que en B45 figuraban como descartados por la regla, y hay 9 falsos positivos que en realidad son vinculaciones erróneas.
2. **Nombres que el gazetteer no tiene.** «Ley de Ministerios» y «L.C.T.» hacen perder 2 pares de dev. El recall de detección en dev pasa de 1,000 a 0,996; en test sigue en 1,000.

**Por qué se pierden los pares de test.** De los 24:

- 16 los descarta la regla: decretos que nombran la norma sin verbo o solo en el CONSIDERANDO, leyes de impuestos citadas por nombre y una cita de texto ordenado;
- 5 son decretos de texto ordenado que el texto no nombra («Ley de Impuesto al Valor Agregado (t.o. en 1997)» vincula al Decreto 280/97);
- 2 no se pueden explicar desde el texto (el DNU 70/2023 con las leyes 23.789 y 18.345);
- 1 es el año escrito como fecha.

**Los 46 falsos positivos de test.**

- 24 son normas citadas en la lista de fundamentos del VISTO.
- 14 son remisiones desde el articulado de una ley.
- 3 tienen un verbo que no actúa sobre la norma.
- 1 es una procedencia no filtrada («creado por la ley 25.565 y … modificado por ley 27.637»).
- 1 es otro decreto con el mismo número.
- 2 son decretos sin año.
- 1 es un error del propio texto: el Decreto 841/22 llama «Ley de Impuesto a las Ganancias» a la Ley 20.744.

**Qué registra InfoLEG sin que el texto lo diga.** De los 80 pares sin mención:

- 36 son normas que complementan a la destino sin citarla;
- 9 son decretos de texto ordenado;
- 8 son derogaciones genéricas;
- 8 son modificatorias de una ley derogada;
- 7 tienen el texto incompleto en InfoLEG;
- 5 son referencias conceptuales («el convenio colectivo de la actividad»);
- 3 nombran la ANSES en lugar del Decreto 2741/91;
- 2 parecen errores del gold, como el Decreto 12/99, que designa un ministro interino de Relaciones Exteriores y aparece vinculado a la Ley de Asociaciones Sindicales;
- 2 no son verificables.

**Decisión.** El parser congelado no cambia. Leer el año escrito como fecha queda como la primera mejora de una v3, para diseñar sobre dev y medir aparte.

### B52 · 16/11/2026 · Hallazgo · Reglas v3: corrigen la normalización, empatan en test

**Qué se hizo.** Con los errores explicados en B51 se diseñó una v3 de las reglas, mirando solo dev (`reglas_v3.py`). La v3 hace seis cambios:

1. lee el año escrito como fecha («Decreto 467 del 14 de abril de 1988»);
2. agrega al gazetteer «Ley de Ministerios» y «L.C.T.», y saca los nombres sueltos de tributos;
3. «Valor Agregado» deja de leerse como verbo;
4. extiende el filtro de procedencia («modificado por», «reemplazado por»);
5. aplica la regla F3: en el articulado, una norma nombrada sin número cuenta si la oración tiene verbo;
6. ignora el número del propio artículo al tipar.

Cada cambio se midió por separado en dev (ablación, script 19). Después la v3 se congeló y test se evaluó una vez. La v2 no se tocó: sus salidas dan idénticas byte a byte.

**Resultados.**

- **Dev:** F1 de 0,733 a 0,750. El año escrito como fecha aporta 1,5 puntos solo; el alias con verbo resta si se aplica sin limpiar el gazetteer.
- **Test:** F1 de 0,828 a 0,826, con una diferencia de −0,1 puntos e intervalo del 95 % entre −1,9 y +1,3. **No mejora.** Las versiones difieren en 9 pares:
  - gana 3 del gold;
  - elimina 1 falso positivo;
  - agrega 3 falsos positivos: leyes nombradas con un verbo que no actúa sobre ellas;
  - pierde 2 del gold, por una regresión: el filtro nuevo de procedencia descarta «texto sustituido por la ley 24.674».
- **Normalización:**
  - ambiguas, de 580 a 251;
  - vinculaciones erróneas verificables, de 31 a 0;
  - pares del gold perdidos ahí, de 10 a 0.
- **Tipo**, sobre los 78 casos: macro-F1 de 0,672 a 0,703. La medida es optimista, porque las correcciones salieron de esa misma muestra.

**Decisión.** La v2 sigue siendo el parser de referencia del artículo, porque es la que se congeló primero y la v3 no la supera en test. La v3 se informa como experimento: muestra que la detección y la normalización ya no limitan, y que lo que queda es la decisión de la regla. Su grafo está aparte, en `data/grafo_v3/` y con `fuente = 'reglas_v3'` en Neo4j. La regresión y el alias «l.c.t.», que no se encuentra por el punto final, quedan para una v4 diseñada sobre dev; no se corrigen después de ver test.

**Documentos.** `docs/analisis_de_fallos.md` reúne todos los fallos con su causa y su ejemplo. `docs/como_se_detecta_una_relacion.md` explica el pipeline con un caso real. Los dos están en el Drive como «08 - Análisis de fallos y cómo se detecta una relación».

### B53 · 16/11/2026 · Dificultad · La API no respondía desde el entorno de la Mac; se saca la temperatura

**Qué pasó.** La primera llamada al parser LLM falló dos veces:

1. **Temperatura.** El SDK 2.9.0 ya no acepta el parámetro `temperature` para los modelos 5.5. Se sacó del pedido. La reproducibilidad no dependía de él: viene de la caché, porque cada respuesta se guarda con la huella del pedido.
2. **Error 401 (no autorizado).** Primero se atribuyó a la clave, porque empieza con `sk-ant-usr`, y ese diagnóstico **era erróneo**. Las claves que crea hoy la Console son personales, están vinculadas a un usuario y tienen ese prefijo; son válidas. El 401 lo devolvía el proxy de red del entorno que usa Claude en la Mac: con una clave inventada respondía igual, «Unauthorized» en texto plano y no el error JSON de la API. Desde el espacio de trabajo en la nube, la misma clave responde 200.

**Qué se hizo.** El parser LLM se corre desde el espacio de trabajo en la nube. La clave queda en `.anthropic_key`, que está en `.gitignore`. El piloto de 5 normas dio:

- 12 pedidos, unos 54.000 tokens de entrada y 16.000 de salida;
- 127 menciones devueltas por el modelo, y ninguna cita que no esté en el texto;
- 115 de esas menciones son normas fuera del corpus (mundo cerrado) y 3 no tienen número;
- 9 relaciones aceptadas.

Después se lanzó la corrida completa, con 8 pedidos en paralelo (`--hilos 8`). El resultado es el mismo que en serie, porque cada respuesta se guarda en la caché. **Se cortó en 230 de 590 lotes porque se acabó el crédito de la cuenta.** Lo hecho no se pierde: queda en la caché y no se vuelve a pagar. El costo real es mayor que la estimación:

- en 230 lotes, unos 990.000 tokens de entrada y 276.000 de salida, alrededor de USD 4,75;
- para todo el corpus, unos USD 12 a 13, contra los USD 8 estimados.

La diferencia está en los tokens de salida, que la estimación no contaba, y en la longitud del prompt.

### B54 · 16/11/2026 · Hallazgo · El parser LLM sube el recall y el tipado; la intersección con las reglas es la única mejora significativa

**Qué se hizo.** Se completó la corrida del parser LLM: 590 lotes, `claude-sonnet-5-5`, unos USD 14. La corrida tuvo dos cortes:

- por falta de crédito;
- por el límite de gasto del workspace de la clave, que el equipo subió.

Ninguno de los dos hizo perder trabajo, porque lo hecho quedó en la caché. Después se corrieron los scripts 15, 16 y 17 y se armó el grafo en `data/grafo_llm/`. Los grafos de reglas no cambian.

**Resultados.**

- **Alucinación:** 8 de 7.688 citas (0,1 %) no están en el texto, y se descartaron.
- **Proyección:** la proyección elegida en dev es la regla F aplicada a lo que extrae el LLM. Test: P 0,763, R 0,938, F1 0,841, contra 0,828 de las reglas v2. La diferencia, +1,3 puntos con intervalo de −1,9 a +4,0, no es significativa.
- **Intersección:** cuenta una relación solo si la extraen las reglas y el LLM. F1 0,838 y precisión 0,804. Es **la única mejora significativa sobre las reglas**: +1,0 puntos, con intervalo de +0,2 a +2,5. Descarta 5 falsos positivos sin perder ninguna relación del gold.
- **Tipo**, sobre los 78 casos: macro-F1 ponderada de 0,672 a **0,883**, y exactitud de 0,754 a 0,849. No está sesgada, porque el LLM no se ajustó con esa muestra.
- **Errores de las reglas en test:** el LLM recupera 12 de los 24 falsos negativos y no pierde ninguna relación que las reglas encontraban. Recupera sobre todo decretos sin verbo en la oración, el CONSIDERANDO y nombres propios. No recupera los 5 de texto ordenado implícito ni los 2 no verificables, que el texto no contiene.
- **Falsos positivos:** el LLM comparte con las reglas los del VISTO (24) y las remisiones (14), y agrega 15 propios.

**Decisión.** Ver D26. Para el artículo, la comparación queda así:

- las reglas son una línea de base fuerte y barata;
- el LLM mejora el recall y, sobre todo, el tipo de relación;
- el híbrido por intersección es el que mejor balancea precisión y recall.

### B55 · 18/11/2026 · Decisión · Parser híbrido en cascada: las reglas filtran y el LLM decide la zona gris

**Por qué.** El híbrido de B54 combinaba al final las salidas de dos parsers. El equipo pidió un parser híbrido propio, en el que las reglas y el LLM trabajen articulados.

**Cómo funciona** (`docs/parser_hibrido.md`):

1. La parte determinista de la v3 (estructura, detección y catálogo) genera un candidato por par de normas.
2. Las reglas lo ubican en una zona: descarte, seguro (articulado, con verbo y sin procedencia, 91 % en InfoLEG) o gris (todo lo demás).
3. El LLM juzga cada candidato con los fragmentos donde se nombra. Da una probabilidad de vínculo, el tipo, el artículo y una cita.
4. Seguro: se acepta. Gris: la regla F3 opina primero y el LLM la corrige solo con confianza (descarta con menos de 0,15, agrega con 0,5 o más).
5. La cita tiene que estar en el fragmento.

El LLM nunca inventa destinos: solo juzga lo que el catálogo resolvió.

**Iteraciones en dev.**

- **Prompt v1, estricto:** aceptó 64 de 544 pares grises, y 296 estaban en InfoLEG; además, 199 respuestas traían código dentro del JSON. F1 en dev: 0,52. Se descartó.
- **Prompt v2:** criterio amplio de InfoLEG («modifica o complementa»), las tasas de base del VISTO y del CONSIDERANDO, una probabilidad y un parseo tolerante.
- **Políticas comparadas en dev:**
  - que el LLM decida toda la zona gris: F1 0,729 con su mejor umbral;
  - que además pueda vetar los seguros: 0,728;
  - que la regla opine primero (política «previa»): **0,758**, el mejor F1 de dev de todo el trabajo.

  Se congeló la previa con 0,15 y 0,5, en lugar del máximo exacto del barrido (0,4), para no ajustar al ruido.

**Test (una vez).** P 0,761, R 0,911, F1 0,829. Las reglas v2 dan 0,828: +0,2 puntos, con intervalo de −3,4 a +3,2. No es significativo.

- **Zona gris:** el LLM agrega 19 pares que la regla rechazaba (8 en InfoLEG) y saca 6 que aceptaba (4 bien sacados).
- **Tipo**, sobre los 78 casos: macro-F1 0,763, contra 0,672 de las reglas y 0,883 del LLM puro. La exactitud baja a 0,646, porque los pares aceptados por el VISTO quedan como MODIFICA.
- **Costo:** USD 3,6 por corrida, contra USD 14 del LLM puro. Más USD 3,4 del prompt v1 descartado.

**Decisión.** Ver D27. El híbrido en cascada se informa como tercer parser. El cuello de botella vuelve a ser el VISTO: el criterio de InfoLEG para vincular una norma citada como fundamento no está en el texto. Grafo en `data/grafo_hibrido/`, con `fuente = 'hibrido'`.

### B56 · 20/11/2026 · Dificultad · Descarga del digesto de la UNNOBA para la PI4

**Contexto.** Para la PI4 hace falta un corpus normativo distinto de InfoLEG, sin relaciones estructuradas. El candidato es el digesto de la UNNOBA (B19, B22). Su robots.txt prohíbe todo acceso automático (`Disallow: /`) y la página de transparencia de la UNNOBA no publica la normativa: solo enlaza al Estatuto y al digesto. Desde los entornos de Claude y de ChatGPT el sitio no responde.

**Qué se hizo** (el 20/11, en parte en una sesión de ChatGPT del equipo):

1. Se guardaron a mano los HTML de once secciones del digesto, entre ellas Posgrado, Cursadas y Escuela de Tecnología.
2. En cada documento hay dos enlaces: `documento.frame.php?cod=N` (versión normal) y `documento.frameim.php?cod=N&arch=ARCHIVO.pdf` (versión con firmas). Se eligió **la versión con firmas**.
3. Las secciones dieron 1.254 apariciones. Deduplicadas por `cod`, quedan **898 documentos únicos**: muchos aparecen en varias secciones (por ejemplo Cursos, Alumnos, Posgrado y Aranceles).
4. ChatGPT armó dos descargadores:
   - `kit_descargador_unnoba_237`, la primera versión, solo para Posgrado, que generaba un ZIP;
   - `Descargar_PDFs_UNNOBA.command`, la versión final, con el catálogo de 898 documentos incorporado. Baja cada PDF por separado, omite los que ya están, reintenta tres veces y registra los fallos.

   No se pudieron probar contra el servidor desde ChatGPT.
5. El equipo corrió el descargador desde su propia computadora y copió los PDF a `data/textos/unnoba/pdf/`.

**Verificación (Claude, 20/11).** Había 941 archivos y todos eran PDF válidos: empiezan con `%PDF` y ninguno pesa menos de 2 KB. Ocupan 390 MB.

- **898** son los del catálogo, con el nombre original del digesto (por ejemplo `RESOLUCIONHCS20181462.pdf`).
- **43** vienen de bajadas anteriores hechas con el navegador, con otro formato de nombre (`RES_HCS_Nº_004_07.pdf`). De esos:
  - las copias «(1)» o «(2)» son idénticas byte por byte. Al copiar, Finder avisó de nombres repetidos, y elegir «omitir» dejó el archivo que ya estaba.
  - otros tienen el mismo contenido que uno del catálogo, con el otro nombre (`ORDENANZA200701.pdf` y `ORD_HCS_Nº_001_07.pdf`).
  - 14 son documentos que no están entre los 898 (por ejemplo RES HCS 1407/18, 872/14 y 880/14).
- En total hay **912 documentos distintos**.

**Datos personales.** Muchas resoluciones (becas, designaciones) traen nombres y DNI. Los PDF no van al repositorio: `*.pdf` ya está en `.gitignore`. Las listas con resúmenes tampoco deberían publicarse sin anonimizar.

**Ordenamiento (con el acuerdo del equipo).**

- Las 29 copias (el mismo contenido con otro nombre, o «(n)») pasaron a `pdf/_duplicados/`, con el motivo de cada una en `LEEME.csv`. Quedaron 912 PDF, uno por documento.
- Los descargadores y un ejemplo del visor se copiaron a `tools/digesto_unnoba/`; la primera versión, a `historico_kit_237/`.
- El catálogo, que estaba dentro del `.command`, se pasó a `data/corpus_unnoba/catalogo.csv` y se le sumaron los 14 documentos que no estaban: 912 filas.
- En Descargas se borraron los duplicados (`PDF_UNNOBA/`, el kit y sus ZIP), después de verificar que cada PDF estaba en el proyecto.
- La lista de Posgrado con resúmenes, que trae nombres y DNI, quedó fuera de git.

**Pendiente.** Elegir la muestra a anotar para la PI4: reglamentos y sus modificaciones, más casos negativos. *(Hecho en B57.)*

### B57 · 20/11/2026 · Hallazgo · PI4: el pipeline se transfiere al digesto de la UNNOBA si el adaptador lleva el vocabulario de la fuente

**Contexto.** La PI4 pregunta si el pipeline funciona sobre otro corpus cambiando solo el adaptador. Con los 912 PDF del digesto (B56) se armó una muestra, se anotó a mano y se corrieron los tres parsers sin ajustarlos.

**Qué se hizo.**

1. **Muestra.** 70 documentos, con semilla 20261120 (`data/corpus_unnoba/muestra_pi4.csv`):
   - 7 ordenanzas;
   - 48 resoluciones de los temas de reglamentos;
   - 15 al azar.
2. **Texto.** `pdftotext` para todos. 38 son escaneados y se pasaron por OCR con tesseract en español; los datos de idioma se bajaron a la VM.
3. **Gold.** Claude leyó los 70 documentos y anotó 108 pares (documento, norma) en tres clases:
   - MOD (19): modifica, ratifica, deja sin efecto, prorroga, reglamenta…;
   - APLICA (26): el dispositivo aplica la norma o se dicta en su marco;
   - CITA (63): antecedente, competencia o remisión.

   Está en `data/corpus_unnoba/gold_pi4.tsv` y queda **pendiente de validación del equipo**.
4. **Adaptador** (`src/grafo_legal/fuentes/unnoba.py`):
   - une las líneas del PDF;
   - separa VISTO, CONSIDERANDO y articulado;
   - detecta las formas de cita propias del digesto: «Resolución (CS) Nro. 44/08», «Res. (CD.ET)», «Ordenanza (CS) 14/09», resoluciones del Rector, listas y la barra que el OCR lee como «1»;
   - normaliza a claves `TIPO-EMISOR-NÚMERO-AÑO`, en mundo abierto.

   Tiene 3 tests (`tests/test_unnoba.py`).
5. **Corrida** (`scripts/21_pi4_unnoba.py`): las reglas F y F3, el parser LLM y el híbrido en cascada, con sus prompts tal cual. Además, la variante «vocab», que cambia solo las frases de los prompts que enumeran tipos de norma. Fueron 252 pedidos, unos USD 3.

**Resultados** (vínculo = MOD ∪ APLICA, 45 pares; gold de la revisión 1, reemplazado en B58):

| Método | P | R | F1 |
|---|---|---|---|
| Reglas F = F3 | 0,695 | 0,911 | 0,788 |
| LLM, prompt de InfoLEG | 0,500 | 0,200 | 0,286 |
| LLM, prompt «vocab» | 0,632 | 0,800 | 0,706 |
| **Híbrido** | **0,759** | **0,978** | **0,854** |
| Híbrido «vocab» | 0,738 | 1,000 | 0,849 |

- El híbrido supera a F3 por +0,066 de F1 (IC 95 % +0,018 a +0,137). Es significativo, a diferencia de InfoLEG.
- La detección de menciones del adaptador da F1 0,981. Es optimista, porque el detector se escribió leyendo los mismos documentos.
- Solo MOD: las reglas dan R 0,526 y el LLM «vocab», 0,684 con P 1,0.

**Qué se pierde al cambiar de corpus.**

1. **El prompt del LLM nombra leyes y decretos.** Con él, el LLM ignora las resoluciones y encuentra 19 de las 108 menciones. Al cambiar tres frases, encuentra 98. El vocabulario de los prompts es parte del adaptador.
2. **El léxico de verbos es el de InfoLEG.** InfoLEG usa la forma impersonal («Sustitúyese»). La UNNOBA usa el infinitivo: «Ratificar», «Dejar sin efecto», «Extender la aplicación». 9 de los 19 MOD quedan sin verbo, y solo 9 pares caen en la zona segura del híbrido.
3. **Lo que agrega la v3 no aparece en este corpus:** F y F3 dan lo mismo.
4. **Un solo criterio de anotación explica casi todos los falsos positivos.** En ocho resoluciones de inscripción, la remisión a la Res. Ministerial 1523/90 y a la Ley 25.871 se anotó como CITA. Son 14 de los 18 falsos positivos de las reglas y los 14 del híbrido.
   - Si se anotan como APLICA, F3 da 0,915 y el híbrido 0,957.
   - La política «cascada» dejaría afuera esas remisiones: 0,944 con el gold actual.
   - El orden de los métodos no cambia: el híbrido queda primero y el LLM con el prompt de InfoLEG, último.

**Correcciones del gold.** Al revisar la primera corrida aparecieron 9 menciones reales que la anotación había salteado: los modelos de constancia de los docs 33, 34 y 36, una cita incidental, una bibliografía y un sello. Se agregaron como CITA, marcadas `[revision: omision de anotacion]`. No cambian el vínculo. El Estatuto del doc 15 se dejó sin corregir, para no seguir ajustando el gold.

**Datos personales.** Los textos de la muestra, el OCR y la cache del LLM traen nombres y DNI, y quedan fuera de git (`.gitignore`). Los CSV de salida no tienen el «motivo» del LLM.

**Pendiente.**

- Que el equipo valide el gold, sobre todo la clase de las remisiones.
- Que un segundo anotador repita una parte, para el kappa.
- Decidir si «ratificar» y el infinitivo de «dejar sin efecto» entran en una v4 de los verbos, diseñada sobre dev de InfoLEG y no sobre esta muestra.

Detalle en `results/pi4_unnoba/RESULTADOS.md` y `docs/pi4_digesto_unnoba.md`. Decisión D28.

### B58 · 20/11/2026 · Decisión · Revisión del gold de la PI4: las remisiones que definen a quién alcanza la resolución son APLICA

**Contexto.** El equipo pidió revisar el gold de la PI4 con una mirada humana y tomar una decisión sobre la duda que más pesaba (B57). En la revisión 1, siete resoluciones de inscripción (docs 33, 34, 35, 36, 38, 39 y 40) tenían dos menciones anotadas como CITA:
- la Res. Ministerial 1523/90, en un artículo que dice que los aspirantes «no incluidos» en ella quedan comprendidos en la presente;
- la Ley de Migraciones 25.871, en la constancia de inscripción «en el marco del art. 7°».

Esos 14 pares explicaban 14 de los 18 falsos positivos de las reglas.

**Qué se hizo.** Claude releyó los 108 pares en contexto, con las oraciones donde aparece cada norma, y aplicó las definiciones escritas antes de correr los métodos.

**Decisión.** Las 14 remisiones pasan a **APLICA**, por estas razones:
1. **Coherencia.** En los docs 25 y 26 ya era APLICA la misma construcción («los alumnos incluidos en las situaciones contempladas por la Resolución…»): la norma sirve para definir a quién alcanza lo que se dispone.
2. **Ubicación.** Está en el dispositivo («Establecer que…»), no en el considerando.
3. **La constancia ejecuta el art. 7 de la ley.** Inscribe al aspirante en el marco de ese artículo, y el modelo de constancia lo aprueba el articulado.
4. **Criterio de InfoLEG.** Coincide con el «complementa» de InfoLEG que usa el TP: se usa la norma para definir a quiénes alcanza la medida.

Además:
- la Res. (CD.ET) 278/2016 del doc 12 pasa a APLICA, porque el art. 2 exige el formato que aprobó esa resolución;
- la Res. (D.ET) 313/2016 del doc 10 pasa a MOD, porque el Consejo aprueba lo actuado ad referéndum: es una ratificación implícita;
- se agrega el Estatuto del doc 15 como CITA.

Se mantuvieron como CITA los formularios de la Res. 368/2010, el Estatuto como competencia y las menciones incidentales. Detalle en `docs/pi4_revision_gold.md`.

**Resultados con la revisión 2** (vínculo, 61 pares):

| Método | P | R | F1 |
|---|---|---|---|
| Reglas F = F3 | 0,932 | 0,902 | 0,917 |
| LLM, prompt de InfoLEG | 0,889 | 0,262 | 0,405 |
| LLM, prompt «vocab» | 0,895 | 0,836 | 0,864 |
| **Híbrido** | **0,983** | **0,934** | **0,958** |
| Híbrido «vocab» | 0,967 | 0,967 | 0,967 |

- El híbrido le gana a las reglas por +0,041, con un IC 95 % de −0,002 a +0,101: **ya no es significativo**.
- El vocabulario del prompt sigue siendo la diferencia más grande: +0,459, con un IC de +0,303 a +0,617.
- Detección de menciones: F1 0,986.
- Solo MOD (20 pares): las reglas dan R 0,500 y el LLM «vocab», 0,650 con P 1,0.

**Riesgo y cómo se acota.** La revisión se hizo después de ver los resultados, y los 16 cambios fueron hacia lo que los métodos predecían. Para acotarlo:
- se aplicaron solo las definiciones previas;
- cada cambio queda marcado en el TSV con su motivo;
- `metricas.json` guarda también los números con la revisión 1. Con ella, el orden de los métodos es el mismo: el híbrido primero y el LLM con el prompt de InfoLEG último.

**Pendiente.** Que un segundo anotador repita una parte, para el kappa.

### B59 · 20/11/2026 · Decisión · Grafos del digesto de la UNNOBA, con el mismo modelo y código que los de InfoLEG

**Contexto.** La PI4 se había evaluado sobre las relaciones (B57, B58), pero los grafos del digesto no se habían armado.

**Qué se hizo.** `scripts/22_grafo_unnoba.py` arma un grafo por parser: `data/grafo_unnoba_reglas`, `data/grafo_unnoba_llm` (prompt «vocab») y `data/grafo_unnoba_hibrido`. No se tocó el modelo ni el código del grafo: se usan la salida estándar, `relaciones.desde_evidencias` y `grafo.construir`/`cargar_neo4j`.

Lo único propio de la fuente es la traducción de las claves:
- las normas del digesto reciben `id_norma` desde 9.000.001 (el grafo usa enteros, y así no chocan con los de InfoLEG);
- el nombre del nodo es legible («Resolución HCS 44/2008»);
- la clave de comparación queda en el sumario.

**Resultado.**
- **Nodos:** 104 normas, 70 de la muestra con texto y 34 citadas sin texto; 342 artículos en el grafo de reglas.
- **Pares con una relación que no es CITA:** 9 en el de reglas, 13 en el del LLM y 58 en el del híbrido.
- **Coherencia con la evaluación:** el grafo de reglas, proyectado con la regla F3, da los mismos 59 pares que la evaluación. Los 58 pares del híbrido son los que aceptó.
- **Neo4j:** los tres se cargaron en el Neo4j local (`bolt://localhost:7688`), sin `--borrar`, con `fuente` = `unnoba_*`. Después de la carga, la base tiene 444 normas en total: 340 de InfoLEG y 104 del digesto.

**Datos personales.** Los DNI se tapan en el texto y en los fragmentos. `relaciones.csv` no va a git, porque los fragmentos pueden traer nombres.

Ejemplo de consulta en `docs/pi4_digesto_unnoba.md`.

### B60 · 20/11/2026 · Hallazgo · Evaluación de los grafos leyéndolos desde Neo4j: ida y vuelta idéntica en las cuatro fuentes

**Contexto.** Hasta ahora el grafo se había evaluado sobre una copia en memoria (B43). Faltaba hacerlo sobre el Neo4j del equipo (F6).

**Qué se hizo.**
- Se cargaron los cuatro grafos de InfoLEG (reglas v2, reglas v3, LLM e híbrido) en el Neo4j local (`bolt://localhost:7688`).
  - **Sin `--borrar`:** la carga es idempotente (MERGE por fuente), así que no pisa nada de lo que ya estaba, incluidos los grafos del digesto.
  - **Por qué no se usó `cargar_y_evaluar_grafo.sh`:** usa `--borrar` y habría vaciado la base.
- Después, `11_evaluar_grafo.py --uri` corrió una vez por fuente, filtrando por `fuente`.
- Salidas en `results/evaluacion_grafo_neo4j/{reglas_v2,reglas_v3,llm,hibrido}/` y el log en `log.txt`.

**Resultados.**

| Fuente | Ida y vuelta | Test P | Test R | Test F1 |
|---|---|---|---|---|
| reglas_v2 | 3.277 = 3.277, idénticas | 0,785 | 0,875 | 0,828 |
| reglas_v3 | 3.149 = 3.149, idénticas | 0,788 | 0,870 | 0,827 |
| llm | 3.247 = 3.247, idénticas | 0,756 | 0,938 | 0,837 |
| hibrido | 3.147 = 3.147, idénticas | 0,771 | 0,911 | 0,835 |

- En las cuatro fuentes, el grafo devuelve exactamente las relaciones que se cargaron.
- Los F1 que se leen desde Neo4j coinciden con la evaluación sobre los CSV.
  - **reglas_v2:** 0,828, como en B36.
  - **LLM:** 0,837 contra 0,841. La diferencia sale de que la proyección del script 11 es la regla F de la v2 sobre las aristas.
  - **Híbrido:** 0,835 con la regla F sobre sus aristas, contra 0,829 con su propia proyección (pares que no son CITA).
- Después de la carga, la base tiene 444 normas: 340 de InfoLEG y 104 del digesto.

**Pendiente.** Probar las consultas de ejemplo de `docs/grafo.md` en el Neo4j Browser.

### B61 · 20/11/2026 · Hallazgo · Texto consolidado de la LCT desde el grafo: coincide con InfoLEG en el 96 % de los artículos (91 % de los que cambian)

**Contexto.** El equipo pidió armar, a partir del grafo, el texto completo de una ley con todas sus modificaciones. La ley elegida fue la de más profundidad. Después había que analizar qué tan verídico es el resultado.

**Qué se hizo** (detalle en `docs/consolidado_lct.md`):
1. **Elegir la ley.** Una consulta Cypher mide la profundidad de cada norma: normas modificatorias, artículos afectados y largo de la cadena de modificaciones. Gana la LCT: 105 normas modificatorias, 107 artículos afectados y profundidad 16 con el híbrido.
2. **Sacar el manifiesto.** Otra consulta Cypher trae los artículos de la ley y todas las relaciones que llegan a ella, con el texto del artículo de origen y qué parsers las vieron. Son 943 relaciones de 107 normas.
3. **Fijar el texto base.** Es el t.o. del Decreto 390/76 (277 artículos), no el texto de 1974: desde 1976 las modificaciones usan la numeración del t.o.
4. **Consolidar** (`scripts/24_consolidar.py`):
   - 235 artículos modificatorios.
   - El LLM extrae las operaciones y el texto nuevo, con verificación literal: salen 172 operaciones.
   - Las sustituciones, incorporaciones y derogaciones se aplican sin LLM. Los cambios parciales los reescribe el LLM, con verificación de cobertura.
   - Se aplicaron 164 operaciones; 8 quedaron afuera con su motivo.
   - Resultado: 293 artículos con historia por artículo. Costo: unos USD 2,4.
5. **Evaluar contra el texto actualizado de InfoLEG.**
   - InfoLEG no se puede descargar desde el entorno de Claude. Por eso se compararon firmas calculadas en el navegador: hash del texto normalizado y MinHash de 4-gramas.
   - Del navegador solo salieron las firmas y los resultados.

**Resultados.**
- **Con firmas en el navegador (primera pasada):**
  - 206 artículos idénticos y 36 casi idénticos;
  - sobre los artículos que cambian, el 92 % termina bien.
- **Con el texto completo** (el equipo guardó `texact.htm`; `scripts/25_evaluar_consolidado.py`):
  - 207 artículos idénticos, 61 casi idénticos (similitud ≥ 0,95) y 13 derogados en los dos: 281 de 293 (95,9 %);
  - sobre los 103 artículos que cambian en alguno de los dos lados, coinciden 94 (91 %). Eso incluye las cadenas largas (art. 245: seis versiones; art. 92 bis: seis) y la reforma de la Ley 27.802 de 2026;
  - de los 107 cambios que registran las notas de InfoLEG, se aplicaron 99 (92,5 %).
- **Errores reales: 6 artículos.**
  - 251, 264, 265 y 266: la Ley 24.522 (Concursos) no está vinculada a la LCT en el grafo. Es recall del parser.
  - 2: la última sustitución de la Ley 27.802 no pasó la verificación literal.
  - 147: no se modela la derogación de una norma modificatoria («no se revive el texto»).
- **Diferencias de forma, no de contenido: otros 6.**
  - 98, 231 y 233: epígrafes que la norma modificatoria no transcribe.
  - 17, 38 y 107: variantes del t.o.

**Qué tan verídico es.**
- Es fiel en las sustituciones completas.
- Su techo es el recall del grafo.
- Los cambios parciales son el punto débil.
- No sabe de vigencias diferidas, suspensiones judiciales ni vetos.

Sirve para mostrar que el grafo alcanza para reconstruir el texto vigente y para medir dónde se pierde. No reemplaza al texto oficial.

**Pendiente.** Que el equipo revise `results/consolidado/lct_consolidada.md`, sobre todo los 8 cambios no aplicados y los 6 errores.

### B62 · 20/11/2026 · Decisión · Todo lo que se hizo a mano en la sesión queda como script en el repositorio

**Contexto.** El equipo pidió que todo lo hecho quede en scripts dentro del repositorio, para que se pueda rastrear y repetir. Varios pasos de la PI4 (B56, B57) y del consolidado (B60, B61) se habían hecho con comandos sueltos en la sesión de Claude:
- extraer el catálogo del descargador;
- apartar copias;
- pdftotext y OCR;
- sortear la muestra;
- cargar en Neo4j sin borrar;
- calcular las firmas en el navegador;
- hacer push desde la Mac.

**Qué se hizo.**

| Script | Qué hace | Verificación |
|---|---|---|
| `scripts/26_digesto_catalogo.py` | Saca el catálogo de 898 documentos que trae embebido el `.command` (base85 + zlib) y suma los 14 PDF bajados a mano | `--verificar`: sale igual al `catalogo.csv` del repositorio |
| `scripts/27_digesto_duplicados.py` | Agrupa los PDF por SHA-256 y aparta copias en `pdf/_duplicados/` con su motivo (`--mover`) | 912 contenidos distintos en `pdf/`; las 29 copias apartadas tienen su original |
| `scripts/28_digesto_textos.py` | Corre pdftotext (`-layout`) en todo y hace OCR (pdftoppm a 200 dpi en gris + tesseract spa) de los escaneados, solo de la muestra o de todos. Escribe `data/corpus_unnoba/textos.csv` | Mismo pdftotext que el usado. 336 escaneados, 38 con OCR (los de la muestra) |
| `scripts/29_digesto_muestra.py` | Arma la muestra de 70: las ordenanzas, los temas de reglamentos y 15 al azar con `random.Random(20261120)`. Escribe el JSONL con el texto y, con `--cuerpos`, la lectura que se usó para anotar | `--verificar`: la muestra sale igual y los textos del JSONL coinciden con `txt/` |
| `scripts/30_cargar_y_evaluar_neo4j.sh` | Carga y evalúa en Neo4j los cuatro grafos de InfoLEG y los del digesto, sin `--borrar` | Es lo que se corrió en B59 y B60 |
| `scripts/firma_texto_navegador.js` | Calcula en el navegador las firmas del texto actualizado de InfoLEG que se usaron en B61. Su par en Python es `scripts/firma_texto.py` | Mismos hashes en los artículos sin cambios |
| `tools/push_github.command` | Hace `git push` desde la Mac con la clave del usuario. El entorno de Claude no llega a GitHub: lo abre con doble clic desde el Finder | Todos los push de B57 a B62 |

Los pasos nuevos están en `correr_pipeline.sh`; el README y `docs/pi4_digesto_unnoba.md` ya los listan.

**Lo que no se puede reproducir exacto.**
- **El OCR:** cambia con la versión de tesseract y con los parámetros. Por eso `28` no rehace un `.txt` que ya existe, salvo con `--rehacer`, y los resultados de la PI4 corresponden a los textos guardados (`muestra_pi4_textos.jsonl`, fuera de git).
- **La descarga de los PDF:** sigue siendo manual, porque el robots.txt del digesto prohíbe automatizarla (B56).

### B63 · 21/11/2026 · Decisión · Tres documentos de cierre: reproducibilidad, estructura del repositorio y conclusiones

**Contexto.** El equipo pidió tres cosas:
- documentar las aclaraciones sobre lo que no se puede reproducir exacto (B62);
- un documento que explique cómo está organizado el repositorio;
- un documento que resuma todas las conclusiones y cómo se llegó a cada una.

**Qué se hizo.** Tres documentos nuevos, en el repo y en el Drive:

| Documento | Repo | Drive | Qué tiene |
|---|---|---|---|
| Reproducibilidad | `docs/reproducibilidad.md` | 13 - Reproducibilidad: qué se repite exacto y qué no | Paso por paso: si da lo mismo, qué hace falta y por qué no cuando no da. Junta lo que estaba en B17, B23, B53, B56, B57, B61 y B62 |
| Estructura del repositorio | `docs/estructura_repositorio.md` | 14 - Estructura del repositorio | Qué hay en cada carpeta, qué script lo genera, qué va a git y qué no, y dónde está cada documento |
| Conclusiones | `docs/conclusiones.md` | 15 - Conclusiones del TP y cómo se llegó a cada una | Las conclusiones ordenadas por PI1 a PI5, cada una con cómo se llegó, la evidencia y el límite, y una respuesta corta para cada PI |

**Aclaraciones nuevas que quedaron escritas.**
- **Qué depende de la Mac del equipo.** Los zips de `data/raw/`, los PDF, el texto y el OCR del digesto, y las cachés de la PI4 no van a git, por tamaño o por datos personales. Sin ellos, el corpus de InfoLEG no se puede verificar contra el portal y la PI4 no se repite sin volver a llamar a la API. Conviene una copia privada del equipo, fuera del Drive compartido.
- **Versiones.** `pdftotext` 22.02.0 (poppler) y tesseract 4.1.1.
- **El gold de la PI4 y las revisiones manuales son anotaciones de Claude**, no cálculos. No se «reproducen»: se validan, y para eso falta el equipo y un segundo anotador.
- **`cargar_y_evaluar_grafo.sh` borra la base.** Es el script histórico de las reglas v2. Para cargar todo sin borrar está `scripts/30_cargar_y_evaluar_neo4j.sh`.

**Otros cambios.**
- `.gitignore` ahora excluye toda la carpeta `data/textos/unnoba/`. Quedaban sin excluir una copia del catálogo y el `LEEME.csv` de las copias apartadas.
- Se actualizaron el README (estado del parser LLM y tabla de documentos) y `docs/ESTADO.md`.

## Cuestiones abiertas

- Cargar los grafos de la v3, del LLM y del híbrido en Neo4j sin `--borrar` (B54, B55); actualizar la tabla final con el LLM y sus híbridos (B48, B49).
- Probar las consultas de ejemplo de `docs/grafo.md` en el Neo4j Browser (la evaluación sobre Neo4j ya está, B60).
- Revisar el texto consolidado de la LCT (`results/consolidado/lct_consolidada.md`), los 8 cambios no aplicados y los 6 errores (B61).
- Mejorar el tipado de las reglas sobre otra muestra de dev, sin tocar los 78 casos de medición (B43, B47).
- Reglas v4, diseñadas sobre dev: sacar «texto sustituido por» del filtro de procedencia, escribir «l.c.t» sin punto, agregar «creado por» e «inclúyense», y exigir el verbo antes de la mención en F3 (B52).
- Decidir si el grafo lleva embeddings (B38).
- Validar las revisiones manuales de cobertura, de la Ley 14.250, de los 30 falsos positivos, de los 78 tipos y de las 60 menciones, y que un segundo anotador repita parte para el kappa (B12, B26, B30, B36, B45, B47).
- Consultar con la cátedra la supervisión distante, la clasificación fina y si se evalúa también la modificación estricta (B02, B14, B27).
- Armar la muestra independiente del gold (B15).
- Segundo anotador sobre una parte del gold de la PI4, para el kappa (B57, B58).
- Decidir si «ratificar» y el infinitivo de «dejar sin efecto» entran en una v4 de los verbos, diseñada sobre dev de InfoLEG (B57).
