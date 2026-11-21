"""Corta cada escena SIN el encabezado leído por la voz, de la toma elegida, y nivela a -16 LUFS."""
import json, re, subprocess
eleg = json.load(open("elegidas.json"))
enc = {"A": json.load(open("enc_A.json")), "B": json.load(open("enc_B.json"))}
out = "/home/claude/video/audios_escenas2"; subprocess.run(["mkdir", "-p", out])
nuevas = {}
for e, info in eleg.items():
    t = info["toma"]; v = enc[t][e]
    a0, a1 = max(0, v["txt_ini"] - 0.06), v["txt_fin"] + 0.15
    r = subprocess.run(["ffmpeg", "-v", "info", "-ss", str(a0), "-to", str(a1), "-i", f"{t}.mp3", "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", r)[-1]); g = -16 - I
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(a0), "-to", str(a1), "-i", f"{t}.mp3",
                    "-af", f"volume={g:.2f}dB,afade=t=in:d=0.03,afade=t=out:st={a1 - a0 - 0.06:.3f}:d=0.06",
                    "-ar", "44100", "-ac", "1", f"{out}/{e}.wav"], check=True)
    nuevas[e] = dict(toma=t, desde=round(a0, 2), hasta=round(a1, 2), encabezado_quitado=[round(v["enc_ini"], 2), round(v["enc_fin"], 2)],
                     lufs=round(I, 1), ganancia_db=round(g, 1))
    print(e, t, round(a0, 2), round(a1, 2), "quita encabezado", nuevas[e]["encabezado_quitado"])
json.dump(nuevas, open("elegidas.json", "w"), indent=1)
