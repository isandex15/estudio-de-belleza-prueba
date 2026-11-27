import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest
import bcrypt

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.usuarios import UsuariosModelo

# python -m pytest ".\pytest\test\puebas unitarias\test_usuario.py::test_validar_usuario_rechaza_campos_obligatorios_vacios" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_usuario.py::test_registrar_usuario_con_password_encriptada" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_usuario.py::test_validar_usuario_rechaza_telefono_con_letras" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_usuario.py::test_validar_usuario_rechaza_cedula_con_letras" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_usuario.py::test_validar_usuario_rechaza_nombre_con_numeros" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_usuario.py::test_validar_usuario_rechaza_apellido_con_numeros" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_usuario.py::test_validar_usuario_rechaza_correo_invalido" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_usuario.py::test_editar_usuario_correctamente" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_usuario.py::test_eliminar_usuario_activo" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_usuario.py::test_eliminar_usuario_inactivo" -q

# python -m pytest ".\pytest\test\puebas unitarias\test_usuario.py" -q



@pytest.fixture
def modelo_usuario(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(conexion_module.mysql.connector, "connect", lambda **kwargs: fake_conn)
    return UsuariosModelo()

# CP-USU-01 (prueba negativa: rechaza el registro de un usuario cuando existen campos obligatorios vacíos)
def test_validar_usuario_rechaza_campos_obligatorios_vacios(modelo_usuario):
    resultado = modelo_usuario.validarUsuario(
        "", "", "", "", "", "", ""
    )

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "obligatoria" in resultado["text"]
    assert "Debe seleccionar un rol" in resultado["text"]


# CP-USU-02 (prueba positiva: registra correctamente un usuario con datos válidos y contraseña encriptada)
def test_registrar_usuario_con_password_encriptada(modelo_usuario):
    modelo_usuario.cedula = "12345678"
    modelo_usuario.nombre_usuario = "Carlos"
    modelo_usuario.apellido_usuario = "Perez"
    modelo_usuario.telefono = "04121234567"
    modelo_usuario.direccion = "Centro"
    modelo_usuario.correo = "carlos@gmail.com"
    modelo_usuario.password = "Clave123"
    modelo_usuario.cod_rol = 1

    resultado = modelo_usuario.registrar()

    mock_cursor = modelo_usuario.conexion.cursor.return_value
    parametros = mock_cursor.execute.call_args[0][1]
    password_encriptada = parametros[3]

    assert resultado == 1
    assert bcrypt.checkpw(b"Clave123", password_encriptada)
    assert password_encriptada != b"Clave123"
    modelo_usuario.conexion.commit.assert_called_once()


# CP-USU-03 (prueba negativa: rechaza el registro de un usuario cuando el teléfono contiene letras)
def test_validar_usuario_rechaza_telefono_con_letras(modelo_usuario):
    resultado = modelo_usuario.validarUsuario(
        "12345678",
        "Carlos",
        "Perez",
        "0412ABC4567",
        "Centro",
        "Clave123",
        1
    )

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "El teléfono solo puede contener números" in resultado["text"]


# CP-USU-04 (prueba negativa: rechaza una cédula que contiene letras)
def test_validar_usuario_rechaza_cedula_con_letras(modelo_usuario):
    resultado = modelo_usuario.validarUsuario(
        "123ABC", "Carlos", "Perez", "04121234567",
        "Centro", "Clave123", 1
    )

    assert resultado["status"] is False
    assert "La cédula solo puede contener números" in resultado["text"]


# CP-USU-05 (prueba negativa: rechaza un nombre que contiene números)
def test_validar_usuario_rechaza_nombre_con_numeros(modelo_usuario):
    resultado = modelo_usuario.validarUsuario(
        "12345678", "Carlos123", "Perez", "04121234567",
        "Centro", "Clave123", 1
    )

    assert resultado["status"] is False
    assert "El nombre no puede contener números" in resultado["text"]


# CP-USU-06 (prueba negativa: rechaza un apellido que contiene números)
def test_validar_usuario_rechaza_apellido_con_numeros(modelo_usuario):
    resultado = modelo_usuario.validarUsuario(
        "12345678", "Carlos", "Perez123", "04121234567",
        "Centro", "Clave123", 1
    )

    assert resultado["status"] is False
    assert "El apellido no puede contener números" in resultado["text"]


# CP-USU-07 (prueba positiva: edita correctamente los datos de un usuario existente)
def test_editar_usuario_correctamente(modelo_usuario):
    modelo_usuario.cedula = "12345678"
    modelo_usuario.nombre_usuario = "Carlos"
    modelo_usuario.apellido_usuario = "Perez"
    modelo_usuario.telefono = "04121234567"
    modelo_usuario.direccion = "Centro"
    modelo_usuario.correo = "carlos@gmail.com"
    modelo_usuario.password = None
    modelo_usuario.status = 1
    modelo_usuario.cod_rol = 1

    resultado = modelo_usuario.editar()

    assert resultado is True
    modelo_usuario.conexion.commit.assert_called_once()


# CP-USU-08 (prueba negativa: impide eliminar un usuario que se encuentra activo)
def test_eliminar_usuario_activo(modelo_usuario):
    mock_cursor = modelo_usuario.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = (1, 1)

    resultado = modelo_usuario.eliminar("12345678")

    assert resultado == -2
    assert mock_cursor.execute.call_count == 1
    modelo_usuario.conexion.commit.assert_not_called()


# CP-USU-09 (prueba positiva: elimina correctamente un usuario inactivo mediante eliminación lógica)
def test_eliminar_usuario_inactivo(modelo_usuario):
    mock_cursor = modelo_usuario.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = (0, 1)
    mock_cursor.rowcount = 1

    resultado = modelo_usuario.eliminar("12345678")

    assert resultado == 1
    assert mock_cursor.execute.call_count == 2
    modelo_usuario.conexion.commit.assert_called_once()