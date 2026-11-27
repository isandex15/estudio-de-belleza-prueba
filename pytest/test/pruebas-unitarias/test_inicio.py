import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# CP-RES-01: python -m pytest ".\pytest\test\puebas unitarias\test_inicio.py::test_registrar_reserva_sin_servicios" -vv
# CP-RES-02: python -m pytest ".\pytest\test\puebas unitarias\test_inicio.py::test_registrar_reserva_sin_productos" -vv
# CP-RES-03: python -m pytest ".\pytest\test\puebas unitarias\test_inicio.py::test_registrar_reserva_sin_especialista" -vv
# CP-RES-04: python -m pytest ".\pytest\test\puebas unitarias\test_inicio.py::test_registrar_reserva_sin_cliente" -vv
# CP-RES-05: python -m pytest ".\pytest\test\puebas unitarias\test_inicio.py::test_cancelar_reserva_activa" -vv
# CP-INI-06: python -m pytest ".\pytest\test\puebas unitarias\test_inicio.py::test_registrar_reserva_sin_codigo_conteo" -q
# CP-INI-07: python -m pytest ".\pytest\test\puebas unitarias\test_inicio.py::test_registrar_reserva_varios_productos_sin_codigo_conteo" -q

# Ejecutar todas las pruebas del archivo:
# python -m pytest ".\pytest\test\puebas unitarias\test_inicio.py" -vv

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.inicio import InicioModelo


