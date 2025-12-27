# Código adaptado de los archivos generate_envs.py y main.py del Laboratorio 5

import json
import os

ENTORNOS = [
    {"nombre": "produccion", "red": "planta-local"},
]

DIRECTORIO_SALIDA = "environments"

def generar_terraform(entorno):
    directorio = os.path.join(DIRECTORIO_SALIDA, entorno["nombre"], "terraform")
    os.makedirs(directorio, exist_ok=True)
    config = {
        "resource": [
            {
                "null_resource": [
                    {
                        entorno["nombre"]: [
                            {
                                "triggers": {
                                    "nombre": entorno["nombre"],
                                    "red": entorno["red"]
                                },
                                "provisioner": [
                                    {
                                        "local-exec": {
                                            "command": f"echo 'Iniciando planta {entorno['nombre']} en red {entorno['red']}'"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    with open(os.path.join(directorio, "main.tf.json"), "w") as f:
        json.dump(config, f, sort_keys=True, indent=4)

def generar_kubernetes(entorno):
    directorio = os.path.join(DIRECTORIO_SALIDA, entorno["nombre"], "kubernetes")
    os.makedirs(directorio, exist_ok=True)
    config = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": f"planta-{entorno['nombre']}-config"
        },
        "data": {
            "ENTORNO": entorno["nombre"],
            "RED": entorno["red"],
            "PH_MIN": "6.5",
            "PH_MAX": "8.5",
            "TURBIDEZ_MAX": "4.0",
            "CAUDAL_MIN": "10.0",
            "CAUDAL_MAX": "100.0"
        }
    }
    with open(os.path.join(directorio, "configmap.json"), "w") as f:
        json.dump(config, f, indent=4)

if __name__ == "__main__":
    for entorno in ENTORNOS:
        generar_terraform(entorno)
        generar_kubernetes(entorno)
    print(f"Generados {len(ENTORNOS)} entornos en '{DIRECTORIO_SALIDA}/'")
