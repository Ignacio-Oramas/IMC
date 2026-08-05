import pytest
from src.core.security import hashear_password, verificar_password

def test_hashing_y_verificacion_exitosa():
    password = "mi_password_segura"
    hash_pwd = hashear_password(password)
    
    assert hash_pwd != password
    assert verificar_password(hash_pwd, password) is True

def test_verificacion_falla_con_password_incorrecta():
    password_real = "secreto123"
    password_falsa = "otro_secreto"
    hash_pwd = hashear_password(password_real)
    
    assert verificar_password(hash_pwd, password_falsa) is False

def test_verificacion_falla_con_hash_invalido():
    assert verificar_password("hash_trucho", "password") is False
