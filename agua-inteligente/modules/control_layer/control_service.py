# Código adaptado del archivo database.py del Laboratorio 10

from contextlib import contextmanager
from pathlib import Path
import sqlite3

DB_PATH = Path("planta.db")

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def ejecutar_comando(valvula, accion):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO comandos (valvula, accion) VALUES (?, ?)",
            (valvula, accion)
        )
        conn.commit()
        return cursor.lastrowid

def listar_comandos():
    with get_conn() as conn:
        cursor = conn.execute(
            "SELECT id, valvula, accion, timestamp FROM comandos"
        )
        rows = cursor.fetchall()
    return [{"id": r[0], "valvula": r[1], "accion": r[2], "timestamp": r[3]} for r in rows]
