import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.clientes import ClientesModelo

# python -m pytest ".\pytest\test\puebas unitarias\test_cliente.py::test_registrar_cliente" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_cliente.py::test_registrar_cliente_error" -q

# python -m pytest ".\pytest\test\puebas unitarias\test_cliente.py::test_eliminar_cliente_con_reservas_activas" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_cliente.py::test_validar_cliente_rechaza_cedula_vacia" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_cliente.py::test_validar_cliente_rechaza_correo_invalido" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_cliente.py::test_registrar_cliente_sin_telefono" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_cliente.py::test_registrar_cliente_sin_correo" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_cliente.py::test_editar_cliente_correctamente" -q

# python -m pytest ".\pytest\test\puebas unitarias\test_cliente.py::test_editar_cliente_sin_modificar_datos" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_cliente.py::test_eliminar_cliente_inactivo_sin_reservas" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_cliente.py::test_eliminar_cliente_activo_con_reservas" -q
# Ejecutar todas las pruebas del archivo
# python -m pytest ".\pytest\test\puebas unitarias\test_cliente.py" -q

@pytest.fixture
def modelo_cliente(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(conexion_module.mysql.connector, "connect", lambda **kwargs: fake_conn)
    return ClientesModelo()


# CP-CLI-01 (prueba positiva: registrar un cliente correctamente) 
def test_registrar_cliente(monkeypatch, modelo_cliente):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    monkeypatch.setattr(modelo_cliente, "conexion", mock_conn)

    modelo_cliente.cedula = "12345678"
    modelo_cliente.nombre_usuario = "Carlos"
    modelo_cliente.apellido_usuario = "Perez"
    modelo_cliente.telefono = "04121234567"
    modelo_cliente.direccion = "Centro"
    modelo_cliente.correo = "carlos@gmail.com"
    modelo_cliente.cod_rol = 3

    resultado = modelo_cliente.registrar()

    assert resultado == 1

    parametros = mock_cursor.execute.call_args[0][1]

    assert parametros[:10] == (
        "12345678",
        "Carlos",
        "Perez",
        "04121234567",
        "Centro",
        "carlos@gmail.com",
        3,
        1,
        "",
        0,
    )

# CP-CLI-0 (prueba negativa: maneja un error al registrar un cliente) 
def test_registrar_cliente_error(monkeypatch, modelo_cliente):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Error al guardar")

    monkeypatch.setattr(modelo_cliente, "conexion", mock_conn)

    modelo_cliente.cedula = "12345678"
    modelo_cliente.nombre_usuario = "Carlos"
    modelo_cliente.apellido_usuario = "Perez"
    modelo_cliente.telefono = "04121234567"
    modelo_cliente.direccion = "Centro"
    modelo_cliente.correo = "carlos@gmail.com"

    resultado = modelo_cliente.registrar()

    assert resultado == 0
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_not_called()


# CP-CLI-0 (prueba negativa: impide eliminar un cliente activo con reservas activas) 
def test_eliminar_cliente_con_reservas_activas(monkeypatch, modelo_cliente):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = [(1,), (2,)]

    monkeypatch.setattr(modelo_cliente, "conexion", mock_conn)

    resultado = modelo_cliente.eliminar("12345678")

    assert resultado == -5
    assert mock_cursor.execute.call_count == 2
    mock_conn.commit.assert_not_called()


# CP-CLI-0 - Rechazar cliente con cédula vacía
def test_validar_cliente_rechaza_cedula_vacia(modelo_cliente):
    resultado = modelo_cliente.validarCliente(
        "", "Carlos", "Perez", "04121234567",
        "Centro", "carlos@gmail.com"
    )

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "La cédula es obligatoria." in resultado["text"]


# CP-CLI-0 - Rechazar cliente con correo electrónico inválido
def test_validar_cliente_rechaza_correo_invalido(modelo_cliente):
    resultado = modelo_cliente.validarCliente(
        "12345678", "Carlos", "Perez", "04121234567",
        "Centro", "carlosgmail.com"
    )

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "El correo electrónico no es válido." in resultado["text"]
# CP-CLI-0 (prueba negativa: rechaza el registro de un cliente sin correo electrónico)
def test_registrar_cliente_sin_correo(modelo_cliente):
    resultado = modelo_cliente.validarCliente(
        "3196486", "Carolina", "González", "04141234567",
        "Caracas", ""
    )

    assert resultado["status"] is False
    assert resultado["title"] == "Datos inválidos"
    assert "El correo electrónico es obligatorio." in resultado["text"]


# CP-CLI- unitaria - Registrar un cliente sin teléfono
def test_registrar_cliente_sin_telefono(modelo_cliente):
    resultado = modelo_cliente.validarCliente(
        "3196486", "Carolina", "González", "",
        "Caracas", "carolina@gmail.com"
    )

    assert resultado["status"] is False
    assert resultado["title"] == "Datos inválidos"
    assert "El teléfono es obligatorio." in resultado["text"]    



    # CP-CLI-16 unitaria - Editar correctamente los datos de un cliente existente
def test_editar_cliente_correctamente(modelo_cliente):
    modelo_cliente.cedula = "3196486"
    modelo_cliente.nombre_usuario = "Carolina"
    modelo_cliente.apellido_usuario = "González"
    modelo_cliente.telefono = "04141234567"
    modelo_cliente.direccion = "Caracas"
    modelo_cliente.correo = "carolina@gmail.com"
    modelo_cliente.status = 1

    resultado = modelo_cliente.editar()

    assert resultado == 1
    modelo_cliente.conexion.commit.assert_called_once()


# CP-CLI-18 unitaria - Editar un cliente sin modificar sus datos
def test_editar_cliente_sin_modificar_datos(modelo_cliente):
    modelo_cliente.cedula = "3196486"
    modelo_cliente.nombre_usuario = "Carolina"
    modelo_cliente.apellido_usuario = "González"
    modelo_cliente.telefono = "04141234567"
    modelo_cliente.direccion = "Caracas"
    modelo_cliente.correo = "carolina@gmail.com"
    modelo_cliente.status = 1

    resultado = modelo_cliente.editar()

    assert resultado == 1
    modelo_cliente.conexion.commit.assert_called_once()



    # CP-CLI- unitaria - Eliminar un cliente inactivo sin reservas activas
def test_eliminar_cliente_inactivo_sin_reservas(modelo_cliente):
    mock_cursor = modelo_cliente.conexion.cursor.return_value
    mock_cursor.fetchone.side_effect = [(0,), (0,)]

    resultado = modelo_cliente.eliminar("3196486")

    assert resultado == 1
    modelo_cliente.conexion.commit.assert_called_once()


# CP-CLI- unitaria - Impedir eliminar un cliente activo con reservas activas
def test_eliminar_cliente_activo_con_reservas(modelo_cliente):
    mock_cursor = modelo_cliente.conexion.cursor.return_value
    mock_cursor.fetchone.side_effect = [(1,), (2,)]

    resultado = modelo_cliente.eliminar("3196486")

    assert resultado == -5
    modelo_cliente.conexion.commit.assert_not_called()