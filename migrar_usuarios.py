"""Migración única de las cuentas ficticias originales."""
import json
from app import USUARIOS
from seguridad import crear_hash


def migrar_usuarios():
    usuarios = json.loads(USUARIOS.read_text(encoding="utf-8"))
    for usuario in usuarios:
        if "clave" in usuario:
            usuario["hash"] = crear_hash(usuario.pop("clave"))
    USUARIOS.write_text(json.dumps(usuarios, indent=2, ensure_ascii=False),
                        encoding="utf-8")


if __name__ == "__main__":
    migrar_usuarios()
    print("Usuarios migrados: archivo final sin campo clave.")
