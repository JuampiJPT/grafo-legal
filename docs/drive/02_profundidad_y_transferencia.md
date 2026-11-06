<!-- Copia del Google Doc "02 - Profundidad del grafo y transferencia de los parsers" (id 11NXbNCoFdEElDpywil-GzxYGavLoGeCEA90TkvPAxWE, revision AHj4eMTHVp3t). La version editable es la del Drive; esta copia se regenera con tools/gdoc_a_md.py. -->

# Profundidad del grafo y transferencia de los parsers

*TP Integrador, Sistemas Inteligentes (UNNOBA). Análisis del 02/11/2026 con datos de InfoLEG actualizados al 31/10/2026. Registrado en la bitácora como B18, B19 y B20.*

## 1. Conclusiones

Medida como cantidad de relaciones por nodo, la profundidad del grafo laboral ya es alta: la LCT tiene 130 modificatorias que son leyes o decretos y está en el puesto 29 de 34.026 normas. El límite no está en la LCT sino en el resto del grafo, donde la mayoría de los nodos tiene una o dos aristas (sección 9).

El dominio laboral alcanza para la cursada, pero el grafo actual tiene forma de estrella: el 37 % de las aristas toca a la Ley de Contrato de Trabajo. Recomendamos ampliarlo con tres leyes laborales más (Empleo, Riesgos del Trabajo y Asociaciones Sindicales). Eso casi duplica el gold, de 406 a 775 pares, sube el test de 131 a 192 pares y baja la concentración en la LCT al 19 %, sin perder el eje en la reforma de 2026.

No conviene cambiar el dominio principal. El tributario es el candidato natural para una segunda prueba: evaluar los tres parsers, diseñados con normas laborales, sobre normas tributarias que no vieron. Esa prueba en otro dominio se suma a la del digesto de la UNNOBA.

El digesto no se puede obtener con scraping: tiene captcha de Cloudflare y su robots.txt prohíbe el rastreo automático. Con una sesión de navegador de un integrante del equipo se puede consultar normalmente, así que la muestra se arma a mano y se anota manualmente, como propone el enunciado.

## 2. Profundidad como estructura del grafo

InfoLEG registra relaciones entre normas completas, así que la profundidad del grafo evaluable se mide a ese nivel. Usamos cinco indicadores sobre el subgrafo de leyes, decretos y decretos-ley de cada dominio, construido igual que nuestro corpus (anclas más un salto):

- **Normas y pares:** tamaño del corpus y del gold.
- **Camino más largo:** la cadena más larga del tipo A modifica a B, que modifica a C. Mide cuántas capas de reforma sobre reforma hay.
- **Caminos de dos saltos:** cantidad de cadenas A, B, C. Son las que hacen interesante una consulta multi-salto en Neo4j.
- **Concentración:** porcentaje de aristas que tocan a la norma más conectada. Un valor alto indica un grafo en estrella, donde casi todo apunta a una sola ley y la evaluación queda dominada por ella.
- **Pares en test:** relaciones cuya norma modificatoria es posterior a 2019.

La profundidad a nivel de artículo (qué artículo modifica a qué artículo) no está en InfoLEG. Nuestro extractor la puede producir desde el texto y el grafo la puede guardar con nodos Artículo, pero solo se puede evaluar con una muestra anotada a mano.

## 3. Comparación de dominios

| Dominio (anclas) | Normas | Pares gold | Pares en test | Camino más largo | Caminos de 2 saltos | Concentración |
|---|---|---|---|---|---|---|
| **Laboral actual** (LCT, Ley 27.802) | 185 | 406 | 131 | 13 | 3.506 | 37 % |
| **Laboral ampliado** (+ Leyes 24.013, 24.557 y 23.551) | 340 | 775 | 192 | 15 | 4.850 | 19 % |
| Tributario (Leyes 20.628, 23.349 y 11.683) | 361 | 1.041 | 127 | 20 | 2.705 | 14 % |
| Previsional (Ley 24.241) | 370 | 975 |  | 21 | 12.114 | 38 % |
| Administración financiera (Ley 24.156) | 322 | 1.030 |  | 37 | 7.215 | 31 % |
| Energía (Leyes 24.065 y 24.076) | 171 | 407 |  | 18 | 1.705 | 26 % |
| Código Penal (Ley 11.179) | 157 | 259 |  | 8 | 1.498 | 60 % |
| Ministerios (Ley 22.520) | 132 | 280 |  | 12 | 796 | 47 % |
| Sociedades (Ley 19.550) | 79 | 132 |  | 9 | 725 | 59 % |
| Código Civil y Comercial (Ley 26.994) | 49 | 99 |  | 6 | 627 | 48 % |
| Defensa del consumidor (Ley 24.240) | 34 | 54 |  | 5 | 61 | 61 % |

