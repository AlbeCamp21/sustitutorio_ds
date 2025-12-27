# Código adaptado de los archivos build.py y main.py del Laboratorio 6

import json
import os
from datetime import datetime

def exportar_reporte(nombre, datos, directorio="reportes"):
    os.makedirs(directorio, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = os.path.join(directorio, f"{nombre}_{ts}.json")
    with open(ruta, "w") as f:
        json.dump(datos, f, indent=2)
    return ruta
