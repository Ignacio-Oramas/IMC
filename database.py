# database.py
import sqlite3

# Ruta de la base de datos
DATABASE = 'database.db'

# Función para obtener la conexión a la base de datos
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
    return conn

# Función para inicializar la base de datos y crear las tablas
def init_db():
    conn = get_db()
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()