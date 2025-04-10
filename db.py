import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("estudos.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS estudos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_hora TEXT,
        materia TEXT,
        tempo TEXT,
        tipo TEXT,
        semana INTEGER
    )''')
    conn.commit()
    conn.close()

def inserir_registro(data_hora, materia, tempo, tipo, semana):
    conn = sqlite3.connect("estudos.db")
    c = conn.cursor()
    c.execute("INSERT INTO estudos (data_hora, materia, tempo, tipo, semana) VALUES (?, ?, ?, ?, ?)",
              (data_hora, materia, tempo, tipo, semana))
    conn.commit()
    conn.close()

def buscar_dados():
    conn = sqlite3.connect("estudos.db")
    df = conn.execute("SELECT * FROM estudos").fetchall()
    colunas = [col[0] for col in conn.execute("PRAGMA table_info(estudos)")]
    conn.close()
    return colunas, df
