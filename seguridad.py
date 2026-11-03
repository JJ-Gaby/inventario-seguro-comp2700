"""Funciones listas para integrar: no implementar criptografía propia."""
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError

_hasher = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)


def crear_hash(clave):
    # La biblioteca genera automáticamente un salt aleatorio.
    return _hasher.hash(clave)


def verificar_clave(hash_guardado, clave):
    try:
        return _hasher.verify(hash_guardado, clave)
    except (VerificationError, InvalidHashError):
        return False
