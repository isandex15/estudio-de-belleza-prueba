
import sys
import uuid
from pathlib import Path

import pytest
import bcrypt

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.usuarios import UsuariosModelo
# Ejecutar todas las pruebas
# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_usuariosi.py" -vv -s --tb=long

# Ejecutar prueba de registro
# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_usuariosi.py::test_registrar" -vv -s --tb=long

# Ejecutar prueba de consulta del usuario registrado
# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_usuariosi.py::test_consultar_usuario_registrado" -vv -s --tb=long

# Ejecutar prueba de registro con cédula existente
# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_usuariosi.py::test_registrar_usuario_cedula_existente" -vv -s --tb=long

# Ejecutar prueba de edición
# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_usuariosi.py::test_editar_usuario" -vv -s --tb=long


# Ejecutar prueba de rechazo de eliminación de usuario activo
# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_usuariosi.py::test_eliminar_usuario_activo" -vv -s --tb=long

# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_usuariosi.py::test_conservar_usuario_activo" -vv -s --tb=long


@pytest.fixture(scope="module")
def datos_usuario():
    modelo = UsuariosModelo()
    cursor = modelo.conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT cod_rol
        FROM seguridad.rol
        WHERE status = 1
        ORDER BY cod_rol
        LIMIT 1
    """)
    rol = cursor.fetchone()
    cursor.close()

    if not rol:
        modelo.conexion.close()
        pytest.fail("La base de datos de pruebas requiere al menos un rol activo.")

    usuarios_creados = []

    datos = {
        "modelo": modelo,
        "cod_rol": rol["cod_rol"],
        "usuarios_creados": usuarios_creados,
    }

    try:
        yield datos
    finally:
        for cedula in usuarios_creados:
            cursor = modelo.conexion.cursor()
            cursor.execute("""
                UPDATE seguridad.usuario
                SET status = 0
                WHERE cedula = %s
            """, (cedula,))
            modelo.conexion.commit()
            cursor.close()

        modelo.conexion.close()


@pytest.fixture(scope="module")
def usuario_registrado(datos_usuario):
    modelo = datos_usuario["modelo"]

    cedula = str(uuid.uuid4().int % 90000000 + 10000000)
    correo = f"usuario.{cedula}@test.com"

    modelo.cedula = cedula
    modelo.nombre_usuario = "Usuario"
    modelo.apellido_usuario = "Prueba"
    modelo.telefono = "04141234567"
    modelo.direccion = "Barquisimeto"
    modelo.correo = correo
    modelo.password = "Prueba123"
    modelo.cod_rol = datos_usuario["cod_rol"]

    resultado = modelo.registrar()
    assert resultado == 1

    datos_usuario["usuarios_creados"].append(cedula)

    return cedula
# CP-USU-01 (prueba positiva: Registra correctamente un usuario)
def test_registrar(datos_usuario, usuario_registrado):
    modelo = datos_usuario["modelo"]
    cedula = usuario_registrado

    usuario = modelo.buscar(cedula)

    assert usuario is not None
    assert usuario["cedula"] == cedula
    assert usuario["nombre_usuario"] == "Usuario"
    assert usuario["apellido_usuario"] == "Prueba"
    assert usuario["telefono"] == "04141234567"
    assert usuario["direccion"] == "Barquisimeto"
    assert usuario["correo"] == f"usuario.{cedula}@test.com"
    assert usuario["cod_rol"] == datos_usuario["cod_rol"]
    assert usuario["status"] == 1
    assert usuario["intentos_fallidos"] == 0

    password_guardado = usuario["password"]
    if isinstance(password_guardado, str):
        password_guardado = password_guardado.encode("utf-8")

    assert bcrypt.checkpw(b"Prueba123", password_guardado)


# CP-USU-02 (prueba positiva: Consultar el usuario después de registrarlo)
def test_consultar_usuario_registrado(datos_usuario, usuario_registrado):
    modelo = datos_usuario["modelo"]
    cedula = usuario_registrado

    usuario = modelo.buscar(cedula)
    usuario_consultado = modelo.consultar_por_cedula(cedula)

    assert usuario is not None
    assert usuario_consultado is not None

    assert usuario["cedula"] == cedula
    assert usuario_consultado["cedula"] == cedula

    assert usuario["nombre_usuario"] == "Usuario"
    assert usuario_consultado["nombre_usuario"] == "Usuario"

    assert usuario["apellido_usuario"] == "Prueba"
    assert usuario_consultado["apellido_usuario"] == "Prueba"

    assert usuario["correo"] == f"usuario.{cedula}@test.com"
    assert usuario_consultado["correo"] == f"usuario.{cedula}@test.com"

    assert usuario["cod_rol"] == datos_usuario["cod_rol"]
    assert usuario_consultado["cod_rol"] == datos_usuario["cod_rol"]

# CP-USU-03 (prueba negativa: Registrar un usuario con una cédula ya existente)
def test_registrar_usuario_cedula_existente(datos_usuario, usuario_registrado):
    modelo = datos_usuario["modelo"]
    cedula = usuario_registrado

    modelo.cedula = cedula
    modelo.nombre_usuario = "Usuario"
    modelo.apellido_usuario = "Prueba"
    modelo.telefono = "04141234567"
    modelo.direccion = "Barquisimeto"
    modelo.correo = f"usuario.{cedula}@test.com"
    modelo.password = "Prueba123"
    modelo.cod_rol = datos_usuario["cod_rol"]

    assert modelo.registrar() is False

    usuario = modelo.buscar(cedula)

    assert usuario is not None
    assert usuario["cedula"] == cedula

# CP-USU-0 (prueba positiva: Edita correctamente los datos de un usuario)
def test_editar_usuario(datos_usuario, usuario_registrado):
    modelo = datos_usuario["modelo"]
    cedula = usuario_registrado

    usuario = modelo.buscar(cedula)
    assert usuario is not None

    password_original = usuario["password"]

    modelo.cedula = cedula
    modelo.nombre_usuario = "Alejandra"
    modelo.apellido_usuario = "Torres"
    modelo.telefono = "04125567890"
    modelo.direccion = "Barquisimeto, Centro"
    modelo.correo = f"alejandra.{cedula}@test.com"
    modelo.password = ""
    modelo.status = usuario["status"]
    modelo.cod_rol = usuario["cod_rol"]

    assert modelo.editar() is True

    usuario_editado = modelo.buscar(cedula)

    assert usuario_editado is not None
    assert usuario_editado["cedula"] == cedula
    assert usuario_editado["nombre_usuario"] == "Alejandra"
    assert usuario_editado["apellido_usuario"] == "Torres"
    assert usuario_editado["telefono"] == "04125567890"
    assert usuario_editado["direccion"] == "Barquisimeto, Centro"
    assert usuario_editado["correo"] == f"alejandra.{cedula}@test.com"
    assert usuario_editado["status"] == 1
    assert usuario_editado["cod_rol"] == datos_usuario["cod_rol"]
    assert usuario_editado["password"] == password_original

# CP-USU-0 (prueba positiva: Elimina un usuario que se encuentra inactivo)



# CP-USU-0 (prueba negativa: Rechaza la eliminación de un usuario que se encuentra activo)
def test_eliminar_usuario_activo():
    modelo = UsuariosModelo()

    try:
        cursor = modelo.conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT cedula
            FROM seguridad.usuario
            WHERE status = 1
              AND cod_rol IS NOT NULL
            ORDER BY cedula
            LIMIT 1
        """)
        usuario = cursor.fetchone()
        cursor.close()

        assert usuario is not None

        cedula = usuario["cedula"]

        usuario = modelo.buscar(cedula)
        assert usuario is not None
        assert usuario["status"] == 1

        resultado = modelo.eliminar(cedula)
        assert resultado == -2

        usuario_actual = modelo.buscar(cedula)
        assert usuario_actual["status"] == 1

    finally:
        modelo.conexion.close()


# CP-USU-0 (prueba negativa: Verificar que un usuario activo se conserve)
def test_conservar_usuario_activo(datos_usuario, usuario_registrado):
    modelo = datos_usuario["modelo"]
    cedula = usuario_registrado

    usuario_antes = modelo.buscar(cedula)
    assert usuario_antes["status"] == 1

    assert modelo.eliminar(cedula) == -2

    usuario_despues = modelo.buscar(cedula)

    assert usuario_despues is not None
    assert usuario_despues["cedula"] == cedula
    assert usuario_despues["status"] == 1