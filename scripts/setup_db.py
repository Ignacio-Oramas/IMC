"""
Script de inicializacion de la base de datos.
Crea las tablas y un usuario de prueba con contrasena hasheada.
"""
import sqlite3
import os
import sys

DATABASE = 'database.db'
SCHEMA = 'schema.sql'

def init_db(force=False):
    if os.path.exists(DATABASE):
        if not force:
            print(f"{DATABASE} ya existe. Usar --force para recrear.")
            return False
        os.remove(DATABASE)
        print("Base de datos anterior eliminada.")

    print(f"Creando base de datos {DATABASE}...")
    conn = sqlite3.connect(DATABASE)
    with open(SCHEMA, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Tablas creadas.")
    return True

def crear_usuario_prueba():
    from argon2 import PasswordHasher
    ph = PasswordHasher()
    
    username = "entrenador"
    password = "password123"
    password_hash = ph.hash(password)
    
    conn = sqlite3.connect(DATABASE)
    try:
        conn.execute(
            'INSERT INTO Entrenador (username, password) VALUES (?, ?)',
            (username, password_hash)
        )
        conn.commit()
        print(f"Usuario creado: {username} / {password}")
    except sqlite3.IntegrityError:
        print("El usuario 'entrenador' ya existe.")
    finally:
        conn.close()

if __name__ == '__main__':
    force = '--force' in sys.argv
    print("Iniciando script de setup...")
    if init_db(force):
        crear_usuario_prueba()
    print("Listo! Ya podes loguearte.")