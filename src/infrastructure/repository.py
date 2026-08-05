import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

class Repository:
    """
    Nuestro 'PDO' de Python. Encapsula la conexión y las consultas.
    Asegura el uso de sentencias preparadas para evitar SQL Injection.
    """
    def __init__(self, db_path=None):
        path = db_path or os.getenv('DATABASE_PATH', 'database.db')
        if not os.path.isabs(path):
            # La raíz del proyecto está dos niveles arriba de este archivo (src/infrastructure)
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            path = os.path.join(base_dir, path)
        self.db_path = path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=20.0)
        conn.row_factory = sqlite3.Row
        return conn

    def fetch_one(self, query, params=()):
        with self._get_connection() as conn:
            return conn.execute(query, params).fetchone()

    def fetch_all(self, query, params=()):
        with self._get_connection() as conn:
            return conn.execute(query, params).fetchall()

    def execute(self, query, params=()):
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor

    # --- Métodos de Negocio ---
    
    def obtener_usuario_por_dni(self, dni):
        return self.fetch_one('SELECT * FROM Usuarios WHERE dni = ?', (dni,))

    def obtener_usuario_por_id(self, usuario_id):
        return self.fetch_one('SELECT * FROM Usuarios WHERE id = ?', (usuario_id,))

    def obtener_entrenador_por_username(self, username):
        return self.fetch_one('SELECT * FROM Entrenador WHERE username = ?', (username,))

    def crear_entrenador(self, username, password_hasheada):
        return self.execute(
            'INSERT INTO Entrenador (username, password) VALUES (?, ?)',
            (username, password_hasheada)
        )

    def actualizar_password_entrenador(self, username, nueva_password_hasheada):
        return self.execute(
            'UPDATE Entrenador SET password = ? WHERE username = ?',
            (nueva_password_hasheada, username)
        )

    def obtener_usuarios_entrenador(self, entrenador_id):
        return self.fetch_all('SELECT * FROM Usuarios WHERE entrenador_id = ?', (entrenador_id,))

    def crear_usuario(self, data):
        return self.execute(
            '''INSERT INTO Usuarios (dni, nombre, apellido, altura, peso_inicial, peso_ideal, entrenador_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (data['dni'], data['nombre'], data['apellido'], data['altura'], 
             data['peso_inicial'], data['peso_ideal'], data['entrenador_id'])
        )

    def actualizar_usuario(self, usuario_id, data):
        return self.execute(
            '''UPDATE Usuarios 
               SET nombre = ?, apellido = ?, altura = ?, peso_inicial = ?, peso_ideal = ?
               WHERE id = ?''',
            (data['nombre'], data['apellido'], data['altura'], 
             data['peso_inicial'], data['peso_ideal'], usuario_id)
        )

    def actualizar_altura(self, usuario_id, nueva_altura):
        return self.execute(
            'UPDATE Usuarios SET altura = ? WHERE id = ?',
            (nueva_altura, usuario_id)
        )

    def eliminar_usuario(self, usuario_id):
        self.execute('DELETE FROM Pesos WHERE usuario_id = ?', (usuario_id,))
        return self.execute('DELETE FROM Usuarios WHERE id = ?', (usuario_id,))

    def registrar_peso(self, usuario_id, mes, anio, peso):
        return self.execute(
            'INSERT INTO Pesos (usuario_id, mes, anio, peso) VALUES (?, ?, ?, ?)',
            (usuario_id, mes, anio, peso)
        )

    def obtener_historial_pesos(self, usuario_id, anio_inicio=None, anio_fin=None):
        query = 'SELECT * FROM Pesos WHERE usuario_id = ?'
        params = [usuario_id]
        
        if anio_inicio:
            query += ' AND CAST(anio AS INTEGER) >= ?'
            params.append(anio_inicio)
        if anio_fin:
            query += ' AND CAST(anio AS INTEGER) <= ?'
            params.append(anio_fin)
            
        query += ' ORDER BY anio, mes'
        return self.fetch_all(query, params)

    def eliminar_peso(self, peso_id):
        return self.execute('DELETE FROM Pesos WHERE id = ?', (peso_id,))
