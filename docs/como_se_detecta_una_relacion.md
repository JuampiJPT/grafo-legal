# Cómo se detecta una relación entre normas

Este documento explica, paso por paso y con un caso real, cómo el parser de reglas pasa del texto de una norma a una arista del grafo. El parser es genérico: solo el primer paso, el adaptador, depende de que el texto venga de InfoLEG. Para otra fuente, como un digesto provincial, se escribe otro adaptador y el resto no cambia.

**Caso de ejemplo.** Ley 24.013, artículo 25:

«ARTICULO 25.- Sustituyese el artículo 198, de la Ley de Contrato de Trabajo (t.o 1976), por lo siguiente: "Artículo 198.- Jornada reducida. …"»

Resultado: `Ley 24013 —SUSTITUYE {articulo: 198}→ Ley 20744`, con la evidencia en los caracteres 16.784 a 16.810 del texto limpio.

## 1. Adaptador: del HTML al texto con estructura

Archivo: `fuentes/infoleg.py`.

- Se pasa el HTML de InfoLEG a texto plano, sacando etiquetas, notas al pie y espacios repetidos (`html_a_texto`).
- Se corta el texto en partes: **VISTO**, **CONSIDERANDO**, **articulado** y anexos. Cada parte, a su vez, se corta en artículos (`segmentar`).
- Cada artículo se guarda con su número y su posición en el texto. Por eso toda relación queda trazable al fragmento exacto.

En el ejemplo, el artículo 25 de la Ley 24.013 queda como un segmento del articulado.

## 2. Detección: encontrar cada vez que se nombra una norma

Archivo: `extractores/menciones.py`. Hay dos detectores.

- **Por número, con expresiones regulares.** Reconoce «Ley N° 24.557», «Decreto 1694/06», «leyes 23.551 y 25.674» y «DNU 70/2023».
  - El año se lee de «/06».
  - Desde la v3, también se lee de la fecha que sigue a la mención: «Decreto 467 del 14 de abril de 1988».
- **Por nombre, con un gazetteer.** Una lista de nombres propios de normas: «Ley de Contrato de Trabajo», «L.C.T.», «Ley de Ministerios», «Ley de Impuesto a las Ganancias», entre otros.

En el ejemplo, el detector por nombre encuentra «Ley de Contrato de Trabajo». La detección casi no falla: en dev encuentra el 99,6 % de las menciones del gold y en test el 100 %.

## 3. Normalización: a qué norma concreta se refiere

Archivo: `catalogo.py`. Cada mención (tipo, número, año) se busca en el catálogo de InfoLEG.

- Si hay **una sola candidata** con ese tipo, número y año, queda **resuelta**.
- Si **falta el año** y hay varias candidatas, queda **ambigua**. Se resuelve por mundo cerrado solo si una sola de ellas está en el corpus; si no, se descarta.
- Si la norma existe pero **no está entre las 340 del corpus**, queda **fuera del corpus**. Es una norma real; no se puede enlazar porque no hay nodo destino.

En el ejemplo, «Ley de Contrato de Trabajo» resuelve a la Ley 20.744 (id 25552). Con la v3 ninguna vinculación verificable queda mal y ningún par del gold se pierde en este paso.

## 4. Extracción: ¿la mención es una relación?

Archivos: `extractores/reglas_v2.py` y `reglas_v3.py`. Nombrar una norma no implica modificarla: muchas menciones son remisiones («según la Ley 24.557»). Para cada mención se calculan cinco señales:

| Señal | Qué mira | En el ejemplo |
|---|---|---|
| Parte | ¿Está en el VISTO, el CONSIDERANDO o el articulado? | Articulado |
| Verbo | ¿La oración tiene un verbo modificatorio (sustitúyese, derógase, modifícase, incorpórase, reglaméntase, apruébase)? | «Sustituyese» |
| Procedencia | ¿Es una cita de origen («t.o. por Decreto …», «modificado por …»)? | No: «t.o 1976» es la versión del destino, no otra norma. |
| Temporal | ¿La norma destino es anterior o contemporánea al origen? Una norma no modifica a otra posterior. | 1974, anterior a 1991: sí |
| Método | ¿Se encontró por número o por nombre? | Por nombre |

