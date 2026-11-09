# Salida estándar de los parsers

Todo parser del TP (reglas, LLM, híbrido) escribe sus resultados en la misma tabla de relaciones, y el grafo se arma solo a partir de ella (bitácora B41). Así, sumar un parser o una fuente de documentos no cambia ni el grafo ni la evaluación. El formato está definido en `src/grafo_legal/salida.py`, que también lo valida.

Una fila es una relación: **un artículo de la norma origen hace algo (el tipo) sobre una norma destino o sobre uno de sus artículos.**

## Tipos de relación

| Tipo | Cuándo | Ejemplo |
|---|---|---|
| `SUSTITUYE` | reemplaza un texto por otro | «Sustitúyese el artículo 245 de la Ley 20.744 por el siguiente…» |
| `INCORPORA` | agrega un texto nuevo | «Incorpórase como artículo 53 bis a la Ley 23.551…» |
| `DEROGA` | deja sin efecto | «Derógase la Ley 25.323» |
| `REGLAMENTA` | reglamenta | «Reglaméntase el artículo 179 de la Ley 20.744» |
| `MODIFICA` | otros cambios: modifica, prorroga, suspende, exime, ratifica | «Modifícase el artículo 7° de la Ley 23.546» |
| `CITA` | la nombra sin cambiarla: remisión o mención en el VISTO o el CONSIDERANDO | «…previstas en el artículo 80 de la Ley 24.013» |

## Columnas

| Columna | Qué es |
|---|---|
| `fuente` | parser que produjo la relación (`reglas_v2`, `llm`, `hibrido`…) |
| `id_norma_origen`, `norma_origen` | norma que contiene el texto |
| `id_articulo_origen`, `articulo_origen` | segmento de origen (`id_norma#orden`; el 0 es el encabezado) y su número |
| `parte_origen` | `visto`, `considerando`, `articulado` o `anexo` |
| `tipo` | uno de los seis tipos |
| `id_norma_destino`, `norma_destino` | norma sobre la que recae la relación |
| `articulo_destino` | número del artículo destino; vacío si la relación es con la norma entera |
| `verbo` | verbo del texto que determinó el tipo (vacío en `CITA`) |
| `metodo` | cómo se detectó la mención: `regex_numero`, `alias`, `llm` |
| `confianza` | probabilidad que da el parser, si la da (vacía en las reglas) |
| `n_menciones` | menciones que sustentan la relación |
| `inicio`, `fin`, `fragmento` | evidencia: posición de la primera mención en el texto y el texto que la rodea |

La clave de una relación es (`fuente`, `id_articulo_origen`, `tipo`, `id_norma_destino`, `articulo_destino`): no puede haber dos filas con la misma clave.

## Cómo la produce el parser de reglas v2

`scripts/09_relaciones.py` toma las menciones de `results/reglas_v2/evidencias.csv` y escribe `results/relaciones/relaciones_reglas_v2.csv`:

- **Qué menciones entran.** Se descartan las citas de procedencia, las menciones a normas posteriores al origen y las de las notas editoriales de InfoLEG, que no son texto de la norma.
- **Tipo.** Sale del verbo de la oración en que aparece la mención. Una mención sin verbo, o que está en el VISTO o el CONSIDERANDO, es una `CITA`.
- **Artículo destino.** Es el «artículo N de la» que precede a la mención en la misma oración. Si hay varios («artículos 232, 233 y 245»), sale una relación por artículo, y un rango de hasta 40 artículos («43 a 65») se expande.

| | Relaciones |
|---|---|
| Total | 3.277 (1.037 pares de normas) |
| `CITA` | 2.332 |
| `SUSTITUYE` | 375 |
| `INCORPORA` | 181 |
| `MODIFICA` | 176 |
| `DEROGA` | 155 |
| `REGLAMENTA` | 58 |
| Con artículo destino | 1.684 (el 71 % de las que no son `CITA`) |

**Calidad del tipado.** Se revisó a mano una muestra de 36 relaciones, 6 por tipo (`docs/revision_manual/revision_tipos_36.csv`). El tipo es correcto en 24 (67 %) y el artículo destino en 30 (83 %). Los errores se repiten:

- **Tipo.** Las nominalizaciones y los verbos que no actúan («la derogación del artículo 2°», «deberá proponer la reglamentación», «prorrogadas por las leyes…») y el «texto ordenado» de una cita se toman como acción. `MODIFICA` es el tipo más afectado: solo 1 de 6 casos es correcto.
- **Artículo destino.** No se reconocen las incorporaciones con la forma «como artículo 53 bis a la Ley», y se confunde un artículo de la reglamentación de una ley con un artículo de la ley.

Mejorar el tipado es la próxima iteración de las reglas, y es lo que se espera que el parser LLM haga mejor.
