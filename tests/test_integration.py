import pytest
from src.core.security import hashear_password

def test_login_exitoso(client, repo):
    # Crear usuario de prueba
    repo.crear_entrenador('testuser', hashear_password('testpass'))
    
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    
    assert b'Inicio de sesi' in response.data or b'Dashboard' in response.data

def test_login_password_incorrecto(client, repo):
    repo.crear_entrenador('testuser', hashear_password('testpass'))
    
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpass'
    })
    
    assert b'incorrectos' in response.data

def test_signup_exitoso(client):
    response = client.post('/signup', data={
        'username': 'newuser',
        'password': 'newpass123'
    }, follow_redirects=True)
    
    assert b'Registro exitoso' in response.data

def test_crear_usuario(client, repo):
    # Login primero
    repo.crear_entrenador('entrenador', hashear_password('pass123'))
    client.post('/login', data={'username': 'entrenador', 'password': 'pass123'})
    
    # Crear usuario
    response = client.post('/crear_usuario', data={
        'dni': '12345678',
        'nombre': 'Juan',
        'apellido': 'Perez',
        'altura': '1.75',
        'peso_inicial': '80.0',
        'peso_ideal': '70.0'
    }, follow_redirects=True)
    
    assert b'creado correctamente' in response.data

def test_protegido_sin_login(client):
    response = client.get('/dashboard_entrenador', follow_redirects=True)
    # Debe redirigir a login
    assert b'login' in response.data.lower() or b'Iniciar' in response.data