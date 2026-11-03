"""Pruebas reales sobre una copia temporal; no altera el inventario entregado."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

RAIZ = Path(__file__).resolve().parent
NOMBRE = "Leyra G. Bonilla Maldonado"


def ejecutar():
    evidencia = RAIZ / "evidencias_locales"
    evidencia.mkdir(exist_ok=True)
    salida = io.StringIO()
    with tempfile.TemporaryDirectory(dir=evidencia) as temporal, contextlib.redirect_stdout(salida):
        carpeta = Path(temporal)
        for nombre in ("app.py", "seguridad.py", "usuarios.json", "inventario.json"):
            shutil.copy2(RAIZ / nombre, carpeta / nombre)
        datos = carpeta / "inventario.json"
        productos = json.loads(datos.read_text(encoding="utf-8"))
        productos[0]["cantidad"] = 10
        datos.write_text(json.dumps(productos, ensure_ascii=False), encoding="utf-8")
        spec = importlib.util.spec_from_file_location("app_pruebas", carpeta / "app.py")
        app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app)

        def cli(entradas):
            entorno = dict(os.environ, PYTHONIOENCODING="utf-8")
            proceso = subprocess.run([sys.executable, str(carpeta / "app.py")],
                                     input=entradas, text=True, encoding="utf-8",
                                     capture_output=True, env=entorno, check=True)
            assert not proceso.stderr, proceso.stderr
            print(proceso.stdout)
            return proceso.stdout

        print("Estudiante:", NOMBRE)
        print("=== 2. Contraseñas ===")
        usuarios = json.loads(app.USUARIOS.read_text(encoding="utf-8"))
        assert all("clave" not in u and u["hash"].startswith("$argon2id$") for u in usuarios)
        print("Esperado y obtenido: dos cuentas con hash Argon2id y sin campo clave.")

        print("=== 3. Autenticación ===")
        admin = app.autenticar("admin", "AdminDemo2700!")
        user = app.autenticar("user", "UserDemo2700!")
        assert admin and user
        print("Credenciales correctas: sesiones admin y user obtenidas.")
        for nombre, clave in (("admin", "incorrecta"), ("no_existe", "incorrecta")):
            assert app.autenticar(nombre, clave) is None
            texto = cli(f"{NOMBRE}\n{nombre}\n{clave}\nsalir\n")
            assert "Credenciales incorrectas." in texto
            assert "1. Consultar" not in texto
            print(nombre, ": esperado y obtenido: rechazo sin menú protegido.")

        print("=== 4. Autorización ===")
        original = datos.read_bytes()
        for sesion in (user, None):
            assert app.modificar_cantidad(sesion, "P001", "99") is False
            assert datos.read_bytes() == original
        assert app.consultar_inventario(None) is False
        print("Esperado y obtenido: tres rechazos; P001 permanece en 10 y archivo idéntico.")

        print("=== 5. Validación ===")
        for entrada in ("-1", "1001", "abc", "2.5", ""):
            antes = datos.read_bytes()
            assert app.modificar_cantidad(admin, "P001", entrada) is False
            assert datos.read_bytes() == antes
            print(repr(entrada), "| esperado: rechazo sin cambios | obtenido: rechazo sin cambios")
        for entrada in ("0", "1000"):
            assert app.modificar_cantidad(admin, "P001", entrada) is True
            assert app.cargar_inventario()[0]["cantidad"] == int(entrada)
            print(repr(entrada), "| esperado: aceptación | obtenido: cantidad", entrada)
        assert app.modificar_cantidad(admin, "P001", "10") is True
        print("P001 restaurado a 10.")

        print("=== 6. Consulta y modificación ===")
        assert app.consultar_inventario(admin) is True
        assert app.consultar_inventario(user) is True
        # Este proceso termina después de guardar 20.
        texto = cli(f"{NOMBRE}\nadmin\nAdminDemo2700!\n2\nP001\n20\n0\n")
        assert "Cantidad actualizada." in texto
        assert app.cargar_inventario()[0]["cantidad"] == 20
        antes = datos.read_bytes()
        assert app.modificar_cantidad(admin, "P999", "99") is False
        assert datos.read_bytes() == antes
        print("Esperado y obtenido: P001=20; P999 no creado y archivo sin cambios.")

        print("=== 7. Persistencia ===")
        texto = cli(f"{NOMBRE}\nadmin\nAdminDemo2700!\n1\n0\n")
        assert "P001 Teclado 20" in texto
        print("Esperado y obtenido: un segundo proceso conserva P001=20.")

        print("=== 9. Errores ===")
        respaldo = datos.read_bytes()
        datos.rename(carpeta / "inventario.respaldo")
        assert app.consultar_inventario(admin) is False
        assert app.modificar_cantidad(admin, "P001", "50") is False
        assert not datos.exists()
        print("Archivo ausente: esperado y obtenido: mensaje controlado y archivo no recreado.")
        datos.write_text("ESTO NO ES JSON", encoding="utf-8")
        assert app.consultar_inventario(admin) is False
        assert app.modificar_cantidad(admin, "P001", "50") is False
        assert datos.read_text(encoding="utf-8") == "ESTO NO ES JSON"
        print("JSON inválido: esperado y obtenido: mensaje controlado y contenido sin sobrescribir.")
        datos.write_bytes((carpeta / "inventario.respaldo").read_bytes())
        assert datos.read_bytes() == respaldo
        assert app.consultar_inventario(admin) is True
        print("Archivo válido restaurado; consulta correcta con P001=20.")

        print("=== 8. Auditoría ===")
        log = app.LOG.read_text(encoding="utf-8")
        eventos = [json.loads(linea) for linea in log.splitlines()]
        for resultado in ("exitoso", "fallido", "rechazado_permisos", "rechazado_sesion"):
            assert any(e["resultado"] == resultado for e in eventos)
        assert all(set(e) <= {"fecha_hora", "usuario", "accion", "resultado",
                             "producto", "anterior", "nueva"} for e in eventos)
        assert all(clave not in log for clave in ("AdminDemo2700!", "UserDemo2700!", "$argon2"))
        print("Eventos requeridos presentes; sin contraseñas ni hashes.")
        (evidencia / "auditoria_pruebas.jsonl").write_text(log, encoding="utf-8")
        print("TODAS LAS COMPROBACIONES PASARON.")
    (evidencia / "resultados.txt").write_text(salida.getvalue(), encoding="utf-8")
    print(salida.getvalue())


if __name__ == "__main__":
    ejecutar()