Con estas señales decide la **regla F** (v2). Una mención es relación si no es procedencia, pasa la condición temporal y además cumple una de estas dos condiciones:

- está en el **VISTO**, donde se enumeran los fundamentos y el 80 % de los pares están en InfoLEG; o
- está en el **articulado, con número**, y el origen no es un decreto o la oración tiene un verbo.

El CONSIDERANDO no cuenta: solo el 24 % de esos pares está en InfoLEG.

La **regla F3** (v3) agrega un caso: en el articulado, una norma nombrada **sin número** también cuenta si la oración tiene verbo. El ejemplo entra por esta vía: se nombra por su nombre y hay un verbo, «Sustituyese».

Los umbrales de la regla se eligieron midiendo en dev (normas hasta 2019). Después la regla se congeló y test se midió una sola vez.

## 5. Tipado: qué clase de relación es

Archivo: `extractores/relaciones.py`.

- El **verbo** de la oración da el tipo:

  | Verbo | Tipo |
  |---|---|
  | sustitúyese | SUSTITUYE |
  | derógase | DEROGA |
  | modifícase | MODIFICA |
  | incorpórase | INCORPORA |
  | reglaméntase o apruébase la reglamentación | REGLAMENTA |
  | sin verbo | CITA |

- Si el texto dice «el artículo 198 de la ley …», el destino es ese **artículo**, no la norma entera. Desde la v3 se ignora el número del propio artículo origen («Artículo 1° — Apruébase …»).

En el ejemplo: tipo SUSTITUYE, artículo destino 198.

## 6. Salida estándar y grafo

Archivos: `salida.py` y `grafo.py`. Cada relación se escribe como una fila con los siguientes campos:

- origen (norma y artículo);
- tipo;
- destino (norma y, si corresponde, artículo);
- verbo;
- método;
- inicio y fin del fragmento;
- el fragmento;
- la **fuente**: `reglas_v2`, `reglas_v3` o `llm`.

Con esas filas se arma el grafo:

```
(:Norma {Ley 24013})-[:CONTIENE]->(:Articulo {25})
(:Articulo {25})-[:SUSTITUYE {verbo, inicio, fin, fragmento, fuente:'reglas_v3'}]->(:Articulo {198})
(:Norma {Ley 20744})-[:CONTIENE]->(:Articulo {198})
```

En Neo4j se carga con `MERGE` por fuente, así que los grafos de la v2, la v3 y el LLM conviven sin pisarse. Una consulta puede elegir la fuente o compararlas.

## 7. Cómo se sabe si la relación está bien

Archivo: `docs/comparacion_con_el_gold.md`. El gold es la lista de modificatorias y modificadas que publica InfoLEG. **Nunca se usa como entrada del parser**: solo para medir.

- Se compara a nivel de **par de normas** (origen, destino).
- Se miden precisión, recall y F1 sobre todo el gold, por separado en dev y en test.
- Cada error tiene su causa en `docs/analisis_de_fallos.md`.

## El parser con LLM, en los mismos términos

Archivo: `extractores/llm.py`. Reemplaza los pasos 4 y 5 por la lectura de un modelo de lenguaje, y deja iguales el adaptador y el catálogo:

1. Se envía cada artículo que menciona alguna norma.
2. El modelo devuelve las relaciones con la cita textual que las justifica.
3. **Se verifica que la cita esté en el texto**; si no está, se descarta (anti-alucinación).
4. La norma destino se resuelve con el mismo catálogo.

Así, la comparación entre los dos parsers mide solo la lectura del texto.
