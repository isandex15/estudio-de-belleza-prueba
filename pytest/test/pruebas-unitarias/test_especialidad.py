
import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.especialidad import EspecialidadModelo

# python -m pytest ".\pytest\test\puebas unitarias\test_especialidad.py::test_validar_especialidad_rechaza_cedula_vacia" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_especialidad.py::test_validar_especialidad_rechaza_especialidad_vacia" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_especialidad.py::test_validar_especialidad_acepta_datos_validos" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_especialidad.py::test_validar_especialidad_rechaza_especialidad_con_espacios" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_especialidad.py::test_validar_especialidad_rechaza_cedula_con_espacios" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_especialidad.py::test_editar_especialista_correctamente" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_especialidad.py::test_eliminar_especialista_con_reservas_activas" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_especialidad.py::test_eliminar_especialista_sin_reservas" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_especialidad.py" -q

@pytest.fixture
def modelo_especialidad(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(
        conexion_module.mysql.connector,
        "connect",
        lambda **kwargs: fake_conn
    )
    return EspecialidadModelo()

# CP-ESP-01 (prueba negativa: rechaza registrar una especialidad cuando la cédula está vacía)
def test_validar_especialidad_rechaza_cedula_vacia(modelo_especialidad):
    resultado = modelo_especialidad.validarEspecialidad("Estilista", "")

    assert resultado["status"] is False
    assert "Debe seleccionar la cédula del personal" in resultado["text"]


# CP-ESP-02 (prueba negativa: rechaza registrar una especialidad cuando el nombre está vacío)
def test_validar_especialidad_rechaza_especialidad_vacia(modelo_especialidad):
    resultado = modelo_especialidad.validarEspecialidad("", "12345678")

    assert resultado["status"] is False
    assert "Debe seleccionar una especialidad" in resultado["text"]


# CP-ESP-03 (prueba positiva: acepta registrar una especialidad cuando los datos son válidos)
def test_validar_especialidad_acepta_datos_validos(modelo_especialidad):
    resultado = modelo_especialidad.validarEspecialidad("Estilista", "12345678")

    assert resultado["status"] is True


# CP-ESP-04 (prueba negativa: rechaza registrar una especialidad cuando el nombre contiene solo espacios)
def test_validar_especialidad_rechaza_especialidad_con_espacios(modelo_especialidad):
    resultado = modelo_especialidad.validarEspecialidad("   ", "12345678")

    assert resultado["status"] is False
    assert "Debe seleccionar una especialidad" in resultado["text"]


# CP-ESP-05 (prueba negativa: rechaza registrar una especialidad cuando la cédula contiene solo espacios)
def test_validar_especialidad_rechaza_cedula_con_espacios(modelo_especialidad):
    resultado = modelo_especialidad.validarEspecialidad("Estilista", "   ")

    assert resultado["status"] is False
    assert "Debe seleccionar la cédula del personal" in resultado["text"]



# CP-ESP-06 (prueba positiva: edita correctamente la especialidad de un especialista)
def test_editar_especialista_correctamente(modelo_especialidad):
    modelo_especialidad.especialista = "Colorista"
    modelo_especialidad.cedula = "12345678"
    modelo_especialidad.status = 1

    resultado = modelo_especialidad.editar()

    assert resultado == 1
    modelo_especialidad.conexion.commit.assert_called_once()


# CP-ESP-07 (prueba negativa: impide eliminar un especialista que tiene reservas activas)
def test_eliminar_especialista_con_reservas_activas(modelo_especialidad):
    mock_cursor = modelo_especialidad.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {
        "reservas": 2,
        "reservas_activas": 1
    }

    resultado = modelo_especialidad.eliminar("12345678")

    assert resultado == "tiene_reservas"
    modelo_especialidad.conexion.commit.assert_not_called()


# CP-ESP-08 (prueba positiva: elimina físicamente un especialista que no tiene reservas)
def test_eliminar_especialista_sin_reservas(modelo_especialidad):
    mock_cursor = modelo_especialidad.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {
        "reservas": 0,
        "reservas_activas": 0
    }
    mock_cursor.rowcount = 1

    resultado = modelo_especialidad.eliminar("12345678")

    assert resultado == "eliminado_fisico"
    modelo_especialidad.conexion.commit.assert_called_once()
