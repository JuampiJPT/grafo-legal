"""Arma el video final con los audios de ElevenLabs (uno por escena).

Uso: python armar_video.py CARPETA_AUDIOS [--solo E02 E03] [--salida video.mp4]

Para cada escena:
  1. La duración sale del audio: 0,4 s de entrada + audio + 0,8 s de cola.
  2. Los pasos se reparten a lo largo del audio. Cada paso arranca con su transición (1,4 s de cuadros
     capturados) y después queda quieto hasta el paso siguiente.
  3. Fusi camina sobre la barra de progreso: rebota con el volumen de la voz y parpadea.
Después se unen las escenas sin recodificar y se agrega el audio.
"""
import argparse, json, math, re, subprocess, wave
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path("/home/claude/video")
FR = RAIZ / "frames"
FPS = 30
VENT = 42          # cuadros de transición por paso (1,4 s)
PRE, POST = 0.4, 0.8
SR = 44100
FUSI = RAIZ / "fusi"


def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])
    return r.stdout


def audios(carpeta):
    fs = sorted([p for p in Path(carpeta).iterdir() if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".ogg")],
                key=lambda p: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", p.name)])
    return fs


def a_wav(src, dst):
    """Audio de la escena con PRE de silencio adelante y POST atrás, mono 44,1 kHz."""
    sh(f'ffmpeg -y -v error -i "{src}" -af "adelay={int(PRE*1000)},apad=pad_dur={POST}" -ac 1 -ar {SR} "{dst}"')
    with wave.open(str(dst)) as w:
        n = w.getnframes()
        datos = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    return n / SR, datos


def envolvente(datos, cuadros):
    """Volumen por cuadro (0..1), suavizado."""
    por = SR / FPS
    def rms(seg):
        return float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
    v = np.array([rms(datos[int(i * por):int((i + 1) * por)]) for i in range(cuadros)])
    v = v / (np.percentile(v, 95) + 1e-6)
    v = np.clip(v, 0, 1)
    return np.convolve(v, np.ones(3) / 3, mode="same")


SPR = {}


def sprite(nombre, alto=150):
    if nombre not in SPR:
        im = Image.open(FUSI / f"fusi_{nombre}.png")
        esc = alto / im.height
        SPR[nombre] = im.resize((int(im.width * esc), alto), Image.NEAREST)
    return SPR[nombre]


