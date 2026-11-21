"""Alinea el guion con un audio sin reconocimiento de voz: empareja las pausas del texto (puntuación y
<break>) con los silencios del audio por programación dinámica, usando sílabas como medida de duración."""
import re, json, sys, subprocess, unicodedata
TXT = "/mnt/user-data/uploads/grafo legal/docs/video/narracion_elevenlabs.txt"
V = "aeiouáéíóúü"


def silabas(t):
    t = unicodedata.normalize("NFC", t.lower())
    return max(1, len(re.findall(rf"[{V}y]+(?![{V}])", t))) if re.search(r"\w", t) else 0


def trozos():
    txt = open(TXT, encoding="utf-8").read()
    partes = re.split(r"^===== (E\d\d)[^\n]*=====\n", txt, flags=re.M)[1:]
    out = []  # (escena, silabas, es_fin_de_escena)
    for esc, t in zip(partes[0::2], partes[1::2]):
        t = re.sub(r"<break[^>]*>", "|", t)
        pedazos = [p for p in re.split(r"[,.;:?!|»—]+|\s«", t) if re.search(r"\w", p)]
        for i, p in enumerate(pedazos):
            out.append((esc, silabas(p), i == len(pedazos) - 1))
    return out


def habla(mp3):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", mp3, "-af", "silencedetect=noise=-40dB:d=0.18", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r)]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3],
                               capture_output=True, text=True).stdout)
    segs, t = [], 0.0
    for s, e in zip(st, en):
        if s > t + 0.05:
            segs.append((t, s))
        t = e
    if dur > t + 0.05:
        segs.append((t, dur))
    return segs


def alinear(tz, segs):
    S = [s for _, s, _ in tz]
    FIN = [f for _, _, f in tz]
    D = [b - a for a, b in segs]
    r = sum(D) / sum(S)              # segundos de voz por sílaba
    n, m = len(S), len(D)
    INF = 1e18
    G = 4
    cost = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0
    cs = [0]
    for s in S: cs.append(cs[-1] + s)
    cd = [0]
    for d in D: cd.append(cd[-1] + d)
    for i in range(n + 1):
        for j in range(m + 1):
            if cost[i][j] >= INF: continue
            for a in range(1, G + 1):
                if i + a > n: break
                if any(FIN[k] for k in range(i, i + a - 1)): break   # una escena no termina a mitad de grupo
                for b in range(1, G + 1):
                    if j + b > m: break
                    pred = (cs[i + a] - cs[i]) * r
                    real = cd[j + b] - cd[j]
                    c = cost[i][j] + abs(pred - real) / (0.25 + 0.15 * pred) + 0.3 * (a - 1) + 0.6 * (b - 1)
                    if c < cost[i + a][j + b]:
                        cost[i + a][j + b] = c; back[i + a][j + b] = (i, j)
    # recorrido hacia atrás: para cada grupo, el trozo final i -> fin del segmento j
    i, j = n, m
    fin_trozo = {}
    while (i, j) != (0, 0):
        pi, pj = back[i][j]
        fin_trozo[i - 1] = segs[j - 1][1]
        i, j = pi, pj
    return fin_trozo, cost[n][m]


if __name__ == "__main__":
    mp3 = sys.argv[1]
    tz = trozos()
    segs = habla(mp3)
    fin, c = alinear(tz, segs)
    escenas = {}
    ultimo = None
    for k, (esc, _, es_fin) in enumerate(tz):
        if k in fin: ultimo = fin[k]
        if es_fin:
            escenas[esc] = ultimo
    print(len(tz), "trozos", len(segs), "segmentos de voz", "costo", round(c, 1))
    json.dump(escenas, open(sys.argv[2], "w"), indent=1)
    for e, t in escenas.items(): print(e, round(t, 2))
