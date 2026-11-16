# Guía de lectura del código (para la presentación)

Este documento recorre el código en el orden en que viaja un documento: del HTML de InfoLEG hasta la arista del grafo y su evaluación. Cada paso dice qué archivo y qué función abrir, y qué mostrar. Todos los módulos tienen comentarios que explican cada expresión regular y cada decisión. El ejemplo de punta a punta es el artículo 70 del Decreto 70/2023, que sustituye el artículo 80 de la LCT (Ley 20.744).

## Mapa

```
                      ┌──────────── específico de la fuente ────────────┐
HTML de InfoLEG ──► fuentes/infoleg.py  html_a_texto() ──► segmentar()
                      └──────────────────────────────────────────────────┘
                                       │ texto limpio + segmentos (encabezado, artículos, anexo, notas)
             ┌─────────────────────────┴─────────────────────────┐
     PARSER DE REGLAS                                       PARSER LLM
  extractores/menciones.py  detectar(), detectar_alias()  extractores/llm.py  seleccionar(), lotes()
  catalogo.py               Catalogo.resolver()           ClienteLLM.pedir()  (API + caché)
  extractores/reglas_v2.py  extraer(), CONFIGS["F_…"]     a_relaciones()      (verifica la cita,
  extractores/relaciones.py desde_evidencias()                                 normaliza con catalogo.py)
             └─────────────────────────┬─────────────────────────┘
                                       │ salida estándar (salida.py): una fila por relación tipada
                                       ▼
                      grafo.py  construir() ──► cargar_neo4j()  /  a_networkx()
                                       │
                                       ▼
              evaluación: 04 (pares), 11 (grafo), 12 (subtareas), 13 (modelo), 15 (LLM), 16 (tipos), 17 (tabla final)
```

## Paso a paso

### 1. Del HTML al texto limpio

- **Archivo y función:** `src/grafo_legal/fuentes/infoleg.py`, `html_a_texto()`.
- **Qué hace:**
  - borra scripts, estilos y comentarios;
  - convierte las etiquetas de bloque (`<p>`, `<br>`, `<tr>`) en saltos de línea;
  - decodifica las entidades (`&aacute;` → «á»);
  - normaliza los espacios.
- **Por qué importa:** todos los offsets (`inicio`, `fin`) que guardan las evidencias, las relaciones y el grafo se cuentan sobre este texto. Es lo que permite volver de una arista al fragmento exacto.
- **Para mostrar:** es el único archivo que depende de InfoLEG. Para el digesto de la UNNOBA se escribe otro adaptador que devuelva la misma lista de `Articulo`.

### 2. Segmentación

- **Archivo y función:** `infoleg.py`, `segmentar()`.
- **Qué hace:** corta el texto en zonas.
  - El **encabezado** es todo lo anterior al primer artículo: título, VISTO y CONSIDERANDO.
  - Cada **artículo** del articulado va desde su marca («ARTÍCULO 70.-», «Art. 2º —») hasta la siguiente. Lo detecta la expresión regular `_ART`, explicada pieza por pieza en el código.
  - El **anexo** empieza en el primer renglón «ANEXO» posterior al articulado.
  - Las **notas** de InfoLEG empiezan en «Nota Infoleg:» o «Antecedentes:».
- **Por qué importa:** la zona es la señal más fuerte de las reglas. Un par citado en el VISTO está en InfoLEG el 80 % de las veces; uno citado solo en el CONSIDERANDO, el 24 %.

### 3. Detección de menciones

- **Archivo y funciones:** `src/grafo_legal/extractores/menciones.py`, `detectar()` y `detectar_alias()`.
- **Qué hace:**
  - `detectar()` arma el patrón TIPO + NOMBRE opcional + «N°» opcional + LISTA de números. Reconoce, por ejemplo:
    - «Decreto de Necesidad y Urgencia N° 70/23»;
    - «Ley de Contrato de Trabajo Nº 20.744»;
    - «Leyes Nros. 24.013, 24.465 y 24.467», que da tres menciones.
  - `detectar_alias()` encuentra nombres propios sin número («Ley de Contrato de Trabajo»), con un gazetteer.
- **Resultado medido** (`results/subtareas`): cuando el número de la norma destino está en el texto, el detector lo encuentra siempre. Pierde 2 pares de dev por nombres que el gazetteer no tiene («Ley de Ministerios», «L.C.T.»). La precisión es 0,97 en una muestra de 60: los 2 errores son nombres de tributos tomados como alias.

### 4. Normalización

- **Archivo y función:** `src/grafo_legal/catalogo.py`, `Catalogo.resolver()`.
- **Qué hace:** de («decreto», «1694», 2006) a un `id_norma`. Las leyes tienen número único. Los decretos se renumeran cada año, así que el año desempata: si falta y hay más de un candidato, no se resuelve.
- **Mundo cerrado:** el catálogo es el corpus. Una mención que no resuelve se conserva como evidencia, pero no genera arista.
- **Resultado medido:**
  - el 48 % de las menciones nombra normas reales fuera del corpus;
  - de las que se resuelven, el 95,9 % es inequívoco también contra todo InfoLEG, y la exactitud estimada es 99,1 %;
      - el error principal: el año del decreto escrito como fecha («Decreto N° 467 del 14 de abril de 1988») no se lee, así que la mención queda ambigua o se vincula a otro decreto con el mismo número.

