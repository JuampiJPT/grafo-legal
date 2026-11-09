# Revisión manual

Las dos muestras se sacaron cuando había dos corpus. Los 30 pares de la sección 1 son del corpus v1, que está contenido en el corpus único con el mismo split, así que siguen valiendo (D11).

## 1. Cobertura textual: 30 pares del gold (`revision_cobertura_30.csv`)

**Muestra.** 30 pares estratificados por categoría: 12 «número», 9 «solo nombre» y 9 «sin mención». La semilla es 20261106. Por cada par se leyó el contexto de la mención y, en los casos sin mención, el título y los artículos de la modificatoria.

**Anotación.** La hizo una primera pasada de Claude y está pendiente de validación humana (columna `validacion_humana`). Para el informe conviene que un integrante del grupo la valide y que un segundo anotador repita al menos 15 casos, para calcular el kappa de Cohen.

**Resultados.**

- **30 de 30 categorías correctas.** No hubo menciones que el detector reportara y no existieran, ni pares «sin mención» que en realidad tuvieran una cita.
- **Tipo de vínculo de los 21 pares con mención:**

  | Tipo | Pares |
  |---|---|
  | Modifica | 7 |
  | Reglamenta | 4 |
  | Texto ordenado | 1 |
  | Remite o complementa | 9 |

  En 7 de los 21, la única mención está en el encabezado (VISTO / CONSIDERANDO). En esos casos la restricción al articulado pierde el par, aunque el vínculo es real (sobre todo en las reglamentaciones).
- **Por qué los 9 pares «sin mención» no son recuperables leyendo el texto:**

  | Motivo | Pares |
  |---|---|
  | Complementa por materia | 3 |
  | Vínculo a través del texto ordenado | 2 |
  | No explicado por el texto publicado | 2 |
  | Modificación transitiva | 1 |
  | Derogación tácita o por materia | 1 |

## 2. Ley 14.250: muestra de sus «modificatorias»

La Ley 14.250 figura como modificada por unas 42.600 normas, y por eso se incluyó como nodo sin expandir. La hipótesis es que casi todas son resoluciones que homologan convenios colectivos y no modifican el texto de la ley.

**Resultado (06/11/2026).** InfoLEG registra 42.860 modificatorias: 28.935 resoluciones, 13.882 disposiciones, 22 decretos, 11 laudos, 6 leyes y 4 de otros tipos.

En la muestra de 30 normas que no son leyes ni decretos (semilla 20261106), **ninguna modifica el texto de la ley**:

| Qué hace la norma | Cantidad |
|---|---|
| Homologa o registra un acuerdo o convenio colectivo | 19 |
| Fija el tope indemnizatorio de un acuerdo ya homologado | 8 |
| Aplica un convenio o no tiene relación visible | 3 |

Dentro del último grupo hay una circular del BCRA sobre regímenes informativos: es ruido del propio gold. Entre los 28 decretos y leyes también aparecen dos decretos secretos de 2015, rotulados «Detención», que difícilmente modifiquen la ley.

La anotación es una primera pasada de Claude y está pendiente de validación humana.

`06_muestra_ley14250.py` genera tres archivos en esta carpeta:

- `ley14250_modificatorias_por_tipo.csv`: cantidad por tipo de norma.
- `ley14250_muestra_30.csv`: 30 normas que no son Ley ni Decreto, para marcar a mano si homologan un convenio.
- `ley14250_leyes_y_decretos.csv`: las leyes y decretos que sí la modifican, que son las que importarían si se expandiera.
