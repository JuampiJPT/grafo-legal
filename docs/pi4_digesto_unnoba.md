# PI4 · Transferencia al digesto de la UNNOBA

**Pregunta (PI4).** ¿El pipeline funciona sobre otro corpus normativo si solo se cambia el adaptador de la fuente?

**Respuesta corta.** Funciona, con dos condiciones.

1. Corriendo los tres parsers sin ajustarlos, el **híbrido** es el mejor, con F1 0,854 para el vínculo. Las reglas dan 0,788.
2. El **vocabulario** de los tipos de norma y de los verbos depende de la fuente, así que tiene que ser parte del adaptador:
   - el LLM con el prompt de InfoLEG ignora las resoluciones y cae a 0,286;
   - el léxico de verbos de InfoLEG no tiene «Ratificar» ni «Dejar sin efecto», y las reglas pierden la mitad del tipo MOD.

Números, errores y límites: `results/pi4_unnoba/RESULTADOS.md`. Bitácora B57, decisión D28.

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
6. **Correcciones del gold.** Después de la primera corrida se agregaron 9 pares CITA que la anotación había salteado. Quedan marcados con `[revision: omision de anotacion]`. No cambian el vínculo. Un posible faltante más, el Estatuto del doc 15, se dejó sin corregir.
7. **Datos personales.** Los textos, el OCR y la cache del LLM traen nombres y DNI, y no van a git. Las salidas CSV no tienen texto libre del LLM.

## Cómo se repite

```bash
# texto de la muestra: data/textos/unnoba/muestra_pi4_textos.jsonl (local, no está en git)
python scripts/21_pi4_unnoba.py --estimar     # 252 pedidos
python scripts/21_pi4_unnoba.py               # con la cache local no llama a la API
```