### 5. Reglas: de mención a evidencia y de evidencia a par

- **Archivo:** `src/grafo_legal/extractores/reglas_v2.py`.
- **`extraer()`:** produce una evidencia por mención resuelta, con lo que la regla necesita para decidir:
  - parte del documento (visto, considerando o articulado);
  - verbo en la oración (expresión regular `VERBOS` de `reglas.py`);
  - restricción temporal (el destino no puede ser posterior al origen);
  - si es una cita de procedencia («t.o. por Decreto 390/76»).
- **`CONFIGS["F_visto_o_articulado_con_verbo_o_ley"]`:** la decisión. Hay vínculo si la mención está en el VISTO, o en el articulado con número cuando el origen es una ley o la oración tiene verbo.
- **Ejemplo:** en «ARTÍCULO 70.- Sustitúyese el artículo 80 de la Ley N° 20.744», la mención es «Ley N° 20.744» (ley 20744 → `id` 25552), está en el articulado, el verbo de la oración es «Sustitúyese» y la ley es de 1974, anterior al decreto. Pasa la regla F.

### 6. Relaciones tipadas: la salida estándar

- **Archivos:** `src/grafo_legal/extractores/relaciones.py` (`desde_evidencias()`) y `src/grafo_legal/salida.py`.
- **Qué hace `desde_evidencias()`, por cada evidencia:**
  - asigna el segmento que la contiene (`merge_asof`), que es el `id_articulo_origen`;
  - tipa con `tipo_por_verbo()`: «Sustitúyese» → `SUSTITUYE`; sin verbo o en el encabezado → `CITA`;
  - busca el artículo destino con `articulos_destino()`, en el «artículo N de la» que precede a la mención;
  - agrupa las menciones con la misma clave.
- **El contrato:** `salida.py` define las columnas y la clave `(fuente, id_articulo_origen, tipo, id_norma_destino, articulo_destino)`. Cualquier parser que escriba esta tabla entra al grafo sin cambiar nada más.
- **Ejemplo:** `reglas_v2, 395521#71, SUSTITUYE, 25552, "80", verbo "Sustitúyese", fragmento "ARTÍCULO 70.- Sustitúyese el artículo 80 de la Ley N° 20.744…"`.

### 7. Parser LLM

- **Archivo:** `src/grafo_legal/extractores/llm.py`; se explica entero en `docs/parser_llm.md`.
- **Para mostrar:**
  - `SISTEMA`, el prompt con la definición de los seis tipos;
  - `a_relaciones()`, que verifica que la cita que devuelve el LLM esté en el texto (si no está, se descarta) y la normaliza con el mismo `Catalogo.resolver()`;
  - la caché, que hace el experimento reproducible sin clave.

### 8. El grafo

- **Archivo y función:** `src/grafo_legal/grafo.py`, `construir()`.
- **Nodos:** `Norma`, uno por norma del corpus, y `Articulo`, uno por segmento, con id `id_norma#orden`.
- **Aristas:** `CONTIENE` de cada norma a sus artículos, más las relaciones tipadas.
- **Destino de cada relación:**
  - si la relación dice el artículo destino, va al nodo de ese artículo;
  - si no, va a la norma entera;
  - si el artículo destino no tiene texto, se crea un nodo «stub» sin texto.
- **Carga:** `cargar_neo4j()` carga con `MERGE`, así que cargar dos veces no duplica. Cada arista lleva su `fuente`, y por eso el grafo del LLM se agrega sin pisar el de las reglas.
- **Ejemplo:** `(Decreto 70 art. 70)-[:SUSTITUYE {fragmento…}]->(Ley 20.744 art. 80)`.

### 9. Evaluación

| Script | Qué mide |
|---|---|
| `04_evaluar.py` | P, R y F1 por par contra InfoLEG, por configuración y por split |
| `11_evaluar_grafo.py` | Ida y vuelta (el grafo devuelve lo cargado) y comparación con InfoLEG leyendo el grafo |
| `12_evaluar_subtareas.py` | Detección, normalización y extracción por separado; embudo; taxonomía de errores |
| `13_modelo_contextual.py` | Modelo con contexto textual (TF-IDF) e híbrido reglas + modelo |
| `15_evaluar_llm.py` | Parser LLM contra InfoLEG e híbridos reglas + LLM |
| `16_evaluar_tipos.py` | Tipo de relación: matriz de confusión y macro-F1 sobre 78 casos revisados |
| `17_comparar_metodos.py` | Tabla final de todos los métodos en test, con intervalos de confianza por bootstrap |

Cómo se compara con el gold: `docs/comparacion_con_el_gold.md`.
