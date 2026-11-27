import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.unidad import UnidadModelo

# python -m pytest ".\pytest\test\puebas unitarias\test_unidad.py::test_validar_unidad_rechaza_nombre_vacio" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_unidad.py::test_validar_unidad_rechaza_presentacion_vacia" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_unidad.py::test_validar_unidad_rechaza_medida_vacia" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_unidad.py::test_validar_unidad_rechaza_nombre_con_letras" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_unidad.py::test_validar_unidad_acepta_nombre_con_solo_numeros" -q

# python -m pytest ".\pytest\test\puebas unitarias\test_unidad.py" -q



@pytest.fixture
def modelo_unidad(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(conexion_module.mysql.connector, "connect", lambda **kwargs: fake_conn)
    return UnidadModelo()


# CP-UNI-01 (prueba negativa: rechaza registrar una unidad cuando el nombre está vacío)
def test_validar_unidad_rechaza_nombre_vacio(modelo_unidad):
    resultado = modelo_unidad.validarNombreUnidad("", 1, 1)

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "El nombre de la unidad es obligatorio" in resultado["text"]


# CP-UNI-02 (prueba negativa: rechaza registrar una unidad cuando la presentación está vacía)
def test_validar_unidad_rechaza_presentacion_vacia(modelo_unidad):
    resultado = modelo_unidad.validarNombreUnidad("12", "", 1)

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "La presentación es obligatoria" in resultado["text"]


# CP-UNI-03 (prueba negativa: rechaza registrar una unidad cuando la medida está vacía)
def test_validar_unidad_rechaza_medida_vacia(modelo_unidad):
    resultado = modelo_unidad.validarNombreUnidad("12", 1, "")

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "La medida es obligatoria" in resultado["text"]


# CP-UNI-04 (prueba negativa: rechaza registrar una unidad cuando el nombre contiene letras)
def test_validar_unidad_rechaza_nombre_con_letras(modelo_unidad):
    resultado = modelo_unidad.validarNombreUnidad("Unidad12", 1, 1)

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "La unidad solo puede contener números" in resultado["text"]


# CP-UNI-05 (prueba positiva:  registrar una unidad cuando el nombre contiene solamente números)
def test_validar_unidad_acepta_nombre_con_solo_numeros(modelo_unidad):
    resultado = modelo_unidad.validarNombreUnidad("12", 1, 1)

    assert resultado["status"] is True



# CP-UNI-06 (prueba negativa: rechaza una unidad cuando el nombre contiene solamente espacios)
def test_validar_unidad_rechaza_nombre_con_espacios(modelo_unidad):
    resultado = modelo_unidad.validarNombreUnidad("   ", 1, 1)

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "El nombre de la unidad es obligatorio" in resultado["text"]


# CP-UNI-07 (prueba negativa: rechaza una unidad cuando el nombre contiene caracteres especiales)
def test_validar_unidad_rechaza_nombre_con_caracteres_especiales(modelo_unidad):
    resultado = modelo_unidad.validarNombreUnidad("12.5", 1, 1)

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "La unidad solo puede contener números" in resultado["text"]


# CP-UNI-08 (prueba negativa: rechaza una unidad cuando el código de presentación contiene solamente espacios)
def test_validar_unidad_rechaza_presentacion_con_espacios(modelo_unidad):
    resultado = modelo_unidad.validarNombreUnidad("12", "   ", 1)

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "La presentación es obligatoria" in resultado["text"]


# CP-UNI-09 (prueba negativa: rechaza una unidad cuando el código de medida contiene solamente espacios)
def test_validar_unidad_rechaza_medida_con_espacios(modelo_unidad):
    resultado = modelo_unidad.validarNombreUnidad("12", 1, "   ")

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "La medida es obligatoria" in resultado["text"]
