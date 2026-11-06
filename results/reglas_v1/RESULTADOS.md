# Parser 1 (reglas): resultados sobre corpus v1

- Reglas congeladas el 06/11/2026. Test se evaluó una sola vez con estas reglas.
- Configuración final: **C** (menciones del articulado más el filtro temporal).
- Archivos: `evidencias.csv` (una fila por mención resuelta, con artículo, offsets y fragmento), `metricas.json` y `errores.csv`.

## Métricas a nivel de par

En la tabla, «gold con texto» excluye los 9 pares cuya modificatoria no tiene texto en InfoLEG.

| Config | Split | Predichos | Gold | TP | FP | FN | P | R | F1 | R (gold con texto) |
|---|---|---|---|---|---|---|---|---|---|---|
| A. todas las menciones | dev | 357 | 275 | 223 | 134 | 52 | 0,625 | 0,811 | 0,706 | 0,838 |
| B. articulado | dev | 304 | 275 | 205 | 99 | 70 | 0,674 | 0,746 | 0,708 | 0,771 |
| **C. articulado + temporal** | dev | 295 | 275 | 204 | 91 | 71 | **0,692** | **0,742** | **0,716** | 0,767 |
| D. C + verbo en el artículo | dev | 213 | 275 | 156 | 57 | 119 | 0,732 | 0,567 | 0,639 | 0,587 |
| E. C + verbo en la oración | dev | 135 | 275 | 114 | 21 | 161 | 0,844 | 0,414 | 0,556 | 0,429 |
| A | test | 164 | 127 | 120 | 44 | 7 | 0,732 | 0,945 | 0,825 | 0,945 |
| B | test | 149 | 127 | 116 | 33 | 11 | 0,778 | 0,913 | 0,841 | 0,913 |
| **C** | test | 148 | 127 | 116 | 32 | 11 | **0,784** | **0,913** | **0,844** | 0,913 |
| D | test | 109 | 127 | 85 | 24 | 42 | 0,780 | 0,669 | 0,720 | 0,669 |
| E | test | 86 | 127 | 73 | 13 | 54 | 0,849 | 0,575 | 0,685 | 0,575 |

## Errores de la configuración C

| Split | Sin mención en el texto | Sin texto | Filtrado por las reglas | FP con número | FP solo por alias |
|---|---|---|---|---|---|
| dev | 43 | 9 | 19 | 79 | 12 |
| test | 7 | 0 | 4 | 25 | 7 |

Los falsos negativos «sin mención» y «sin texto» son el techo del enfoque textual: ningún parser que lea solo el texto de la modificatoria puede recuperarlos.

## Lectura

1. **El filtro de zona sirve, el de verbo no, para este gold.** Restringir al articulado sube la precisión 5 puntos y casi no pierde recall. Exigir un verbo modificatorio deja afuera las reglamentaciones y las remisiones que InfoLEG también registra como «modifica/complementa» (ver D6 en `docs/decisiones.md`). Las configuraciones D y E quedan como base para la tarea de tipar la relación.
2. **Los falsos positivos son, en su mayoría, citas sin vínculo en InfoLEG.** Ejemplos: «en el marco del procedimiento preventivo de crisis previsto en … la Ley Nº 24.013», o «exención en el impuesto a las ganancias, ley 20.628». No siempre son errores del parser: el gold de InfoLEG registra algunas remisiones y otras no. Antes de cerrar la precisión conviene muestrear 30 FP y revisarlos a mano.
3. **Test da mejor que dev (0,844 contra 0,716), pero no por las reglas.** El 54% de los pares de test sale de tres normas recientes y largas que citan todo por número: Ley 27.802, DNU 70/2023 y Ley 27.742. Además, test casi no tiene modificatorias viejas sin mención. Es un sesgo del corte temporal, y es el motivo del corpus v2 (D2).
4. **Vínculos por texto ordenado.** InfoLEG enlaza el decreto que aprobó el texto ordenado (por ejemplo, IVA t.o. 1997 = Decreto 280/97) cuando el texto solo cita la ley por su nombre. Una regla de alias por texto ordenado recuperaría algunos de estos pares. Queda para la versión siguiente del parser y se mide en dev de v2.