Los pares en test se calcularon solo para los tres candidatos finales. Los valores del laboral actual difieren levemente de los del documento 01 (183 normas y 402 pares) porque el portal sumó dos decretos de octubre de 2026 (bitácora B17).

## 4. Lectura de los resultados

**El laboral tiene más profundidad potencial de la que usamos.** La LCT tiene 130 normas modificatorias directas, 1.115 a dos saltos y 1.768 a tres (contando solo leyes y decretos). El límite lo pone nuestra decisión de expandir un solo salto, no el dominio.

**La ampliación mejora la forma del grafo, no solo el tamaño.** Con cinco anclas, ninguna ley concentra más del 19 % de las aristas. Las métricas dejan de medir sobre todo qué tan bien se detecta la LCT, y hay más cadenas para las consultas multi-salto de la PI5.

**El tributario es más denso pero más difícil.** Tiene el gold más grande y la menor concentración. Pero 89 de sus pares tienen la norma modificatoria sin texto, y las leyes de Ganancias e IVA se suelen citar por nombre y texto ordenado ("Ley de Impuesto a las Ganancias, t.o. 2019") en lugar de por número. En nuestro corpus laboral, esas dos leyes ya aparecían citadas solo por nombre. Eso lo vuelve una buena prueba de normalización para el LLM, pero un mal punto de partida para las reglas.

**Algunas cadenas largas no son profundidad real.** El camino de 37 en administración financiera probablemente sea una sucesión de leyes de presupuesto y decretos que modifican a los anteriores. No lo revisamos caso por caso, pero conviene desconfiar de los caminos largos en dominios con normas anuales.

**Los códigos son poco profundos en InfoLEG.** El Código Civil y Comercial y Defensa del Consumidor tienen pocos pares y mucha concentración. No sirven como dominio principal.

## 5. Recomendación sobre el corpus

- **Corpus principal:** laboral ampliado (340 normas, 775 pares). Mantiene la narrativa de la reforma de 2026 y la demo con la Ley 27.802.
- **Prueba en otro dominio:** tributario, evaluado una sola vez y sin ajustar nada, para medir cuánto se pierde fuera del dominio de diseño.
- **Prueba en otro corpus:** el digesto de la UNNOBA, con anotación manual (sección 6).

Si el equipo adopta la ampliación, el corpus pasa a una versión 2 y se regeneran el split, la cobertura textual y los textos. La versión 1 queda documentada en el documento 01.

## 6. Transferencia al digesto de la UNNOBA

### 6.1 Qué encontramos

- El sitio digesto.unnoba.edu.ar publica los actos resolutorios del Rectorado, el Consejo Superior, los consejos directivos de las escuelas y el Instituto de Posgrado, desde 2003.
- Está detrás de Cloudflare. Desde un navegador automatizado sin sesión aparece un captcha ("Verifique que es un ser humano"); desde el navegador de un integrante del equipo, ya verificado, se navega sin problemas.
- Su robots.txt prohíbe todo rastreo automático (User-agent: * / Disallow: /).
- Los documentos son PDF. La Ordenanza HCS 035/12 tiene texto embebido (2 páginas, sin imágenes), así que no necesita OCR. La Ordenanza HCS 001/07 pesa 2,1 MB y contiene una imagen, así que probablemente sea un escaneo: los documentos más antiguos pueden necesitar OCR. Solo se revisaron estos dos. Además de los listados por emisor y año, el digesto tiene una sección de reglamentaciones vigentes organizada por tema (por ejemplo, Reglamento de Alumnos), con la lista de ordenanzas de cada tema y un resumen de cada una. Las ordenanzas se citan como "Ordenanza HCS Nº 035/12" u "Ordenanza (CS) Nro. 23/09", y los resúmenes ya muestran relaciones con otras ordenanzas, como la Ordenanza (CS) 23/09, Reglamento General de Alumnos.

### 6.2 Qué implica

