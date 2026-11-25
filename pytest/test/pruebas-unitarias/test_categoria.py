import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

#python -m pytest .\Estudio-attelier\pytest\test\test_categoria.py -q
#python -m pytest .\Estudio-attelier\pytest\test\test_categoria.py::test_registrar_categoria -vv
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.categorias import CategoriaModelo


@pytest.fixture
def modelo_categoria(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(
        conexion_module.mysql.connector,
        "connect",
        lambda **kwargs: fake_conn,
    )
    return CategoriaModelo()


def test_validar_nombre_categoria_acepta_nombre_valido(modelo_categoria):
    resultado = modelo_categoria.validarNombreCategoria("Cuidado capilar")

    assert resultado["status"] is True


def test_validar_nombre_categoria_rechaza_nombre_vacio(modelo_categoria):
    resultado = modelo_categoria.validarNombreCategoria("   ")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_nombre_categoria_rechaza_numeros_o_caracteres_especiales(
    modelo_categoria,
):
    resultado = modelo_categoria.validarNombreCategoria("Cuidado 2")

    assert resultado["status"] is False
    assert resultado["title"] == "Dato inválido"


def test_validar_nombre_categoria_rechaza_nombre_corto(modelo_categoria):
    resultado = modelo_categoria.validarNombreCategoria("AB")

    assert resultado["status"] is False
    assert resultado["title"] == "Nombre inválido"


def test_validar_nombre_categoria_rechaza_nombre_largo(modelo_categoria):
    resultado = modelo_categoria.validarNombreCategoria("A" * 51)

    assert resultado["status"] is False
    assert resultado["title"] == "Nombre muy largo"


def test_validar_status_categoria_acepta_status_activo(modelo_categoria):
    resultado = modelo_categoria.validarStatus("1")

    assert resultado["status"] is True


def test_validar_status_categoria_acepta_status_inactivo(modelo_categoria):
    resultado = modelo_categoria.validarStatus("0")

    assert resultado["status"] is True


def test_validar_status_categoria_rechaza_status_invalido(modelo_categoria):
    resultado = modelo_categoria.validarStatus("2")

    assert resultado["status"] is False
    assert resultado["title"] == "Estado inválido"


def test_registrar_categoria(modelo_categoria):
    mock_cursor = modelo_categoria.conexion.cursor.return_value
    modelo_categoria.nombre_categoria = "Cuidado capilar"

    resultado = modelo_categoria.registrar()

    assert resultado == 1
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == ("Cuidado capilar",)
    modelo_categoria.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_consultar_categorias(modelo_categoria):
    mock_cursor = modelo_categoria.conexion.cursor.return_value
    categorias = [{"cod_categoria": 3, "nombre_categoria": "Cuidado capilar"}]
    mock_cursor.fetchall.return_value = categorias

    resultado = modelo_categoria.consultar()

    assert resultado == categorias
    mock_cursor.execute.assert_called_once()
    assert "FROM categoria" in mock_cursor.execute.call_args.args[0]
    mock_cursor.close.assert_called_once()


def test_buscar_categoria_por_nombre(modelo_categoria):
    mock_cursor = modelo_categoria.conexion.cursor.return_value
    categoria = {"cod_categoria": 3, "nombre_categoria": "Cuidado capilar"}
    mock_cursor.fetchone.return_value = categoria

    resultado = modelo_categoria.buscar("Cuidado capilar")

    assert resultado == categoria
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == ("Cuidado capilar",)
    mock_cursor.close.assert_called_once()


def test_editar_categoria(modelo_categoria):
    mock_cursor = modelo_categoria.conexion.cursor.return_value
    modelo_categoria.nombre_categoria = "Cuidado facial"
    modelo_categoria.status = 1
    modelo_categoria.cod_categoria = 3

    resultado = modelo_categoria.editar()

    assert resultado == 1
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == (
        "Cuidado facial",
        1,
        3,
    )
    modelo_categoria.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_categoria_sin_productos_asociados(modelo_categoria):
    mock_cursor = modelo_categoria.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 0}

    resultado = modelo_categoria.eliminar(3)

    assert resultado == "eliminado"
    assert mock_cursor.execute.call_count == 2
    assert mock_cursor.execute.call_args_list[0].args[1] == (3,)
    assert mock_cursor.execute.call_args_list[1].args[1] == (3,)
    modelo_categoria.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_categoria_con_productos_asociados_no_la_borra(modelo_categoria):
    mock_cursor = modelo_categoria.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 2}

    resultado = modelo_categoria.eliminar(3)

    assert resultado == "existe_producto"
    mock_cursor.execute.assert_called_once()
    modelo_categoria.conexion.commit.assert_not_called()
    mock_cursor.close.assert_called_once()