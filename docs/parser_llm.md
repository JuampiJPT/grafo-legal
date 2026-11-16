# Parser LLM

El parser LLM (`src/grafo_legal/extractores/llm.py`) cumple el mismo contrato que el parser de reglas: recibe los segmentos del adaptador y devuelve relaciones en la salida estándar (`docs/salida_estandar.md`). Lo único que cambia es quién lee el texto. En las reglas son expresiones regulares; acá es un modelo de lenguaje grande. Así los dos parsers se comparan con la misma evaluación y alimentan el mismo modelo de grafo (bitácora B48).

## Cómo funciona

```
segmentos del adaptador ──► 1 prefiltro ──► 2 lotes ──► 3 LLM (JSON) ──► 4 verificación de la cita
                                                                              │
                         salida estándar (fuente = llm) ◄── 5 normalización ◄─┘
                                       (mismo catálogo que las reglas)
```

1. **Prefiltro, sin LLM.** Solo se mandan los segmentos del encabezado y del articulado que contienen alguna palabra que pueda introducir una norma: ley, decreto, DNU, código, régimen o estatuto. Un artículo que no nombra ninguna norma no puede tener una relación con otra. Las notas de InfoLEG y los anexos no se mandan, igual que en las reglas.
2. **Lotes.** Los segmentos de una norma se agrupan en lotes de hasta 12.000 caracteres. Cada uno lleva su identificador (`[S12] Artículo 11`) para que el LLM diga de qué artículo sale cada relación. Un artículo más largo se parte en pedazos, y cada pedazo recuerda su desplazamiento.
3. **Prompt.** El modelo recibe la definición de los seis tipos, con ejemplos de técnica legislativa argentina, y devuelve un JSON con una entrada por relación:
   - segmento;
   - cita textual exacta;
   - tipo, número y año de la norma destino;
   - artículo destino;
   - tipo de relación;
   - verbo.

   Se usa temperatura 0. El prompt está en `llm.SISTEMA` y su versión en `llm.VERSION_PROMPT`.
4. **Verificación de la cita (anti-alucinación).** La cita que devuelve el LLM se busca en el texto del segmento. Si aparece, se guardan sus offsets en el texto limpio de la norma, y la relación queda trazable a su evidencia igual que en las reglas. Si no aparece, la relación se descarta y se cuenta: la tasa de citas que no están en el texto es una medida de alucinación.
5. **Normalización.** El tipo, el número y el año que da el LLM se resuelven contra el mismo catálogo que usan las reglas (`catalogo.py`, mundo cerrado). Así la comparación entre parsers mide solo la lectura del texto, no la normalización.
6. **Caché.** Cada respuesta se guarda en `results/relaciones_llm/cache/`, con nombre igual a la huella SHA-256 del pedido (modelo, versión del prompt, prompt y texto). La caché va en el repositorio. Volver a correr no llama a la API y da exactamente lo mismo, así que el experimento es reproducible sin la clave y sin costo.

El LLM nunca ve el gold de InfoLEG. El gold lo lee solo `scripts/15_evaluar_llm.py`.

## Modelo y costo

| | Valor |
|---|---|
| Modelo por defecto | `claude-sonnet-5-5` (se cambia con `--modelo`) |
| Normas | 306 |
| Lotes (pedidos a la API) | 590 |
| Entrada estimada | ~1,8 millones de tokens (`--estimar`) |
| Costo estimado con Sonnet 5.5 ($2 / $10 por millón de tokens de entrada / salida) | unos USD 8 |
| Costo estimado con Haiku 5.5 ($0,10 / $0,50) | menos de USD 0,50 |

## Cómo se corre

```bash
cd "/Users/jptmac/Documents/grafo legal"
echo "TU_API_KEY" > .anthropic_key          # está en .gitignore: no se sube nunca
export ANTHROPIC_API_KEY=$(cat .anthropic_key)
python scripts/14_parser_llm.py --estimar   # cuenta lotes y tokens, no llama a la API
python scripts/14_parser_llm.py --limite 5  # piloto con 5 normas
python scripts/14_parser_llm.py             # todo el corpus
python scripts/15_evaluar_llm.py            # contra InfoLEG, mismo protocolo que las reglas
python scripts/16_evaluar_tipos.py          # tipos, sobre los 78 casos revisados
python scripts/10_armar_grafo.py --relaciones results/relaciones_llm/relaciones_llm.csv --out data/grafo_llm
```

## Evaluación

- **Contra InfoLEG (`15_evaluar_llm.py`).** Las relaciones del LLM se proyectan a pares de normas y se comparan con el gold, igual que las reglas. Se prueban cuatro proyecciones y se elige una en dev:
  - cualquier relación que no sea `CITA`;
  - lo anterior más cualquier mención del VISTO;
  - la regla F aplicada a las relaciones del LLM;
  - todas las relaciones.

  En todas se aplica la misma restricción temporal de las reglas. Con la proyección elegida se arman dos híbridos con las reglas: la unión (más recall) y la intersección (más precisión).
- **Tipos (`16_evaluar_tipos.py`).** Sobre los mismos 78 casos revisados a mano que las reglas.
- **Tabla final (`17_comparar_metodos.py`).** Todos los métodos sobre el mismo test, con intervalos de confianza por bootstrap.

## Grafo del LLM

El grafo del LLM no reemplaza al de las reglas. Sus CSV van a `data/grafo_llm/`; los de las reglas siguen en `data/grafo/`.

En Neo4j, las aristas se identifican por tipo y por `fuente`. Cargar el LLM **sin** `--borrar` agrega sus aristas (`fuente = 'llm'`) a los mismos nodos `Norma` y `Articulo`, sin tocar las de `reglas_v2`:

```bash
export NEO4J_PASSWORD=$(cat .neo4j_password)
python scripts/10_armar_grafo.py --relaciones results/relaciones_llm/relaciones_llm.csv \
    --out data/grafo_llm --uri bolt://localhost:7688      # SIN --borrar
python scripts/11_evaluar_grafo.py --relaciones results/relaciones_llm/relaciones_llm.csv \
    --fuente llm --out results/evaluacion_grafo_llm --uri bolt://localhost:7688
```

Así, en la demo se pueden comparar las dos lecturas del mismo artículo:

```cypher
MATCH (o:Articulo)-[r]->(d) WHERE o.id = '395521#71'
RETURN r.fuente, type(r), d.id, r.fragmento
```
