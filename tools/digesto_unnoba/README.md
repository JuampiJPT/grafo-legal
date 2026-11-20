# Descarga del digesto de la UNNOBA (PI4)

El digesto (https://digesto.unnoba.edu.ar) **prohíbe el acceso automático** en su robots.txt (`Disallow: /`) y no responde desde los entornos de Claude ni de ChatGPT. Por eso los PDF se bajaron desde la computadora de un integrante del equipo, con su sesión (bitácora B56). Las herramientas de esta carpeta son las que se usaron, guardadas para que el proceso se pueda reproducir.

| Archivo | Qué hace |
|---|---|
| `Descargar_PDFs_UNNOBA.command` | **Versión usada.** Tiene adentro el catálogo de 898 documentos únicos, que salen de 11 secciones guardadas como HTML. Baja la versión **con firmas** de cada PDF con su nombre original (por ejemplo `RESOLUCIONHCS20181462.pdf`). Omite los que ya están, reintenta tres veces y registra los fallos en `errores_descarga.csv`. Uso: `bash Descargar_PDFs_UNNOBA.command [--tipo firmas\|normal\|ambos] [--limite N]`. Guarda en `~/Downloads/PDF_UNNOBA`. |
| `descargar_tema_digesto.js` | Alternativa para una sola sección: se pega en la consola del navegador, en la página de la sección, y arma un ZIP con los PDF con firmas. |
| `ejemplo_documento.frameim.html` | Ejemplo de la página del visor con firmas (`documento.frameim.php?cod=N&arch=ARCHIVO.pdf`), que embebe el PDF. |
| `historico_kit_237/` | Primera versión, solo para la sección Posgrado (237 documentos). Generaba un ZIP. Quedó reemplazada por el `.command`. |

## Resultado

Los PDF están en `data/textos/unnoba/pdf/` y no se suben a git (`*.pdf` está en `.gitignore`, porque muchos documentos traen nombres y DNI).

- **912 documentos distintos:** los 898 del catálogo y 14 que se bajaron a mano antes.
- **29 copias** (el mismo contenido con otro nombre, o copias «(1)») apartadas en `pdf/_duplicados/`, con el motivo de cada una en `LEEME.csv`.

`data/corpus_unnoba/catalogo.csv` tiene una fila por documento: cod, título, archivo, los dos enlaces, las secciones donde aparece y el origen (`catalogo_digesto` o `descarga_manual`).

## Después de la descarga (todo en scripts, B62)

```bash
python scripts/26_digesto_catalogo.py            # catálogo (el que está embebido en el .command + descargas a mano)
python scripts/27_digesto_duplicados.py --mover  # aparta copias repetidas en pdf/_duplicados/
python scripts/28_digesto_textos.py --ocr muestra   # pdftotext y OCR de los escaneados de la muestra
python scripts/29_digesto_muestra.py             # muestra de la PI4
```
