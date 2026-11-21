# Guion del video explicativo del TP

Guion del video que cuenta el trabajo de punta a punta. Cada escena tiene dos partes:

- **Narración:** el texto para ElevenLabs, escrito para leerse en voz alta. Los números y las siglas van como se dicen.
- **En pantalla:** qué se muestra mientras tanto: código, capturas, gráficos y tablas, con el archivo del repo de donde sale cada cosa.

El texto solo con la narración, listo para pegar en ElevenLabs, está en `narracion_elevenlabs.txt`. Bitácora B65.

**Duración estimada:** unos 13 minutos con voz a ritmo normal (unas 2.050 palabras de narración).

**Cómo grabarlo con ElevenLabs:**
- Generar **un audio por escena** (E01.mp3, E02.mp3, …). Así el video se arma con la duración exacta de cada audio, y si hay que corregir una frase se regenera solo esa escena.
- Voz en español latinoamericano, estilo narrador. Estabilidad media (alrededor de 50 %) y similitud alta (alrededor de 75 %).
- Las pausas están marcadas con `<break time="0.8s" />`. ElevenLabs las respeta en los modelos que admiten SSML; si el modelo elegido no las admite, se pueden borrar.
- Revisar la pronunciación de: InfoLEG («ínfo leg»), Neo4j («neo for yei»), Cypher («sáifer»), TF-IDF («te efe i de efe»), F1 («efe uno»). Si una suena mal, se puede escribir como se pronuncia o usar un diccionario de pronunciación de ElevenLabs.

---

## E01 · Presentación (≈ 25 s)

**En pantalla:** título «Extracción de relaciones entre normas y grafo normativo trazable». Debajo: «Sistemas Inteligentes · UNNOBA · Problemática III». De fondo, un grafo animado de normas conectadas.

**Narración:**
> En este video vamos a contar, paso a paso, cómo construimos un sistema que lee normas argentinas, descubre qué norma modifica a cuál, y arma con eso un grafo donde cada conexión se puede justificar con el texto. <break time="0.8s" /> Es el trabajo integrador de Sistemas Inteligentes, Problemática tres.

## E02 · El problema (≈ 40 s)

**En pantalla:** el texto real del artículo 25 de la Ley 24.013, «Sustitúyese el artículo 198 de la Ley de Contrato de Trabajo…» (`data/textos/infoleg/html/412.html`). Se resaltan «Sustitúyese», «artículo 198» y «Ley de Contrato de Trabajo». Después se convierte en una flecha: `Ley 24.013 —SUSTITUYE (art. 198)→ Ley 20.744`.

**Narración:**
> Las normas no viven aisladas. Una ley sustituye un artículo de otra, un decreto la reglamenta, otra la deroga. <break time="0.6s" /> Por ejemplo, el artículo veinticinco de la Ley de Empleo dice: «Sustitúyese el artículo ciento noventa y ocho de la Ley de Contrato de Trabajo». <break time="0.6s" /> Para una persona, eso es una relación entre dos normas. Para una computadora, es solo texto. <break time="0.6s" /> El problema que encaramos es ese: pasar del texto a la relación, de forma automática.

## E03 · El experimento (≈ 40 s)

**En pantalla:** un diagrama en tres pasos.
1. «Ocultar»: las bases de relaciones de InfoLEG se tapan con un candado.
2. «Reconstruir»: el texto de las normas entra al sistema y salen flechas.
3. «Comparar»: las flechas del sistema se ponen al lado de las de InfoLEG, con verde y rojo.

**Narración:**
> InfoLEG, la base de normativa nacional, nos da algo muy valioso: además del texto, publica qué normas modifican a cuáles. <break time="0.6s" /> Eso nos permite hacer un experimento controlado. Le escondemos al sistema esas relaciones, lo dejamos leer solo el texto, y después comparamos lo que encontró con lo que registra InfoLEG. <break time="0.6s" /> Las relaciones de InfoLEG nunca entran al extractor. Solo se usan para medir.

## E04 · Las preguntas (≈ 35 s)

**En pantalla:** las cinco preguntas de investigación, que aparecen de a una. La PI1 y la PI2 quedan resaltadas como «cursada».

