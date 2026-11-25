
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

#python -m pytest .\Estudio-attelier\pytest\test\test_compra.py::test_validar_total_rechaza_cero -vv
#python -m pytest .\Estudio-attelier\pytest\test\test_compra.py -q
#python -m pytest .\Estudio-attelier\pytest\test\test_compra.py::test_validar_total_rechaza_cero -vv
#python -m pytest .\Estudio-attelier\pytest\test\test_compra.py::test_editar_compra_actualiza_compra_detalle_y_stock -vv
#python -m pytest .\Estudio-attelier\pytest\test\test_compra.py::test_eliminar_compra -vv
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.compra import CompraModelo


@pytest.fixture
def modelo_compra(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(conexion_module.mysql.connector, "connect", lambda **kwargs: fake_conn)
    return CompraModelo()


def test_validar_total_rechaza_cero(modelo_compra):
    resultado = modelo_compra.validarTotal("0")

    assert resultado["status"] is False
    assert resultado["title"] == "Total inválido"


def test_validar_fecha_compra_acepta_fecha_valida(modelo_compra):
    resultado = modelo_compra.validarFechaCompra("2026-10-27")

    assert resultado["status"] is True


def test_validar_fecha_compra_rechaza_fecha_invalida(modelo_compra):
    resultado = modelo_compra.validarFechaCompra("fecha-invalida")

    assert resultado["status"] is False
    assert resultado["title"] == "Fecha inválida"


def test_validar_fecha_compra_rechaza_fecha_vacia(modelo_compra):
    resultado = modelo_compra.validarFechaCompra("")

    assert resultado["status"] is False
    assert resultado["title"] == "Fecha requerida"


def test_validar_proveedor_acepta_codigo_valido(modelo_compra):
    resultado = modelo_compra.validarProveedor("5")

    assert resultado["status"] is True


def test_validar_proveedor_rechaza_codigo_invalido(modelo_compra):
    resultado = modelo_compra.validarProveedor("proveedor-invalido")

    assert resultado["status"] is False
    assert resultado["title"] == "Proveedor inválido"


def test_validar_proveedor_rechaza_codigo_vacio(modelo_compra):
    resultado = modelo_compra.validarProveedor("")

    assert resultado["status"] is False
    assert resultado["title"] == "Proveedor requerido"


def test_validar_total_rechaza_valor_no_numerico(modelo_compra):
    resultado = modelo_compra.validarTotal("total-invalido")

    assert resultado["status"] is False
    assert resultado["title"] == "Total inválido"


def test_validar_total_acepta_valor_positivo(modelo_compra):
    resultado = modelo_compra.validarTotal("22.50")

    assert resultado["status"] is True


def test_validar_productos_rechaza_cantidad_invalida(modelo_compra):
    productos = [{"cod_producto": 1, "cantidad": 0, "precio": 25.5}]

    resultado = modelo_compra.validarProductos(productos)

    assert resultado["status"] is False
    assert resultado["title"] == "Cantidad inválida"


def test_validar_productos_rechaza_lista_vacia(modelo_compra):
    resultado = modelo_compra.validarProductos([])

    assert resultado["status"] is False
    assert resultado["title"] == "Productos requeridos"


def test_validar_productos_rechaza_precio_invalido(modelo_compra):
    productos = [{"cod_producto": 1, "cantidad": 2, "precio": 0}]

    resultado = modelo_compra.validarProductos(productos)

    assert resultado["status"] is False
    assert resultado["title"] == "Precio inválido"


def test_validar_productos_acepta_producto_valido(modelo_compra):
    productos = [{"cod_producto": 1, "cantidad": 2, "precio": 25.5}]

    resultado = modelo_compra.validarProductos(productos)

    assert resultado["status"] is True


def test_registrar_compra(monkeypatch, modelo_compra):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.callproc.return_value = (None, None, None, None, 123)
    mock_conn.cursor.return_value = mock_cursor

    monkeypatch.setattr(modelo_compra, "conn", lambda: mock_conn)

    resultado = modelo_compra.registrar_completa(
        "2026-10-27",
        5,
        [{"cod_producto": 1, "cantidad": 2, "precio_unitario": 10.5}],
        "V-12345678-9",
    )

    assert resultado == 123
    mock_cursor.callproc.assert_called_once_with(
        "sp_registrar_compra_completa",
        (
            "2026-10-27",
            5,
            '[{"cod_producto": 1, "cantidad": 2, "precio_unitario": 10.5}]',
            "V-12345678-9",
            None,
        ),
    )




def test_consultar_compras(modelo_compra):
    mock_cursor = modelo_compra.conexion.cursor.return_value
    compras = [{"cod_compra": 12, "total": 22.0, "status": 1}]
    mock_cursor.fetchall.return_value = compras

    resultado = modelo_compra.consultar()

    assert resultado == compras
    mock_cursor.execute.assert_called_once()
    consulta = mock_cursor.execute.call_args.args[0]
    assert "FROM compra c" in consulta
    assert "ORDER BY c.cod_compra DESC" in consulta
    mock_cursor.close.assert_called_once()


def test_editar_compra_actualiza_compra_detalle_y_stock(modelo_compra):
    mock_conn = modelo_compra.conexion
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(7, 2)]
    mock_conn.cursor.return_value = mock_cursor
    modelo_compra.fecha_compra = "2026-10-27"
    modelo_compra.total = 33
    modelo_compra.cod_proveedor = 5
    modelo_compra.status = 1

    resultado = modelo_compra.editar(
        12,
        [{"cod_producto": 9, "cantidad": 3, "precio": 11}],
    )

    assert resultado == 1
    llamadas = [
        (" ".join(llamada.args[0].split()), llamada.args[1:])
        for llamada in mock_cursor.execute.call_args_list
    ]
    assert len(llamadas) == 6
    assert llamadas[0][1] == ((12,),)
    assert llamadas[1][1] == ((2, 7),)
    assert llamadas[2][1] == ((12,),)
    assert llamadas[3][1] == (("2026-10-27", 33, 5, 1, 12),)
    assert llamadas[4][1] == ((12, 9, 3, 11.0),)
    assert llamadas[5][1] == ((3, 9),)
    assert "SELECT cod_producto, cantidad" in llamadas[0][0]
    assert "UPDATE compra" in llamadas[3][0]
    assert "INSERT INTO detalle_compra" in llamadas[4][0]
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_compra(modelo_compra):
    mock_conn = modelo_compra.conexion
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    resultado = modelo_compra.eliminar("12", "V-12345678-9")

    assert resultado == "cancelado"
    mock_cursor.callproc.assert_called_once_with(
        "sp_cancelar_compra",
        (12, "V-12345678-9"),
    )
    mock_cursor.close.assert_called_once()
    mock_conn.rollback.assert_not_called()
