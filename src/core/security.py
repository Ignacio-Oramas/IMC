from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hashear_password(password: str) -> str:
    """Hashea una contraseña usando Argon2id."""
    return ph.hash(password)

def verificar_password(hash_almacenado: str, password_plana: str) -> bool:
    """Verifica si la contraseña coincide con el hash."""
    try:
        return ph.verify(hash_almacenado, password_plana)
    except VerifyMismatchError:
        return False
    except Exception:
        return False
