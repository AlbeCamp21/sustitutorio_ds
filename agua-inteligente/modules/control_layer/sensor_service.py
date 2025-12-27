# Código adaptado del archivo database.py del Laboratorio 10

from contextlib import contextmanager
from pathlib import Path
import sqlite3

DB_PATH = Path("planta.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sensores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                valor REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def agregar_lectura(tipo, valor):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sensores (tipo, valor) VALUES (?, ?)",
            (tipo, valor)
        )
        conn.commit()
        return cursor.lastrowid

def listar_lecturas():
    with get_conn() as conn:
        cursor = conn.execute(
            "SELECT id, tipo, valor, timestamp FROM sensores"
        )
        rows = cursor.fetchall()
    return [{"id": r[0], "tipo": r[1], "valor": r[2], "timestamp": r[3]} for r in rows]
