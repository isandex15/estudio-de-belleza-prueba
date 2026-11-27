import sys 
from pathlib import Path 
from unittest.mock import MagicMock

import pytest


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.personal import PersonalModelo

@pytest.fixture
def modelo_personal(monkeypatch):
    fake_conn = MagicMock()
    monkeypatch.setattr(conexion_module.mysql.connector, "connect", lambda **kwargs: fake_conn)
    return PersonalModelo()

# CP-PER-01 (Prueba positiva de validación de Cédula)
def test_validar_cedula_valida(modelo_personal):
    resultado = modelo_personal.validarCedula("1234567890")

    assert resultado["status"] is True
    assert resultado["value"] == "1234567890"



# CP-PER-02 (Prueba negativa: cédula inválida)
def test_validar_cedula_invalida(modelo_personal):
    resultado = modelo_personal.validarCedula("AB")

    assert resultado["status"] is False
    assert resultado["title"] == "Dato inválido"



# CP-PER-03 (prueba positiva de nombre)
def test_validar_nombre_usuario_valido(modelo_personal):
    resultado = modelo_personal.validarNombreUsuario("Jessica")

    assert resultado["status"] is True
    assert resultado["value"] == "Jessica"



# CP-PER-04 (prueba negativa: nombre con caracteres especiales o números)
def test_validar_nombre_usuario_invalido(modelo_personal):
    resultado = modelo_personal.validarNombreUsuario("Jessica123*")

    assert resultado["status"] is False
    assert "no puede contener caracteres especiales" in resultado["text"]



# CP-PER-05 (prueba positiva de apellido)
def test_validar_apellido_usuario_valido(modelo_personal):
    resultado = modelo_personal.validarApellidoUsuario("Gonzalez")

    assert resultado["status"] is True
    assert resultado["value"] == "Gonzalez"



# CP-PER-06 (prueba negativa de apellido)
def test_validar_apellido_usuario_invalido(modelo_personal):
    resultado = modelo_personal.validarApellidoUsuario("Gonzalez123")

    assert resultado["status"] is False
    assert "no puede contener caracteres especiales" in resultado["text"]



# CP-PER-07 (prueba positiva de teléfono)
def test_validar_telefono_valido(modelo_personal):
    resultado = modelo_personal.validarTelefono("04121234567")

    assert resultado["status"] is True



# CP-PER-08 (prueba negativa de teléfono)
def test_validar_telefono_invalido(modelo_personal):
    resultado = modelo_personal.validarTelefono("telefono")

    assert resultado["status"] is False
    assert "Teléfono no válido" in resultado["text"]



# CP-PER-09 (prueba positiva de dirección)
def test_validar_direccion_valida(modelo_personal):
    resultado = modelo_personal.validarDireccion("Av. Principal 123")

    assert resultado["status"] is True
    assert resultado["value"] == "Av. Principal 123"



# CP-PER-10 (prueba negativa de dirección)
def test_validar_direccion_invalida(modelo_personal):
    resultado = modelo_personal.validarDireccion("A")

    assert resultado["status"] is False
    assert "Dirección no válida" in resultado["text"]



# CP-PER-11 (prueba positiva de correo válido)
def test_validar_correo_valido(modelo_personal):
    resultado = modelo_personal.validarCorreo("branj2205@gmail.com")

    assert resultado ["status"] is True
    assert resultado ["value"] == "branj2205@gmail.com"



# CP-PER-12 (prueba positiva de correo vacío opcional)
def test_validar_correo_vacio_opcional(modelo_personal):
    resultado = modelo_personal.validarCorreo("")

    assert resultado["status"] is True
    assert resultado["value"] == ""



# CP-PER-13 (prueba negativa: correo inválido)
def test_validar_correo_invalido(modelo_personal):
    resultado = modelo_personal.validarCorreo("branj2205@empresa.com")

    assert resultado["status"] is False
    assert "Ingrese un correo válido" in resultado["text"]



# CP-PER-14 (prueba positiva de rol válido)
def test_validar_rol_valido(modelo_personal):
    resultado = modelo_personal.validarCodRol("1")
                                        

    assert resultado["status"] is True
    assert resultado["value"] == 1



# CP-PER-15 (prueba negativa de rol)
def test_validar_rol_invalido(modelo_personal):
    resultado = modelo_personal.validarCodRol("0")

    assert resultado["status"] is False
    assert "Rol no válido" in resultado["text"]



# CP-PER-16 (prueba positiva de registro de personal)
def test_registrar_personal_valido(modelo_personal):
    modelo_personal.cedula = "1234567890"
    modelo_personal.nombre_usuario = "Jessica"
    modelo_personal.apellido_usuario = "Gonzalez"
    modelo_personal.telefono = "04121234567"
    modelo_personal.direccion = "Av. Principal 123"
    modelo_personal.correo = "jessica@gmail.com"
    modelo_personal.cod_rol = 1

    resultado = modelo_personal.registrar()

    assert resultado == 1
    modelo_personal.conexion.commit.assert_called_once()



# CP-PER-17 (prueba negativa de registro de personal)
def test_registrar_personal_error(modelo_personal):
    modelo_personal.conexion.cursor.return_value.execute.side_effect = Exception(
        "fallo simulado"
    )

    resultado = modelo_personal.registrar()

    assert resultado is False
    modelo_personal.conexion.rollback.assert_called_once()



# CP-PER-18 (prueba positiva de edición de personal)
def test_editar_personal_valido(modelo_personal):
    modelo_personal.cedula = "1234567890"
    modelo_personal.nombre_usuario = "Jessica"
    modelo_personal.apellido_usuario = "Gonzalez"
    modelo_personal.telefono = "04121234567"
    modelo_personal.direccion = "Av. Principal 123"
    modelo_personal.correo = "jessica@gmail.com"
    modelo_personal.status = 1
    modelo_personal.cod_rol = 1

    resultado = modelo_personal.editar()

    assert resultado == 1
    modelo_personal.conexion.commit.assert_called_once()



# CP-PER-19 (prueba negativa de edición de personal)
def test_editar_personal_error(modelo_personal):
    modelo_personal.conexion.cursor.return_value.execute.side_effect = Exception(
        "fallo simulado"
    )

    resultado = modelo_personal.editar()

    assert resultado is False
    modelo_personal.conexion.rollback.assert_called_once()



# CP-PER-20 (prueba negativa: no elimina personal asociado a especialista)
def test_eliminar_personal_asociado_especialista(modelo_personal):
    modelo_personal.conexion.cursor.return_value.fetchone.return_value = (1,)

    resultado = modelo_personal.eliminar("1234567890")

    assert resultado == -2
    modelo_personal.conexion.commit.assert_not_called()



# CP-PER-21 (prueba positiva de eliminación de personal)
def test_eliminar_personal_no_asociado(modelo_personal):
    modelo_personal.conexion.cursor.return_value.fetchone.return_value = (0,)

    resultado = modelo_personal.eliminar("1234567890")

    assert resultado == 1
    modelo_personal.conexion.commit.assert_called_once()



# CP-PER-22 (prueba de error al eliminar personal)
def test_eliminar_personal_error(modelo_personal):
    modelo_personal.conexion.cursor.return_value.execute.side_effect = Exception(
        "fallo simulado"
    )

    resultado = modelo_personal.eliminar("1234567890")

    assert resultado is False
    modelo_personal.conexion.rollback.assert_called_once()