# Parser híbrido en cascada: las reglas filtran, el LLM decide la zona gris

Es el tercer parser del trabajo:

- código en `src/grafo_legal/extractores/hibrido.py`;
- script en `scripts/20_parser_hibrido.py`;
- resultados en `results/hibrido/`;
- grafo en `data/grafo_hibrido/`.

Bitácora B55 y decisión D27.

## Qué problema resuelve

Las reglas y el LLM fallan en cosas distintas:

- **Las reglas** detectan y normalizan casi sin errores: con la v3, ninguna vinculación verificable está mal. Pero deciden si hay relación mirando solo la superficie: en qué parte está la mención y si la oración tiene un verbo. Donde eso no alcanza, aciertan entre el 15 % y el 90 %.
- **El LLM puro** lee mejor la oración, pero además de decidir tiene que encontrar cada norma y escribir su número, y eso le cuesta caro: tiene que leer todo el corpus.

El híbrido anterior combinaba al final las salidas de los dos (intersección o unión). Este es un **solo parser en cascada**: cada etapa hace lo que mejor sabe hacer y le pasa a la siguiente solo lo que no pudo resolver.

## Cómo funciona

```
 texto de la norma
       │
 1. ESTRUCTURA Y CANDIDATOS (determinista: mismas piezas que las reglas v3)
       adaptador → árbol de la norma (VISTO, CONSIDERANDO, articulado, anexos, notas)
       detector  → cada mención a otra norma (número, nombre propio, año en la fecha)
       catálogo  → norma concreta (mundo cerrado)
       → un CANDIDATO por par (norma origen, norma destino), con todas sus menciones
       │
 2. FILTRO POR REGLAS: tres zonas
       DESCARTE  todas las menciones posteriores al origen, o solo en anexos o notas
       SEGURO    mención en el articulado, con verbo modificatorio en la oración y sin procedencia
       GRIS      todo lo demás
       │
 3. JUICIO DEL LLM (solo sobre candidatos SEGUROS y GRISES)
       por cada norma origen, sus candidatos con los fragmentos donde se nombran,
       la mención marcada entre ⟦ ⟧ → probabilidad de vínculo, tipo, artículo destino,
       cita textual y motivo
       │
 4. DECISIÓN
       SEGURO → se acepta; el LLM solo pone el tipo
       GRIS   → la regla F3 da una opinión previa y el LLM la corrige con confianza:
                  si F3 lo acepta, se descarta solo si el LLM le da menos de 0,15
                  si F3 lo rechaza, se acepta solo si el LLM le da 0,5 o más
       │
 5. VERIFICACIÓN: la cita del LLM tiene que estar en los fragmentos;
       si no está, el juicio no cuenta y queda lo que decía la regla
       │
 salida estándar (fuente = hibrido) → grafo
```

### Ejemplo de pedido

Este es un pedido real (Decreto 1382/2001), recortado:

```
NORMA ORIGEN: Decreto 1382 — Sistema integrado de proteccion a la familia (2001)

CANDIDATOS:
[C1] Ley 24013 — Ley de empleo (1991)
  (1) ARTICULADO, artículo 28: «… con destino al financiamiento del FONDO NACIONAL DE EMPLEO (⟦Ley Nº 24.013⟧) …»
  (2) VISTO: «… VISTO Las ⟦Leyes Nros. 22.431, 24.013⟧, 24.241 y 24.714 …»
[C2] Ley 24241 — Sistema integrado de jubilaciones y pensiones (1993)
  …
```

El LLM responde un JSON con una entrada por candidato: `probabilidad`, `relacion`, `tipo`, `articulo_destino`, `cita` y `motivo`.

### Por qué así

- **El LLM nunca inventa destinos.** Solo juzga normas que el texto nombra y que el catálogo resolvió. No puede alucinar un número ni vincular con otra norma del mismo número.
- **El LLM responde una pregunta cerrada:** ¿esta norma se vincula con esta otra? No tiene que extraer todo. Ve justo la evidencia que importa.
- **Cada decisión queda trazable.** `candidatos.csv` dice para cada par en qué zona cayó, qué opinaba la regla, qué probabilidad dio el LLM y por qué (el campo `motivo`), y si la cita se verificó.
- **Sale más barato que el LLM puro.** Lee unos 1.000 fragmentos y no las 306 normas completas: USD 3,6 por corrida, contra USD 14.

## Decisiones (todas tomadas mirando solo dev)