No se puede ni se debe scrapear. La API de Cloudflare no cambia esto, porque respeta robots.txt y no evita captchas. Hay dos vías válidas: pedir a la UNNOBA una copia de un conjunto de resoluciones para uso académico, o que un integrante del equipo descargue a mano una muestra de 30 a 50 documentos. La primera es más prolija para un trabajo publicable. La segunda alcanza para el tamaño que pide el enunciado.

### 6.3 Qué cambia en el pipeline

| Módulo | InfoLEG | Digesto UNNOBA |
|---|---|---|
| Adaptador de fuente | HTML estático | PDF a texto, con OCR si son escaneos |
| Segmentación | Artículos en HTML | Artículos en texto plano extraído del PDF |
| Detección | "Ley N° 20.744", "Decreto 1694/06" | "Resolución C.S. N° 123/15", "Ordenanza", más citas a leyes nacionales |
| Normalización | ID de InfoLEG | ID propio (por ejemplo res-cs-123-2015) y, para normas nacionales, el ID de InfoLEG |
| Gold | Bases complementarias | Anotación manual, con doble anotación de una muestra y acuerdo medido con kappa de Cohen |

Las citas a normas nacionales, como la Ley 24.521 de Educación Superior, permiten conectar el grafo del digesto con el de InfoLEG. Ese cruce entre corpus también sirve para la demostración.

## 7. Diseño de los tres parsers

Los tres extractores reciben lo mismo (artículos segmentados con su ubicación) y devuelven lo mismo (aristas con origen, destino normalizado, tipo, fragmento, ubicación, método y confianza). Así se comparan sobre los mismos conjuntos y se cambian sin tocar el resto del pipeline.

| Componente | Regex/AST | LLM puro | Híbrido |
|---|---|---|---|
| Estructura del documento | Árbol norma, artículo, inciso, armado desde el HTML o el texto | Se le pasa el artículo como texto | Árbol de regex/AST |
| Detección de menciones | Gramática de citas normativas (tipo, número, año, artículo) | El modelo las identifica | Regex/AST propone candidatos con alta cobertura |
| Normalización a ID | Tabla de lookup por tipo y número | El modelo devuelve tipo y número, la tabla resuelve el ID | Tabla; el LLM resuelve referencias implícitas ("la ley citada") y por nombre |
| Clasificación de la relación | Verbo de la oración (modifícase, sustitúyese, derógase) | El modelo, con salida en un esquema Pydantic | El LLM confirma o descarta cada candidato y lo clasifica |
| Evidencia | Offsets exactos del match | Fragmento citado por el modelo, verificado contra el texto | Offsets del candidato |
| Costo | Casi nulo | Alto: todos los artículos pasan por el modelo | Medio: solo los candidatos |

En "Regex/AST", AST se refiere a dos árboles: el de la estructura del documento y el de cada cita, que una gramática (por ejemplo con Lark) arma a partir de frases como "el inciso b) del artículo 92 bis de la Ley N° 20.744". Es más robusto que una regex suelta porque separa la cita en sus partes antes de normalizar.

En el LLM puro hay que verificar que el fragmento citado por el modelo exista en el texto. Si no existe, la arista se marca como no trazable, que es un tipo de error propio de este enfoque.

## 8. Diseño experimental de la transferencia

| Escenario | Datos | Gold | Qué responde |
|---|---|---|---|
| E1. Mismo dominio, normas posteriores | Test laboral (desde 2020) | InfoLEG | PI1 y PI2 |
| E2. Otro dominio, misma fuente | Tributario | InfoLEG | Robustez fuera del dominio de diseño |
| E3. Otro corpus | Digesto UNNOBA | Anotación manual | PI4, transferencia institucional |

Los tres parsers se evalúan en los tres escenarios, con las métricas por subtarea del enunciado (detección, normalización y relación), más el costo (tokens y tiempo) y la caída de F1 respecto de E1. En E2 y E3 no se ajusta nada con esos datos.

Para E3 se reportan dos versiones: sin modificaciones y con adaptación mínima, que solo agrega el adaptador de PDF y las reglas de identificación de resoluciones. Contar cuántas líneas de código hubo que cambiar sirve como medida concreta de qué tan independiente de la fuente es el pipeline.

La hipótesis de trabajo es que la regex/AST pierde más en E3, porque las citas universitarias tienen otra forma, y que el híbrido queda cerca del LLM puro con mucho menos costo si la detección de candidatos mantiene buena cobertura. Conviene escribir estas hipótesis antes de medir, para que el informe no las acomode a los resultados.

