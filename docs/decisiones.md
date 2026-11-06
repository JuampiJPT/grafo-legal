# Decisiones que afectan al código

Este archivo es un resumen. El razonamiento completo, con las dificultades y las alternativas descartadas, está en la bitácora del TP (Google Drive).

## D1. Snapshot congelado (06/11/2026)

El corpus v1 queda fijo en el snapshot de InfoLEG del 30/09/2026: 183 normas y 402 pares. Los datos del 31/10 darían 185 y 406, pero cambiar de snapshot obligaría a rehacer la cobertura y los splits cada mes. Todos los resultados del informe se reportan sobre v1. Ver `data/corpus_v1/SNAPSHOT.md`.

## D2. Corpus v2 laboral ampliado (06/11/2026)

Se agrega un corpus v2 que, además de las semillas de v1, expande desde la Ley 24.013 (Empleo), la Ley 24.557 (Riesgos del Trabajo) y la Ley 23.551 (Asociaciones Sindicales). En el análisis previo daba unas 340 normas, 775 pares y 192 pares de test. En v1, la LCT concentra la mayoría de los pares; en v2 el nodo más conectado concentra un 19%.

Para qué sirve v2:

1. Un test más grande. El test de v1 tiene 127 pares y el 54% sale de tres normas: Ley 27.802 (38), DNU 70/2023 (17) y Ley 27.742 (13).
2. Medir cuánto cae el F1 al aplicar las reglas, congeladas en v1, sobre normas nuevas.

Se descartó sumar otro nodo grande fuera del dominio laboral, como el SIPA o el empleo público. La comparación entre dominios se hace con el corpus tributario (E2) y con el digesto UNNOBA (E3).

## D3. Pipeline oficial = scripts (06/11/2026)

Los datos oficiales son los que producen los scripts de `scripts/`, corridos con `correr_pipeline.sh`. Lo que se hizo en el navegador sirvió como exploración y queda documentado en la bitácora. La única excepción es el corpus v1, por D1.

## D4. Normalización con mundo cerrado

El catálogo de normalización es el corpus. Una mención a una norma que no está en el corpus se descarta como arista, aunque se conserva en las evidencias. El gold también se limita al corpus, así que esto no distorsiona la evaluación. Para el grafo final se puede usar el catálogo completo de InfoLEG.

## D5. Desambiguación de decretos

Los números de decreto se repiten todos los años. Si una mención da el año («Decreto 27/18»), se exige que coincida. Si no lo da, la mención se resuelve solo cuando hay un único decreto con ese número en el catálogo, y queda como riesgo documentado.

Los «decretos-leyes» de 1966-73 y 1976-83 se numeran en la serie de leyes, y InfoLEG los cataloga como Ley. Por eso «Decreto-Ley 17.258/67» se resuelve a la Ley 17.258.

## D6. La relación del gold es «modifica o complementa»

La base complementaria de InfoLEG no distingue entre modificar, reglamentar o simplemente remitir. En la revisión manual de 30 pares (`docs/revision_manual/`), de los 21 que tienen mención explícita:

| Tipo de vínculo | Pares |
|---|---|
| Modificación propiamente dicha | 7 |
| Reglamentación | 4 |
| Texto ordenado | 1 |
| Remisión («se regirá por…», «conforme a…») o complemento | 9 |

Por eso la configuración final del parser de reglas no exige un verbo modificatorio: hacerlo baja el F1 de dev de 0,716 a 0,556.

Consecuencia para el TP: hace falta distinguir dos tareas. Una es recuperar el vínculo de InfoLEG, que es lo que mide el gold. La otra es tipar la relación (modifica, reglamenta, remite), y para esa hay que anotar a mano una muestra. Esto queda como pregunta para la cátedra.

## D7. Iteración sobre dev, test una sola vez

Sobre dev hubo dos iteraciones de reglas: los patrones de menciones (núm., N.°, nombre intercalado, listas con «(t.o. 1976) y sus modificatorias», decretos-leyes) y los verbos en subjuntivo («Agréguese», «Modifíquese»). Después las reglas se congelaron y test se evaluó una vez, el 06/11/2026.
