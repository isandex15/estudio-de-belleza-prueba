import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

#python -m pytest .\Estudio-attelier\pytest\test\test_proveedor.py -q
#python -m pytest .\Estudio-attelier\pytest\test\test_proveedor.py::test_registrar_proveedor -vv
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.proveedor import ProveedorModelo


@pytest.fixture
def modelo_proveedor(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(
        conexion_module.mysql.connector,
        "connect",
        lambda **kwargs: fake_conn,
    )
    return ProveedorModelo()


def test_validar_cedula_acepta_cedula_valida(modelo_proveedor):
    resultado = modelo_proveedor.validarCedula("12345678")

    assert resultado["status"] is True


def test_validar_cedula_rechaza_cedula_vacia(modelo_proveedor):
    resultado = modelo_proveedor.validarCedula("")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_cedula_rechaza_formato_invalido(modelo_proveedor):
    resultado = modelo_proveedor.validarCedula("12345A")

    assert resultado["status"] is False
    assert resultado["title"] == "Cédula inválida"


def test_validar_nombre_acepta_nombre_valido(modelo_proveedor):
    resultado = modelo_proveedor.validarNombre("María Elena")

    assert resultado["status"] is True


def test_validar_nombre_rechaza_nombre_vacio(modelo_proveedor):
    resultado = modelo_proveedor.validarNombre("   ")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_nombre_rechaza_numeros_o_caracteres_especiales(
    modelo_proveedor,
):
    resultado = modelo_proveedor.validarNombre("María2")

    assert resultado["status"] is False
    assert resultado["title"] == "Dato inválido"


def test_validar_apellido_acepta_apellido_valido(modelo_proveedor):
    resultado = modelo_proveedor.validarApellido("Pérez")

    assert resultado["status"] is True


def test_validar_apellido_rechaza_apellido_vacio(modelo_proveedor):
    resultado = modelo_proveedor.validarApellido("")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_apellido_rechaza_numeros_o_caracteres_especiales(
    modelo_proveedor,
):
    resultado = modelo_proveedor.validarApellido("Pérez-2")

    assert resultado["status"] is False
    assert resultado["title"] == "Dato inválido"


def test_validar_rif_acepta_rif_valido(modelo_proveedor):
    resultado = modelo_proveedor.validarRif("J123456789")

    assert resultado["status"] is True


def test_validar_rif_rechaza_rif_vacio(modelo_proveedor):
    resultado = modelo_proveedor.validarRif("")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_rif_rechaza_formato_invalido(modelo_proveedor):
    resultado = modelo_proveedor.validarRif("X123")

    assert resultado["status"] is False
    assert resultado["title"] == "RIF inválido"


def test_validar_telefono_acepta_telefono_valido(modelo_proveedor):
    resultado = modelo_proveedor.validarTelefono("04121234567")

    assert resultado["status"] is True


def test_validar_telefono_rechaza_telefono_vacio(modelo_proveedor):
    resultado = modelo_proveedor.validarTelefono("")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_telefono_rechaza_formato_invalido(modelo_proveedor):
    resultado = modelo_proveedor.validarTelefono("0412ABC")

    assert resultado["status"] is False
    assert resultado["title"] == "Teléfono inválido"


def test_validar_correo_acepta_correo_valido(modelo_proveedor):
    resultado = modelo_proveedor.validarCorreo("proveedor@ejemplo.com")

    assert resultado["status"] is True


def test_validar_correo_rechaza_correo_vacio(modelo_proveedor):
    resultado = modelo_proveedor.validarCorreo("")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_correo_rechaza_formato_invalido(modelo_proveedor):
    resultado = modelo_proveedor.validarCorreo("correo-invalido")

    assert resultado["status"] is False
    assert resultado["title"] == "Correo inválido"


def test_registrar_proveedor(modelo_proveedor):
    mock_cursor = modelo_proveedor.conexion.cursor.return_value
    modelo_proveedor.cedula = "12345678"
    modelo_proveedor.nombre = "María"
    modelo_proveedor.apellido = "Pérez"
    modelo_proveedor.rif = "J123456789"
    modelo_proveedor.telefono = "04121234567"
    modelo_proveedor.correo = "proveedor@ejemplo.com"

    resultado = modelo_proveedor.registrar()

    assert resultado == 1
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == (
        "12345678",
        "María",
        "Pérez",
        "J123456789",
        "04121234567",
        "proveedor@ejemplo.com",
    )
    modelo_proveedor.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_consultar_proveedores(modelo_proveedor):
    mock_cursor = modelo_proveedor.conexion.cursor.return_value
    proveedores = [{"cod_proveedor": 2, "nombre": "María", "apellido": "Pérez"}]
    mock_cursor.fetchall.return_value = proveedores

    resultado = modelo_proveedor.consultar()

    assert resultado == proveedores
    mock_cursor.execute.assert_called_once()
    assert "FROM proveedor" in mock_cursor.execute.call_args.args[0]
    mock_cursor.close.assert_called_once()


def test_buscar_proveedor_por_cedula(modelo_proveedor):
    mock_cursor = modelo_proveedor.conexion.cursor.return_value
    proveedor = {"cod_proveedor": 2, "cedula": "12345678"}
    mock_cursor.fetchone.return_value = proveedor

    resultado = modelo_proveedor.buscar("12345678")

    assert resultado == proveedor
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == ("12345678",)
    mock_cursor.close.assert_called_once()


def test_editar_proveedor(modelo_proveedor):
    mock_cursor = modelo_proveedor.conexion.cursor.return_value
    modelo_proveedor.cod_proveedor = 2
    modelo_proveedor.cedula = "12345678"
    modelo_proveedor.nombre = "María"
    modelo_proveedor.apellido = "Pérez"
    modelo_proveedor.rif = "J123456789"
    modelo_proveedor.telefono = "04121234567"
    modelo_proveedor.correo = "proveedor@ejemplo.com"
    modelo_proveedor.status = 1

    resultado = modelo_proveedor.editar()

    assert resultado == 1
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == (
        "12345678",
        "María",
        "Pérez",
        "J123456789",
        "04121234567",
        "proveedor@ejemplo.com",
        1,
        2,
    )
    modelo_proveedor.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_proveedor_sin_compras_asociadas(modelo_proveedor):
    mock_cursor = modelo_proveedor.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 0}

    resultado = modelo_proveedor.eliminar(2)

    assert resultado == "eliminado"
    assert mock_cursor.execute.call_count == 2
    assert mock_cursor.execute.call_args_list[0].args[1] == (2,)
    assert mock_cursor.execute.call_args_list[1].args[1] == (2,)
    modelo_proveedor.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_proveedor_con_compras_asociadas_no_lo_borra(modelo_proveedor):
    mock_cursor = modelo_proveedor.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 1}

    resultado = modelo_proveedor.eliminar(2)

    assert resultado == "existe_compra"
    mock_cursor.execute.assert_called_once()
    modelo_proveedor.conexion.commit.assert_not_called()
    mock_cursor.close.assert_called_once()