@pytest.fixture
def modelo_inicio(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(conexion_module.mysql.connector, "connect", lambda **kwargs: fake_conn)
    return InicioModelo()


# CP-RES-0 unitaria -  registrar una reserva sin servicios
def test_registrar_reserva_sin_servicios(monkeypatch, modelo_inicio):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.callproc.side_effect = Exception(
        "Debe seleccionar al menos un tipo de servicio."
    )
    monkeypatch.setattr(modelo_inicio, "conexion", mock_conn)

    resultado = modelo_inicio.registrarReserva(
        "3196486", [], "2026-11-08", "11:00 AM", "3123446"
    )

    assert resultado["success"] is False
    assert resultado["message"] == "Debe seleccionar al menos un tipo de servicio."


# CP-RES-0 unitaria- registrar una reserva sin productos
def test_registrar_reserva_sin_productos(monkeypatch, modelo_inicio):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.callproc.side_effect = Exception(
        "Debe seleccionar productos."
    )
    monkeypatch.setattr(modelo_inicio, "conexion", mock_conn)

    resultado = modelo_inicio.registrarReserva(
        "3196486", [1], "2026-11-08", "10:00 AM", "3123446"
    )

    assert resultado["success"] is False
    assert resultado["message"] == "Debe seleccionar productos."


# CP-RES-0 unitaria - Registrar una reserva sin cliente
def test_registrar_reserva_sin_cliente(monkeypatch, modelo_inicio):
    modelo_inicio.conexion.cursor().callproc.side_effect = Exception(
        "Debe ingresar la cedula de un cliente existente."
    )

    resultado = modelo_inicio.registrarReserva(
        "", [1], "2026-11-08", "10:00 AM", "3123446",
        cod_productos=[{"cod_producto": 1, "cantidad": 1}]
    )

    assert resultado["success"] is False
    assert resultado["message"] == "Debe ingresar la cedula de un cliente existente."


# CP-RES-0 unitaria - Registrar una reserva sin especialista
def test_registrar_reserva_sin_especialista(monkeypatch, modelo_inicio):
    modelo_inicio.conexion.cursor().callproc.side_effect = Exception(
        "Debe seleccionar un especialista existente."
    )

    resultado = modelo_inicio.registrarReserva(
        "3196486", [1], "2026-11-08", "10:00 AM", "",
        cod_productos=[{"cod_producto": 1, "cantidad": 1}]
    )

    assert resultado["success"] is False
    assert resultado["message"] == "Debe seleccionar un especialista existente."



# CP-INI-0 unitaria - Registrar una reserva con un producto sin código de conteo
def test_registrar_reserva_sin_codigo_conteo(monkeypatch, modelo_inicio):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr(modelo_inicio, "conexion", mock_conn)

    mock_resultado = MagicMock()
    mock_resultado.fetchone.return_value = (
        78, "Carolina", "González", "Especialista", "2026-11-08", "10:00 AM"
    )
    mock_cursor.stored_results.return_value = [mock_resultado]
    mock_cursor.fetchall.return_value = []

    resultado = modelo_inicio.registrarReserva(
        "3196486", [1], "2026-11-08", "10:00 AM", "3123446",
        cod_productos=[{"cod_producto": 1, "cantidad": 1}]
    )

    assert resultado["success"] is False
    assert resultado["message"] == "No existe un cod_conteo para el producto 1"
    mock_conn.rollback.assert_called_once()



# CP-INI-0 unitaria - Registrar una reserva con varios productos y falta el código de conteo de uno
def test_registrar_reserva_varios_productos_sin_codigo_conteo(monkeypatch, modelo_inicio):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr(modelo_inicio, "conexion", mock_conn)

    mock_resultado = MagicMock()
    mock_resultado.fetchone.return_value = (
        78, "Carolina", "González", "Especialista", "2026-11-08", "10:00 AM"
    )
    mock_cursor.stored_results.return_value = [mock_resultado]
    mock_cursor.fetchall.return_value = [(1, 15)]

    resultado = modelo_inicio.registrarReserva(
        "3196486", [1], "2026-11-08", "10:00 AM", "3123446",
        cod_productos=[
            {"cod_producto": 1, "cantidad": 1},
            {"cod_producto": 2, "cantidad": 2}
        ]
    )

    assert resultado["success"] is False
    assert resultado["message"] == "No existe un cod_conteo para el producto 2"
    mock_conn.rollback.assert_called_once()



# CP-RES-0 unitaria - Cancelar correctamente una reserva activa
def test_cancelar_reserva_activa(monkeypatch, modelo_inicio):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    monkeypatch.setattr(modelo_inicio, "conexion", mock_conn)

    mock_cursor.fetchone.return_value = {
        "fecha": "2026-11-08",
        "hora": "10:00 AM",
        "cedula_especialista": "3123446",
        "status": 1
    }

    resultado = modelo_inicio.sp_Cancelar_Reserva(78)

    assert resultado == "cancelado"


# CP-INI-08 (prueba positiva: acepta una fecha de reserva no vacía)
def test_validar_reserva_acepta_fecha_no_vacia(modelo_inicio):
    resultado = modelo_inicio.validarReserva(
        "3196486", [1], "2026-11-25", "10:00 AM", "3123446"
    )

    assert resultado["status"] is True


# CP-INI-09 (prueba positiva: acepta una hora de reserva no vacía)
def test_validar_reserva_acepta_hora_no_vacia(modelo_inicio):
    resultado = modelo_inicio.validarReserva(
        "3196486", [1], "2026-11-25", "10:00 AM", "3123446"
    )

    assert resultado["status"] is True


# CP-INI-10 (prueba positiva: acepta una cantidad de producto igual a uno)
def test_validar_reserva_acepta_cantidad_producto_igual_a_uno(modelo_inicio):
    resultado = modelo_inicio.validarReserva(
        "3196486", [1], "2026-11-25", "10:00 AM", "3123446",
        cod_productos=[{"cod_producto": 1, "cantidad": 1}]
    )

    assert resultado["status"] is True


# CP-INI-11 (prueba positiva: acepta una reserva con varios servicios)
def test_validar_reserva_acepta_reserva_con_varios_servicios(modelo_inicio):
    resultado = modelo_inicio.validarReserva(
        "3196486", [1, 2, 3], "2026-11-25", "10:00 AM", "3123446"
    )

    assert resultado["status"] is True


# CP-INI-12 (prueba positiva: acepta cédulas que contienen solo números)
def test_validar_reserva_acepta_cedulas_numericas_validas(modelo_inicio):
    resultado = modelo_inicio.validarReserva(
        "3196486", [1], "2026-11-25", "10:00 AM", "3123446"
    )

    assert resultado["status"] is True    