import os
import secrets

import bcrypt
import mysql.connector


cedula = os.environ.get("LOCUST_CEDULA", "").strip()
github_env = os.environ.get("GITHUB_ENV")
if not cedula:
    raise RuntimeError("LOCUST_CEDULA es requerido para preparar el usuario de CI.")
if not github_env:
    raise RuntimeError("GITHUB_ENV es requerido para exportar la contraseña temporal.")

password = secrets.token_urlsafe(18)
password_hash = bcrypt.hashpw(
    password.encode("utf-8"),
    bcrypt.gensalt(),
).decode("utf-8")

connection = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
    database=os.environ["DB_NAME"],
)

try:
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE seguridad.usuario
        SET nombre_usuario = 'Usuario',
            apellido_usuario = 'Locust CI',
            password = %s,
            telefono = '04120000001',
            direccion = 'Entorno temporal de CI',
            correo = 'locust-ci@example.test',
            status = 1,
            cod_rol = 1,
            intentos_fallidos = 0,
            ultimo_acceso = NULL,
            fecha_registro = CURRENT_DATE
        WHERE cedula = %s
        """,
        (password_hash, cedula),
    )
    if cursor.rowcount != 1:
        raise RuntimeError(f"No existe el usuario de prueba {cedula} en la base CI.")
    connection.commit()
    cursor.close()
finally:
    connection.close()

with open(github_env, "a", encoding="utf-8") as file:
    file.write(f"LOCUST_PASSWORD={password}\n")
