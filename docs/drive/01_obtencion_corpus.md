<!-- Copia del Google Doc "01 - Obtención y construcción del corpus" (id 1Wig8INrhRbKYEDA9HWgzcQaWHJzAzo215VkD1feGjBk, revision AHj4eMTTKvny). La version editable es la del Drive; esta copia se regenera con tools/gdoc_a_md.py. -->

# Obtención y construcción del corpus

*TP Integrador, Sistemas Inteligentes (UNNOBA). Problemática III: extracción de relaciones entre normas. Registro de la etapa de obtención de datos, 27 de octubre de 2026.*

## 1. Resumen

El corpus de trabajo queda formado por **183 normas nacionales del dominio laboral** (leyes, decretos y decretos-ley) y un conjunto de evaluación (gold standard) de **402 relaciones dirigidas** del tipo "la norma A modifica o complementa a la norma B". Ambos se obtuvieron de las bases oficiales de InfoLEG publicadas por el Ministerio de Justicia. El conjunto se dividió temporalmente: 275 relaciones para desarrollo (normas modificatorias hasta 2019) y 127 para test (2020 en adelante, incluidas la Ley 27.742 y la Ley 27.802).

El gold se usa únicamente para evaluar. El extractor trabajará solo con el texto de las normas, descargado de InfoLEG (sección 11).

## 2. Fuente de los datos

