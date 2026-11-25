# Presentación para el coloquio (B71)

`presentacion_coloquio.pptx` es la presentación para exponer el TP en el examen final oral. Tiene 21 diapositivas, para unos 20 a 25 minutos, y cada una trae en las notas del orador lo que se dice en ella.

- **Contenido.** Es el mismo recorrido del video explicativo, condensado para exponer: problema, datos, pipeline, reglas, modelos supervisados, LLM, resultados, efecto del tamaño del corpus, grafo, PI4, PI5, conclusiones y plan.
- **Origen de las cifras y figuras.** Todas salen de `results/` y del informe de avance. Las figuras son las de `docs/informe_avance/figuras/`, y el grafo del corpus está en `img/`.
- **Video.** El video (`docs/video/`) queda para uso interno del equipo, para repasar las explicaciones. No se usa en el coloquio.
- **Integrantes** (en la portada, por orden alfabético): Cidoni, Valentino; Lodeiro, Bruno; Martino, Lucas; Tagliaferro, Juan Pedro.

**Regenerarla.** Desde la raíz del repo, con `pptxgenjs` instalado (`npm install pptxgenjs`):

```
APPLY_THEME=<ruta a apply_theme.js> node docs/presentacion/armar_presentacion.js
```

`apply_theme.js` escribe la paleta en el tema del archivo. Viene con las herramientas que usó Claude para armarla. Sin él, la presentación se genera igual, pero con los colores por defecto de Office.
- **Identidad UNNOBA (B74).** La presentación sigue el Manual de identidad institucional de la UNNOBA (Res. CS 731/2014): celeste #4698CB y gris Cool Gray 8 como colores, la familia Century para títulos (Century Schoolbook, la alternativa oficial que trae Office) y Arial en lugar de TheSans/Trade Gothic, que no vienen instaladas. Portada gris con filetes blancos y el isologotipo en negativo; diapositivas de contenido con el encabezado del manual (filete, rótulo de sección y número) y el isologotipo en el pie. El cuadrado del isotipo es el motivo de los marcadores. Los logos (`img/unnoba_positivo.png`, `img/unnoba_negativo.png`) se extrajeron de la página 6 del manual. Las figuras del informe conservan su paleta.
