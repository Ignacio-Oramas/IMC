import pytest
import sys
import os

# Agregar raiz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.repository import Repository

@pytest.fixture
def test_db():
    """DB en memoria para tests."""
    import sqlite3
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.executescript('''
        CREATE TABLE Entrenador (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        CREATE TABLE Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dni TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            altura REAL,
            peso_inicial REAL,
            peso_ideal REAL,
            entrenador_id INTEGER,
            FOREIGN KEY(entrenador_id) REFERENCES Entrenador(id)
        );
        CREATE TABLE Pesos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            mes TEXT,
            anio TEXT,
            peso REAL,
            FOREIGN KEY(usuario_id) REFERENCES Usuarios(id)
        );
    ''')
    yield conn
    conn.close()

@pytest.fixture
def repo(test_db):
    """Repository que usa la DB en memoria."""
    class TestRepo(Repository):
        def __init__(self, conn):
            super().__init__()
            self._conn_override = conn
            
        def _get_connection(self):
            return self._conn_override
            
        def fetch_one(self, query, params=()):
            return self._conn_override.execute(query, params).fetchone()
            
        def fetch_all(self, query, params=()):
            return self._conn_override.execute(query, params).fetchall()
            
        def execute(self, query, params=()):
            self._conn_override.execute(query, params)
            self._conn_override.commit()
            
        def obtener_entrenador_por_username(self, username):
            return self.fetch_one('SELECT * FROM Entrenador WHERE username = ?', (username,))
            
        def crear_entrenador(self, username, password):
            self.execute('INSERT INTO Entrenador (username, password) VALUES (?, ?)', (username, password))
            
        def obtener_usuario_por_dni(self, dni):
            return self.fetch_one('SELECT * FROM Usuarios WHERE dni = ?', (dni,))
            
        def obtener_usuario_por_id(self, uid):
            return self.fetch_one('SELECT * FROM Usuarios WHERE id = ?', (uid,))
            
        def crear_usuario(self, data):
            self.execute(
                'INSERT INTO Usuarios (dni, nombre, apellido, altura, peso_inicial, peso_ideal, entrenador_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (data['dni'], data['nombre'], data['apellido'], data['altura'], data['peso_inicial'], data['peso_ideal'], data['entrenador_id'])
            )
            
        def obtener_usuarios_entrenador(self, entr_id):
            return self.fetch_all('SELECT * FROM Usuarios WHERE entrenador_id = ?', (entr_id,))
            
        def registrar_peso(self, uid, mes, anio, peso):
            self.execute('INSERT INTO Pesos (usuario_id, mes, anio, peso) VALUES (?, ?, ?, ?)', (uid, mes, anio, peso))
            
        def obtener_historial_pesos(self, uid, *args):
            return self.fetch_all('SELECT * FROM Pesos WHERE usuario_id = ? ORDER BY anio, mes', (uid,))
            
        def eliminar_usuario(self, uid):
            self.execute('DELETE FROM Pesos WHERE usuario_id = ?', (uid,))
            self.execute('DELETE FROM Usuarios WHERE id = ?', (uid,))
            
        def actualizar_altura(self, uid, altura):
            self.execute('UPDATE Usuarios SET altura = ? WHERE id = ?', (altura, uid))
            
    return TestRepo(test_db)

@pytest.fixture
def app_with_repo(test_db):
    """App de Flask con el repo de test injectado."""
    from flask import Flask
    from src.web.routes import register_routes
    from src.infrastructure.repository import Repository
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_dir = os.path.join(root_dir, 'templates')
    app = Flask(__name__, template_folder=template_dir)
    app.config['SECRET_KEY'] = 'test_secret'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    class TestRepo(Repository):
        def __init__(self, conn):
            super().__init__('test.db') #dummy path
            self._conn_override = conn
            
        def _get_connection(self):
            return self._conn_override
            
        def fetch_one(self, query, params=()):
            return self._conn_override.execute(query, params).fetchone()
            
        def fetch_all(self, query, params=()):
            return self._conn_override.execute(query, params).fetchall()
            
        def execute(self, query, params=()):
            self._conn_override.execute(query, params)
            self._conn_override.commit()
            
        def obtener_entrenador_por_username(self, u):
            return self.fetch_one('SELECT * FROM Entrenador WHERE username = ?', (u,))
            
        def crear_entrenador(self, u, p):
            self.execute('INSERT INTO Entrenador (username, password) VALUES (?, ?)', (u, p))
            
        def obtener_usuario_por_dni(self, d):
            return self.fetch_one('SELECT * FROM Usuarios WHERE dni = ?', (d,))
            
        def obtener_usuario_por_id(self, i):
            return self.fetch_one('SELECT * FROM Usuarios WHERE id = ?', (i,))
            
        def obtener_usuarios_entrenador(self, e):
            return self.fetch_all('SELECT * FROM Usuarios WHERE entrenador_id = ?', (e,))
            
        def crear_usuario(self, d):
            self.execute(
                'INSERT INTO Usuarios (dni, nombre, apellido, altura, peso_inicial, peso_ideal, entrenador_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (d['dni'], d['nombre'], d['apellido'], d['altura'], d['peso_inicial'], d['peso_ideal'], d['entrenador_id'])
            )
            
        def registrar_peso(self, u, m, a, p):
            self.execute('INSERT INTO Pesos (usuario_id, mes, anio, peso) VALUES (?, ?, ?, ?)', (u, m, a, p))
            
        def obtener_historial_pesos(self, u, *args):
            return self.fetch_all('SELECT * FROM Pesos WHERE usuario_id = ?', (u,))
            
        def eliminar_usuario(self, u):
            self.execute('DELETE FROM Pesos WHERE usuario_id = ?', (u,))
            self.execute('DELETE FROM Usuarios WHERE id = ?', (u,))
            
        def actualizar_altura(self, u, a):
            self.execute('UPDATE Usuarios SET altura = ? WHERE id = ?', (a, u))
            
        def actualizar_usuario(self, u, d):
            self.execute(
                'UPDATE Usuarios SET nombre=?, apellido=?, altura=?, peso_inicial=?, peso_ideal=? WHERE id=?',
                (d['nombre'], d['apellido'], d['altura'], d['peso_inicial'], d['peso_ideal'], u)
            )
            
        def eliminar_peso(self, p):
            self.execute('DELETE FROM Pesos WHERE id = ?', (p,))

    register_routes(app, TestRepo(test_db))
    return app

@pytest.fixture
def client(app_with_repo):
    return app_with_repo.test_client()