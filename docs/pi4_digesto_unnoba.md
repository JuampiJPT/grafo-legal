# PI4 · Transferencia al digesto de la UNNOBA

**Pregunta (PI4).** ¿El pipeline funciona sobre otro corpus normativo si solo se cambia el adaptador de la fuente?

**Respuesta corta.** Funciona, con dos condiciones.

1. Corriendo los tres parsers sin ajustarlos, el **híbrido** es el mejor, con F1 0,958 para el vínculo. Las reglas dan 0,917, pero la diferencia entre los dos no es significativa con 70 documentos.
2. El **vocabulario** de los tipos de norma y de los verbos depende de la fuente, así que tiene que ser parte del adaptador:
   - el LLM con el prompt de InfoLEG ignora las resoluciones y cae a 0,405;
   - el léxico de verbos de InfoLEG no tiene «Ratificar» ni «Dejar sin efecto», y las reglas pierden la mitad del tipo MOD.

Números, errores y límites: `results/pi4_unnoba/RESULTADOS.md`. Revisión del gold: `docs/pi4_revision_gold.md`. Bitácora B57 y B58, decisión D28.

## Cómo funciona

```
PDF del digesto ──pdftotext / OCR (tesseract spa)──► texto ──► fuentes/unnoba.py ──► evidencias
                                                                  │  limpiar(): une las líneas de maquetación
                                                                  │  segmentar(): VISTO / CONSIDERANDO / articulado
                                                                  │  detectar(): menciones -> claves TIPO-EMISOR-N-AÑO
                                                                  ▼
                       reglas F/F3 (sin cambios) · parser LLM (sin cambios) · híbrido (sin cambios)
                                                                  ▼
                                    pares (documento, norma) ──► evaluación contra gold_pi4.tsv
```

1. **Texto.** Hay 912 PDF únicos del digesto (B56). Para la muestra, `pdftotext` saca el texto, y en los 38 escaneados se usa OCR. El documento se corta después del artículo «Regístrese…»: las firmas y los anexos quedan fuera, como las notas en InfoLEG.
2. **Partes** (`segmentar`). Las partes se ubican por las fórmulas del documento:
   - **VISTO:** desde «Visto».
   - **CONSIDERANDO:** desde «Considerando» hasta «RESUELVE:» u «ORDENA:». Incluye la fórmula «Por ello, EL CONSEJO SUPERIOR… en uso de sus atribuciones (Art. 76 del Estatuto)», que en InfoLEG también cae en el considerando.
   - **Articulado:** el resto, partido por «Artículo N».
3. **Menciones** (`detectar`). El detector reconoce estas formas:
   - «Resolución (CS) Nro. 44/08», «Res. (CD.ET) 64/2013», «Ordenanza (CS) 14/09»;
   - listas: «Resoluciones (CS) 32/2007, 92/2008 y 77/2008»;
   - resoluciones del Rector sin emisor, por la numeración de miles: «Resolución Nro. 3565/2011»;
   - «Resolución Ministerial», «Ley N° 24.521», «Ley de Educación Superior», «Decreto 499/95» y «Estatuto»;
   - la corrección del OCR que lee la barra como «1» («53112012» → 531/2012).
4. **Claves.** Cada mención queda como `TIPO-EMISOR-NÚMERO-AÑO`, por ejemplo `RES-HCS-44-2008`. Se compara **sin emisor**, porque muchas citas no lo escriben. Es **mundo abierto**: no hay un catálogo cerrado, porque el digesto publicado es parcial.
5. **Parsers.** Corren las mismas funciones de InfoLEG sobre esas evidencias:
   - **reglas:** F de la v2 y F3 de la v3;
   - **LLM:** `llm.lotes`, `mensaje_usuario` y la verificación de la cita;
   - **híbrido:** `hibrido.candidatos`, `fragmentos`, `mensaje` y `decidir` con la política «previa» y los umbrales 0,15 y 0,5.

   El origen es una resolución y nunca un decreto. La condición «o el origen no es un decreto» de F, que en InfoLEG separaba leyes de decretos, siempre se cumple.

## Decisiones

1. **Muestra estratificada.** Siete ordenanzas, 48 resoluciones de los temas de reglamentos (Reglamentación, Cursadas, Regularidades, Trabajo Final, Ingreso) y 15 al azar como negativos. Se sorteó con una semilla fija. Se eligieron los reglamentos porque ahí están las modificaciones. Al azar, casi todo serían becas y designaciones sin relaciones.
2. **Tres clases en el gold** (MOD, APLICA, CITA). Se evalúa MOD ∪ APLICA como «vínculo», que es lo más cercano al «modifica o complementa» de InfoLEG. Así los números se pueden comparar con los de InfoLEG sin redefinir los métodos.
3. **Comparar sin emisor.** «Res. 44/08» y «Resolución (CS) 44/2008» son la misma norma. El costo es un caso: el doc 10 cita una resolución de otro órgano con el mismo número que la propia, y se toma como autocita.
4. **Los prompts tal cual, y una variante «vocab» aparte.** Así se mide cuánto pesa el vocabulario. La variante cambia solo las frases que enumeran tipos de norma (tres en el prompt del LLM y dos en el del híbrido) y deja igual el criterio y los ejemplos.
5. **Sin ajuste.** No se tocaron las reglas, los umbrales ni la política del híbrido. El detector es lo único nuevo, y es el adaptador.
6. **Correcciones del gold.** Hubo dos revisiones.
   - **Revisión 1** (B57): se agregaron 9 pares CITA que la anotación había salteado.
   - **Revisión 2** (B58): se releyeron los 108 pares en contexto.
     - 14 remisiones pasaron a APLICA, por coherencia con los docs 25 y 26: el articulado usa la norma para definir a quién alcanza.
     - Una exigencia de formato pasó a APLICA y una ratificación implícita a MOD.
     - Se agregó el Estatuto del doc 15.

   Todo está marcado en el TSV, y los números con la revisión 1 se informan como sensibilidad.
