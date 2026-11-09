<!-- Copia del Google Doc "00 - Bitácora del TP" (id 1kXhR_wDGRq8TsD8jtcxX6sSWMZPaRJS9fggNjLIReCY, revision AHj4eMScRny_). La version editable es la del Drive; esta copia se regenera con tools/gdoc_a_md.py. -->

# Bitácora del TP Integrador

*Sistemas Inteligentes (UNNOBA). Problemática III: extracción de relaciones entre normas y grafo normativo trazable. Iniciada el 27/10/2026, última entrada el 09/11/2026.*

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
- RELACION_EXTRAIDA: una arista por par y por parser. Hay 771 de reglas v2, 804 de reglas v1 y 713 del clasificador.
- MENCIONA (4.430): va de un artículo a la norma que cita, con offsets, fragmento, verbo y si la regla v2 la cuenta.

**Por qué así.** Si lo de InfoLEG y lo extraído compartieran tipo de relación, una consulta podría mezclarlos sin decirlo. Con una arista por parser, comparar parsers es una sola consulta, y el LLM y el híbrido se agregan sin cambiar el modelo. Las menciones salen de un artículo que lleva el texto, así cada arista de las reglas se rastrea hasta su fragmento. Un test comprueba que las aristas de reglas v2 coinciden exactamente con los pares que tienen una mención que cuenta.

**Qué hay.** El script 09 arma los CSV en data/grafo y, con una conexión, los carga en Neo4j con restricciones de unicidad y un índice de texto completo sobre los artículos. docs/grafo.md tiene cinco consultas de ejemplo, con su pregunta en lenguaje natural, para empezar el text-to-Cypher.

**Dificultad.** Desde el entorno de Claude no se pudo descargar Neo4j. Los CSV y la trazabilidad están verificados, y dos consultas se probaron sobre una copia del grafo en memoria (networkx y grand-cypher). El Cypher de carga se corre por primera vez en la máquina del equipo.

**Abierto.** El grafo no tiene embeddings. Si el text-to-Cypher se complementa con recuperación semántica, van en los artículos, con un índice vectorial de Neo4j, pero antes hay que elegir el modelo de embeddings.

### B39 · 09/11/2026 · Dificultad · Sin acceso de escritura a GitHub desde la sesión de Claude

El repositorio usa SSH (git@github.com:JuampiJPT/grafo-legal.git), y desde la sesión de Claude no hay salida por SSH ni una cuenta de GitHub vinculada. Los commits quedan en el repositorio local de la Mac y el push lo hace el equipo. Para que Claude pueda subir cambios hay que vincular GitHub en la configuración de claude.ai.

## Cuestiones abiertas

- Cargar el grafo en un Neo4j 5 y correr las consultas de ejemplo (B38).
- Elegir el LLM y el acceso para los parsers LLM e híbrido, y decidir si el grafo lleva embeddings (B38).
- Validar las revisiones manuales de cobertura, de la Ley 14.250 y de los 30 falsos positivos, y que un segundo anotador repita parte para el kappa (B12, B26, B30, B36).
- Consultar con la cátedra la supervisión distante, la clasificación fina y si se evalúa también la modificación estricta (B02, B14, B27).
- Armar la muestra independiente del gold (B15).
- Elegir cómo obtener el corpus del digesto (B19).
