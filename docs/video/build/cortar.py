import json, re, subprocess
from alinear import habla
an = json.load(open("analisis.json"))
esc = list(an["A"])
def score(d): return d["err"] + 0.3 * d["err_max"] + (0.2 if (d.get("pico") or -9) > -1.0 else 0)
# programación dinámica: mejor toma por escena con penalidad por cambiar de toma
SW = 0.15
best = {"A": (score(an["A"][esc[0]]), ["A"]), "B": (score(an["B"][esc[0]]), ["B"])}
for e in esc[1:]:
    nb = {}
    for t in "AB":
        c = min((best[p][0] + (SW if p != t else 0), p) for p in "AB")
        nb[t] = (c[0] + score(an[t][e]), best[c[1]][1] + [t])
    best = nb
elec = min(best.values())[1]
segs = {t: habla(f"{t}.mp3") for t in "AB"}
out = "/home/claude/video/audios_escenas"; subprocess.run(["mkdir", "-p", out])
elegidas = {}
for e, t in zip(esc, elec):
    ini, fin = an[t][e]["ini"], an[t][e]["fin"]
    primer = min(a for a, b in segs[t] if a >= ini - 0.01)
    a0, a1 = max(0, primer - 0.08), fin + 0.15
    # volumen integrado de la escena y ganancia a -16 LUFS
    r = subprocess.run(["ffmpeg", "-v", "info", "-ss", str(a0), "-to", str(a1), "-i", f"{t}.mp3", "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", r)[-1])
    g = -16 - I
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(a0), "-to", str(a1), "-i", f"{t}.mp3",
                    "-af", f"volume={g:.2f}dB,afade=t=in:d=0.03,afade=t=out:st={a1 - a0 - 0.06:.3f}:d=0.06",
                    "-ar", "44100", "-ac", "1", f"{out}/{e}.wav"], check=True)
    elegidas[e] = dict(toma=t, desde=round(a0, 2), hasta=round(a1, 2), lufs=round(I, 1), ganancia_db=round(g, 1))
    print(e, t, round(a0, 1), round(a1, 1), "dur", round(a1 - a0, 1), "LUFS", I)
json.dump(elegidas, open("elegidas.json", "w"), indent=1)
print("A:", elec.count("A"), "B:", elec.count("B"))
