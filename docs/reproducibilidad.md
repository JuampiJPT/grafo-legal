# Reproducibilidad: qué se repite exacto y qué no

Este documento junta las aclaraciones sobre qué se puede repetir del TP y con qué resultado. Algunas estaban dispersas en la bitácora: B17, B23, B53, B56, B57, B61 y B62. Bitácora B63.

Para cada paso dice tres cosas:
- **si da exactamente lo mismo** al volver a correrlo;
- **qué hace falta** para que dé lo mismo;
- **por qué**, cuando no da lo mismo.

La regla general: todo lo que está en el repositorio se vuelve a generar igual con `bash correr_pipeline.sh`, sin pedidos a la red y sin la clave de la API. Lo que no se puede repetir exacto quedó guardado tal como se usó, y está marcado abajo.

## Resumen

| Paso | ¿Da lo mismo? | Qué hace falta | Por qué no, si no |
|---|---|---|---|
| Corpus y gold de InfoLEG | **Sí**, verificado por SHA-256 | Los zips del portal del 06/11/2026 en `data/raw/` (fuera de git) | Sin esos zips, el portal da otra versión: publica una nueva cada mes y no guarda las anteriores (B17) |
| Textos de InfoLEG (306 HTML) | **Sí** | Nada: están en el repo con su SHA-256 | Si se bajaran de nuevo podrían cambiar, porque InfoLEG los actualiza |
| Dataset, reglas v1/v2/v3, subtareas, errores, tipos | **Sí** | Nada | Es código determinista |
| Clasificador, modelo contextual, bootstrap | **Sí** | Nada | Usan semillas fijas (20261109 y 20261116) |
| Parser LLM, híbridos y consolidado sobre InfoLEG | **Sí**, sin llamar a la API | La caché, que está en git (`results/relaciones_llm/cache/`, `results/hibrido/cache/`, `results/consolidado/cache/`) | Sin la caché, una corrida nueva da respuestas parecidas pero no idénticas: el modelo no es determinista y el SDK ya no acepta `temperature` (B53) |
| Grafos (CSV) y carga en Neo4j | **Sí** | Neo4j del TP para cargarlos (`docs/grafo.md`) | — |
| Texto actualizado de la LCT (referencia del consolidado) | **Sí**, con el archivo guardado | `data/textos/infoleg/html/25552_texact.html`, guardado a mano el 20/11/2026 | InfoLEG lo actualiza con cada reforma; uno bajado más adelante puede traer cambios nuevos |
| PDF del digesto UNNOBA | **No se automatiza** | Bajarlos a mano con `tools/digesto_unnoba/` | El robots.txt del digesto prohíbe el acceso automático (B19, B56) |
| Catálogo y muestra de la PI4 | **Sí**, verificado | Los PDF en `data/textos/unnoba/pdf/` | — |
| Texto con `pdftotext` | **Sí** con la misma versión | poppler 22.02.0 | Otra versión de poppler puede cortar líneas distinto |
| OCR de los escaneados | **No byte a byte** | Los `.txt` guardados (fuera de git) | Cambia con la versión de tesseract (se usó 4.1.1) y con sus parámetros |
| Evaluación PI4 (LLM e híbrido) | **Sí**, en la Mac del equipo | La caché local `results/pi4_unnoba/cache_*` (fuera de git) | La caché no va a git porque tiene nombres y DNI; en otra máquina hay que volver a llamar a la API |
| Gold de la PI4 | **Es una anotación**, no un cálculo | `data/corpus_unnoba/gold_pi4.tsv` | Lo anotó Claude, no una persona del equipo; falta un segundo anotador (B58) |
| Revisiones manuales | **Son anotaciones** | `docs/revision_manual/` | Las hizo Claude y el equipo las tiene que validar |
| `git push` | — | `tools/push_github.command`, abierto en la Mac | El entorno de Claude no llega a GitHub por SSH (B39) |

## 1. Corpus de InfoLEG

