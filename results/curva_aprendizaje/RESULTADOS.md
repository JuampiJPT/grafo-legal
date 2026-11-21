# Curva de aprendizaje de los modelos supervisados (B68)

Script: `scripts/32_curva_aprendizaje.py`. Figura: `docs/informe_avance/figuras/fig8_curva_aprendizaje.png`.

## Pregunta

Los modelos de los scripts 08 (random forest con 22 atributos) y 13 (TF-IDF con regresión logística) empatan o pierden contra las reglas. ¿Es porque se entrenaron con pocos datos o porque su representación no alcanza?

## Con cuántos datos se entrenaron

| Qué | Cantidad |
|---|---|
| Normas del corpus, con texto | 340, de las cuales 306 tienen texto |
| Pares candidatos, todos | 1.091 |
| Pares candidatos en dev, para entrenar | 801, de 230 normas de origen; 472 positivos y 329 negativos |
| Pares candidatos en test | 290, de 43 normas de origen |
| Pares por partición de entrenamiento en la CV | unos 640, de unas 184 normas |
| Relaciones Ley/Decreto con texto en ambos extremos en toda la base de InfoLEG | 37.248, de 18.201 normas de origen |

Las etiquetas del entrenamiento salen del gold de InfoLEG (`en_gold`). El dataset usa 273 normas de origen (230 en dev y 43 en test), alrededor del 1,5 % de las 18.201 normas modificatorias que InfoLEG podría etiquetar en estos tipos de norma. Su gold tiene 775 relaciones, contra 37.248 en la base completa: unas 48 veces menos. El corpus se limitó al dominio laboral: 5 semillas expandidas un salto (decisión D11). Fue una decisión de alcance para poder revisar errores a mano, no una limitación de las fuentes. Los modelos nunca se entrenaron con un corpus más grande.

## Método

- **Validación.** Solo dev; test no se toca (B16). Se usó validación cruzada agrupada por norma de origen (5 particiones), igual que en 08 y 13.
- **Submuestreo.** En cada partición se entrena con el 10, 20, 30, 50, 70 y 100 % de las normas de origen del entrenamiento. Cada fracción se sortea 5 veces, y la de 100 % una sola. Se evalúa siempre sobre la partición de validación completa.
- **Hiperparámetros fijos**, los que eligieron 08 y 13:

  | Modelo | Configuración | Umbral |
  |---|---|---|
  | Random forest | 400 árboles | 0,45 |
  | TF-IDF + atributos | C = 30 | 0,20 |
  | TF-IDF solo | C = 10 | 0,40 |
- **Métricas.** Se miden sobre los pares candidatos: F1 con el umbral fijo y precisión promedio (AP, que no depende del umbral). También se mide la F1 sobre el propio entrenamiento.
- **Diferencia con 08 y 13.** Las F1 de esos scripts son contra el gold completo, que incluye los pares que el detector no propone. En dev, ningún clasificador puede recuperar el 19 % del gold, porque el recall de los candidatos es 0,81. Por eso las cifras de este análisis son más altas que las de 08 y 13.

## Resultados (media entre particiones; ± desvío entre particiones)

| Modelo | 61 pares | 188 pares | 316 pares | 641 pares (todo) | F1 sobre el propio entrenamiento |
|---|---|---|---|---|---|
| Random forest, F1 | 0,727 | 0,774 | 0,774 | 0,814 ± 0,042 | 0,936 |
| TF-IDF + atributos, F1 | 0,735 | 0,793 | 0,809 | 0,831 ± 0,040 | 0,986 |
| TF-IDF solo, F1 | 0,731 | 0,765 | 0,782 | 0,800 ± 0,039 | 0,992 |
| Reglas F (no se entrenan) | 0,812 | 0,812 | 0,812 | 0,812 ± 0,026 | — |
| Random forest, AP | 0,834 | 0,868 | 0,874 | 0,897 | |
| TF-IDF + atributos, AP | 0,822 | 0,872 | 0,890 | 0,909 | |

Una recta en log(n) ajustada a las curvas da +0,020 a +0,026 de F1 por cada vez que se duplican los datos.

## Lectura

1. **Las curvas no se aplanan.** Las tres siguen subiendo entre el 50 % y el 100 % de los datos, y la AP también, con más de 0,5 puntos cada 100 pares. Con los datos actuales los modelos todavía están limitados por la cantidad de datos.
2. **Hay alta varianza.** La brecha entre la F1 sobre el entrenamiento y la de validación es de 0,12 en el random forest y de 0,16 a 0,19 en TF-IDF. Los modelos de texto casi memorizan el entrenamiento (F1 de 0,99). Esa brecha es la señal típica de que faltan datos, o de que sobra capacidad para los datos que hay.
3. **El cruce con las reglas llega recién al final.** Con todo dev, los modelos alcanzan a las reglas y el de TF-IDF con atributos las pasa por poco: 0,831 contra 0,812. Pero el desvío entre particiones es de unos 0,04, así que la diferencia no es concluyente. Es coherente con el empate que se midió en test.
4. **La calidad de las etiquetas no es la causa principal.** El análisis de errores (`results/errores_explicados/RESULTADOS.md`) encontró solo 5 posibles omisiones del gold en dev. La mayoría de los falsos positivos son citas en el VISTO (48) y remisiones desde una ley (66). Distinguirlos exige saber a qué norma se aplica el verbo, y ahí también pesa la representación (bolsa de palabras).
5. **Extrapolación, solo indicativa.** Si la tendencia logarítmica se mantuviera, duplicar los datos daría unos 2,5 puntos de F1 y multiplicarlos por 10 daría unos 8 puntos. Proyectar fuera del rango medido no está garantizado, y la base de InfoLEG ofrece unas 50 veces más relaciones.

## Conclusión

La conclusión anterior («con atributos de superficie el techo lo pone la representación») era incompleta. Con 801 pares de dev, la causa medible es la **cantidad de datos**: las curvas siguen subiendo y la brecha entre entrenamiento y validación es grande. Que las curvas no se aplanen no prueba que la representación alcance: con más datos podrían aplanarse antes de superar con claridad a las reglas. La prueba directa sería ampliar el corpus con más normas de InfoLEG.

## Cómo ampliar el entrenamiento

1. **Más normas y textos.**
   - Elegir más normas de origen Ley y Decreto en la base complementaria de InfoLEG, que ya está en `data/raw`.
   - Bajar sus textos con `scripts/02_descargar_textos.py`.
   - Regenerar candidatos y atributos con los scripts 03 y 07.
   - Cuidar que ninguna norma de test entre al entrenamiento.
   - Desde los entornos de esta sesión, InfoLEG devuelve 403 por el filtro de red; la descarga hay que hacerla desde la Mac.
2. **Repetir esta curva con el doble y con 10 veces más datos**, para ver si se aplana.
3. **Si se aplana por debajo del LLM**, la limitación es la representación: pasar a un transformer en español con marcado de la mención.