**Narración:**
> El trabajo responde cinco preguntas. <break time="0.5s" /> Qué tan bien funcionan las reglas, los modelos y los enfoques híbridos. <break time="0.4s" /> Si combinar reglas con modelos mejora. <break time="0.4s" /> Qué formas de escribir producen más errores. <break time="0.4s" /> Si el sistema se puede llevar a otro cuerpo normativo, como el digesto de la UNNOBA. <break time="0.4s" /> Y qué aporta guardar todo en un grafo con su evidencia.

## E05 · De dónde salen los datos (≈ 50 s)

**En pantalla:** captura del Portal de Datos Abiertos de la Justicia con las tres bases. Una tabla con sus filas: normativa nacional 430.834, modificatorias 380.481, modificadas 385.118. Al lado, un fragmento de `data/corpus/procedencia.json` con la URL y el SHA-256 de cada zip.

**Narración:**
> Empezamos por los datos. El Portal de Datos Abiertos de la Justicia publica tres bases: la de normativa nacional, con más de cuatrocientas treinta mil normas, y dos bases complementarias, de normas modificadas y de normas modificatorias. <break time="0.6s" /> De ahí sale el gold, es decir, la lista de relaciones contra la que vamos a medir. <break time="0.6s" /> Cada archivo que bajamos quedó registrado con su dirección, su fecha y su huella digital, para poder demostrar exactamente con qué datos trabajamos.

## E06 · Cómo armamos el corpus (≈ 55 s)

**En pantalla:**
1. El código de expansión de `scripts/01_obtener_corpus.py` (el bloque «Expansión a 1 salto»).
2. Una animación de un grafo: aparecen las cinco leyes ancla (20.744, 27.802, 24.013, 24.557 y 23.551) y, alrededor, las normas que las modifican o que ellas modifican.
3. Un contador final: 340 normas, 306 con texto, 775 pares del gold.

**Narración:**
> No queríamos trabajar con dos o tres leyes sueltas, así que elegimos el derecho laboral. <break time="0.5s" /> Partimos de cinco leyes ancla, entre ellas la Ley de Contrato de Trabajo y la Ley de Empleo, y agregamos todas las normas conectadas a ellas en un salto. <break time="0.6s" /> Este código hace exactamente eso: toma cada ancla, busca sus vecinas en las bases de InfoLEG y se queda solo con leyes y decretos. <break time="0.6s" /> El resultado es un corpus de trescientas cuarenta normas, trescientas seis con texto, y setecientos setenta y cinco relaciones conocidas.

## E07 · Desarrollo y prueba, separados en el tiempo (≈ 40 s)

**En pantalla:** una línea de tiempo de 1934 a 2026 con un corte en el 31/12/2019. A la izquierda, «dev: 583 pares»; a la derecha, «test: 192 pares». Un candado sobre test, con la leyenda «se evalúa una sola vez».

**Narración:**
> Para que la evaluación sea honesta, separamos los datos en el tiempo. <break time="0.5s" /> Todo lo que se dictó hasta dos mil diecinueve es para desarrollar: ahí miramos errores y ajustamos reglas. <break time="0.5s" /> Lo que se dictó desde dos mil veinte queda guardado como prueba, y cada versión del sistema se mide ahí una sola vez. <break time="0.6s" /> Así simulamos lo que pasaría con normas nuevas que el sistema nunca vio.

## E08 · Congelar los datos (≈ 30 s)

**En pantalla:** dos tablas de hashes, del 30/09 y del 31/10, con las diferencias en rojo. Después, `correr_pipeline.sh` comparando byte a byte: «corpus_normas.csv idéntico al congelado».

**Narración:**
> Nos llevamos una sorpresa: el portal publica una versión nueva cada mes y no guarda las anteriores. <break time="0.5s" /> En un mes cambiaron los datos y aparecieron decretos nuevos. <break time="0.5s" /> Por eso congelamos el corpus y guardamos los archivos originales. Hoy cualquiera puede regenerarlo y comprobar que sale idéntico, byte por byte.

## E09 · Los textos y el adaptador (≈ 55 s)

**En pantalla:**
1. Captura de la página de InfoLEG de la Ley 24.013 (`412.html` renderizado).
2. El mismo texto ya limpio, con las zonas coloreadas: encabezado, VISTO, CONSIDERANDO, artículos y notas.
3. El código de `fuentes/infoleg.py`: la expresión regular `_ART`, con sus comentarios, y la función `segmentar`.

