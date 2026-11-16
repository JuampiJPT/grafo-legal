# Modelo con contexto textual e híbrido reglas + modelo

`scripts/13_modelo_contextual.py` implementa el método basado en modelos «a partir del contexto textual» que pide la consigna, y una primera aproximación al híbrido de la PI2 (bitácora B46).

## Qué lee el modelo

Por cada par candidato (norma origen → norma destino) se juntan los fragmentos de todas sus menciones: 150 caracteres a cada lado, los que el parser ya guarda como evidencia. En cada fragmento:

- la mención del destino se reemplaza por la palabra `DESTINO`;
- los dígitos se reemplazan por `#`, para que el modelo aprenda el contexto y no los números de normas;
- adelante va la parte del documento donde está la mención (`PARTE_visto`, `PARTE_articulado`…).

Ejemplo: «Sustitúyese el artículo 80 de la Ley N° 20.744 por» queda como `PARTE_articulado Sustitúyese el artículo ## de la DESTINO por`.

Sobre eso se calcula un TF-IDF de unigramas y bigramas de palabras y se entrena una regresión logística. Hay dos variantes: solo el texto (`contexto`), y el texto más los atributos de superficie del clasificador de 08 (`contexto+superficie`).

## Híbrido

Con las mismas evidencias que usa la regla F, los candidatos se separan en tres grupos:

| Grupo | Criterio | Candidatos dev | En el gold |
|---|---|---|---|
| Seguro sí | Mención en el VISTO, o en el articulado con verbo en la oración | 407 | 82 % |
| Seguro no | Ninguna mención cuenta: solo notas, anexos, procedencia o destino posterior | 64 | 9 % |
| Zona gris | El resto: articulado sin verbo, solo CONSIDERANDO, solo alias | 330 | 40 % |

Las reglas deciden los grupos seguros y el modelo decide la zona gris, donde las reglas aciertan menos.

## Protocolo

El mismo de 08:

- **Selección en dev.** Validación cruzada de 5 particiones, agrupada por norma origen. Se eligen C (de 0,3 a 100) y el umbral (de 0,20 a 0,80).
- **Modelo final.** Se entrena con todo dev y test se evalúa una sola vez, el 16/11/2026, con el script congelado (SHA-256 `d7734e9d…`). Después solo se agregó al script que guarde la probabilidad de cada variante en `predicciones.csv`. Se volvió a correr y `comparacion.csv` dio idéntico.
- **Métricas.** Contra todo el gold del split.

## Resultados

| Método | dev (CV) P | R | F1 | test P | R | F1 |
|---|---|---|---|---|---|---|
| Reglas v2, configuración F | 0,750 | 0,717 | 0,733 | 0,785 | 0,875 | 0,828 |
| Clasificador de superficie (08, random forest) | 0,766 | 0,695 | 0,728 | 0,799 | 0,849 | 0,823 |
| Modelo contextual, solo texto (C=10, umbral 0,40) | 0,705 | 0,746 | 0,725 | 0,697 | 0,839 | 0,761 |
| Modelo contextual, texto + superficie (C=30, umbral 0,20) | 0,746 | 0,756 | 0,751 | 0,760 | 0,807 | 0,783 |
| Híbrido: reglas + modelo de solo texto en la zona gris | 0,714 | 0,770 | 0,741 | 0,716 | 0,932 | 0,810 |
| **Híbrido: reglas + modelo texto + superficie en la zona gris** | 0,736 | 0,763 | 0,749 | 0,780 | 0,906 | **0,839** |

## Lectura

1. **El modelo con contexto, solo, no supera a las reglas.** En dev empata y en test cae a 0,761 con solo texto y a 0,783 con atributos. Con 801 pares de entrenamiento, un TF-IDF aprende rasgos del dominio que no transfieren de un período al siguiente: test son las normas de 2020 en adelante.
2. **El híbrido da el mejor F1 de test (0,839),** un punto más que las reglas, con más recall (0,906 contra 0,875) y precisión parecida. La mejora sale de la zona gris: el modelo recupera relaciones que las reglas descartaban, como decretos que remiten a una ley en el articulado sin verbo. Con 192 pares de test, un punto no es una diferencia significativa. El intervalo del 95 % de la diferencia con las reglas va de −2,2 a +4,0 puntos (bootstrap por norma origen, `results/comparacion/`, bitácora B49). En cambio, el modelo de solo texto es significativamente peor que las reglas: entre −13,6 y −1,5 puntos.
3. **Lo que pesa en el modelo** (`terminos.csv`). A favor de que haya relación: `parte_articulado articulo`, `la destino`, `siguiente` (de «por el siguiente»), `el articulo`, `parte_visto`. En contra: `alcance`, `especial`, `caso`, `contrato de`, `por ley`. Son señales de técnica legislativa («sustitúyese el artículo # de la DESTINO por el siguiente») frente a remisiones de contenido.

## Archivos

- `metricas.json`: hiperparámetros elegidos, CV y test de cada variante, grupos.
- `predicciones.csv`: probabilidad por candidato (en dev, la de la validación cruzada).
- `comparacion.csv`: la tabla de arriba.
- `terminos.csv`: los 30 n-gramas con más peso a favor y en contra.