def cuadros_fusi(dst, vol, semilla):
    """PNG RGBA 240x200 por cuadro: Fusi rebota con la voz y parpadea cada ~3,5 s."""
    dst.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(semilla)
    parpadeos = set()
    t = rng.uniform(1.0, 2.5)
    while t * FPS < len(vol):
        for d in range(4):
            parpadeos.add(int(t * FPS) + d)
        t += rng.uniform(2.8, 4.5)
    for i, v in enumerate(vol):
        fase = math.sin(i / FPS * 2 * math.pi * 2.2)
        salto = 4 + 14 * v * abs(fase)           # rebota más cuando habla
        estiro = 1 + 0.04 * v * fase             # leve estiramiento
        im = sprite("blink" if i in parpadeos else "idle")
        w, h = im.width, int(im.height * estiro)
        s = im.resize((w, h), Image.NEAREST)
        lienzo = Image.new("RGBA", (240, 200), (0, 0, 0, 0))
        # sombra
        sombra = Image.new("RGBA", (int(w * (0.8 - salto / 120)), 10), (0, 0, 0, int(60 - salto)))
        lienzo.paste(sombra, ((240 - sombra.width) // 2, 192), sombra)
        lienzo.paste(s, ((240 - w) // 2, int(194 - h - salto)), s)
        lienzo.save(dst / f"f{i:05d}.png")


def video_escena(nombre, dur, pasos, fusi_x, vol, salida):
    total = int(round(dur * FPS))
    # cuándo arranca cada paso: el 0 al principio, el resto repartido sobre la narración
    narr = dur - PRE - POST
    inicio = [0] + [int(round((PRE + narr * k / pasos) * FPS)) for k in range(1, pasos)] + [total]
    lista = []
    for k in range(pasos):
        largo = inicio[k + 1] - inicio[k]
        trans = min(VENT, largo)
        for i in range(trans):
            lista.append((FR / nombre / f"p{k}_{i:03d}.jpg", 1))
        if largo > trans:
            lista.append((FR / nombre / f"p{k}_{VENT - 1:03d}.jpg", largo - trans))
    txt = RAIZ / "tmp" / f"{nombre}_lista.txt"
    txt.parent.mkdir(exist_ok=True)
    with open(txt, "w") as f:
        for p, n in lista:
            f.write(f"file '{p}'\nduration {n / FPS:.6f}\n")
        f.write(f"file '{lista[-1][0]}'\n")
    tmp = salida.with_suffix(".tmp.mp4")
    if nombre == "E01":    # la portada ya tiene a Fusi grande
        sh(f'ffmpeg -y -v error -f concat -safe 0 -i "{txt}" -vf "fps={FPS},format=yuv420p" -frames:v {total} '
           f'-c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r {FPS} "{tmp}"')
    else:
        fdir = RAIZ / "tmp" / f"fusi_{nombre}"
        cuadros_fusi(fdir, vol[:total], int(nombre[1:3]) if len(nombre) == 3 else int(nombre[1:3]) * 10 + ord(nombre[3]))
        x = int(fusi_x - 120)
        y = 1080 - 34 - 8 - 196
        sh(f'ffmpeg -y -v error -f concat -safe 0 -i "{txt}" -framerate {FPS} -i "{fdir}/f%05d.png" '
           f'-filter_complex "[0:v]fps={FPS}[b];[b][1:v]overlay={x}:{y}:shortest=1,format=yuv420p" -frames:v {total} '
           f'-c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r {FPS} "{tmp}"')
    tmp.rename(salida)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audios")
    ap.add_argument("--solo", nargs="*")
    ap.add_argument("--salida", default=str(RAIZ / "video_tp_grafo_legal.mp4"))
    a = ap.parse_args()
    meta = json.loads((RAIZ / "meta.json").read_text())
    fs = audios(a.audios)
    escenas = sorted(meta)
    assert len(fs) == len(escenas), f"hay {len(fs)} audios, se esperan {len(escenas)}"
    # el nombre de cada audio tiene que coincidir con su escena (E15b.mp3 -> E15b)
    for n, f in zip(escenas, fs):
        assert f.stem.split("_")[0] == n, f"el audio {f.name} no corresponde a la escena {n}"
    out = RAIZ / "escenas"
    out.mkdir(exist_ok=True)
    wavs = []
    for nombre, src in zip(escenas, fs):
        wav = RAIZ / "tmp" / f"{nombre}.wav"
        wav.parent.mkdir(exist_ok=True)
        dur, datos = a_wav(src, wav)
        wavs.append(wav)
        if a.solo and nombre not in a.solo:
            continue
        vol = envolvente(datos, int(round(dur * FPS)) + 2)
        video_escena(nombre, dur, meta[nombre]["pasos"], meta[nombre]["fusi_x"], vol, out / f"{nombre}.mp4")
        print(nombre, f"{dur:.1f} s", src.name, flush=True)
    if a.solo:
        return
    lst = RAIZ / "tmp" / "escenas.txt"
    lst.write_text("".join(f"file '{out / (n + '.mp4')}'\n" for n in escenas))
    sh(f'ffmpeg -y -v error -f concat -safe 0 -i "{lst}" -c copy "{RAIZ}/tmp/solo_video.mp4"')
    lsa = RAIZ / "tmp" / "audios.txt"
    lsa.write_text("".join(f"file '{w}'\n" for w in wavs))
    sh(f'ffmpeg -y -v error -f concat -safe 0 -i "{lsa}" -c:a pcm_s16le "{RAIZ}/tmp/audio.wav"')
    tmp = Path(a.salida).with_suffix(".tmp.mp4")
    sh(f'ffmpeg -y -v error -i "{RAIZ}/tmp/solo_video.mp4" -i "{RAIZ}/tmp/audio.wav" -map 0:v -map 1:a -c:v copy '
       f'-c:a aac -b:a 192k -shortest -movflags +faststart "{tmp}"')
    tmp.rename(a.salida)
    print("listo:", a.salida)


if __name__ == "__main__":
    main()
