import secrets

import pytest

from admin.config.config import DB_SEGURIDAD_NAME
from admin.modelo.personal import PersonalModelo


@pytest.fixture
def datos_personal(ready_test_database):
    modelo = PersonalModelo()
    cursor = modelo.conexion.cursor()
    cursor.execute(
        f"""
        SELECT cod_rol
        FROM {DB_SEGURIDAD_NAME}.rol
        WHERE status = 1
          AND LOWER(rol) IN ('gerente', 'empleado')
        ORDER BY cod_rol
        LIMIT 1
        """
    )
    rol = cursor.fetchone()
    cursor.close()

    if not rol:
        modelo.conexion.close()
        pytest.fail(
            "Se requiere un rol gerente o empleado activo para la prueba de personal."
        )

    datos = {
        "modelo": modelo,
        "cedula": "IT" + secrets.token_hex(5).upper(),
        "correo": f"it_{secrets.token_hex(5)}@gmail.com",
        "cod_rol": rol[0],
    }

    try:
        yield datos
    finally:
        cursor = modelo.conexion.cursor()
        cursor.execute(
            f"DELETE FROM {DB_SEGURIDAD_NAME}.usuario WHERE cedula = %s",
            (datos["cedula"],),
        )
        modelo.conexion.commit()
        cursor.close()
        modelo.conexion.close()


@pytest.fixture
def personal_registrado(datos_personal):
    modelo = datos_personal["modelo"]
    modelo.cedula = datos_personal["cedula"]
    modelo.nombre_usuario = "Integracion"
    modelo.apellido_usuario = "Temporal"
    modelo.telefono = "5550101"
    modelo.direccion = "Direccion de prueba"
    modelo.correo = datos_personal["correo"]
    modelo.cod_rol = datos_personal["cod_rol"]
    modelo.password = "PruebaIntegracion123"

    assert modelo.registrar() == 1
    personal = modelo.buscar(datos_personal["cedula"])
    assert personal is not None
    assert personal["status"] == 1
    return datos_personal


# CP-PER-23 (Prueba positiva de registro de personal)
def test_registrar_personal(personal_registrado):
    datos = personal_registrado
    personal = datos["modelo"].buscar(datos["cedula"])
    assert personal is not None
    assert personal["status"] == 1


# CP-PER-24 (Prueba positiva de edición de personal)
def test_editar_personal(personal_registrado):
    datos = personal_registrado
    modelo = datos["modelo"]
    modelo.nombre_usuario = "Editado"
    modelo.status = 1
    assert modelo.editar() == 1
    assert modelo.buscar(datos["cedula"])["nombre_usuario"] == "Editado"


# CP-PER-25 (Prueba positiva de consulta de personal)
def test_consultar_personal(personal_registrado):
    datos = personal_registrado
    modelo = datos["modelo"]
    assert any(
        fila["cedula"] == datos["cedula"]
        for fila in modelo.consultar()
    )


# CP-PER-26 (Prueba positiva de eliminación de personal)
def test_eliminar_personal(personal_registrado):
    datos = personal_registrado
    modelo = datos["modelo"]
    assert modelo.eliminar(datos["cedula"]) == 1
    assert modelo.buscar(datos["cedula"])["status"] == 2


# CP-PER-27 (Prueba negativa: rechaza registrar una cédula ya existente)
def test_rechazar_registro_personal_duplicado(personal_registrado):
    datos = personal_registrado
    modelo = datos["modelo"]

    assert modelo.registrar() is False
    personal = modelo.buscar(datos["cedula"])
    assert personal is not None
    assert personal["status"] == 1
