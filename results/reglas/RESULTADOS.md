# Parser 1 (reglas): resultados sobre el corpus único

Estas son las reglas **v1**, congeladas el 06/11/2026 después de diseñarlas sobre el dev del corpus v1. Se aplicaron sin cambios al corpus único el 09/11/2026. Es la primera vez que este parser ve los 308 pares nuevos de dev y los 65 nuevos de test.

## Métricas a nivel de par

| Config | Split | P | R | F1 | F1 sin pares del v1 |
|---|---|---|---|---|---|
| A. todas las menciones | dev | 0,589 | 0,810 | **0,682** | **0,562** |
| B. articulado | dev | 0,642 | 0,652 | 0,647 | 0,506 |
| C. articulado + temporal | dev | 0,653 | 0,650 | 0,652 | 0,514 |
| D. C + verbo en el artículo | dev | 0,708 | 0,482 | 0,574 | 0,461 |
| E. C + verbo en la oración | dev | 0,792 | 0,360 | 0,495 | 0,418 |
| A | test | 0,638 | 0,964 | 0,768 | 0,553 |
| B | test | 0,719 | 0,854 | 0,781 | 0,551 |
| **C** (configuración final) | test | **0,732** | **0,854** | **0,788** | **0,563** |
| D | test | 0,735 | 0,651 | 0,691 | 0,543 |
| E | test | 0,856 | 0,526 | 0,652 | 0,509 |

En la última columna se descartan los pares del corpus v1, que se usaron para diseñar las reglas (dev) o ya se evaluaron (test). Son 308 pares de dev y 65 de test.

## Comparación con el corpus v1

| Configuración C | Dev | Test |
|---|---|---|
| Sobre el corpus v1 (06/11) | 0,716 | 0,844 |
| Sobre el corpus único | 0,652 | 0,788 |
| Solo pares nuevos | 0,514 | 0,563 |

## Lectura

1. **Las reglas no generalizan bien a los pares nuevos.** En los pares nuevos el F1 cae unos 14 puntos en dev (de 0,652 a 0,514) y 22 en test (de 0,788 a 0,563). Caen la precisión (alrededor de 0,46) y el recall. De los 201 falsos positivos nuevos de dev, solo 27 apuntan a las semillas agregadas (Leyes 24.013, 24.557 y 23.551). Los destinos más frecuentes son la LCT (19), la Ley de Ganancias (15), la Ley 24.557 (14), el Decreto 390/76 (12) y la Ley de IVA (11). El Decreto 390/76 aparece porque las normas citan la LCT como «Ley 20.744 (t.o. por Decreto 390/76)»: el detector cuenta el decreto del texto ordenado como una mención aparte. Ganancias e IVA suelen nombrarse de paso.
2. **El filtro de articulado ya no conviene.** En el corpus único, la configuración A supera a la C en dev (0,682 contra 0,652). En los pares nuevos, restringir al articulado baja el recall de 0,81 a 0,57. De los 73 pares nuevos que filtra la regla de zona, en 72 la mención está solo en el encabezado (VISTO / CONSIDERANDO) o en un anexo.
3. **Esto habilita una iteración nueva de reglas, solo sobre dev.** El dev del corpus único tiene 308 pares que no se usaron para diseñar. El test (192 pares) se evalúa una sola vez con las reglas v2 congeladas, y se reporta también sin los 127 pares del v1.

## Errores de la configuración C

| Split | Sin mención | Sin texto | Filtrado por reglas | FP con número | FP solo alias |
|---|---|---|---|---|---|
| dev | 76 | 35 | 93 | 161 | 40 |
| test | 7 | 0 | 21 | 51 | 9 |
