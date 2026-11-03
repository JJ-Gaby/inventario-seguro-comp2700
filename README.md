# Inventario académico con controles de seguridad

Estudiante: Leyra G. Bonilla Maldonado

Corrección de la base suministrada para COMP2700, M3. Aplicación de terminal
en Python con archivos JSON y auditoría JSONL. Utiliza únicamente datos ficticios.

## Requisitos y ejecución

Python 3.10 o posterior y las dependencias de `requirements.txt`.
Desde la carpeta del proyecto, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

No hace falta activar el entorno virtual. Si Python no está instalado, instale
Python antes de ejecutar estos comandos. Al iniciar, escriba su nombre para que
aparezca en la terminal. Las rutas de datos son relativas a `app.py`.

Cuentas públicas exclusivamente ficticias:

- `admin` / `AdminDemo2700!`: consulta y modifica.
- `user` / `UserDemo2700!`: consulta; no puede modificar.

Las contraseñas anteriores se documentan para probar estas cuentas ficticias.
`usuarios.json` contiene solamente usuario, rol y hash Argon2id; no contiene
el campo `clave`. Los hashes ya están generados. `migrar_usuarios.py` conserva
el procedimiento de migración de la base original y no hace falta ejecutarlo.

## Archivos y pruebas

- `app.py`: aplicación corregida.
- `seguridad.py`: funciones suministradas por el curso, sin cambios.
- `migrar_usuarios.py`: convierte claves originales a hashes y elimina `clave`.
- `inventario.json`: datos ficticios; P001 queda en 20 al finalizar las pruebas.
- `usuarios.json`: cuentas ficticias con hashes.
- `auditoria.jsonl`: muestra real de eventos obtenidos en las pruebas locales.
- `pruebas.py`: casos de autenticación, autorización, validación, consulta,
  persistencia, auditoría y archivos ausentes o inválidos.

```powershell
.\.venv\Scripts\python.exe pruebas.py
```

Las pruebas utilizan una copia temporal dentro de `evidencias_locales`, comienzan
con P001 en 10 y no alteran el inventario entregado. Guardan `resultados.txt` y
`auditoria_pruebas.jsonl`. Terminan con `TODAS LAS COMPROBACIONES PASARON` si
los resultados coinciden con lo esperado. La persistencia se prueba con dos
procesos distintos de la aplicación. No se incluyen capturas fabricadas.

Para obtener capturas reales, ejecute las pruebas en su terminal y capture cada
sección con su nombre visible. Las pruebas directas obtienen las sesiones con
`autenticar`, sin crear diccionarios con roles inventados.

## Fuentes y uso de IA

La base original y `seguridad.py` fueron suministrados por el curso.
Se utilizó ChatGPT/Codex para analizar las debilidades, proponer las correcciones,
generar pruebas y preparar borradores de las explicaciones. Se verificó el
código ejecutando casos válidos e inválidos y comparando los archivos antes y
después. La estudiante debe revisar el código y comprenderlo antes de entregar.

- argon2-cffi, *How to Hash a Password*:
  https://argon2-cffi.readthedocs.io/en/stable/howto.html
- Python, documentación de `json`:
  https://docs.python.org/3/library/json.html

## Límites del prototipo

Los permisos se comprueban dentro del proceso. Un usuario con acceso de escritura
a los archivos puede alterarlos; una sesión tampoco es un token firmado.
No se implementan MFA, cifrado, recuperación de contraseñas ni protección externa
del log. La escritura del inventario no es atómica y no hay bloqueo entre
procesos. Si falla la auditoría después de guardar un cambio, se informa el
error, pero el cambio ya está guardado. Son límites del prototipo.

Repositorio del proyecto:
https://github.com/JJ-Gaby/inventario-seguro-comp2700

Las respuestas y evidencias de Blackboard se preparan por separado. Las pruebas
deben corresponder al commit indicado en la entrega. La evaluación se conserva
como borrador hasta que la estudiante decida enviarla.
No publique `.venv`, `__pycache__`, evidencias con datos privados ni credenciales
reales. `.gitignore` excluye los entornos y las evidencias locales.