**Narración:**
> Después bajamos el texto de cada norma desde InfoLEG: trescientos seis archivos, cada uno con su huella digital. <break time="0.6s" /> El primer componente del sistema es el adaptador. Toma la página web, le saca las etiquetas y la convierte en texto limpio. <break time="0.5s" /> Después la corta en partes: el VISTO, el CONSIDERANDO, cada artículo y los anexos. <break time="0.6s" /> Esta expresión regular reconoce el comienzo de un artículo en todas sus variantes: con tilde, sin tilde, abreviado, con «bis». <break time="0.5s" /> Y algo clave: cada pedazo guarda su posición exacta en el texto. Eso es lo que después nos permite señalar la evidencia de cada relación.

## E10 · Detectar menciones (≈ 50 s)

**En pantalla:**
1. El código de `extractores/menciones.py`: los patrones `_TIPO`, `_NUM` y `_LISTA`.
2. Ejemplos que se iluminan al detectarse: «Ley N° 24.557», «Decreto 1694/06», «Leyes Nros. 23.551 y 25.674», «DNU 70/2023», «Ley de Contrato de Trabajo».

**Narración:**
> El segundo paso es encontrar cada vez que el texto nombra otra norma. <break time="0.5s" /> Usamos dos detectores. Uno con expresiones regulares, que reconoce leyes, decretos y decretos de necesidad y urgencia escritos de muchas formas, incluso en listas, como «leyes veintitrés mil quinientos cincuenta y uno y veinticinco mil seiscientos setenta y cuatro». <break time="0.6s" /> El otro es un diccionario de nombres propios, porque a veces el texto no da el número: dice «Ley de Contrato de Trabajo». <break time="0.6s" /> La detección casi no falla: encuentra más del noventa y nueve por ciento de las menciones.

## E11 · Normalizar: ¿qué norma es? (≈ 50 s)

**En pantalla:** un diagrama de cuatro salidas desde «mención»: resuelta, ambigua, fuera del corpus, no encontrada. Ejemplo: «Decreto 467 del 14 de abril de 1988», donde el año está escrito como fecha; se marca en rojo en la v2 y en verde en la v3.

**Narración:**
> Encontrar la mención no alcanza. Hay que saber a qué norma concreta se refiere. <break time="0.5s" /> Cada mención se busca en el catálogo de InfoLEG por tipo, número y año. <break time="0.5s" /> Si hay una sola posible, queda resuelta. Si falta el año y hay varias, queda ambigua. <break time="0.5s" /> Y casi la mitad de las menciones nombran normas reales que no están en nuestro corpus. <break time="0.6s" /> El error más frecuente era el año escrito como fecha, por ejemplo «Decreto cuatrocientos sesenta y siete del catorce de abril de mil novecientos ochenta y ocho». La versión tres de las reglas lo corrige.

## E12 · El parser de reglas (≈ 60 s)

**En pantalla:**
1. El código de la configuración F en `extractores/reglas_v2.py` (el diccionario `CONFIGS`).
2. Un gráfico de barras: «VISTO 80 % en el gold» contra «CONSIDERANDO 24 %».
3. Un ejemplo de cita de procedencia tachada: «t.o. por Decreto 390/76».

**Narración:**
> Ahora la decisión: ¿esta mención es una relación o solo una cita? <break time="0.5s" /> La primera versión de las reglas aceptaba solo menciones en los artículos. Pero revisando errores descubrimos algo importante. <break time="0.6s" /> Cuando una norma aparece en el VISTO, está en el gold el ochenta por ciento de las veces. Cuando aparece solo en el CONSIDERANDO, apenas el veinticuatro por ciento. <break time="0.6s" /> Así nació la regla F: acepta las menciones del VISTO, y las del articulado cuando hay un verbo como «sustitúyese» o «derógase», o cuando quien habla es una ley. <break time="0.5s" /> Y descarta las citas que solo indican de dónde viene un texto, como «texto ordenado por el Decreto trescientos noventa del setenta y seis».

## E13 · El tipo de relación y la salida estándar (≈ 45 s)

**En pantalla:**
1. Una tabla con los seis tipos y un ejemplo de cada uno: SUSTITUYE, INCORPORA, DEROGA, REGLAMENTA, MODIFICA y CITA.
2. Una fila real de `results/relaciones/relaciones_reglas_v2.csv`: fuente, origen, artículo, parte, tipo, destino, artículo destino, verbo, inicio, fin y fragmento.

