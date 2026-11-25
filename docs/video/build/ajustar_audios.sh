#!/usr/bin/env bash
# Ajuste de los audios de ElevenLabs antes de armar el video (B72).
# Uso: ajustar_audios.sh CARPETA_MP3 CARPETA_SALIDA
#   - recorta el silencio del principio y del final (umbral -50 dB);
#   - normaliza la sonoridad a -16 LUFS con pico real de -1 dBTP, el mismo nivel
#     que los audios de la versión 2 (ElevenLabs entrega alrededor de -22 LUFS);
#   - convierte a WAV mono de 44,1 kHz, que es lo que espera armar_video.py.
set -euo pipefail
src="$1"; dst="$2"; mkdir -p "$dst"
for f in "$src"/*.mp3; do
  n=$(basename "$f" .mp3)
  ffmpeg -y -v error -i "$f" -af "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,\
areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse,\
loudnorm=I=-16:TP=-1:LRA=11:linear=true,aresample=44100" -ac 1 -ar 44100 "$dst/$n.wav"
  echo "$n listo"
done
