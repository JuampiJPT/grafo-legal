import json, re, subprocess, numpy as np
from alinear import trozos, habla, alinear
tz = trozos()
def analizar(mp3):
    segs = habla(mp3)
    fin, _ = alinear(tz, segs)
    # costo por escena: recalculo grupo a grupo
    S=[s for _,s,_ in tz]; D=[b-a for a,b in segs]; r=sum(D)/sum(S)
    esc_de=[e for e,_,_ in tz]
    ends=sorted(fin.items())
    res={}
    prev_i=-1; prev_t=0.0
    escenas={}
    for k,(e,_,es_fin) in enumerate(tz):
        if es_fin: escenas[e]=k
    ini=0.0; out={}
    k0=0
    for e,kf in escenas.items():
        t1=fin[kf]
        sil=sum(S[k0:kf+1])
        habla_s=sum(min(b,t1)-max(a,ini) for a,b in segs if b>ini and a<t1)
        pausas=[segs[j+1][0]-segs[j][1] for j in range(len(segs)-1) if segs[j][1]>=ini and segs[j+1][0]<=t1]
        # error de alineación: grupos dentro de la escena
        errs=[]
        idx=[k for k in sorted(fin) if k0<=k<=kf]
        last=k0-1; lt=ini
        for k in idx:
            pred=sum(S[last+1:k+1])*r
            real=sum(min(b,fin[k])-max(a,lt) for a,b in segs if b>lt and a<fin[k])
            errs.append(abs(pred-real)); last=k; lt=fin[k]
        out[e]=dict(ini=round(ini,2), fin=round(t1,2), sil_por_s=round(sil/max(habla_s,1e-6),2),
                    err=round(float(np.mean(errs)),3), err_max=round(float(max(errs)),2),
                    pausa_max=round(max(pausas) if pausas else 0,2))
        ini=t1; k0=kf+1
    return out
def pico(mp3, ini, fin):
    r=subprocess.run(["ffmpeg","-v","info","-ss",str(ini),"-to",str(fin),"-i",mp3,"-af","astats=metadata=0:measure_overall=Peak_level+Number_of_Infs","-f","null","-"],capture_output=True,text=True).stderr
    m=re.findall(r"Peak level dB: ([-0-9.inf]+)",r)
    return float(m[-1]) if m else None
A=analizar("A.mp3"); B=analizar("B.mp3")
json.dump({"A":A,"B":B},open("analisis.json","w"),indent=1)
print("esc  A:err errmax ritmo pausa pico | B:err errmax ritmo pausa pico")
for e in A:
    pa=pico("A.mp3",A[e]["ini"],A[e]["fin"]); pb=pico("B.mp3",B[e]["ini"],B[e]["fin"])
    A[e]["pico"]=pa; B[e]["pico"]=pb
    a,b=A[e],B[e]
    print(e, f"{a['err']:.2f} {a['err_max']:.2f} {a['sil_por_s']:.2f} {a['pausa_max']:.2f} {pa} | {b['err']:.2f} {b['err_max']:.2f} {b['sil_por_s']:.2f} {b['pausa_max']:.2f} {pb}")
json.dump({"A":A,"B":B},open("analisis.json","w"),indent=1)