**Narración:**
> Además de decidir si hay relación, el sistema dice de qué tipo es, mirando el verbo: sustituye, incorpora, deroga, reglamenta, modifica, o simplemente cita. <break time="0.6s" /> Todo termina en una tabla común, que llamamos salida estándar. <break time="0.5s" /> Cada fila es una relación con su evidencia: de qué artículo sale, a qué norma y artículo apunta, qué verbo la sostiene, y la posición exacta del fragmento en el texto. <break time="0.5s" /> Cualquier parser escribe esta misma tabla, y eso hace que todo lo que viene después sea intercambiable.

## E14 · Los datasets (≈ 50 s)

**En pantalla:**
1. Dos tablas de pandas: `articulos.csv` (8.066 segmentos) y `pares_candidatos.csv` (1.091 pares).
2. La fila real del par Ley 24.013 → Ley 20.744 con sus atributos: 28 menciones, todas en el articulado, verbo en la oración, origen ley y `en_gold = 1`.

**Narración:**
> Con todo eso armamos dos datasets en formato tabla. <break time="0.5s" /> El primero tiene los ocho mil sesenta y seis segmentos de texto, cada uno con su zona y su posición. <break time="0.5s" /> El segundo tiene mil noventa y un pares candidatos: cada par de normas que el detector encontró, con veintidós atributos. <break time="0.5s" /> Por ejemplo, la Ley de Empleo y la Ley de Contrato de Trabajo: veintiocho menciones, todas en el articulado, con verbo modificatorio. <break time="0.5s" /> Y una etiqueta que dice si el par está en el gold. Con este dataset entrenamos los modelos.

## E15 · Los modelos clásicos (≈ 40 s)

**En pantalla:** dos tarjetas. «Random forest con 22 atributos: F1 0,823». «TF-IDF del contexto: F1 0,783». Debajo, la palabra «empate» sobre la marca de las reglas (0,828).

**Narración:**
> El primer intento con aprendizaje automático fue un random forest sobre esos atributos. <break time="0.5s" /> Llegó prácticamente al mismo resultado que las reglas: efe uno de cero coma ochenta y dos. <break time="0.5s" /> Un modelo que lee las palabras alrededor de cada mención, con te efe i de efe, solo fue peor. <break time="0.6s" /> La conclusión fue clara: con atributos de superficie no hay mucho más para ganar. Hacía falta algo que entienda la oración.

## E16 · El parser con un modelo de lenguaje (≈ 65 s)

**En pantalla:**
1. Un diagrama: segmentos → prefiltro → lotes → LLM → verificación de la cita → normalización.
2. Un fragmento del prompt (`llm.SISTEMA`) con la definición de los seis tipos.
3. Una respuesta real en JSON de la caché, con «Sustitúyese el artículo 2 del Régimen de Contrato de Trabajo…».
4. La verificación: la cita buscada en el texto y marcada en verde; una inventada, en rojo y tachada.
5. La caché: una carpeta con archivos nombrados por su huella SHA-256.

**Narración:**
> Entonces sumamos un modelo de lenguaje grande. <break time="0.5s" /> Le mandamos los artículos que nombran alguna norma, junto con una explicación de los seis tipos de relación, y nos devuelve, en un formato estructurado, cada relación con la cita textual de donde la sacó. <break time="0.6s" /> Acá viene un detalle importante: buscamos esa cita, literal, en el texto. Si no está, la relación se descarta. <break time="0.5s" /> Así evitamos que el modelo invente: solo el cero coma uno por ciento de las citas no estaban en el texto. <break time="0.6s" /> Además, cada respuesta queda guardada con una huella del pedido. Volver a correr el experimento no cuesta nada y da exactamente lo mismo. Procesar todo el corpus costó catorce dólares.

## E17 · Los híbridos (≈ 55 s)

**En pantalla:**
1. Diagrama de Venn: reglas ∩ LLM y reglas ∪ LLM.
2. El híbrido en cascada: los candidatos caen en tres zonas (descarte en gris, seguro en verde, gris en amarillo), y solo la zona gris va al LLM, con los umbrales 0,15 y 0,5.

**Narración:**
> Con dos parsers que fallan en cosas distintas, probamos combinarlos. <break time="0.5s" /> La forma más simple: quedarse solo con lo que encuentran los dos, o con lo que encuentra cualquiera de los dos. <break time="0.6s" /> La más elaborada es el híbrido en cascada. Las reglas hacen lo que saben hacer bien, que es encontrar y normalizar, y separan los casos en tres grupos: los que seguro no son, los que seguro son, y una zona gris. <break time="0.5s" /> Solo la zona gris va al modelo de lenguaje, que decide con la opinión de la regla como punto de partida. <break time="0.5s" /> Así se usa el modelo donde realmente hace falta, a un cuarto del costo.

