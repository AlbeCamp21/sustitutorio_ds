# Código adaptado de los archivos generate_infra.py (Laboratorio 6) y database.py (Laboratorio 10)

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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS comandos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                valvula TEXT NOT NULL,
                accion TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada")
