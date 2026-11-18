# Parser híbrido en cascada: resultados

La explicación completa (cómo funciona, decisiones y resultados) está en [`docs/parser_hibrido.md`](../../docs/parser_hibrido.md).

Lo congelado el 18/11/2026, mirando solo dev:

- prompt `hibrido-v2-2026-11-18`;
- política `previa`, con umbrales 0,15 para descartar y 0,5 para agregar.

Test se evaluó una sola vez.

| | P | R | F1 |
|---|---|---|---|
| dev | 0,771 | 0,746 | **0,758** |
| test | 0,761 | 0,911 | 0,829 |

## Archivos

- `candidatos.csv`: un candidato (par de normas) por fila. Trae la zona, la opinión de la regla F3, la probabilidad, el tipo y el motivo que da el LLM, si la cita se verificó y la decisión de cada política.
- `relaciones_hibrido.csv`: la salida estándar, con `fuente = hibrido`.
- `metricas.json`: métricas por política y por zona, y el barrido de umbrales en dev.
- `cache/`: las respuestas del LLM de los prompts v1 (descartado) y v2. Con la caché, volver a correr no llama a la API.
