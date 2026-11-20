#!/usr/bin/env python3
"""Descarga los PDF de documentos.csv y crea un ZIP con los archivos descargados.
Requiere Python 3, sin bibliotecas adicionales. Ejecutar desde una red que pueda abrir digesto.unnoba.edu.ar.
"""
import csv
import io
import re
import sys
import time
import zipfile
from pathlib import Path
from urllib.request import Request, build_opener, HTTPCookieProcessor
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
import http.cookiejar

BASE=Path(__file__).resolve().parent
PDF_DIR=BASE/'PDF_UNNOBA'
ZIP_PATH=BASE/'UNNOBA_documentos.zip'
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'
OPENER=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
class Candidates(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        # Some versions of Digesto serve the PDF in a nested frame/embed.
        if tag in ('iframe','frame','embed','object','a','source'):
            for key in ('src','data','href'):
                if d.get(key): self.links.append((tag,d[key]))

def get(url):
    req=Request(url,headers={'User-Agent':UA,'Accept':'application/pdf,text/html,*/*','Referer':'https://digesto.unnoba.edu.ar/'})
    with OPENER.open(req,timeout=35) as r:
        return r.read(),r.geturl(),r.headers.get('Content-Type','')

def resolve_pdf(url, depth=0, visited=None):
    if visited is None:visited=set()
    if url in visited or depth>4:return None
    visited.add(url)
    body, final_url, typ=get(url)
    if body.lstrip().startswith(b'%PDF-'):
        return body
    if 'pdf' in typ.lower() and body[:10].find(b'%PDF')!=-1:
        return body
    # HTML container with embedded PDF: recursively follow references
    try: html=body.decode('utf-8',errors='replace')
    except Exception: return None
    parser=Candidates();parser.feed(html)
    candidates=[]
    for tag, link in parser.links:
        absolute=urljoin(final_url,link)
        if urlparse(absolute).netloc.endswith('unnoba.edu.ar'):
            candidates.append((tag,absolute))
    # Prefer direct PDFs and embedded frames over navigation links.
    candidates.sort(key=lambda x:(0 if '.pdf' in x[1].lower() else 1 if x[0] in ('frame','iframe','embed','object') else 2))
    for _, candidate in candidates:
        if '.pdf' in candidate.lower() or any(q in candidate.lower() for q in ('documento.', 'visualiz', 'descarga', 'archivo')) or depth==0:
            try:
                result=resolve_pdf(candidate,depth+1,visited)
                if result:return result
            except Exception:pass
    # Handle basic javascript redirects, if any
    match=re.search(r'''(?:window\.location|location\.href|src)\s*=\s*['"]([^'"]+\.pdf(?:\?[^'"]*)?)['"]''',html,re.I)
    if match:
        return resolve_pdf(urljoin(final_url,match.group(1)),depth+1,visited)
    return None

def main():
    PDF_DIR.mkdir(exist_ok=True)
    with (BASE/'documentos.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    names=set(); success=[]; errors=[]
    print('Documentos:',len(rows),'\nDestino:',PDF_DIR,'\n')
    for i,row in enumerate(rows,1):
        name=Path(row['archivo']).name
        if name in names:continue
        names.add(name)
        target=PDF_DIR/name
        if target.exists() and target.read_bytes()[:5]==b'%PDF-':
            success.append(target);print(f'[{i}/{len(rows)}] Ya descargado: {name}');continue
        print(f'[{i}/{len(rows)}] Descargando: {name}',flush=True)
        for attempt in range(1,4):
            try:
                data=resolve_pdf(row['url'])
                if not data: raise ValueError('El enlace no devolvió un PDF válido')
                target.write_bytes(data)
                success.append(target);break
            except Exception as e:
                if attempt==3:
                    errors.append((name,row['url'],str(e)))
                    print('  ERROR:',str(e)[:180])
                else:time.sleep(1.5*attempt)
        time.sleep(0.15)
    with zipfile.ZipFile(ZIP_PATH,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in success:z.write(p,p.name)
    if errors:
        with (BASE/'errores_descarga.csv').open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f);w.writerow(['archivo','url','error']);w.writerows(errors)
    print(f'\nCompletado: {len(success)} PDF, {len(errors)} errores')
    print('ZIP creado:',ZIP_PATH)
    if errors:print('Revisá errores_descarga.csv para los documentos que faltaron.')
    input('Presioná Enter para cerrar...')

if __name__=='__main__':main()
