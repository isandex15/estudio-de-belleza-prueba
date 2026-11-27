import sys 
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.moneda import MonedaModelo

@pytest.fixture
def modelo_moneda(monkeypatch):
    fake_conn = MagicMock()
    monkeypatch.setattr(conexion_module.mysql.connector, "connect", lambda **kwargs: fake_conn)
    return MonedaModelo()

# CP-MON-01 (Prueba positiva de validación)
def test_validar_moneda_valida(modelo_moneda):
    resultado = modelo_moneda.validarMoneda("Dolar")

    assert resultado["status"] is True
    assert resultado["value"] == "Dolar"



# CP-MON-02 (prueba negativa: rechaza nombre vacío)
def test_validar_moneda_rechaza_nombre_vacio(modelo_moneda):
    resultado = modelo_moneda.validarMoneda("  ")

    assert resultado["status"] is False 
    assert resultado["icon"] == "warning"
    assert "obligatorio" in resultado["text"]



# CP-MON-03 (prueba negativa: rechaza caracteres especiales o números)
def test_validar_moneda_rechaza_caracteres_invalidos(modelo_moneda):
    resultado = modelo_moneda.validarMoneda("Dolar123*")

    assert resultado["status"] is False
    assert "no puede contener números ni caracteres especiales" in resultado["text"]


# CP-MON-04 (Prueba negativa: rechaza nombre que supera 15 caracteres)
def test_validar_moneda_rechaza_nombre_largo(modelo_moneda):
    resultado = modelo_moneda.validarMoneda("TransferenciaPlus")

    assert resultado["status"] is False
    assert resultado["title"] == "limite de caracteres alcanzado"


# CP-MON-05 (Prueba positiva de registro de moneda)
def test_registrar_moneda_valida(modelo_moneda):
    modelo_moneda.nombre_moneda = "Dolar"

    resultado = modelo_moneda.registrar()

    assert resultado == 1
    modelo_moneda.conexion.commit.assert_called_once()


# CP-MON-06 (Prueba negativa de registro de moneda)
def test_registrar_moneda_error(modelo_moneda):
    modelo_moneda.nombre_moneda = "Dolar"
    modelo_moneda.conexion.cursor.return_value.execute.side_effect = Exception(
        "fallo simulado"
    )

    resultado = modelo_moneda.registrar()

    assert resultado == 0
    modelo_moneda.conexion.commit.assert_not_called()


# CP-MON-07 (Prueba positiva de edición de moneda)
def test_editar_moneda_valida(modelo_moneda):
    modelo_moneda.cod_moneda = 1
    modelo_moneda.nombre_moneda = "Euro"
    modelo_moneda.status = 1

    resultado = modelo_moneda.editar()

    assert resultado == 1
    modelo_moneda.conexion.commit.assert_called_once()


# CP-MON-08 (Prueba negativa de edición de moneda)
def test_editar_moneda_error(modelo_moneda):
    modelo_moneda.cod_moneda = 1
    modelo_moneda.nombre_moneda = "Euro"
    modelo_moneda.status = 1
    modelo_moneda.conexion.cursor.return_value.execute.side_effect = Exception(
        "fallo simulado"
    )

    resultado = modelo_moneda.editar()

    assert resultado == 0
    modelo_moneda.conexion.commit.assert_not_called()


# CP-MON-09 (Prueba negativa de eliminación de moneda inexistente)
def test_eliminar_moneda_inexistente(modelo_moneda):
    modelo_moneda.conexion.cursor.return_value.fetchone.return_value = None

    resultado = modelo_moneda.eliminar(999)

    assert resultado == -2
    modelo_moneda.conexion.commit.assert_not_called()


# CP-MON-10 (Prueba negativa de eliminación de moneda asociada a pagos activos)
def test_eliminar_moneda_con_pago_activo(modelo_moneda):
    modelo_moneda.conexion.cursor.return_value.fetchone.side_effect = [
        (1,),
        (1,)
    ]

    resultado = modelo_moneda.eliminar(1)

    assert resultado == -2
    modelo_moneda.conexion.commit.assert_not_called()


# CP-MON-11 (Prueba positiva de eliminación física de moneda)
def test_eliminar_moneda_sin_asociaciones(modelo_moneda):
    cursor = modelo_moneda.conexion.cursor.return_value
    cursor.fetchone.side_effect = [(1,), (0,)]
    cursor.rowcount = 1

    resultado = modelo_moneda.eliminar(1)

    assert resultado == 1
    modelo_moneda.conexion.commit.assert_called_once()


# CP-MON-12 (Prueba positiva de eliminación lógica de moneda inactiva)
def test_eliminar_moneda_inactiva(modelo_moneda):
    cursor = modelo_moneda.conexion.cursor.return_value
    cursor.fetchone.side_effect = [(0,), (0,)]
    cursor.rowcount = 1

    resultado = modelo_moneda.eliminar(1)

    assert resultado == 1
    modelo_moneda.conexion.commit.assert_called_once()


# CP-MON-13 (Prueba positiva de actualización de tasas con nombres acentuados)
def test_actualizar_tasas_automaticas_reconoce_monedas(modelo_moneda):
    monedas = [
        {"cod_moneda": 1, "nombre_moneda": "Dólar"},
        {"cod_moneda": 2, "nombre_moneda": "Euro"},
        {"cod_moneda": 3, "nombre_moneda": "USDT"},
    ]
    cursor_catalogo = MagicMock()
    cursor_catalogo.fetchall.return_value = monedas
    cursores_cambio = [MagicMock() for _ in monedas]
    for cursor in cursores_cambio:
        cursor.fetchone.return_value = None
    modelo_moneda.conexion.cursor.side_effect = [
        cursor_catalogo,
        *cursores_cambio
    ]

    resultado = modelo_moneda.actualizar_tasas_automaticas(
        tasa_bcv=100,
        tasa_usdt_ves=120,
        tasa_euro_usd=1.1
    )

    assert resultado == 3
    valores_guardados = [
        cursor.execute.call_args_list[1][0][1][0]
        for cursor in cursores_cambio
    ]
    assert valores_guardados == pytest.approx([100, 110, 120])


# CP-MON-14 (Prueba negativa: no guarda tasas estimadas sin fuente disponible)
def test_actualizar_tasas_automaticas_omite_euro_y_usdt_sin_fuente(modelo_moneda):
    cursor_catalogo = MagicMock()
    cursor_catalogo.fetchall.return_value = [
        {"cod_moneda": 2, "nombre_moneda": "Euro"},
        {"cod_moneda": 3, "nombre_moneda": "USDT"},
    ]
    modelo_moneda.conexion.cursor.return_value = cursor_catalogo

    resultado = modelo_moneda.actualizar_tasas_automaticas(
        tasa_bcv=100,
        tasa_usdt_ves=0,
        tasa_usdt_binance=0,
        tasa_paralelo=0,
        tasa_euro_usd=0
    )

    assert resultado == 0
    modelo_moneda.conexion.cursor.assert_called_once_with(dictionary=True)
    modelo_moneda.conexion.commit.assert_not_called()