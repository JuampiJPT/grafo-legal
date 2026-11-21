"""Como alinear.py, pero con los encabezados que la voz leyó («E cero cinco · De dónde salen los datos»)."""
import re, json, sys, subprocess
from alinear import silabas, TXT
NUM = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"]
DECENA = {1: "diez once doce trece catorce quince dieciséis diecisiete dieciocho diecinueve".split(),
          2: "veinte veintiuno veintidós veintitrés veinticuatro veinticinco".split()}
def numero(n):
    return f"cero {NUM[n]}" if n < 10 else DECENA[n // 10][n % 10]
def trozos():
    txt = open(TXT, encoding="utf-8").read()
    bloques = re.findall(r"^===== (E(\d\d)) · ([^=\n]+?) =====\n(.*?)(?=^=====|\Z)", txt, flags=re.M | re.S)
    out = []  # (escena, silabas, tipo) tipo: "enc" (encabezado), "fin_enc", "txt", "fin"
    for esc, n, titulo, t in bloques:
        out.append((esc, silabas("e " + numero(int(n))), "enc"))
        out.append((esc, silabas(titulo), "fin_enc"))
        t = re.sub(r"<break[^>]*>", "|", t)
        ped = [p for p in re.split(r"[,.;:?!|»—]+|\s«", t) if re.search(r"\w", p)]
        for i, p in enumerate(ped):
            out.append((esc, silabas(p), "fin" if i == len(ped) - 1 else "txt"))
    return out
def habla(mp3, ruido="-35dB", d="0.12"):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", mp3, "-af", f"silencedetect=noise={ruido}:d={d}", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r)]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3],
                               capture_output=True, text=True).stdout)
    segs, t = [], 0.0
    for s, e in zip(st, en):
        if s > t + 0.04: segs.append((t, s))
        t = e
    if dur > t + 0.04: segs.append((t, dur))
    return segs
def alinear(tz, segs):
    S = [s for _, s, _ in tz]; CORTE = [k in ("fin", "fin_enc") for _, _, k in tz]
    D = [b - a for a, b in segs]; r = sum(D) / sum(S)
    n, m, G = len(S), len(D), 5
    INF = 1e18
    cost = [[INF] * (m + 1) for _ in range(n + 1)]; back = [[None] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0
    cs = [0]; [cs.append(cs[-1] + s) for s in S]
    cd = [0]; [cd.append(cd[-1] + d) for d in D]
    for i in range(n + 1):
        for j in range(m + 1):
            if cost[i][j] >= INF: continue
            for a in range(1, G + 1):
                if i + a > n: break
                if any(CORTE[k] for k in range(i, i + a - 1)): break
                for b in range(1, G + 1):
                    if j + b > m: break
                    pred = (cs[i + a] - cs[i]) * r; real = cd[j + b] - cd[j]
                    c = cost[i][j] + abs(pred - real) / (0.25 + 0.15 * pred) + 0.3 * (a - 1) + 0.6 * (b - 1)
                    if c < cost[i + a][j + b]:
                        cost[i + a][j + b] = c; back[i + a][j + b] = (i, j)
    i, j = n, m; fin = {}; ini = {}
    while (i, j) != (0, 0):
        pi, pj = back[i][j]
        fin[i - 1] = segs[j - 1][1]; ini[pi] = segs[pj][0]
        i, j = pi, pj
    return fin, ini, cost[n][m]
if __name__ == "__main__":
    tz = trozos(); segs = habla(sys.argv[1])
    fin, ini, c = alinear(tz, segs)
    res = {}
    for k, (esc, _, tipo) in enumerate(tz):
        if tipo == "enc": res.setdefault(esc, {})["enc_ini"] = ini[k]
        if tipo == "fin_enc": res[esc]["enc_fin"] = fin[k]; res[esc]["txt_ini"] = ini[k + 1]
        if tipo == "fin": res[esc]["txt_fin"] = fin[k]
    print(len(tz), "trozos", len(segs), "segmentos", "costo", round(c, 1))
    json.dump(res, open(sys.argv[2], "w"), indent=1)
    for e, v in res.items():
        print(e, {k: round(x, 2) for k, x in v.items()}, "encabezado", round(v["enc_fin"] - v["enc_ini"], 2), "s")