- **Qué se congeló.** El corpus único (340 normas, 775 pares del gold) se armó el 06/11/2026 con `scripts/01_obtener_corpus.py` sobre las tres bases del portal de datos. Los CSV resultantes están en `data/corpus/` y **no se regeneran**: `data/corpus/SNAPSHOT.md` tiene sus SHA-256 y los de las bases de origen.
- **Cómo se verifica.** `correr_pipeline.sh` vuelve a armar el corpus en `data/verificacion/` con los zips guardados en `data/raw/` y comprueba que dé byte a byte lo mismo.
- **La aclaración.** `data/raw/` no está en git, porque son zips grandes (67 MB). Si no están, el paso 1 baja los zips del portal, y como el portal publica una versión nueva cada mes, el corpus regenerado ya no coincide. El script lo avisa. Pasó una vez: entre el 30/09 y el 31/10 cambiaron los hashes y aparecieron dos decretos nuevos (B17). Por eso se decidió congelar y guardar los zips (B23).

## 2. Textos de InfoLEG

Los 306 HTML están en `data/textos/infoleg/html/`, con la URL, la fecha y el SHA-256 de cada uno en `manifiesto_textos.csv`. `02_descargar_textos.py` solo pide los que faltan, así que con el repo completo no hace ningún pedido.

El texto actualizado de la LCT (`25552_texact.html`) se guardó aparte. Lo bajó el equipo desde el navegador el 20/11/2026, porque ni la VM ni el espacio de Claude llegaban a InfoLEG. Antes de tenerlo, la comparación se hizo con firmas calculadas en el navegador (`scripts/firma_texto_navegador.js`). Esas firmas quedan como respaldo: con el archivo completo, `25_evaluar_consolidado.py` hace la comparación con el texto entero y llega a las mismas conclusiones (B61).

## 3. Lo determinista

Las reglas, el dataset, la evaluación, la explicación de errores, los tipos y los grafos no tienen azar: con las mismas entradas dan las mismas salidas. Lo que tiene azar usa semilla fija:

| Qué | Semilla |
|---|---|
| Muestra de la Ley 14.250 | 20261106 |
| Clasificador (random forest, permutación) | 20261109 |
| Modelo contextual y bootstrap de la tabla final | 20261116 |
| Muestra de la PI4 y bootstrap de la PI4 | 20261120 |

La única diferencia entre corridas es el campo `fecha` de algunos `metricas.json`, que guarda cuándo se corrió. Los números no cambian.

## 4. Lo que usa el LLM

- **Por qué no es determinista.** Un modelo de lenguaje puede dar respuestas distintas al mismo pedido. Para fijar el resultado se guarda cada respuesta en una caché, con la huella SHA-256 del pedido: el modelo, la versión del parser, el prompt del sistema y el mensaje con el texto (B48). Si el pedido es el mismo, se lee la respuesta guardada y no se llama a la API.
- **La temperatura.** Se sacó del pedido porque el SDK ya no la acepta para los modelos 5.5 (B53). No cambia la reproducibilidad, que viene de la caché.
- **InfoLEG.** Las cachés del parser LLM, del híbrido en cascada y del consolidado están en git. Con ellas, los scripts 14, 15, 20 y 24 dan exactamente lo mismo sin clave.
- **Digesto UNNOBA.** Las cachés de la PI4 no van a git, porque las respuestas del modelo citan fragmentos con nombres y DNI. Solo se repite exacto en la Mac del equipo. En otra máquina, `21_pi4_unnoba.py --estimar` dice cuántos pedidos haría (252), y una corrida nueva daría números cercanos pero no idénticos.
- **Si cambia el modelo.** Los pedidos usan `claude-sonnet-5-5`. Si se cambia el modelo o el prompt, cambia la huella, la caché no sirve y la corrida es nueva. Eso es a propósito: no se mezclan respuestas de versiones distintas.

## 5. Digesto de la UNNOBA

### 5.1 La descarga de los PDF es manual

El robots.txt del digesto (`digesto.unnoba.edu.ar`) prohíbe el acceso automático, así que el TP no lo automatiza (B19, B56). El equipo bajó los PDF con la sesión abierta en su navegador, usando `tools/digesto_unnoba/` (detalle en su `README.md`):
- `Descargar_PDFs_UNNOBA.command` baja los 898 documentos del catálogo que lleva adentro;
- 14 documentos más se bajaron a mano y figuran en el catálogo como `descarga_manual`.

