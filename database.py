import sqlite3
from datetime import datetime

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

# Funciones para Usuarios
def obtener_usuario_por_dni(dni):
    conn = get_db()
    usuario = conn.execute('SELECT * FROM Usuarios WHERE dni = ?', (dni,)).fetchone()
    conn.close()
    return usuario

def actualizar_altura(usuario_id, nueva_altura):
    conn = get_db()
    conn.execute(
        'UPDATE Usuarios SET altura = ? WHERE id = ?', 
        (nueva_altura, usuario_id)
    )
    conn.commit()
    conn.close()

# Funciones para Pesos
def registrar_peso(usuario_id, mes, peso):
    conn = get_db()
    # Verificar si ya existe un registro para el mes
    existente = conn.execute(
        'SELECT * FROM Pesos WHERE usuario_id = ? AND mes = ?', 
        (usuario_id, mes)
    ).fetchone()
    
    if existente:
        # Si existe, actualizar el peso
        conn.execute(
            'UPDATE Pesos SET peso = ? WHERE id = ?', 
            (peso, existente['id'])
        )
    else:
        # Si no existe, crear un nuevo registro
        conn.execute(
            'INSERT INTO Pesos (usuario_id, mes, peso) VALUES (?, ?, ?)', 
            (usuario_id, mes, peso)
        )
    conn.commit()
    conn.close()

def obtener_historial_pesos(usuario_id):
    conn = get_db()
    pesos = conn.execute('''
        SELECT mes, peso, strftime('%Y-%m-%d', fecha_registro) as fecha 
        FROM Pesos 
        WHERE usuario_id = ?
        ORDER BY fecha_registro DESC
    ''', (usuario_id,)).fetchall()
    conn.close()
    return pesos

# Funciones para Entrenador
def obtener_usuarios_entrenador(entrenador_id):
    conn = get_db()
    usuarios = conn.execute('SELECT * FROM Usuarios WHERE entrenador_id = ?', (entrenador_id,)).fetchall()
    conn.close()
    return usuarios

def actualizar_usuario(usuario_id, nombre, apellido, altura, peso_inicial, peso_ideal):
    conn = get_db()
    conn.execute(
        '''
        UPDATE Usuarios 
        SET nombre = ?, apellido = ?, altura = ?, peso_inicial = ?, peso_ideal = ?
        WHERE id = ?
        ''',
        (nombre, apellido, altura, peso_inicial, peso_ideal, usuario_id)
    )
    conn.commit()
    conn.close()

def obtener_usuario_por_id(usuario_id):
    conn = get_db()
    usuario = conn.execute('SELECT * FROM Usuarios WHERE id = ?', (usuario_id,)).fetchone()
    conn.close()
    return usuario