## 9. Profundidad por nodo: cuántas relaciones tiene cada norma

Si la profundidad se mide como el grado de un nodo, es decir la cantidad de relaciones de una norma, la LCT ya es una de las normas más profundas de InfoLEG. De las 34.026 leyes y decretos con al menos una modificatoria registrada, la mediana tiene 1, el percentil 90 tiene 3 y el percentil 99 tiene 20. La LCT tiene 130 modificatorias que son leyes o decretos y ocupa el puesto 29: está en el 0,1 % superior.

En total, InfoLEG le registra 267 relaciones de entrada a la LCT. Las otras 137 son resoluciones, disposiciones, circulares, comunicaciones y un acta, que quedaron afuera por el filtro de tipo (bitácora B08). Sumarlas aumentaría el grado, pero en su mayoría son actos de aplicación, con la misma objeción que la Ley 14.250 (bitácora B07).

De las 130 modificatorias, en 93 el texto menciona el número 20.744, en 13 solo la nombra como contrato de trabajo, en 18 no hay mención y 6 no tienen texto descargado. En 53 de las 93 aparece un verbo de modificación cerca del número. Son conteos automáticos y aproximados, que hay que validar a mano.

Dentro del corpus actual la distribución es muy desigual: la mediana es de 2 relaciones por norma, el percentil 90 de 7 y el máximo de 151, que corresponde a la LCT (130 de entrada y 21 de salida). Le siguen la Ley 27.802 (45), la Ley de Empleo (31) y la Ley 27.541 (18). La mayoría de los nodos del grafo son hojas con una o dos aristas.

Hay normas con más grado, pero un grado alto no siempre sirve. Entre las leyes y decretos con más modificatorias están la Ley 24.080 de tratados internacionales (358), la Ley 24.241 del SIPA (341), la Ley 24.156 de Administración Financiera (318), el Decreto 357/2002 de organigrama (318) y la Ley 12.665 de museos y monumentos (315). En varias de ellas las relaciones parecen ser aprobaciones o declaraciones repetitivas, como decretos que declaran monumentos o aprueban tratados. Eso da muchas aristas con la misma frase, que inflan las métricas sin aportar variedad. Lo sugieren los títulos; no lo verificamos caso por caso.

Dentro del ámbito laboral, las normas con más grado que la LCT son la Ley 24.185 de convenciones colectivas del sector público (219), el Decreto 214/2006, convenio colectivo de la Administración Pública Nacional (180), y el Decreto 2098/2008, convenio del SINEP (138). Les sigue la Ley 25.164 de empleo público (126). Forman un subdominio de empleo público denso, pero es probable que muchas de sus modificatorias sean homologaciones de actas paritarias con texto muy parecido.

Conclusión: para tener un nodo con muchas relaciones no hace falta cambiar de ley, porque la LCT ya está entre las 30 normas con más modificatorias de InfoLEG. Si se quiere un segundo nodo de alto grado, las opciones con sentido son la Ley 24.241 (SIPA), que es de un dominio cercano, o el subdominio de empleo público, en ambos casos verificando antes que sus modificatorias no sean repetitivas.

## 10. Limitaciones de este análisis

- Las métricas de profundidad se calcularon sobre el grafo de InfoLEG, no sobre lo que el texto expresa. Un dominio profundo en InfoLEG puede tener poca evidencia textual.
- Las anclas de cada dominio las elegimos nosotros. Otra elección cambiaría los números, y no comprobamos si cambiaría también el orden entre dominios.
- Los caminos largos no se revisaron caso por caso (sección 4).
- El formato de los PDF del digesto se verificó solo en dos documentos (sección 6.1).

## Referencias

- Ministerio de Justicia de la Nación: Base Infoleg de Normativa Nacional, datos actualizados al 31/10/2026. [https://datos.jus.gob.ar/dataset/base-de-datos-legislativos-infoleg](https://datos.jus.gob.ar/dataset/base-de-datos-legislativos-infoleg) (consultado el 02/11/2026)
- Universidad Nacional del Noroeste de la Provincia de Buenos Aires: Digesto Electrónico. [https://digesto.unnoba.edu.ar](https://digesto.unnoba.edu.ar) (consultado el 02/11/2026)
- Cloudflare: Browser Rendering REST API. [https://developers.cloudflare.com/browser-rendering/rest-api](https://developers.cloudflare.com/browser-rendering/rest-api)
