"""Inventario académico con controles básicos de seguridad."""
import json
from datetime import datetime, timezone
from pathlib import Path
from seguridad import verificar_clave

RAIZ = Path(__file__).resolve().parent
DATOS = RAIZ / "inventario.json"
USUARIOS = RAIZ / "usuarios.json"
LOG = RAIZ / "auditoria.jsonl"


def cargar_inventario():
    try:
        return json.loads(DATOS.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("No se encontró inventario.json. Restaure el archivo válido.")
    except (json.JSONDecodeError, UnicodeError):
        print("inventario.json no contiene JSON válido. Restaure el archivo válido.")
    except OSError:
        print("No se pudo leer inventario.json.")
    return None


def guardar_inventario(productos):
    try:
        # r+ exige un archivo existente y permite validarlo antes de escribir.
        with DATOS.open("r+", encoding="utf-8") as archivo:
            json.load(archivo)
            archivo.seek(0)
            archivo.write(json.dumps(productos, indent=2, ensure_ascii=False))
            archivo.truncate()
        return True
    except FileNotFoundError:
        print("No se encontró inventario.json. No se creó otro archivo.")
    except (json.JSONDecodeError, UnicodeError):
        print("inventario.json no contiene JSON válido. No se sobrescribió.")
    except OSError:
        print("No se pudo guardar inventario.json.")
    return False


def registrar_evento(usuario, accion, resultado, **detalles):
    evento = {"fecha_hora": datetime.now(timezone.utc).isoformat(),
              "usuario": usuario, "accion": accion, "resultado": resultado}
    for campo in ("producto", "anterior", "nueva"):
        if campo in detalles:
            evento[campo] = detalles[campo]
    try:
        with LOG.open("a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(evento, ensure_ascii=False) + "\n")
        return True
    except OSError:
        print("No se pudo escribir la auditoría.")
        return False


def autenticar(nombre, clave):
    try:
        usuarios = json.loads(USUARIOS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        print("No se pudo leer el archivo de usuarios.")
        registrar_evento(nombre, "login", "error_archivo")
        return None
    for usuario in usuarios:
        if (usuario["usuario"] == nombre
                and verificar_clave(usuario["hash"], clave)):
            registrar_evento(nombre, "login", "exitoso")
            return {"usuario": nombre, "rol": usuario["rol"]}
    registrar_evento(nombre, "login", "fallido")
    print("Credenciales incorrectas.")
    return None


def sesion_valida(sesion):
    if not isinstance(sesion, dict):
        return False
    if not isinstance(sesion.get("usuario"), str):
        return False
    if sesion["usuario"] == "":
        return False
    if sesion.get("rol") not in ("admin", "user"):
        return False
    return True


def consultar_inventario(sesion):
    if not sesion_valida(sesion):
        print("Acceso rechazado: se requiere una sesión válida.")
        registrar_evento("sin_sesion", "consultar", "rechazado_sesion")
        return False
    productos = cargar_inventario()
    if productos is None:
        return False
    for producto in productos:
        print(producto["id"], producto["nombre"], producto["cantidad"])
    return True


def validar_cantidad(entrada):
    if not isinstance(entrada, str):
        return None
    try:
        cantidad = int(entrada)
    except ValueError:
        return None
    if cantidad < 0 or cantidad > 1000:
        return None
    return cantidad


def modificar_cantidad(sesion, identificador, entrada):
    if not sesion_valida(sesion):
        print("Acceso rechazado: se requiere una sesión válida.")
        registrar_evento("sin_sesion", "modificar", "rechazado_sesion",
                         producto=identificador)
        return False
    if sesion["rol"] != "admin":
        print("Acceso rechazado: solo admin puede modificar cantidades.")
        registrar_evento(sesion["usuario"], "modificar", "rechazado_permisos",
                         producto=identificador)
        return False
    cantidad = validar_cantidad(entrada)
    if cantidad is None:
        print("Cantidad inválida: escriba un entero entre 0 y 1000.")
        return False
    productos = cargar_inventario()
    if productos is None:
        return False
    for producto in productos:
        if producto["id"] == identificador:
            anterior = producto["cantidad"]
            producto["cantidad"] = cantidad
            if not guardar_inventario(productos):
                return False
            registrar_evento(
                sesion["usuario"], "modificar", "exitoso",
                producto=identificador, anterior=anterior, nueva=cantidad
            )
            print("Cantidad actualizada.")
            return True
    print("Producto inexistente. No se realizó ningún cambio.")
    return False


def main():
    print("Inventario académico — versión corregida")
    print("Estudiante:", input("Escriba su nombre: "))
    sesion = None
    while True:
        if sesion is None:
            nombre = input("Usuario (o salir): ")
            if nombre == "salir":
                break
            sesion = autenticar(nombre, input("Contraseña de prueba: "))
            continue
        print("1. Consultar | 2. Modificar | 3. Cerrar sesión | 0. Salir")
        opcion = input("Opción: ")
        if opcion == "1":
            consultar_inventario(sesion)
        elif opcion == "2":
            identificador = input("ID del producto: ")
            entrada = input("Nueva cantidad: ")
            modificar_cantidad(sesion, identificador, entrada)
        elif opcion == "3":
            sesion = None
        elif opcion == "0":
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
