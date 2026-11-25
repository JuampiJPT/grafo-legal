# Cómo se arma el video explicativo (B66)

Scripts que generan el video a partir de `docs/video/guion_video.md` y los audios de ElevenLabs.

1. `escenas.py` define las 25 escenas en HTML. Los ejemplos salen del repo: código, CSV, la caché del LLM y las figuras del informe. Cada elemento tiene un paso (`data-step`) y una animación: entra deslizándose, aparece, una barra crece, un número cuenta o se resalta un texto.
2. `capturar_todo.py` abre cada escena con Chromium (Playwright) y captura 1,4 s de transición a 30 fps por paso. Escribe `meta.json`, con la cantidad de pasos y la posición de Fusi.
3. `armar_video.py CARPETA_AUDIOS` arma el video:
   - cada escena dura lo que su audio, más 0,4 s antes y 0,8 s después;
   - los pasos se reparten a lo largo de la narración;
   - Fusi camina sobre la barra de progreso, rebota con el volumen de la voz y parpadea;
   - al final se unen las escenas sin recodificar y se agrega el audio.
4. `preview.py E05 E06` captura el estado final de algunas escenas, para revisarlas.

**Fusi** es la mascota de FusionDevs. Su sprite se reconstruyó en píxeles a partir de la calcomanía «Fusi matero» del pack de FusionDevs. Los PNG de Fusi y los cuadros capturados no van al repo.

**Requisitos:** Python con `playwright` (Chromium), `pygments`, `numpy` y `Pillow`, y `ffmpeg`.

**Corrección (B67).** La voz había leído los encabezados («E05 · De dónde salen los datos»). Por eso los cortes válidos son los de `alinear2.py` y `cortar2.py`, que alinean con el encabezado incluido y lo quitan.

**Versión 3 (B69).** La escena E15 se reemplazó por siete escenas sobre los modelos (`escenas_modelos.py`: E15, E15b … E15g). `escenas.NOMBRADAS` da el nombre y la función de cada escena. `capturar_todo.py` y `armar_video.py` usan esos nombres, y el orden alfabético (E15 < E15b < … < E15g < E16) es el orden del video. Los audios se nombran igual que la escena (`E15b.mp3`), y `armar_video.py` verifica que coincidan. La narración nueva está en `narracion_modelos_elevenlabs.md`, con un audio por escena y sin encabezados.

**Uso interno (B71).** El video queda para que el equipo repase las explicaciones; para el coloquio se usa `docs/presentacion/presentacion_coloquio.pptx`. La escena E15g suma una tarjeta sobre qué conclusiones dependen del tamaño del corpus.
