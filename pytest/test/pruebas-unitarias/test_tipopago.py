import sys 
from pathlib import Path 
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.tipopagos import TipopagosModelo

@pytest.fixture
def modelo_tipopagos(monkeypatch):
    fake_conn = MagicMock()
    monkeypatch.setattr(conexion_module.mysql.connector, "connect", lambda **kwargs: fake_conn)
    return TipopagosModelo()


# CP-TP-01 (Prueba positiva de validación)
def test_validar_tipo_pago_valido(modelo_tipopagos):
    resultado = modelo_tipopagos.validarTipoPago("Divisas")

    assert resultado["status"] is True


# CP-TP-02 (prueba negativa: rechaza nombre vacío)
def test_validar_tipo_pago_rechaza_nombre_vacio(modelo_tipopagos):
    resultado = modelo_tipopagos.validarTipoPago("  ")

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "obligatorio" in resultado["text"]

# CP-TP-03 (prueba negativa: rechaza caracteres especiales o números)
def test_validar_tipo_pago_rechaza_caracteres_invalidos(modelo_tipopagos):
    resultado = modelo_tipopagos.validarTipoPago("Pago123*")

    assert resultado["status"] is False
    assert "no puede contener números ni caracteres especiales" in resultado["text"]


# CP-TP-04 (prueba negativa: rechaza nombres que superan 15 caracteres)
def test_validar_tipo_pago_rechaza_nombre_largo(modelo_tipopagos):
    resultado = modelo_tipopagos.validarTipoPago("TransferenciaPlus")

    assert resultado["status"] is False
    assert resultado["title"] == "limite de caracteres alcanzado"


# CP-TP-05 (prueba positiva de registro de tipo de pago)
def test_registrar_tipo_pago_valido(modelo_tipopagos):
    modelo_tipopagos.nombre_tipo_pago = "Divisas"

    resultado = modelo_tipopagos.registrar()

    assert resultado == 1
    modelo_tipopagos.conexion.commit.assert_called_once()


# CP-TP-06 (prueba negativa de registro de tipo de pago)
def test_registrar_tipo_pago_error(modelo_tipopagos):
    modelo_tipopagos.nombre_tipo_pago = "Divisas"
    modelo_tipopagos.conexion.cursor.return_value.execute.side_effect = Exception(
        "fallo simulado"
    )

    resultado = modelo_tipopagos.registrar()

    assert resultado == 0
    modelo_tipopagos.conexion.commit.assert_not_called()


# CP-TP-07 (prueba positiva de edición de tipo de pago)
def test_editar_tipo_pago_valido(modelo_tipopagos):
    modelo_tipopagos.cod_tipo_pago = 1
    modelo_tipopagos.nombre_tipo_pago = "Transferencia"
    modelo_tipopagos.status = 1

    resultado = modelo_tipopagos.editar()

    assert resultado == 1
    modelo_tipopagos.conexion.commit.assert_called_once()


# CP-TP-08 (prueba negativa de edición de tipo de pago)
def test_editar_tipo_pago_error(modelo_tipopagos):
    modelo_tipopagos.cod_tipo_pago = 1
    modelo_tipopagos.nombre_tipo_pago = "Transferencia"
    modelo_tipopagos.status = 1
    modelo_tipopagos.conexion.cursor.return_value.execute.side_effect = Exception(
        "fallo simulado"
    )

    resultado = modelo_tipopagos.editar()

    assert resultado == 0
    modelo_tipopagos.conexion.commit.assert_not_called()


# CP-TP-09 (prueba negativa: no elimina tipo de pago inexistente)
def test_eliminar_tipo_pago_inexistente(modelo_tipopagos):
    modelo_tipopagos.conexion.cursor.return_value.fetchone.return_value = None

    resultado = modelo_tipopagos.eliminar(999)

    assert resultado == -2
    modelo_tipopagos.conexion.commit.assert_not_called()


# CP-TP-10 (prueba negativa: no elimina tipo de pago asociado a pagos activos)
def test_eliminar_tipo_pago_con_pago_activo(modelo_tipopagos):
    modelo_tipopagos.conexion.cursor.return_value.fetchone.side_effect = [
        (1,),
        (1,)
    ]

    resultado = modelo_tipopagos.eliminar(1)

    assert resultado == -2
    modelo_tipopagos.conexion.commit.assert_not_called()


# CP-TP-11 (prueba positiva de eliminación física de tipo de pago)
def test_eliminar_tipo_pago_sin_asociaciones(modelo_tipopagos):
    cursor = modelo_tipopagos.conexion.cursor.return_value
    cursor.fetchone.side_effect = [(1,), (0,)]
    cursor.rowcount = 1

    resultado = modelo_tipopagos.eliminar(1)

    assert resultado == 1
    modelo_tipopagos.conexion.commit.assert_called_once()


# CP-TP-12 (prueba positiva de eliminación lógica de tipo de pago inactivo)
def test_eliminar_tipo_pago_inactivo(modelo_tipopagos):
    cursor = modelo_tipopagos.conexion.cursor.return_value
    cursor.fetchone.side_effect = [(0,), (0,)]
    cursor.rowcount = 1

    resultado = modelo_tipopagos.eliminar(1)

    assert resultado == 1
    modelo_tipopagos.conexion.commit.assert_called_once()