7. **Datos personales.** Los textos, el OCR y la cache del LLM traen nombres y DNI, y no van a git. Las salidas CSV no tienen texto libre del LLM.

## Grafos del digesto

`scripts/22_grafo_unnoba.py` arma un grafo por parser con el mismo modelo y el mismo código que los de InfoLEG: la salida estándar (`salida.py`), las relaciones por artículo (`relaciones.desde_evidencias`) y `grafo.construir`/`cargar_neo4j`. Están en `data/grafo_unnoba_reglas/`, `data/grafo_unnoba_llm/` y `data/grafo_unnoba_hibrido/`, y no tocan los grafos de InfoLEG. En Neo4j se cargan sin `--borrar`, con `fuente` = `unnoba_reglas_v3`, `unnoba_llm` o `unnoba_hibrido`.

- **Nodos `:Norma`:** 104.
  - Las 70 de la muestra tienen `split = 'unnoba_muestra'` y texto.
  - Las 34 que ellas citan tienen `split = 'unnoba_citada'`, sin texto. Entre ellas están la Ordenanza 14/2009, la Res. 531/2012, la Ley 24.521 y el Estatuto.
  - El grafo usa `id_norma` enteros, así que a las normas del digesto se les asigna un id desde 9.000.001, que no choca con los de InfoLEG.
  - `nombre` es legible (por ejemplo «Resolución HCS 44/2008») y `sumario` empieza con la clave de comparación («clave RES-44-2008»).
- **Nodos `:Articulo`:** el encabezado de cada documento (#0) y un nodo por artículo del dispositivo. Además, los artículos destino que se nombran («artículos 2 y 3 de la Res. 44/08») se crean como nodos sin texto.
- **Aristas:** las mismas que en InfoLEG.

  | Grafo | Pares con relación que no es CITA | Aristas |
  |---|---|---|
  | Reglas | 9 | 137 CITA, 11 MODIFICA, 1 REGLAMENTA, 1 INCORPORA |
  | LLM («vocab») | 13 | 133 CITA y 23 con otro tipo |
  | Híbrido | 58 | 88 CITA, 56 MODIFICA, 5 REGLAMENTA, 1 INCORPORA |

  - En el **grafo de reglas**, como en InfoLEG, el tipo sale del verbo, y todo lo del VISTO y del CONSIDERANDO es CITA. El vínculo de la regla F3 se obtiene proyectando ese grafo: da los mismos 59 pares que la evaluación.
  - El **grafo del híbrido** marca con su tipo los 58 pares que acepta. Sin un verbo de la regla, el tipo es MODIFICA, que en el modelo de InfoLEG quiere decir «modifica o complementa». Ahí entran los APLICA del gold.
- **Datos personales:** los DNI se tapan en el texto y en los fragmentos. Igual, `relaciones.csv` no va a git, porque los fragmentos pueden traer nombres. `normas.csv`, `articulos.csv` (sin texto) y `resumen.json` sí van.

Ejemplo de consulta: qué normas del digesto modifican o complementan la Ordenanza 14/2009 (Reglamento de Posgrado), según el híbrido.

```cypher
MATCH (o:Norma)-[:CONTIENE]->(:Articulo)-[r {fuente:'unnoba_hibrido'}]->(d)
WHERE type(r) <> 'CITA' AND (d.nombre = 'Ordenanza HCS 14/2009' OR (d)<-[:CONTIENE]-(:Norma {nombre:'Ordenanza HCS 14/2009'}))
RETURN o.nombre, type(r), r.parte_origen, r.fragmento
```

## Cómo se repite

Todo está en scripts. Lo único manual es bajar los PDF, porque el robots.txt del digesto prohíbe automatizarlo: lo hace el equipo con `tools/digesto_unnoba/Descargar_PDFs_UNNOBA.command`.

```bash
python scripts/26_digesto_catalogo.py            # catálogo de 912 documentos (898 del descargador + 14 a mano)
python scripts/27_digesto_duplicados.py --mover  # aparta copias repetidas en pdf/_duplicados/ (con LEEME.csv)
python scripts/28_digesto_textos.py --ocr muestra   # pdftotext de todo; OCR (tesseract spa) de los escaneados de la muestra
python scripts/29_digesto_muestra.py --cuerpos   # muestra de 70 (semilla 20261120), JSONL con el texto y lectura para anotar
python scripts/21_pi4_unnoba.py --estimar        # 252 pedidos
python scripts/21_pi4_unnoba.py                  # evaluación (con la cache local no llama a la API)
python scripts/22_grafo_unnoba.py                # grafos (--uri bolt://localhost:7688 para cargarlos)
```

`26` y `29` tienen `--verificar`, que comprueba que el catálogo y la muestra del repositorio salen iguales sin escribir nada. Los dos dan iguales, y los textos del JSONL coinciden con `txt/`.

El OCR no es reproducible byte a byte: cambia con la versión de tesseract y con los parámetros. Por eso `28` no rehace un `.txt` que ya existe, salvo con `--rehacer`. Los resultados de la PI4 corresponden a los textos guardados.
