import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

#python -m pytest .\Estudio-attelier\pytest\test\test_marca.py -q
#python -m pytest .\Estudio-attelier\pytest\test\test_marca.py::test_registrar_marca -vv
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.marca import MarcaModelo


@pytest.fixture
def modelo_marca(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(
        conexion_module.mysql.connector,
        "connect",
        lambda **kwargs: fake_conn,
    )
    return MarcaModelo()


def test_validar_nombre_marca_acepta_nombre_valido(modelo_marca):
    resultado = modelo_marca.validarNombreMarca("Belleza Natural")

    assert resultado["status"] is True


def test_validar_nombre_marca_rechaza_nombre_vacio(modelo_marca):
    resultado = modelo_marca.validarNombreMarca("   ")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_nombre_marca_rechaza_numeros_o_caracteres_especiales(
    modelo_marca,
):
    resultado = modelo_marca.validarNombreMarca("Marca 2")

    assert resultado["status"] is False
    assert resultado["title"] == "Dato inválido"


def test_validar_nombre_marca_rechaza_nombre_corto(modelo_marca):
    resultado = modelo_marca.validarNombreMarca("AB")

    assert resultado["status"] is False
    assert resultado["title"] == "Nombre inválido"


def test_validar_status_marca_acepta_status_activo(modelo_marca):
    resultado = modelo_marca.validarStatus("1")

    assert resultado["status"] is True


def test_validar_status_marca_acepta_status_inactivo(modelo_marca):
    resultado = modelo_marca.validarStatus("0")

    assert resultado["status"] is True


def test_validar_status_marca_rechaza_status_invalido(modelo_marca):
    resultado = modelo_marca.validarStatus("2")

    assert resultado["status"] is False
    assert resultado["title"] == "Estado inválido"


def test_registrar_marca(modelo_marca):
    mock_cursor = modelo_marca.conexion.cursor.return_value
    modelo_marca.nombre_marca = "Belleza Natural"

    resultado = modelo_marca.registrar()

    assert resultado == 1
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == ("Belleza Natural",)
    modelo_marca.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_consultar_marcas(modelo_marca):
    mock_cursor = modelo_marca.conexion.cursor.return_value
    marcas = [{"cod_marca": 5, "nombre_marca": "Belleza Natural"}]
    mock_cursor.fetchall.return_value = marcas

    resultado = modelo_marca.consultar()

    assert resultado == marcas
    mock_cursor.execute.assert_called_once()
    assert "FROM marca" in mock_cursor.execute.call_args.args[0]
    mock_cursor.close.assert_called_once()


def test_buscar_marca_por_nombre(modelo_marca):
    mock_cursor = modelo_marca.conexion.cursor.return_value
    marca = {"cod_marca": 5, "nombre_marca": "Belleza Natural"}
    mock_cursor.fetchone.return_value = marca

    resultado = modelo_marca.buscar("Belleza Natural")

    assert resultado == marca
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == ("Belleza Natural",)
    mock_cursor.close.assert_called_once()


def test_editar_marca(modelo_marca):
    mock_cursor = modelo_marca.conexion.cursor.return_value
    modelo_marca.nombre_marca = "Belleza Actualizada"
    modelo_marca.status = 1
    modelo_marca.cod_marca = 5

    resultado = modelo_marca.editar()

    assert resultado == 1
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == (
        "Belleza Actualizada",
        1,
        5,
    )
    modelo_marca.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_marca_sin_productos_asociados(modelo_marca):
    mock_cursor = modelo_marca.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 0}

    resultado = modelo_marca.eliminar(5)

    assert resultado == "eliminado"
    assert mock_cursor.execute.call_count == 2
    assert mock_cursor.execute.call_args_list[0].args[1] == (5,)
    assert mock_cursor.execute.call_args_list[1].args[1] == (5,)
    modelo_marca.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_marca_con_productos_asociados_no_la_borra(modelo_marca):
    mock_cursor = modelo_marca.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 2}

    resultado = modelo_marca.eliminar(5)

    assert resultado == "existe_producto"
    mock_cursor.execute.assert_called_once()
    modelo_marca.conexion.commit.assert_not_called()
    mock_cursor.close.assert_called_once()