## E18 · El grafo en Neo4j (≈ 55 s)

**En pantalla:**
1. El modelo: `(:Norma)-[:CONTIENE]->(:Articulo)-[:SUSTITUYE]->(:Articulo)`.
2. Un dibujo del vecindario de la LCT: la ley en el centro y aristas de colores por tipo.
3. Una consulta Cypher y su resultado con el fragmento: `MATCH (o:Articulo)-[r]->(d) WHERE o.id = '395521#71' RETURN r.fuente, type(r), d.id, r.fragmento`.
4. Las cuatro fuentes (reglas v2, reglas v3, LLM e híbrido) sobre los mismos nodos.

**Narración:**
> Con la salida estándar armamos el grafo en Neo4j. <break time="0.5s" /> Las normas contienen artículos, y los artículos se conectan con flechas que dicen qué hacen: sustituye, deroga, reglamenta. <break time="0.5s" /> Cada flecha guarda el fragmento de texto que la justifica y el parser que la encontró. <break time="0.6s" /> Por eso podemos cargar los cuatro parsers sobre los mismos nodos, sin pisarse, y preguntar, por ejemplo, cómo leyó cada uno el mismo artículo. <break time="0.5s" /> Verificamos que el grafo devuelve exactamente lo que se le cargó: tres mil doscientas setenta y siete relaciones de ida y tres mil doscientas setenta y siete de vuelta.

## E19 · Cómo evaluamos (≈ 40 s)

**En pantalla:**
1. Las fórmulas de precisión, recall y F1, con un ejemplo de verdaderos positivos, falsos positivos y falsos negativos.
2. Una animación del bootstrap: se remuestrean normas de origen y se forma una campana con su intervalo.

**Narración:**
> Para medir usamos precisión, cuánto de lo que encontramos es correcto; recall, cuánto de lo correcto encontramos; y efe uno, que combina las dos. <break time="0.6s" /> Como el conjunto de prueba tiene ciento noventa y dos pares, una diferencia de un punto puede ser casualidad. <break time="0.5s" /> Por eso calculamos intervalos de confianza remuestreando las normas dos mil veces. Una mejora cuenta solo si su intervalo no toca el cero.

## E20 · Resultados: la comparación (≈ 65 s)

**En pantalla:** la Figura de métodos con sus intervalos (`docs/informe_avance/figuras/fig3_metodos.png`), con zoom a tres puntos: reglas v2 (0,828), LLM (0,841) y reglas ∩ LLM (0,838, en naranja).

**Narración:**
> Y ahora, los resultados. <break time="0.5s" /> Todos los métodos sobre las mismas ciento noventa y dos relaciones de prueba. <break time="0.6s" /> Las reglas llegan a un efe uno de cero coma ochenta y tres. El modelo de lenguaje, a cero coma ochenta y cuatro, con el mejor recall: encuentra el noventa y cuatro por ciento de las relaciones. <break time="0.6s" /> Pero la única mejora que se sostiene estadísticamente es la intersección entre reglas y modelo: un punto más, ganado en precisión. <break time="0.6s" /> Y donde el modelo realmente se destaca es en el tipo de relación: pasa de cero coma sesenta y siete a cero coma ochenta y ocho.

## E21 · Dónde se pierde (≈ 50 s)

**En pantalla:**
1. El embudo de pérdidas (`fig2_embudo.png`): 192 → 192 → 185 → 185 → 184 → 168.
2. Las causas de los errores (`fig5_errores.png`), resaltando «Cita en el VISTO: 24».
3. Las matrices de confusión de tipos (`fig4_tipos.png`), resaltando la columna CITA.

**Narración:**
> Analizamos cada error, uno por uno. <break time="0.5s" /> El embudo muestra algo revelador: casi nada se pierde detectando o normalizando. Lo que cuesta es decidir. <break time="0.6s" /> La mitad de los falsos positivos son normas citadas en el VISTO que InfoLEG no registra como relación. <break time="0.5s" /> Y en los tipos, el error típico de las reglas es tomar una simple mención como si fuera una modificación, por ejemplo «la derogación del artículo dos». El modelo de lenguaje casi no comete ese error.