`26_digesto_catalogo.py` reconstruye el catálogo de 912 documentos desde ese descargador, y `--verificar` confirma que sale igual al del repo. Lo que no se puede garantizar es que el digesto siga publicando los mismos archivos: si cambia un PDF, cambia su SHA-256 y `27_digesto_duplicados.py` lo muestra.

### 5.2 `pdftotext` es reproducible con la misma versión

`28_digesto_textos.py` corre `pdftotext -layout` (poppler 22.02.0) sobre todos los PDF. Con la misma versión el texto es el mismo. Un documento se trata como escaneado si da menos de 200 caracteres: son 336 de 912.

### 5.3 El OCR no es reproducible byte a byte

De los 70 documentos de la muestra, 38 son escaneos, y su texto sale de OCR: `pdftoppm` a 200 dpi en gris y `tesseract` 4.1.1 en español.

- **Qué pasa.** El resultado del OCR cambia con la versión de tesseract, con los datos de idioma y con los parámetros. Se probaron varias configuraciones y ninguna reprodujo byte a byte el texto que se había usado. Las diferencias son de caracteres sueltos: una barra leída como «1», una tilde, un salto de línea.
- **Qué se hizo.** `28_digesto_textos.py` **no rehace un `.txt` que ya existe**, salvo con `--rehacer`. Los resultados de la PI4 corresponden a los textos guardados: `data/textos/unnoba/txt/` y `muestra_pi4_textos.jsonl`, en la Mac del equipo y fuera de git por los datos personales. `29_digesto_muestra.py --verificar` comprueba que el JSONL coincide con los `.txt`.
- **Qué impacto tendría.** Un OCR distinto puede cambiar alguna mención, por ejemplo «53112012» en lugar de 531/2012. El adaptador corrige ese caso, pero otro error del OCR podría hacer que se gane o se pierda un par. Con 61 pares de vínculo, un par mueve el F1 alrededor de 0,01.

### 5.4 La muestra y el gold

- **La muestra** se sortea con `random.Random(20261120)` y `29_digesto_muestra.py --verificar` confirma que sale la misma.
- **El gold no es un cálculo, es una anotación.** Lo anotó Claude leyendo cada documento (`cuerpos_muestra.txt`, fuera de git), en dos revisiones (B57, B58). Cada cambio de la revisión 2 está marcado en el TSV, y los números con la revisión 1 se informan como sensibilidad. Para que sea un gold defendible falta que un segundo anotador del equipo repita una parte y se calcule el kappa.

## 6. Neo4j

- **Qué se repite.** Los grafos se arman como CSV (`data/grafo*/`), y esos CSV son reproducibles. La carga usa `MERGE` y cada arista lleva su `fuente`. Cargar varias veces, o cargar fuentes nuevas, no duplica ni pisa nada: por eso se carga sin `--borrar` (`scripts/30_cargar_y_evaluar_neo4j.sh`).
- **Qué depende de la máquina.** El contenedor Neo4j corre en la Mac del equipo (`bolt://localhost:7688`), con la clave en `.neo4j_password`, fuera de git. El manifiesto del consolidado (`23_consultar_consolidado.py`) sale de esa base. Su resultado está guardado en `results/consolidado/manifiesto_25552_*.json`, así que `24` y `25` se pueden correr sin Neo4j.

## 7. Lo que se hace desde la Mac

El entorno de Claude no llega a GitHub por SSH (B39). Los commits se hacen en el repo de la Mac, y el push lo hace `tools/push_github.command`, abierto con doble clic desde el Finder, con la clave del equipo. No cambia ningún resultado: es solo cómo se suben los commits.

## 8. Qué guardar para que siga siendo reproducible

- Los zips de `data/raw/` del 06/11/2026.
- `data/textos/unnoba/` completo: PDF, `txt/` y el JSONL.
- Las cachés de la PI4 (`results/pi4_unnoba/cache_llm/` y `cache_hibrido/`).
- `.neo4j_password` y el volumen del contenedor Neo4j.

Nada de eso va a git, por tamaño o por datos personales. Conviene una copia en un lugar privado del equipo, no en el Drive compartido, porque tiene nombres y DNI.
