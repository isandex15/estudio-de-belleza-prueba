import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.rol import RolModelo

# python -m pytest ".\pytest\test\puebas unitarias\test_rol.py::test_validar_rol_rechaza_numeros_y_caracteres_especiales" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_rol.py::test_validar_rol_rechaza_rol_vacio" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_rol.py::test_eliminar_rol_con_usuarios_asociados" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_rol.py::test_validar_rol_acepta_rol_con_solo_letras" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_rol.py::test_registrar_rol_retorna_cero_si_falla" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_rol.py::test_editar_rol_correctamente" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_eliminar_rol_con_usuarios_asociados" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_buscar_rol_existente" -q

# python -m pytest ".\pytest\test\puebas unitarias\test_rol.py" -q

@pytest.fixture
def modelo_rol(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(conexion_module.mysql.connector, "connect", lambda **kwargs: fake_conn)
    return RolModelo()


# CP-ROL-0 (prueba negativa: rechaza el registro de un rol que contiene números o caracteres especiales)
def test_validar_rol_rechaza_numeros_y_caracteres_especiales(modelo_rol):
    resultado = modelo_rol.validarRol("Admin@123")

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "solo puede contener letras" in resultado["text"]


# CP-ROL-0 (prueba negativa: impide registrar un rol vacío) 
def test_validar_rol_rechaza_rol_vacio(modelo_rol):
    resultado = modelo_rol.validarRol("")

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "obligatorio" in resultado["text"]

# CP-ROL-0 (prueba negativa: impide eliminar un rol que tiene usuarios asociados)
def test_eliminar_rol_con_usuarios_asociados(monkeypatch, modelo_rol):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"total": 2}

    monkeypatch.setattr(modelo_rol, "conexion", mock_conn)

    resultado = modelo_rol.eliminar(1)

    assert resultado == "existe_usuarios"
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_not_called()

# CP-ROL-0 (prueba positiva: acepta registrar un rol que contiene solamente letras)
def test_validar_rol_acepta_rol_con_solo_letras(modelo_rol):
    resultado = modelo_rol.validarRol("Administrador")

    assert resultado["status"] is True


# CP-ROL-0 (prueba negativa: rechaza el registro de un rol cuando falla el procedimiento almacenado)
def test_registrar_rol_retorna_cero_si_falla(modelo_rol):
    mock_cursor = modelo_rol.conexion.cursor.return_value
    mock_cursor.callproc.side_effect = Exception("Error al registrar")

    modelo_rol.rol = "Administrador"

    resultado = modelo_rol.registrar()

    assert resultado == 0
    modelo_rol.conexion.rollback.assert_called_once()


# CP-ROL-0 (prueba positiva: edita correctamente un rol existente)
def test_editar_rol_correctamente(modelo_rol):
    modelo_rol.cod_rol = 1
    modelo_rol.rol = "Supervisor"
    modelo_rol.status = 1

    resultado = modelo_rol.editar()

    assert resultado == 1
    modelo_rol.conexion.commit.assert_called_once()


# CP-ROL-0 (prueba negativa: impide eliminar un rol que tiene usuarios asociados)
def test_eliminar_rol_con_usuarios_asociados(modelo_rol):
    mock_cursor = modelo_rol.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 2}

    resultado = modelo_rol.eliminar(1)

    assert resultado == "existe_usuarios"
    mock_cursor.execute.assert_called_once()
    modelo_rol.conexion.commit.assert_not_called()


# CP-ROL-0 (prueba positiva: encuentra un rol existente)
def test_buscar_rol_existente(modelo_rol):
    mock_cursor = modelo_rol.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {
        "cod_rol": 1,
        "rol": "Administrador",
        "status": 1
    }

    resultado = modelo_rol.buscar("Administrador")

    assert resultado is not None
    assert resultado["rol"] == "Administrador"
    assert resultado["cod_rol"] == 1