## E22 · Otro digesto: la UNNOBA (≈ 55 s)

**En pantalla:**
1. El pipeline con solo la primera caja cambiada: PDF → `pdftotext` / OCR → `fuentes/unnoba.py`.
2. Ejemplos de menciones del digesto: «Resolución (CS) Nro. 44/08», «Ordenanza (CS) 14/09».
3. El gráfico de la PI4 (`fig6_pi4.png`), resaltando el salto de 0,405 a 0,864 al agregar el vocabulario.

**Narración:**
> La pregunta siguiente era si todo esto sirve fuera de InfoLEG. <break time="0.5s" /> Tomamos setenta documentos del digesto de la UNNOBA, donde nadie registró las relaciones, y cambiamos solo el adaptador. <break time="0.6s" /> Las reglas llegaron a cero coma noventa y dos, y el híbrido a cero coma noventa y seis. <break time="0.6s" /> Pero hubo una lección: el modelo de lenguaje, con las instrucciones pensadas para leyes y decretos, ignoraba las resoluciones. Con tres frases nuevas sobre el vocabulario de la universidad, pasó de cero coma cuarenta a cero coma ochenta y seis. <break time="0.5s" /> El vocabulario de cada fuente tiene que ser parte del adaptador.

## E23 · Reconstruir la ley vigente desde el grafo (≈ 60 s)

**En pantalla:**
1. El ranking de profundidad: la LCT primera, con 105 modificatorias y una cadena de 16 saltos.
2. La historia del artículo 245, versión por versión: Ley 23.697 → Ley 24.013 → Ley 25.877 → DNU 70/2023 → Ley 27.802.
3. El gráfico del consolidado (`fig7_consolidado.png`): 281 de 293 artículos coinciden.

**Narración:**
> Para poner a prueba el grafo hicimos algo ambicioso: reconstruir el texto vigente de la Ley de Contrato de Trabajo usando solo lo que tiene el grafo. <break time="0.5s" /> Tomamos todas las modificaciones, en orden cronológico, y las aplicamos una por una. <break time="0.6s" /> El artículo doscientos cuarenta y cinco, el de la indemnización por despido, pasa por cinco normas distintas, y el sistema lo reconstruye bien. <break time="0.6s" /> Al compararlo con el texto actualizado de InfoLEG, coinciden doscientos ochenta y uno de doscientos noventa y tres artículos. <break time="0.5s" /> Los pocos errores vienen de relaciones que el grafo no tenía, no de la reconstrucción.

## E24 · Conclusiones (≈ 60 s)

**En pantalla:** cinco tarjetas, una por pregunta, que aparecen de a una:
- PI1: reglas 0,83 · LLM 0,84 · el techo es la tarea.
- PI2: híbrido +1 punto, el único significativo.
- PI3: VISTO, remisiones, decretos sin verbo.
- PI4: se transfiere, con el vocabulario en el adaptador.
- PI5: trazabilidad, ida y vuelta idéntica y ley consolidada al 96 %.

**Narración:**
> Para cerrar, lo que aprendimos. <break time="0.5s" /> Uno: reglas bien diseñadas ya funcionan muy bien, y el límite no está en el método sino en la tarea. Hay relaciones que el texto no dice. <break time="0.5s" /> Dos: combinar reglas con un modelo de lenguaje mejora, pero poco, y sobre todo en precisión. <break time="0.5s" /> Tres: el error está en decidir, especialmente con las citas del VISTO. <break time="0.5s" /> Cuatro: el sistema se transfiere a otro digesto si el adaptador conoce su vocabulario. <break time="0.5s" /> Y cinco: un grafo con evidencia no solo guarda relaciones; alcanza para reconstruir el texto vigente de una ley.

## E25 · Lo que sigue y cierre (≈ 35 s)

**En pantalla:** la lista de próximos pasos: validación humana y kappa, una muestra independiente, comparar modelos, consultas en lenguaje natural sobre el grafo. Al final, la dirección del repositorio `github.com/JuampiJPT/grafo-legal` y la carpeta de documentación.

**Narración:**
> Nos queda trabajo para el final: validar las anotaciones con un segundo anotador, probar con una muestra independiente, comparar modelos de lenguaje, y poder consultar el grafo en lenguaje natural. <break time="0.6s" /> Todo el código, los datos y cada decisión que tomamos están documentados en el repositorio y en la bitácora. <break time="0.6s" /> Gracias por ver.
