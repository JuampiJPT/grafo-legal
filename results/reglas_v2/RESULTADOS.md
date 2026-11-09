# Parser 1 (reglas v2): resultados sobre el corpus único

Las reglas **v2** se diseñaron el 09/11/2026 solo con los errores del dev del corpus único (bitácora B36) y se congelaron antes de mirar test. Test se evaluó una vez, ese mismo día. El código está en `src/grafo_legal/extractores/reglas_v2.py`; las reglas v1 siguen congeladas en `reglas.py` y sus resultados en `results/reglas/`.

Huella de lo congelado (SHA-256): `reglas_v2.py` 323a8630…, `menciones.py` daeb3f48…, `catalogo.py` f68a9e6a….

## Qué cambia respecto de v1

1. **VISTO y CONSIDERANDO.** El encabezado se parte en VISTO y CONSIDERANDO. En dev, los pares citados en el VISTO están en el gold el 80 % de las veces; los que solo aparecen en el CONSIDERANDO, el 24 %.
2. **Citas de procedencia.** Se descarta la mención de la norma que dio origen a un texto: «Ley 20.744 (t.o. por Decreto 390/76)», «sustituido por el artículo 2° del Decreto 1278/00».
3. **Verbos.** «Complementarias» y «reglamentarios» dejan de contar como verbo modificatorio.
4. **Regla de par (configuración F).** Se predice el par si hay una mención no posterior al origen y que no sea de procedencia, que cumpla una de estas dos condiciones:
   - está en el VISTO;
   - está en el articulado, con número, y el origen es una ley o la oración tiene un verbo.

## Métricas a nivel de par

| Config | Split | P | R | F1 | F1 sin pares del v1 |
|---|---|---|---|---|---|
| A. todas las menciones | dev | 0,612 | 0,805 | 0,695 | 0,583 |
| C. articulado + temporal | dev | 0,671 | 0,647 | 0,658 | 0,526 |
| **F. VISTO, o articulado con verbo o con origen ley** | dev | **0,750** | **0,717** | **0,733** | **0,668** |
| F sin la condición del VISTO | dev | 0,749 | 0,429 | 0,545 | 0,426 |
| F sin la condición para decretos | dev | 0,698 | 0,751 | 0,723 | 0,643 |
| A | test | 0,653 | 0,958 | 0,776 | 0,570 |
| C | test | 0,738 | 0,849 | 0,789 | 0,570 |
| **F** (configuración final) | test | **0,785** | **0,875** | **0,828** | **0,671** |
| F sin la condición del VISTO | test | 0,835 | 0,526 | 0,645 | 0,426 |
| F sin la condición para decretos | test | 0,727 | 0,927 | 0,815 | 0,639 |

En v2, los 308 pares nuevos de dev ya no son pares no vistos: con ellos se diseñaron las reglas. Los 192 pares de test sí son todos no vistos para v2.

## Comparación con v1 (configuración final de cada versión)

| | Dev | Test | Test sin pares del v1 |
|---|---|---|---|
| Reglas v1, configuración C | 0,652 | 0,788 | 0,563 |
| Reglas v2, configuración F | 0,733 | 0,828 | 0,671 |

## Lectura

1. **La mejora se sostiene en test.** El F1 sube 8 puntos en dev y 4 en test, y 11 en los 65 pares de test que no pertenecen al v1. El cambio que más aporta es aceptar el VISTO: sin él, el F1 de test baja a 0,645.
2. **La condición para decretos cambia recall por precisión.** Sin ella, test tiene más recall (0,927) y menos precisión (0,727); con ella, el F1 es 1,3 puntos mejor en test y 1 punto mejor en dev.
3. **Lo que queda son remisiones.** En la revisión de 30 falsos positivos de dev (`docs/revision_manual/revision_fp_dev_30.csv`), 16 son remisiones en el articulado («conforme a la ley…», «previstas en la ley…»), 9 son normas de listas largas del VISTO, 2 son citas de procedencia y 3 parecen modificaciones reales que InfoLEG no registra. Separar la remisión de la modificación sin perder recall pide entender la oración, que es lo que se le va a pedir al parser LLM.

## Errores de la configuración F

| Split | Sin mención | Sin texto | Filtrado por reglas | FP con número | FP solo alias |
|---|---|---|---|---|---|
| dev | 76 | 35 | 54 | 138 | 1 |
| test | 7 | 0 | 17 | 45 | 1 |
