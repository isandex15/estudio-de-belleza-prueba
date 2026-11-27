import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.empresa import EmpresaModelo


# python -m pytest ".\pytest\test\puebas unitarias\test_empresa.py::test_validar_empresa_rechaza_nombre_y_correo_vacios" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_empresa.py::test_validar_empresa_rechaza_direccion_vacia" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_empresa.py::test_validar_empresa_rechaza_telefono_vacio" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_empresa.py::test_validar_empresa_rechaza_correo_invalido" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_empresa.py::test_validar_empresa_rechaza_logo_formato_no_permitido" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_empresa.py::test_registrar_empresa" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_empresa.py" -q



@pytest.fixture
def modelo_empresa(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(conexion_module.mysql.connector, "connect", lambda **kwargs: fake_conn)
    return EmpresaModelo()


# CP-EMP-0 (prueba negativa: impide registrar una empresa cuando el nombre y el correo electrónico están vacíos)
def test_validar_empresa_rechaza_nombre_y_correo_vacios(modelo_empresa):
    resultado = modelo_empresa.validarEmpresa(
        "", "Centro", "", "04121234567",
        "Estudio de belleza", MagicMock(filename="logo.png")
    )

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "nombre de la empresa es obligatorio" in resultado["text"]
    assert "correo electrónico es obligatorio" in resultado["text"]

# CP-EMP-0 (prueba negativa: rechaza el registro de una empresa con dirección vacía)
def test_validar_empresa_rechaza_direccion_vacia(modelo_empresa):
    resultado = modelo_empresa.validarEmpresa(
        "ATELIER GUIMAR", "", "atelier@gmail.com", "04121234567",
        "Estudio de belleza", MagicMock(filename="logo.png")
    )

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "La dirección es obligatoria." in resultado["text"]


# CP-EMP-0 (prueba negativa: rechaza el registro de una empresa con teléfono vacío)
def test_validar_empresa_rechaza_telefono_vacio(modelo_empresa):
    resultado = modelo_empresa.validarEmpresa(
        "ATELIER GUIMAR", "Centro", "atelier@gmail.com", "",
        "Estudio de belleza", MagicMock(filename="logo.png")
    )

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "El teléfono es obligatorio." in resultado["text"]


# CP-EMP-0 (prueba negativa: rechaza el registro de una empresa con correo electrónico inválido)
def test_validar_empresa_rechaza_correo_invalido(modelo_empresa):
    resultado = modelo_empresa.validarEmpresa(
        "ATELIER GUIMAR", "Centro", "ateliergmail.com", "04121234567",
        "Estudio de belleza", MagicMock(filename="logo.png")
    )

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "El correo electrónico no es válido." in resultado["text"]


# CP-EMP-0 (prueba negativa: rechaza el registro de una empresa con logo de formato no permitido)
def test_validar_empresa_rechaza_logo_formato_no_permitido(modelo_empresa):
    resultado = modelo_empresa.validarEmpresa(
        "ATELIER GUIMAR", "Centro", "atelier@gmail.com", "04121234567",
        "Estudio de belleza", MagicMock(filename="logo.gif")
    )

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "El logo debe ser una imagen PNG, JPG o JPEG." in resultado["text"]



# CP-EMP-0 (prueba positiva: registra una empresa correctamente con todos los campos obligatorios )
def test_registrar_empresa(monkeypatch, modelo_empresa):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    monkeypatch.setattr(modelo_empresa, "conexion", mock_conn)

    modelo_empresa.nombre = "ATELIER GUIMAR"
    modelo_empresa.direccion = "Centro"
    modelo_empresa.telefono = "04121234567"
    modelo_empresa.email = "atelier@gmail.com"
    modelo_empresa.descripcion_empresa = "Estudio de belleza"
    modelo_empresa.logo = "static/assets/img/logo.png"
    modelo_empresa.fecha_actualizacion = "2026-11-11"

    resultado = modelo_empresa.registrar()

    assert resultado == 1
    mock_cursor.execute.assert_called_once_with(
        """
                INSERT INTO empresa
                (nombre, direccion, telefono, email, descripcion_empresa, logo, fecha_actualizacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
        (
            "ATELIER GUIMAR",
            "Centro",
            "04121234567",
            "atelier@gmail.com",
            "Estudio de belleza",
            "static/assets/img/logo.png",
            "2026-11-11"
        )
    )


# CP-EMP-06 (prueba negativa: rechaza registrar una empresa cuando el nombre contiene números)
def test_validar_empresa_rechaza_nombre_con_numeros(modelo_empresa):
    resultado = modelo_empresa.validarEmpresa(
        "ATELIER123", "Centro", "atelier@gmail.com", "04121234567",
        "Estudio de belleza", MagicMock(filename="logo.png")
    )

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "El nombre de la empresa no puede contener números." in resultado["text"]


# CP-EMP-07 (prueba negativa: rechaza registrar una empresa cuando el teléfono contiene letras)
def test_validar_empresa_rechaza_telefono_con_letras(modelo_empresa):
    resultado = modelo_empresa.validarEmpresa(
        "ATELIER GUIMAR", "Centro", "atelier@gmail.com", "0412ABC4567",
        "Estudio de belleza", MagicMock(filename="logo.png")
    )

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "El teléfono solo puede contener números." in resultado["text"]


# CP-EMP-08 (prueba negativa: rechaza registrar una empresa cuando la descripción está vacía)
def test_validar_empresa_rechaza_descripcion_vacia(modelo_empresa):
    resultado = modelo_empresa.validarEmpresa(
        "ATELIER GUIMAR", "Centro", "atelier@gmail.com", "04121234567",
        "", MagicMock(filename="logo.png")
    )

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "La descripción de la empresa es obligatoria." in resultado["text"]


# CP-EMP-09 (prueba negativa: rechaza registrar una empresa cuando el logo está vacío)
def test_validar_empresa_rechaza_logo_vacio(modelo_empresa):
    resultado = modelo_empresa.validarEmpresa(
        "ATELIER GUIMAR", "Centro", "atelier@gmail.com", "04121234567",
        "Estudio de belleza", MagicMock(filename="")
    )

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "El logo de la empresa es obligatorio." in resultado["text"]    