# Corpus v1: snapshot congelado

Estos archivos son la versión oficial del corpus v1 y **no se regeneran**. El portal de datos publica cada mes una versión nueva de la base y no guarda las anteriores. Con los datos al 31/10/2026, el mismo criterio da 185 normas y 406 pares, en lugar de 183 y 402. Por eso el corpus que se usa para evaluar queda fijo en los archivos de esta carpeta (decisión D1 en `docs/decisiones.md`).

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `corpus_normas.csv` | 48.093 | `4cdf4a4d3bb5b61305fd85734ed6e419604dfdd9e954ef1b6bb401902730226c` |
| `gold_relaciones.csv` | 19.938 | `7591a3f630be5479a8a11a9d1889cd529e81691b9e3d3c75df2723b1b2e8029c` |
| `cobertura_textual_gold.csv` | derivado | lo regenera `scripts/05_cobertura_textual.py` |

## Fuentes (datos actualizados al 30/09/2026)

SHA-256 de los CSV que contienen los zips descargados del portal:

- Base Infoleg de Normativa Nacional: `ef2501812d4d9b504018576462e96daf04fdcc776fb8d5201394a22f08428adf`
- Base Complementaria de Normas Modificatorias: `82e8bff91f489b77a40e4a6be0427fb5ba91ba9657a6cc1730cc2d658f25e30b`
- Base Complementaria de Normas Modificadas: `5c64583dcb523964ceea736fcc69e0477bf26ecb4b348c160a1d3bced4000e8f`

## Cómo se construyó

- La descarga se hizo desde el navegador, porque el entorno de trabajo no tenía salida a datos.jus.gob.ar. El procesamiento siguió el mismo criterio que `scripts/01_obtener_corpus.py`.
- El script oficial se corre ahora en una máquina con red (`correr_pipeline.sh`). Escribe en `data/verificacion/corpus_v1_snapshot_actual/`, de modo que el v1 regenerado con datos nuevos se puede comparar con este. Las diferencias esperadas son solo las normas y pares que InfoLEG agregó después del 30/09.

## Contenido

- Semillas que se expanden: Ley 20.744 (id 25552) y Ley 27.802 (id 423680).
- Nodos que se incluyen sin expandir: Ley 14.250 (id 46379) y Ley 27.742 (id 401266).
- Tipos de norma: Ley, Decreto y Decreto/Ley.
- 183 normas, 168 de ellas con texto en InfoLEG.
- 402 pares: 275 en dev y 127 en test. El corte temporal es el 31/12/2019 y el split lo define la norma modificatoria.

## Cobertura textual

Clasificación de los pares del gold según cómo menciona el texto de la modificatoria a la norma modificada:

| Categoría | Pares |
|---|---|
| Cita por número | 322 |
| Cita solo por nombre | 21 |
| Sin mención | 50 |
| Sin texto | 9 |

La primera versión de esta clasificación se calculó en el navegador el 28/10 y daba 322 / 20 / 51 / 9. La versión del script coincide con aquella en 401 de los 402 pares. El par restante (Ley 23.947 → Ley 20.744) pasó de «sin mención» a «solo nombre», porque el texto dice «Ley de Contrato de Trabajo» sin número.
