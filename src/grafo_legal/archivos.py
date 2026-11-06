"""Escritura segura de archivos de salida.

Se escribe en un temporal de la misma carpeta y se reemplaza el destino con os.replace. Asi un
corte a mitad de camino nunca deja un CSV truncado, y se puede regenerar un archivo aunque el
usuario no tenga permiso de escritura sobre el archivo viejo (alcanza con permiso sobre la carpeta,
como pasa con archivos creados por otra herramienta).
"""

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def abrir_para_escribir(ruta, newline=""):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{ruta.name}.", suffix=".tmp", dir=ruta.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline=newline) as f:
            yield f
        os.chmod(tmp, 0o644)
        os.replace(tmp, ruta)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def escribir_texto(ruta, texto: str) -> None:
    with abrir_para_escribir(ruta) as f:
        f.write(texto)