Los datos provienen del dataset [Base Infoleg de Normativa Nacional](https://datos.jus.gob.ar/dataset/base-de-datos-legislativos-infoleg) del Portal de Datos Abiertos de la Justicia Argentina.

| **Organismo responsable** | Ministerio de Justicia. Secretaría de Justicia. Dirección Nacional del Sistema Argentino de Información Jurídica |
|---|---|
| **Cobertura** | Normas publicadas en la primera sección del Boletín Oficial desde mayo de 1997, más la normativa referenciada por ellas |
| **Licencia** | Creative Commons Attribution 4.0 |
| **Datos actualizados al** | 30 de septiembre de 2026 (según el portal) |
| **Frecuencia de actualización** | Mensual |
| **Fecha de descarga** | 27 de octubre de 2026 |
| **Documentación de campos** | [Metadata del dataset en GitHub](https://github.com/datos-justicia-argentina/Base-de-datos-legislativos-infoleg/blob/master/Base-de-datos-legislativos-Infoleg-metadata.md) |

Se descargaron los tres archivos completos (no las muestras de 1000 registros). Como el contenido del portal cambia todos los meses, se registró el hash SHA-256 de cada CSV descomprimido. Si alguien vuelve a descargar y obtiene otro hash, los datos cambiaron y los conteos pueden no coincidir.

| Archivo | Zip (bytes) | Filas | SHA-256 del CSV |
|---|---|---|---|
| [base-infoleg-normativa-nacional](https://datos.jus.gob.ar/dataset/d9a963ea-8b1d-4ca3-9dd9-07a4773e8c23/resource/bf0ec116-ad4e-4572-a476-e57167a84403/download/base-infoleg-normativa-nacional.zip) | 49.743.478 | 429.648 | ef2501812d4d9b504018576462e96daf04fdcc776fb8d5201394a22f08428adf |
| [base-complementaria-infoleg-normas-modificatorias](https://datos.jus.gob.ar/dataset/d9a963ea-8b1d-4ca3-9dd9-07a4773e8c23/resource/dea3c247-5a5d-408f-a224-39ae0f8eb371/download/base-complementaria-infoleg-normas-modificatorias.zip) | 9.503.901 | 379.163 | 82e8bff91f489b77a40e4a6be0427fb5ba91ba9657a6cc1730cc2d658f25e30b |
| [base-complementaria-infoleg-normas-modificadas](https://datos.jus.gob.ar/dataset/d9a963ea-8b1d-4ca3-9dd9-07a4773e8c23/resource/0c4fdafe-f4e8-4ac2-bc2e-acf50c27066d/download/base-complementaria-infoleg-normas-modificadas.zip) | 10.485.306 | 383.793 | 5c64583dcb523964ceea736fcc69e0477bf26ecb4b348c160a1d3bced4000e8f |

Los archivos crudos no se copiaron a esta carpeta por su tamaño (unos 380 MB descomprimidos). Se identifican por su URL oficial y su hash, y el script los descarga de nuevo.

## 3. Qué contiene cada archivo

**Base normativa.** Una fila por norma, con 17 columnas: identificador (*id_norma*), tipo, número, organismo, fechas de sanción y de publicación, títulos, links al texto original y al texto actualizado, y la cantidad de normas que la modifican y que ella modifica. No incluye el texto completo: solo los links al HTML en InfoLEG.

**Bases complementarias.** Una fila por relación, con *id_norma_modificatoria* e *id_norma_modificada*, más el tipo, número, fecha y títulos de una de las dos normas. Al cruzarlas con la base normativa se verificó lo siguiente:

- Las dos bases complementarias contienen exactamente los mismos 375.808 pares únicos. Solo cambia cuál de las dos normas describen las columnas descriptivas: la de modificatorias describe a la norma modificada, y la de modificadas describe a la norma modificatoria. Para el gold alcanza con una de ellas; se usó la de modificatorias.
- La base de modificatorias tiene 3.355 filas duplicadas (379.163 filas para 375.808 pares). Se eliminaron.
- Todos los identificadores de ambas columnas existen en la base normativa, así que cada par se puede vincular con los datos de sus dos normas.

## 4. Criterio de selección del corpus

Usar la base completa no es viable para el TP: son 429.648 normas, la descarga de todos los textos llevaría días y el análisis manual de errores que pide el enunciado sería imposible. Se eligió un subconjunto temático, conectado y de un tamaño que permita revisar casos a mano.

**Dominio.** Derecho laboral, con eje en la reforma de 2026. Se partió de cuatro normas semilla:

| Norma | id_norma | Publicación | Rol |
|---|---|---|---|
| Ley 20.744, Ley de Contrato de Trabajo | 25552 | 27/09/1974 | Semilla, se expande |
| Ley 27.802, Ley de Modernización Laboral | 423680 | 06/03/2026 | Semilla, se expande |
| Ley 14.250, Convenios Colectivos de Trabajo | 46379 | 20/10/1953 | Nodo incluido, no se expande |
| Ley 27.742, Ley de Bases | 401266 | 08/07/2024 | Nodo incluido, no se expande |

**Expansión.** Se agregaron todas las normas que modifican a una semilla expandible o que son modificadas por ella (un salto en el grafo de InfoLEG).

**Filtro por tipo.** Solo se conservaron leyes, decretos y decretos-ley. Las resoluciones y disposiciones quedaron afuera.

Tres decisiones requieren justificación:

- **La Ley 14.250 no se expande.** Tiene 42.598 relaciones, casi todas resoluciones (28.935) y disposiciones (13.620) de la Secretaría de Trabajo que homologan convenios colectivos. Se presume que esas normas no expresan la relación con un verbo como "modifícase" (homologan un convenio en el marco de la ley), por lo que inflarían el gold con pares difíciles de recuperar desde el texto. Esta presunción se verificará leyendo una muestra.
- **Se excluyen resoluciones y disposiciones** por el mismo motivo y para mantener un corpus de normas de rango legal, cuyo texto suele expresar la modificación de forma explícita.
- **Un solo salto.** Con dos saltos el corpus crece a 4.115 normas y 12.380 pares, lo que excede la escala de revisión manual.

Alternativas evaluadas antes de elegir:

| Variante | Normas | Pares gold |
|---|---|---|
| **Elegida:** expandir LCT y Ley 27.802, un salto | 183 | 402 |
| Expandir también la Ley 27.742, un salto | 251 | 643 |
| Dos saltos desde las semillas | 4.115 | 12.380 |

La segunda variante sigue siendo manejable y es la opción natural si se necesita más volumen de test.

## 5. Construcción del gold standard

El gold está formado por todos los pares de la base complementaria en los que tanto la norma modificatoria como la modificada pertenecen al corpus. Las relaciones hacia normas que quedaron afuera no se incluyen en el gold; en la evaluación se contarán aparte como "destino fuera del corpus", que es una de las categorías de error del enunciado.

InfoLEG agrupa bajo esta relación distintos vínculos: modificación, sustitución, derogación, reglamentación, prórroga y complementación. Por eso el TP trabaja con la relación general "modifica o complementa", como permite el enunciado.

## 6. División en desarrollo y test

Se usó un corte temporal: las normas publicadas hasta el 31/12/2019 son de desarrollo y las posteriores son de test. Se toma la fecha de publicación en el Boletín Oficial y, si falta, la de sanción. En el gold, el split lo define la norma modificatoria, porque es la que el extractor lee.

Con este corte se mide si las reglas y prompts diseñados con normas viejas funcionan sobre normas que no se vieron durante el desarrollo. El test incluye las reformas laborales recientes: el DNU 70/2023, la Ley 27.742 y la Ley 27.802.

En 114 pares la norma modificatoria está en test y la modificada en desarrollo. Es esperable, porque una norma nueva modifica normas anteriores, y no constituye una fuga: el extractor nunca recibe el gold, y la norma modificada solo aparece como destino a normalizar.

## 7. Resultado

| Medida | Valor |
|---|---|
| Normas en el corpus | 183 (99 leyes, 77 decretos, 7 decretos-ley) |
| Normas en desarrollo / test | 158 / 25 |
| Pares gold | 402 |
| Pares gold en desarrollo / test | 275 / 127 (68,4 % / 31,6 %) |
| Normas que aparecen como modificatorias | 155 |
| Período cubierto | 1889 a 2026, concentrado desde 1990 |
| Normas sin link a texto en InfoLEG | 15 (todas anteriores a 1994) |
| Pares gold cuya norma modificatoria no tiene link a texto | 9 |

Los 9 pares sin texto de origen no pueden ser recuperados por ningún extractor. Son un techo conocido para el recall y se reportarán como tales.

## 8. Archivos generados

| Archivo | Contenido |
|---|---|
| [corpus_normas.csv](https://drive.google.com/file/d/1xk9MsNr805Bsf4XC0ddo4Bfzp5iAWGXP/view) | Una fila por norma del corpus: metadatos de InfoLEG, links al texto, rol (semilla o expansión), split y si tiene link de texto. |
| [gold_relaciones.csv](https://drive.google.com/file/d/1QYyYJv9C409-sThaTKnqqo9mVeCAd14a/view) | Una fila por relación: IDs y etiquetas de la norma modificatoria y la modificada, fecha de la modificatoria y split. Solo para evaluación. |
| [01_obtener_corpus.py](https://drive.google.com/file/d/1ysW-9Cy2OXpK1s7F8KW_cxlrCLI8c8UO/view) | Script que descarga las bases y aplica el criterio de selección para regenerar los dos CSV. |

Hashes SHA-256 de los CSV generados, para verificar una regeneración:

- corpus_normas.csv (48.093 bytes): 4cdf4a4d3bb5b61305fd85734ed6e419604dfdd9e954ef1b6bb401902730226c
- gold_relaciones.csv (19.938 bytes): 7591a3f630be5479a8a11a9d1889cd529e81691b9e3d3c75df2723b1b2e8029c

## 9. Procedimiento seguido

- Descarga de los tres zip completos desde las URLs oficiales del portal.
- Descompresión y lectura de los CSV (UTF-8, delimitados por coma). Se verificó que todas las filas tuvieran la cantidad de columnas esperada.
- Cálculo del hash SHA-256 de cada CSV.
- Verificación de la estructura: equivalencia de las dos bases complementarias, columnas descriptivas, duplicados e IDs huérfanos (sección 3).
- Localización de las semillas en la base normativa por tipo y número.
- Expansión a un salto y filtro por tipo de norma (sección 4).
- Construcción del gold y asignación del split (secciones 5 y 6).
- Exportación de los dos CSV y cálculo de sus hashes.

Los archivos de esta carpeta se generaron ejecutando ese procedimiento sobre los datos descargados. El script *01_obtener_corpus.py* implementa el mismo criterio en Python. Se probó con datos sintéticos, pero todavía no se corrió sobre los datos completos. Con los datos al 30/09/2026 debería producir 183 normas y 402 pares. El 02/11/2026 el portal ya publicaba datos al 31/10/2026 y, con el mismo criterio, el resultado pasa a 185 normas y 406 pares (bitácora B17). Por eso los CSV de esta carpeta son el snapshot oficial del TP: el script reproduce el procedimiento, no los mismos números.

## 10. Limitaciones

- **El gold no es perfecto.** Refleja lo que InfoLEG cargó. Puede incluir relaciones que no se expresan en el texto de la norma (por ejemplo, vínculos registrados solo por criterio documental) y omitir otras que sí aparecen.
- **Relaciones históricas atípicas.** La Ley 20.744 de 1974 figura como modificatoria de 21 normas anteriores dentro del corpus, en general porque las derogó o reemplazó. Esos pares conviene revisarlos a mano durante el desarrollo.
- **Sesgo de dominio.** Todo el corpus es laboral. Los resultados no necesariamente se trasladan a otras áreas del derecho.
- **Datos vivos.** El portal se actualiza todos los meses. Una nueva descarga puede cambiar los conteos; los hashes permiten detectarlo.
- **Anexos sin descargar.** Tres normas remiten a anexos en PDF que no se descargaron (sección 11.2).

## 11. Descarga de los textos

Se descargó el HTML de las 168 normas con link a texto el 28/10/2026, entre las 00:32 y las 00:35 UTC, sin errores. Se usó el texto original (norma.htm) en 166 casos y el texto actualizado (texact.htm) en los 2 que no tienen original: la Ley 2.637 (Código de Comercio) y el Decreto-Ley 13.839/46.

### 11.1 Método

InfoLEG sirve HTML estático desde un servidor Apache (cabecera server: Apache-Coyote/1.1). No usa Cloudflare ni otra protección contra bots, no publica robots.txt y sus páginas no necesitan JavaScript. Por eso alcanza con pedidos HTTP simples, sin navegador remoto ni servicios de scraping. Se hizo un pedido por segundo y se previeron hasta tres reintentos por error; no hubo ninguno.

La URL de cada texto se deriva del id_norma: /infolegInternet/anexos/{bloque}-{bloque+4999}/{id}/norma.htm, donde el bloque es el id redondeado hacia abajo al múltiplo de 5000. Se verificó que la regla reproduce las 168 URLs de la base normativa.

Las páginas declaran ISO-8859-1 o no declaran codificación. Se decodificaron como Windows-1252, que además incluye las comillas y guiones tipográficos que usa InfoLEG. Para cada archivo se registró la URL, la fecha y hora de descarga, el tamaño, la codificación declarada, la cantidad de artículos detectados y el SHA-256 en [manifiesto_textos.csv](https://drive.google.com/file/d/1hixXrMA5iJLm8ScDckMBDRHxgJAQKlDI/view). Los HTML no se suben a esta carpeta: se regeneran con [02_descargar_textos.py](https://drive.google.com/file/d/1R1Ne-IirgwmI34Elv4JPjuP4jh6y9GsJ/view) y se verifican contra esos hashes.

### 11.2 Resultado

Se obtuvieron 6,3 MB de HTML y 5,1 millones de caracteres de texto. La mediana es de 9.766 caracteres por norma, con un mínimo de 450 y un máximo de 315.883 (Decreto 824/2019, texto ordenado del Impuesto a las Ganancias). Se detectaron 6.845 encabezados de artículo y 1.090 apariciones de verbos de modificación (modifícase, sustitúyese, derógase, incorpórase y similares) en 89 normas.

Hay casos a revisar. La página de la Ley 24.522 tiene solo 450 caracteres y ningún artículo, y la del Código de Comercio tampoco tiene artículos detectables. El Decreto 137/2026 es solo la promulgación de la Ley 27.802. Tres normas remiten a anexos en PDF que no se descargaron: la Ley 27.431, el Decreto 191/2021 y el Decreto 493/2021.

### 11.3 Cobertura textual del gold

Para estimar el máximo que puede alcanzar un extractor basado en texto, se buscó en cada relación del gold si el texto de la norma modificatoria menciona a la modificada. La búsqueda es automática y aproximada: cuenta como mención el número de la norma, con o sin punto de miles, y para seis leyes muy citadas también su nombre.

De las 393 relaciones con texto disponible, 322 (81,9 %) mencionan el número de la norma destino, 20 (5,1 %) la nombran solo por su nombre, como "Ley de Contrato de Trabajo" o "Impuesto a las Ganancias", y 51 (13,0 %) no tienen ninguna mención detectable. En test la mención por número llega a 118 de 127 relaciones (92,9 %); en desarrollo es de 204 sobre 266 con texto (76,7 %).

Las relaciones sin mención se concentran en normas antiguas. Por ejemplo, en 10 de los 21 pares en que la Ley 20.744 figura como modificatoria de una ley anterior, el texto no nombra a esa ley. Son vínculos registrados por InfoLEG con criterio documental, que ningún extractor que lea solo el texto puede recuperar. El detalle por relación está en [cobertura_textual_gold.csv](https://drive.google.com/file/d/1mwYAy0B7v2V6A2IpXu6ier8eshCgN8gQ/view), que, igual que el gold, es material de evaluación y no se usa como entrada del extractor.

### 11.4 Uso de Cloudflare

Se evaluó la Browser Rendering REST API de Cloudflare, cuyos endpoints /content, /markdown y /crawl renderizan páginas en un navegador remoto y devuelven HTML o Markdown. Para InfoLEG no hace falta: el sitio no tiene JavaScript que renderizar ni bloqueos contra bots, y la API exige una cuenta y un token de Cloudflare. Además, según su documentación, el crawler se identifica como bot, respeta robots.txt y no evita las protecciones contra bots ni los captchas, así que tampoco destrabaría un sitio protegido. Su conversión a Markdown podría servir más adelante para el digesto universitario de la PI4, si esas páginas dependen de JavaScript.

## 12. Próximo paso

Segmentar cada texto en artículos, guardar el texto limpio junto con la ubicación de cada artículo y empezar el baseline de reglas sobre el split de desarrollo. Antes conviene revisar a mano las tres normas con anexos en PDF y las dos páginas sin artículos.

## Referencias

- Ministerio de Justicia de la Nación: Base Infoleg de Normativa Nacional. Portal de Datos Abiertos de la Justicia Argentina. [https://datos.jus.gob.ar/dataset/base-de-datos-legislativos-infoleg](https://datos.jus.gob.ar/dataset/base-de-datos-legislativos-infoleg) (consultado el 27/10/2026)
- Datos Justicia Argentina: Base de datos legislativos Infoleg, metadata. [https://github.com/datos-justicia-argentina/Base-de-datos-legislativos-infoleg](https://github.com/datos-justicia-argentina/Base-de-datos-legislativos-infoleg)
- InfoLEG, Información Legislativa y Documental. [https://www.infoleg.gob.ar](https://www.infoleg.gob.ar)
- Cloudflare: Browser Rendering REST API y endpoint /crawl. [https://developers.cloudflare.com/browser-rendering/rest-api](https://developers.cloudflare.com/browser-rendering/rest-api) (consultado el 27/10/2026)
