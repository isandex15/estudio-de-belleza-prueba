import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

#python -m pytest .\Estudio-attelier\pytest\test\test_tipoproducto.py -q
#python -m pytest .\Estudio-attelier\pytest\test\test_tipoproducto.py::test_registrar_tipo_producto -vv
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.tipoproducto import TipoProductoModelo


@pytest.fixture
def modelo_tipo_producto(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(
        conexion_module.mysql.connector,
        "connect",
        lambda **kwargs: fake_conn,
    )
    return TipoProductoModelo()


def test_validar_nombre_tipo_producto_acepta_nombre_valido(modelo_tipo_producto):
    resultado = modelo_tipo_producto.validarNombreTipoProducto("Cuidado capilar")

    assert resultado["status"] is True


def test_validar_nombre_tipo_producto_rechaza_nombre_vacio(modelo_tipo_producto):
    resultado = modelo_tipo_producto.validarNombreTipoProducto("   ")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_nombre_tipo_producto_rechaza_numeros_o_caracteres_especiales(
    modelo_tipo_producto,
):
    resultado = modelo_tipo_producto.validarNombreTipoProducto("Cuidado 2")

    assert resultado["status"] is False
    assert resultado["title"] == "Dato inválido"


def test_validar_nombre_tipo_producto_rechaza_nombre_corto(modelo_tipo_producto):
    resultado = modelo_tipo_producto.validarNombreTipoProducto("AB")

    assert resultado["status"] is False
    assert resultado["title"] == "Nombre corto"


def test_validar_nombre_tipo_producto_rechaza_nombre_largo(modelo_tipo_producto):
    resultado = modelo_tipo_producto.validarNombreTipoProducto("A" * 51)

    assert resultado["status"] is False
    assert resultado["title"] == "Nombre demasiado largo"


def test_validar_codigo_tipo_producto_acepta_codigo_numerico(modelo_tipo_producto):
    resultado = modelo_tipo_producto.validarCodigo("12")

    assert resultado["status"] is True


def test_validar_codigo_tipo_producto_rechaza_codigo_vacio(modelo_tipo_producto):
    resultado = modelo_tipo_producto.validarCodigo("")

    assert resultado["status"] is False
    assert resultado["title"] == "Código vacío"


def test_validar_codigo_tipo_producto_rechaza_codigo_no_numerico(
    modelo_tipo_producto,
):
    resultado = modelo_tipo_producto.validarCodigo("12A")

    assert resultado["status"] is False
    assert resultado["title"] == "Código inválido"


def test_registrar_tipo_producto(modelo_tipo_producto):
    mock_cursor = modelo_tipo_producto.conexion.cursor.return_value
    modelo_tipo_producto.nombre_tipo_producto = "Cuidado capilar"

    resultado = modelo_tipo_producto.registrar()

    assert resultado["status"] is True
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == ("Cuidado capilar",)
    modelo_tipo_producto.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_registrar_tipo_producto_rechaza_nombre_invalido(modelo_tipo_producto):
    mock_cursor = modelo_tipo_producto.conexion.cursor.return_value
    modelo_tipo_producto.nombre_tipo_producto = "AB"

    resultado = modelo_tipo_producto.registrar()

    assert resultado["status"] is False
    assert resultado["title"] == "Nombre corto"
    mock_cursor.execute.assert_not_called()
    modelo_tipo_producto.conexion.commit.assert_not_called()


def test_consultar_tipos_producto(modelo_tipo_producto):
    mock_cursor = modelo_tipo_producto.conexion.cursor.return_value
    tipos = [{"cod_tipo_producto": 4, "nombre_tipo_producto": "Cuidado capilar"}]
    mock_cursor.fetchall.return_value = tipos

    resultado = modelo_tipo_producto.consultar()

    assert resultado == tipos
    mock_cursor.execute.assert_called_once()
    assert "FROM tipo_producto" in mock_cursor.execute.call_args.args[0]
    mock_cursor.close.assert_called_once()


def test_buscar_tipo_producto_por_nombre(modelo_tipo_producto):
    mock_cursor = modelo_tipo_producto.conexion.cursor.return_value
    tipo = {"cod_tipo_producto": 4, "nombre_tipo_producto": "Cuidado capilar"}
    mock_cursor.fetchone.return_value = tipo

    resultado = modelo_tipo_producto.buscar("Cuidado capilar")

    assert resultado == tipo
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == ("Cuidado capilar",)
    mock_cursor.close.assert_called_once()


def test_editar_tipo_producto(modelo_tipo_producto):
    mock_cursor = modelo_tipo_producto.conexion.cursor.return_value
    modelo_tipo_producto.cod_tipo_producto = 4
    modelo_tipo_producto.nombre_tipo_producto = "Cuidado facial"
    modelo_tipo_producto.status = 1

    resultado = modelo_tipo_producto.editar()

    assert resultado["status"] is True
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == (
        "Cuidado facial",
        1,
        4,
    )
    modelo_tipo_producto.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_editar_tipo_producto_rechaza_codigo_invalido(modelo_tipo_producto):
    mock_cursor = modelo_tipo_producto.conexion.cursor.return_value
    modelo_tipo_producto.cod_tipo_producto = "4A"
    modelo_tipo_producto.nombre_tipo_producto = "Cuidado facial"

    resultado = modelo_tipo_producto.editar()

    assert resultado["status"] is False
    assert resultado["title"] == "Código inválido"
    mock_cursor.execute.assert_not_called()
    modelo_tipo_producto.conexion.commit.assert_not_called()


def test_eliminar_tipo_producto_sin_productos_asociados(modelo_tipo_producto):
    mock_cursor = modelo_tipo_producto.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 0}

    resultado = modelo_tipo_producto.eliminar(4)

    assert resultado["status"] is True
    assert mock_cursor.execute.call_count == 2
    assert mock_cursor.execute.call_args_list[0].args[1] == (4,)
    assert mock_cursor.execute.call_args_list[1].args[1] == (4,)
    modelo_tipo_producto.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_tipo_producto_con_asociaciones_no_lo_borra(modelo_tipo_producto):
    mock_cursor = modelo_tipo_producto.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 2}

    resultado = modelo_tipo_producto.eliminar(4)

    assert resultado["status"] is False
    assert resultado["title"] == "No se puede eliminar"
    mock_cursor.execute.assert_called_once()
    modelo_tipo_producto.conexion.commit.assert_not_called()
    mock_cursor.close.assert_called_once()


def test_eliminar_tipo_producto_rechaza_codigo_invalido(modelo_tipo_producto):
    mock_cursor = modelo_tipo_producto.conexion.cursor.return_value

    resultado = modelo_tipo_producto.eliminar("4A")

    assert resultado["status"] is False
    assert resultado["title"] == "Código inválido"
    mock_cursor.execute.assert_not_called()
    modelo_tipo_producto.conexion.commit.assert_not_called()