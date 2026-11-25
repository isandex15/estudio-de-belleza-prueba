import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

#python -m pytest .\Estudio-attelier\pytest\test\test_tiposervicio.py -q
#python -m pytest .\Estudio-attelier\pytest\test\test_tiposervicio.py::test_registrar_tipo_servicio -vv

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.tiposervicios import TiposervicioModelo


@pytest.fixture
def modelo_tiposervicio(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(
        conexion_module.mysql.connector,
        "connect",
        lambda **kwargs: fake_conn,
    )
    return TiposervicioModelo()


def test_validar_nombre_servicio_acepta_nombre_valido(modelo_tiposervicio):
    resultado = modelo_tiposervicio.validarNombreServicio("Corte y peinado")

    assert resultado["status"] is True


def test_validar_nombre_servicio_rechaza_nombre_vacio(modelo_tiposervicio):
    resultado = modelo_tiposervicio.validarNombreServicio("   ")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_nombre_servicio_rechaza_numeros_y_caracteres_especiales(
    modelo_tiposervicio,
):
    resultado = modelo_tiposervicio.validarNombreServicio("Corte 2")

    assert resultado["status"] is False
    assert resultado["title"] == "Dato inválido"


def test_validar_precio_acepta_precio_valido(modelo_tiposervicio):
    resultado = modelo_tiposervicio.validarPrecio("25.50")

    assert resultado["status"] is True


def test_validar_precio_rechaza_precio_vacio(modelo_tiposervicio):
    resultado = modelo_tiposervicio.validarPrecio("")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_precio_rechaza_formato_invalido(modelo_tiposervicio):
    resultado = modelo_tiposervicio.validarPrecio("precio-invalido")

    assert resultado["status"] is False
    assert resultado["title"] == "Precio inválido"


def test_validar_precio_rechaza_cero(modelo_tiposervicio):
    resultado = modelo_tiposervicio.validarPrecio("0")

    assert resultado["status"] is False
    assert resultado["title"] == "Precio inválido"


def test_registrar_tipo_servicio(modelo_tiposervicio):
    mock_cursor = modelo_tiposervicio.conexion.cursor.return_value
    modelo_tiposervicio.nombre_servicio = "Corte y peinado"
    modelo_tiposervicio.precio = "25.50"

    resultado = modelo_tiposervicio.registrar()

    assert resultado == 1
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == ("Corte y peinado", "25.50")
    modelo_tiposervicio.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_consultar_tiposervicios(modelo_tiposervicio):
    mock_cursor = modelo_tiposervicio.conexion.cursor.return_value
    servicios = [
        {
            "cod_tipo_servicio": 4,
            "nombre_servicio": "Corte y peinado",
            "precio": 25.5,
            "status": 1,
        }
    ]
    mock_cursor.fetchall.return_value = servicios

    resultado = modelo_tiposervicio.consultar()

    assert resultado == servicios
    mock_cursor.execute.assert_called_once()
    assert "FROM tipo_servicio" in mock_cursor.execute.call_args.args[0]
    mock_cursor.close.assert_called_once()


def test_buscar_tipo_servicio(modelo_tiposervicio):
    mock_cursor = modelo_tiposervicio.conexion.cursor.return_value
    servicio = {"cod_tipo_servicio": 4, "nombre_servicio": "Corte y peinado"}
    mock_cursor.fetchone.return_value = servicio

    resultado = modelo_tiposervicio.buscar("Corte y peinado")

    assert resultado == servicio
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == ("Corte y peinado",)
    mock_cursor.close.assert_called_once()


def test_editar_tipo_servicio(modelo_tiposervicio):
    mock_cursor = modelo_tiposervicio.conexion.cursor.return_value
    modelo_tiposervicio.cod_tipo_servicio = 4
    modelo_tiposervicio.nombre_servicio = "Corte actualizado"
    modelo_tiposervicio.precio = "30.00"
    modelo_tiposervicio.status = 1

    resultado = modelo_tiposervicio.editar()

    assert resultado == 1
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == (
        "Corte actualizado",
        "30.00",
        1,
        4,
    )
    modelo_tiposervicio.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_tipo_servicio_sin_asociaciones(modelo_tiposervicio):
    mock_cursor = modelo_tiposervicio.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 0}

    resultado = modelo_tiposervicio.eliminar(4)

    assert resultado == "eliminado"
    assert mock_cursor.execute.call_count == 2
    assert mock_cursor.execute.call_args_list[0].args[1] == (4,)
    assert mock_cursor.execute.call_args_list[1].args[1] == (4,)
    modelo_tiposervicio.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_tipo_servicio_con_asociaciones_no_lo_borra(modelo_tiposervicio):
    mock_cursor = modelo_tiposervicio.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 2}

    resultado = modelo_tiposervicio.eliminar(4)

    assert resultado == "existe_servicio"
    mock_cursor.execute.assert_called_once()
    modelo_tiposervicio.conexion.commit.assert_not_called()
    mock_cursor.close.assert_called_once()