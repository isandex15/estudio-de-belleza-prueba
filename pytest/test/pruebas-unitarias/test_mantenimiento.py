import sys 
from pathlib import Path
from unittest.mock import MagicMock

import pytest 

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.config.config import DB_SEGURIDAD_NAME
from admin.modelo.mantenimiento import MantenimientoModelo

@pytest.fixture
def modelo_mantenimiento(monkeypatch):
    fake_conn = MagicMock()
    monkeypatch.setattr(conexion_module.mysql.connector, "connect", lambda **kwargs: fake_conn)
    return MantenimientoModelo()


#CP-MAN-01 (Prueba positiva de validación de nombre de archivo)
def test_validar_nombre_archivo_valido(modelo_mantenimiento):
    resultado = modelo_mantenimiento.validarNombreArchivo("respaldo_2026.sql.txt")
    assert resultado["status"] is True


#CP-MAN-02 (Prueba negativa de validación de nombre de archivo)
def test_validar_nombre_archivo_invalido(modelo_mantenimiento):
    resultado = modelo_mantenimiento.validarNombreArchivo("script.exe")
    assert resultado["status"] is False
    assert resultado["title"] == "Dato inválido"


#CP-MAN-03 (Prueba positiva de validación de tamaño)
def test_validar_tamano_valido(modelo_mantenimiento):
    resultado = modelo_mantenimiento.validarTamano(1024)
    assert resultado["status"] is True
    assert resultado["value"] == 1024


#CP-MAN-04 (Prueba negativa de validación de tamaño)
def test_validar_tamano_invalido(modelo_mantenimiento):
    resultado = modelo_mantenimiento.validarTamano(0)
    assert resultado["status"] is False
    assert "Tamaño inválido" in resultado["text"]


#CP-MAN-05 (Prueba positiva de validación de fecha)
def test_validar_fecha_valida(modelo_mantenimiento):
    resultado = modelo_mantenimiento.validarFecha("2026-05-22")
    assert resultado["status"] is True
    assert resultado["value"] == "2026-05-22"


#CP-MAN-06 (Prueba negativa de validación de fecha)
def test_validar_fecha_invalida(modelo_mantenimiento):
    resultado = modelo_mantenimiento.validarFecha("2026-13-40")
    assert resultado["status"] is False
    assert "Fecha inválida" in resultado["text"]


#CP-MAN-07 (Prueba positiva de registro de mantenimiento)
def test_registrar_mantenimiento_valido(modelo_mantenimiento):
    modelo_mantenimiento.nombre_archivo = "respaldo_2026.sql.txt"
    modelo_mantenimiento.tamano = 1024
    modelo_mantenimiento.fecha = "2026-05-22"
    modelo_mantenimiento.hora = "14:30:00"
    modelo_mantenimiento.cedula_usuario = "123456789"

    resultado = modelo_mantenimiento.registrar()

    assert resultado is True
    modelo_mantenimiento.conexion.commit.assert_called_once()


#CP-MAN-08 (Prueba negativa de registro de mantenimiento)
def test_registrar_mantenimiento_invalido(modelo_mantenimiento):
    modelo_mantenimiento.nombre_archivo = "respaldo_2026.sql.txt"
    modelo_mantenimiento.tamano = 1024
    modelo_mantenimiento.fecha = "2026-05-22"
    modelo_mantenimiento.hora = "14:30:00"
    modelo_mantenimiento.cedula_usuario = "123456789"
    cursor = modelo_mantenimiento.conexion.cursor.return_value
    cursor.callproc.side_effect = Exception("fallo simulado")
    cursor.execute.side_effect = Exception("fallo simulado")

    resultado = modelo_mantenimiento.registrar()

    assert resultado is False
    modelo_mantenimiento.conexion.rollback.assert_called_once()


#CP-MAN-09 (Prueba positiva de eliminación de mantenimiento)
def test_eliminar_mantenimiento_existente(modelo_mantenimiento):
    cursor = modelo_mantenimiento.conexion.cursor.return_value
    cursor.rowcount = 1

    resultado = modelo_mantenimiento.eliminar(1)

    assert resultado is True
    cursor.execute.assert_called_once_with(
        f"DELETE FROM {DB_SEGURIDAD_NAME}.mantenimiento WHERE cod_mantenimiento = %s",
        (1,)
    )
    modelo_mantenimiento.conexion.commit.assert_called_once()


#CP-MAN-10 (Prueba negativa de eliminación de mantenimiento inexistente)
def test_eliminar_mantenimiento_inexistente(modelo_mantenimiento):
    cursor = modelo_mantenimiento.conexion.cursor.return_value
    cursor.rowcount = 0

    resultado = modelo_mantenimiento.eliminar(999)

    assert resultado is False
    modelo_mantenimiento.conexion.commit.assert_called_once()


#CP-MAN-11 (Prueba de error al eliminar mantenimiento)
def test_eliminar_mantenimiento_error(modelo_mantenimiento):
    cursor = modelo_mantenimiento.conexion.cursor.return_value
    cursor.execute.side_effect = Exception("fallo simulado")

    resultado = modelo_mantenimiento.eliminar(1)

    assert resultado is False
    modelo_mantenimiento.conexion.rollback.assert_called_once()
