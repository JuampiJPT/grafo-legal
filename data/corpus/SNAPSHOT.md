# Corpus del TP: snapshot congelado

Este es el **único corpus** del TP (decisión D11, bitácora B33). Es el dominio laboral ampliado, construido con `scripts/01_obtener_corpus.py` sobre las bases de InfoLEG descargadas el 06/11/2026. Los archivos de esta carpeta **no se regeneran**: el portal publica cada mes una versión nueva y no guarda las anteriores. `correr_pipeline.sh` vuelve a armar el corpus en `data/verificacion/` con los zips guardados en `data/raw` y comprueba que dé exactamente lo mismo.

| Archivo | Bytes | SHA-256 |
|---|---|---|
| `corpus_normas.csv` | 87.917 | `4583ddfef39980ea7dc550c4bd104255c4fa99d942b25a40c2a0f3f4d239b056` |
| `gold_relaciones.csv` | 38.285 | `d1632ae051a40921d290296b9a532e2bd7ff1efb554bb5da2a779c3b018851d9` |
| `cobertura_textual_gold.csv` | derivado | lo regenera `scripts/05_cobertura_textual.py` |
| `pares_evaluados_en_v1.csv` | | los 402 pares del corpus v1 anterior, con su split (ver abajo) |
| `procedencia.json` | | URLs, fecha de descarga, hashes de los CSV del portal y conteos |

## Fuentes (descarga del 06/11/2026)

SHA-256 de los CSV contenidos en los zips del portal:

| Base | Filas | SHA-256 |
|---|---|---|
| Base Infoleg de Normativa Nacional | 430.834 | `c9347a2da68c43ebad5f6c68e3820361c9ae00c535dcc0b8e7da112b46030a7e` |
| Base Complementaria de Normas Modificatorias | 380.481 | `b6f92136b0a178913fd6b71a58e2758abb0ddc1331f40d120518a14d59d542bf` |
| Base Complementaria de Normas Modificadas | 385.118 | `1e6d3e51e172477eabb104a126559d86a6810de6e30551d1433973a5a2f86a22` |

## Contenido

- **Semillas que se expanden un salto:** Leyes 20.744 (LCT), 27.802 (Modernización Laboral), 24.013 (Empleo), 24.557 (Riesgos del Trabajo) y 23.551 (Asociaciones Sindicales).
- **Nodos sin expandir:** Ley 14.250 y Ley 27.742.
- **Tipos de norma:** Ley, Decreto y Decreto/Ley.
- **Normas:** 340, de las cuales 306 tienen texto en InfoLEG.
- **Pares del gold:** 775, 583 en dev y 192 en test. El corte temporal es el 31/12/2019, por la fecha de la norma modificatoria.

## Relación con el corpus v1 anterior

Hasta el 09/11/2026 se usaron dos corpus. El v1 (183 normas, 402 pares, snapshot del 30/09) está contenido en este: sus 402 pares están acá con el mismo split. Las reglas del parser se diseñaron mirando los 275 pares de dev del v1, y los 127 de test del v1 se evaluaron una vez. `pares_evaluados_en_v1.csv` los identifica, para reportar también las métricas sobre los pares que nunca se usaron:

| Split | Pares del v1 | Pares nuevos | Total |
|---|---|---|---|
| dev | 275 | 308 | 583 |
| test | 127 | 65 | 192 |

El v1 sigue disponible en el historial de git (commit `cc6da6a`) y en el documento 01 del Drive.

## Cobertura textual

| | Dev | Test |
|---|---|---|
| Cita por número | 451 | 183 |
| Cita solo por nombre | 21 | 2 |
| Sin mención | 76 | 7 |
| Sin texto | 35 | 0 |
