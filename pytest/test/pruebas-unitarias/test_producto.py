import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pytest

#python -m pytest .\Estudio-attelier\pytest\test\test_producto.py -q
#python -m pytest .\Estudio-attelier\pytest\test\test_producto.py::test_registrar_producto -vv
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.producto import ProductoModelo


@pytest.fixture
def modelo_producto(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(
        conexion_module.mysql.connector,
        "connect",
        lambda **kwargs: fake_conn,
    )
    return ProductoModelo()


def test_validar_nombre_producto_acepta_nombre_valido(modelo_producto):
    resultado = modelo_producto.validarNombreProducto("Crema facial 250 ml")

    assert resultado["status"] is True


def test_validar_nombre_producto_rechaza_nombre_vacio(modelo_producto):
    resultado = modelo_producto.validarNombreProducto("   ")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_nombre_producto_rechaza_caracteres_no_permitidos(modelo_producto):
    resultado = modelo_producto.validarNombreProducto("Crema@facial")

    assert resultado["status"] is False
    assert resultado["title"] == "Nombre inválido"


def test_validar_precio_acepta_precio_valido(modelo_producto):
    resultado = modelo_producto.validarPrecio("25.50")

    assert resultado["status"] is True


def test_validar_precio_rechaza_precio_vacio(modelo_producto):
    resultado = modelo_producto.validarPrecio("")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_precio_rechaza_formato_invalido(modelo_producto):
    resultado = modelo_producto.validarPrecio("25.555")

    assert resultado["status"] is False
    assert resultado["title"] == "Precio inválido"


def test_validar_precio_rechaza_cero(modelo_producto):
    resultado = modelo_producto.validarPrecio("0")

    assert resultado["status"] is False
    assert resultado["title"] == "Precio inválido"


def test_validar_stock_acepta_stock_valido(modelo_producto):
    resultado = modelo_producto.validarStock("25")

    assert resultado["status"] is True


def test_validar_stock_rechaza_stock_vacio(modelo_producto):
    resultado = modelo_producto.validarStock("")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_stock_rechaza_valores_no_numericos(modelo_producto):
    resultado = modelo_producto.validarStock("10.5")

    assert resultado["status"] is False
    assert resultado["title"] == "Stock inválido"


def test_validar_selects_acepta_codigos_seleccionados(modelo_producto):
    resultado = modelo_producto.validarSelects(1, 2, 3, 4, 5, 6)

    assert resultado["status"] is True


def test_validar_selects_rechaza_datos_requeridos_vacios(modelo_producto):
    resultado = modelo_producto.validarSelects(None, 2, 3, 4, 5, 6)

    assert resultado["status"] is False
    assert resultado["title"] == "Datos incompletos"


def test_validar_fecha_vencimiento_acepta_fecha_futura(modelo_producto):
    fecha = (datetime.now().date() + timedelta(days=1)).isoformat()

    resultado = modelo_producto.validarFechaVencimiento(fecha)

    assert resultado["status"] is True


def test_validar_fecha_vencimiento_rechaza_fecha_vacia(modelo_producto):
    resultado = modelo_producto.validarFechaVencimiento("")

    assert resultado["status"] is False
    assert resultado["title"] == "Fecha requerida"


def test_validar_fecha_vencimiento_rechaza_formato_invalido(modelo_producto):
    resultado = modelo_producto.validarFechaVencimiento("fecha-invalida")

    assert resultado["status"] is False
    assert resultado["title"] == "Fecha inválida"


def test_validar_fecha_vencimiento_rechaza_fecha_pasada(modelo_producto):
    fecha = (datetime.now().date() - timedelta(days=1)).isoformat()

    resultado = modelo_producto.validarFechaVencimiento(fecha)

    assert resultado["status"] is False
    assert resultado["title"] == "Fecha vencida"


def test_registrar_producto(modelo_producto):
    mock_cursor = modelo_producto.conexion.cursor.return_value
    mock_cursor.lastrowid = 21
    modelo_producto.nombre_producto = "Crema facial"
    modelo_producto.precio_producto = "25.50"
    modelo_producto.stock = "10"
    modelo_producto.cod_categoria = 1
    modelo_producto.cod_marca = 2
    modelo_producto.cod_unidad = 3
    modelo_producto.fecha_vencimiento = "2027-01-01"
    modelo_producto.cod_tipo_producto = 4

    resultado = modelo_producto.registrar()

    assert resultado == 1
    assert mock_cursor.execute.call_count == 2
    assert mock_cursor.execute.call_args_list[0].args[1] == (
        "Crema facial",
        "25.50",
        "10",
        1,
        2,
        3,
    )
    assert mock_cursor.execute.call_args_list[1].args[1] == (
        "2027-01-01",
        21,
        4,
    )
    modelo_producto.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_consultar_productos(modelo_producto):
    mock_cursor = modelo_producto.conexion.cursor.return_value
    productos = [{"cod_producto": 21, "nombre_producto": "Crema facial"}]
    mock_cursor.fetchall.return_value = productos

    resultado = modelo_producto.consultar()

    assert resultado == productos
    mock_cursor.execute.assert_called_once()
    assert "FROM producto p" in mock_cursor.execute.call_args.args[0]
    mock_cursor.close.assert_called_once()


def test_obtener_producto_por_codigo(modelo_producto):
    mock_cursor = modelo_producto.conexion.cursor.return_value
    producto = {"cod_producto": 21, "nombre_producto": "Crema facial"}
    mock_cursor.fetchone.return_value = producto

    resultado = modelo_producto.obtener(21)

    assert resultado == producto
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == (21,)
    mock_cursor.close.assert_called_once()


def test_buscar_producto_por_nombre(modelo_producto):
    mock_cursor = modelo_producto.conexion.cursor.return_value
    producto = {"cod_producto": 21, "nombre_producto": "Crema facial"}
    mock_cursor.fetchone.return_value = producto

    resultado = modelo_producto.buscar("Crema facial")

    assert resultado == producto
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == ("Crema facial",)
    mock_cursor.close.assert_called_once()


def test_buscar_producto_por_nombre_y_catalogos(modelo_producto):
    mock_cursor = modelo_producto.conexion.cursor.return_value
    producto = {"cod_producto": 21, "nombre_producto": "Crema facial"}
    mock_cursor.fetchone.return_value = producto

    resultado = modelo_producto.buscar("Crema facial", 1, 2, 4)

    assert resultado == producto
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == ("Crema facial", 1, 2, 4)
    mock_cursor.close.assert_called_once()


def test_editar_producto(modelo_producto):
    mock_cursor = modelo_producto.conexion.cursor.return_value
    modelo_producto.nombre_producto = "Crema actualizada"
    modelo_producto.precio_producto = "30.00"
    modelo_producto.cod_categoria = 1
    modelo_producto.cod_marca = 2
    modelo_producto.cod_unidad = 3
    modelo_producto.status = 1
    modelo_producto.fecha_vencimiento = "2027-02-01"
    modelo_producto.cod_tipo_producto = 4
    modelo_producto.cod_producto = 21

    resultado = modelo_producto.editar()

    assert resultado == 1
    assert mock_cursor.execute.call_count == 2
    assert mock_cursor.execute.call_args_list[0].args[1] == (
        "Crema actualizada",
        "30.00",
        1,
        2,
        3,
        1,
        21,
    )
    assert mock_cursor.execute.call_args_list[1].args[1] == (
        "2027-02-01",
        4,
        21,
    )
    modelo_producto.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_producto_sin_compras_asociadas(modelo_producto):
    mock_cursor = modelo_producto.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 0}

    resultado = modelo_producto.eliminar(21)

    assert resultado == "eliminado"
    assert mock_cursor.execute.call_count == 2
    assert mock_cursor.execute.call_args_list[0].args[1] == (21,)
    assert mock_cursor.execute.call_args_list[1].args[1] == (21,)
    modelo_producto.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_producto_con_compras_asociadas_no_lo_borra(modelo_producto):
    mock_cursor = modelo_producto.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 1}

    resultado = modelo_producto.eliminar(21)

    assert resultado == "existe_compra"
    mock_cursor.execute.assert_called_once()
    modelo_producto.conexion.commit.assert_not_called()
    mock_cursor.close.assert_called_once()