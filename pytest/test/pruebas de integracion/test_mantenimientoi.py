from datetime import date, datetime
import secrets

import pytest

from admin.config.config import DB_SEGURIDAD_NAME
from admin.modelo.mantenimiento import MantenimientoModelo


@pytest.fixture
def datos_mantenimiento(ready_test_database):
    modelo = MantenimientoModelo()
    cursor = modelo.conexion.cursor()
    cursor.execute(
        f"""
        SELECT cedula
        FROM {DB_SEGURIDAD_NAME}.usuario
        WHERE status = 1
        ORDER BY cedula
        LIMIT 1
        """
    )
    usuario = cursor.fetchone()
    cursor.close()
    modelo.conexion.commit()

    if not usuario:
        modelo.conexion.close()
        pytest.fail(
            "Se requiere al menos un usuario activo para la prueba de mantenimiento."
        )

    datos = {
        "modelo": modelo,
        "cedula": usuario[0],
        "archivo": f"integracion_{secrets.token_hex(8)}.txt",
    }

    try:
        yield datos
    finally:
        cursor = modelo.conexion.cursor()
        cursor.execute(
            f"DELETE FROM {DB_SEGURIDAD_NAME}.mantenimiento WHERE nombre_archivo = %s",
            (datos["archivo"],),
        )
        modelo.conexion.commit()
        cursor.close()
        modelo.conexion.close()


@pytest.fixture
def mantenimiento_registrado(datos_mantenimiento):
    modelo = datos_mantenimiento["modelo"]
    modelo.nombre_archivo = datos_mantenimiento["archivo"]
    modelo.tamano = "128"
    modelo.fecha = date.today().isoformat()
    modelo.hora = datetime.now().strftime("%H:%M:%S")
    modelo.cedula_usuario = datos_mantenimiento["cedula"]

    assert modelo.validarMantenimiento()["status"] is True
    assert modelo.registrar() is True
    cursor = modelo.conexion.cursor(dictionary=True)
    cursor.execute(
        f"""
        SELECT cod_mantenimiento, nombre_archivo, tamano, cedula_usuario
        FROM {DB_SEGURIDAD_NAME}.mantenimiento
        WHERE nombre_archivo = %s
        """,
        (datos_mantenimiento["archivo"],),
    )
    mantenimiento = cursor.fetchone()
    cursor.close()
    assert mantenimiento is not None
    datos_mantenimiento["mantenimiento"] = mantenimiento
    return datos_mantenimiento


# CP-MAN-12 (Prueba positiva de registro de mantenimiento)
def test_registrar_mantenimiento(mantenimiento_registrado):
    datos = mantenimiento_registrado
    mantenimiento = datos["mantenimiento"]
    assert int(mantenimiento["tamano"]) == 128
    assert mantenimiento["cedula_usuario"] == datos["cedula"]


# CP-MAN-13 (Prueba positiva de consulta de mantenimiento)
def test_consultar_mantenimiento(mantenimiento_registrado):
    datos = mantenimiento_registrado
    modelo = datos["modelo"]
    mantenimiento = datos["mantenimiento"]
    assert any(
        fila["cod_mantenimiento"] == mantenimiento["cod_mantenimiento"]
        for fila in modelo.consultar()
    )


# CP-MAN-14 (Prueba positiva de eliminación de mantenimiento)
def test_eliminar_mantenimiento(mantenimiento_registrado):
    datos = mantenimiento_registrado
    modelo = datos["modelo"]
    cod_mantenimiento = datos["mantenimiento"]["cod_mantenimiento"]

    modelo.conexion.commit()
    assert modelo.eliminar(cod_mantenimiento) is True

    cursor = modelo.conexion.cursor()
    cursor.execute(
        f"SELECT COUNT(*) FROM {DB_SEGURIDAD_NAME}.mantenimiento "
        "WHERE cod_mantenimiento = %s",
        (cod_mantenimiento,),
    )
    assert cursor.fetchone()[0] == 0
    cursor.close()


# CP-MAN-15 (Prueba negativa: rechaza eliminar un mantenimiento inexistente)
def test_rechazar_eliminacion_mantenimiento_inexistente(datos_mantenimiento):
    modelo = datos_mantenimiento["modelo"]
    cursor = modelo.conexion.cursor()
    cursor.execute(
        f"SELECT COALESCE(MAX(cod_mantenimiento), 0) + 1 "
        f"FROM {DB_SEGURIDAD_NAME}.mantenimiento"
    )
    cod_inexistente = cursor.fetchone()[0]
    cursor.close()

    assert modelo.eliminar(cod_inexistente) is False
