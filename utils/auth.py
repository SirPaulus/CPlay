import hashlib

def hash_password(password: str) -> str:
    """Возвращает хэш пароля."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Проверяет, соответствует ли пароль хэшу."""
    return hash_password(password) == hashed