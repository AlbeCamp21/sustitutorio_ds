# Código adaptado del archivo database.py del Laboratorio 10

from pathlib import Path
import sqlite3

DB_PATH = Path("planta.db")

def contar_registros():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sensores")
        sensores = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM comandos")
        comandos = cursor.fetchone()[0]
    return {"sensores": sensores, "comandos": comandos}