| # | Decisión | Alternativas | Por qué |
|---|---|---|---|
| 1 | Los candidatos salen de las **reglas v3** | v2 | La v3 normaliza mejor: lee el año escrito como fecha y ninguna vinculación verificable queda mal. Su regresión («texto sustituido por») acá no pesa, porque esos pares caen en la zona gris y los juzga el LLM. |
| 2 | **Zona segura** = articulado + verbo + no procedencia | Mandar todo al LLM | En dev, el 91 % de esos pares está en InfoLEG; el LLM solo agrega costo y riesgo. Igual se le pregunta, para el tipo. |
| 3 | **Criterio amplio de InfoLEG** («modifica o complementa») | Modificación estricta | El gold es amplio (B27). El prompt v1, estricto, aceptó solo 64 de 544 pares grises de dev, y 296 estaban en InfoLEG. Bajaba el F1 a 0,52. |
| 4 | El prompt le da al LLM las **tasas de base** (VISTO, alrededor del 80 %; solo CONSIDERANDO, alrededor del 25 %) | No darlas | Salen de dev (B36). Sin ellas, el LLM trata el VISTO como simple antecedente. |
| 5 | El LLM da una **probabilidad** y no solo sí o no | Solo sí o no | Permite elegir el umbral en dev y combinarla con la regla. |
| 6 | **Política «previa»**: la regla F3 opina primero y el LLM la corrige con confianza | «cascada»: el LLM decide toda la zona gris; «llm_veta»: también puede rechazar los seguros | En dev, «previa» da F1 0,758; «cascada», a lo sumo 0,729 con su mejor umbral; «llm_veta», 0,728. El LLM, solo, es menos preciso que la regla en el VISTO. Sirve para corregirla cuando está muy seguro. |
| 7 | Umbrales **0,15 para descartar y 0,5 para agregar** | El máximo del barrido en dev, 0,15 y 0,4 (F1 0,760) | La diferencia es de 0,2 puntos. Se eligió 0,5 porque es el umbral natural de una probabilidad y no ajusta al ruido de dev. |
| 8 | **Verificar la cita** | Confiar en el LLM | Mismo control anti-alucinación que el LLM puro. Se descartaron 10 juicios de 1.006. |
| 9 | **Tipo:** el del LLM en la relación que cita; las demás relaciones del par, el de las reglas | El de las reglas siempre | El LLM tipa mucho mejor (B54). |
| 10 | La salida conserva **todas** las relaciones por artículo de las reglas v3; los pares no aceptados quedan como CITA | Una fila por par aceptado | Así el grafo tiene el mismo detalle que los otros parsers y el tipo se puede evaluar sobre los mismos 78 casos. |
| 11 | **Parseo tolerante**: se limpia `.replace(...)` dentro del JSON | Reintentar | En la v1, 199 respuestas traían código adentro del JSON. En la v2 ya no pasó, pero se deja el arreglo. |

El prompt v1 queda en la caché, con su versión, como registro del intento descartado.

## Resultados

### Detección de relaciones (pares de normas contra InfoLEG)

| Método | P test | R test | F1 dev | F1 test | Diferencia con reglas v2 (IC 95 %) |
|---|---|---|---|---|---|
| Reglas v2 | 0,785 | 0,875 | 0,733 | 0,828 | — |
| Reglas v3 | 0,779 | 0,880 | 0,750 | 0,826 | −0,1 [−1,9; +1,3] |
| LLM puro | 0,763 | 0,938 | 0,741 | 0,841 | +1,3 [−1,9; +4,0] |
| Intersección reglas y LLM | 0,804 | 0,875 | 0,735 | 0,838 | +1,0 [+0,2; +2,5] |
| **Híbrido en cascada** | 0,761 | **0,911** | **0,758** | 0,829 | +0,2 [−3,4; +3,2] |

- **En dev es el mejor de todos** (0,758). En test empata con las reglas: sube el recall de 0,880 a 0,911 y baja la precisión.
- **Qué hace el LLM en la zona gris de test:**
  - de los pares que F3 rechazaba, agrega 19: 8 están en InfoLEG y 11 no;
  - de los que F3 aceptaba, saca 6: 4 no estaban en InfoLEG.
- **Por qué no gana más:** en el VISTO, el LLM no es más preciso que la regla. Separar la norma que se reglamenta de la que solo se cita depende de un criterio que InfoLEG no publica.

### Tipo de relación (los mismos 78 casos)

| | Macro-F1 ponderada | Exactitud ponderada |
|---|---|---|
| Reglas v2 | 0,672 | 0,754 |
| Híbrido | 0,763 | 0,646 |
| LLM puro | 0,883 | 0,849 |

El híbrido mejora la macro-F1 de las reglas, pero baja la exactitud. Cuando acepta un par por el VISTO, le pone MODIFICA, porque el LLM lo lee como «complementa». En la revisión manual, esas menciones eran CITA. El LLM puro sigue siendo el mejor para el tipo.

### Costo

| | Pedidos | Tokens de entrada | Tokens de salida | Costo |
|---|---|---|---|---|
| Prompt v1 (descartado) | 274 | 940 mil | 152 mil | USD 3,4 |
| **Prompt v2** | 274 | 995 mil | 161 mil | **USD 3,6** |

## Conclusión para el artículo

- La cascada ordena bien el trabajo: lo determinista detecta y normaliza, y el LLM juzga.
- Es el método con mejor F1 en dev y uno de los de más recall en test, por un cuarto del costo del LLM puro.
- La mejora en test no es significativa. El cuello de botella sigue siendo el mismo: decidir si una norma citada en el VISTO está vinculada según el criterio de InfoLEG.
- Para el tipo de relación, conviene el LLM puro.

## Reproducir

```bash
python scripts/20_parser_hibrido.py --estimar           # cuenta pedidos y tokens
python scripts/20_parser_hibrido.py --incluir-test      # sin clave usa la caché (results/hibrido/cache)
python scripts/10_armar_grafo.py --relaciones results/hibrido/relaciones_hibrido.csv --out data/grafo_hibrido
```

En Neo4j se carga sin `--borrar`; queda con `fuente = 'hibrido'`, al lado de los otros grafos.
