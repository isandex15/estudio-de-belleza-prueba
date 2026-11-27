
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.presentacion import PresentacionModelo
# python -m pytest ".\pytest\test\puebas unitarias\test_presentacion.py::test_validar_presentacion_rechaza_numeros_y_caracteres_especiales" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_presentacion.py::test_validar_presentacion_rechaza_presentacion_vacia" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_presentacion.py::test_editar_presentacion_correctamente" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_presentacion.py::test_eliminar_presentacion_asociada" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_presentacion.py::test_eliminar_presentacion_sin_asociaciones" -q

# python -m pytest ".\pytest\test\puebas unitarias\test_presentacion.py" -q


@pytest.fixture
def modelo_presentacion(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(conexion_module.mysql.connector, "connect", lambda **kwargs: fake_conn)
    return PresentacionModelo()


# CP-PRE-0 (prueba negativa: rechaza una registrar presentación que contiene números o caracteres especiales) 
def test_validar_presentacion_rechaza_numeros_y_caracteres_especiales(modelo_presentacion):
    resultado = modelo_presentacion.validarPresentacion("Caja@123")

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "no puede contener números ni caracteres especiales" in resultado["text"]


# CP-PRE-0 (prueba negativa: impide registrar una presentación vacía) 
def test_validar_presentacion_rechaza_presentacion_vacia(modelo_presentacion):
    resultado = modelo_presentacion.validarPresentacion("")

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "obligatoria" in resultado["text"]



# CP-PRE-0 (prueba positiva: edita correctamente el nombre de una presentación existente)
def test_editar_presentacion_correctamente(modelo_presentacion):
    modelo_presentacion.cod_presentacion = 1
    modelo_presentacion.presentacion = "Botella"
    modelo_presentacion.status = 1

    resultado = modelo_presentacion.editar()

    assert resultado == 1
    modelo_presentacion.conexion.commit.assert_called_once()


# CP-PRE-0 (prueba negativa: impide eliminar una presentación asociada a una unidad)
def test_eliminar_presentacion_asociada(modelo_presentacion):
    mock_cursor = modelo_presentacion.conexion.cursor.return_value
    mock_cursor.fetchone.side_effect = [(1,), (2,)]

    resultado = modelo_presentacion.eliminar(1)

    assert resultado == -2
    assert mock_cursor.execute.call_count == 2
    modelo_presentacion.conexion.commit.assert_not_called()


# CP-PRE-0 (prueba positiva: elimina una presentación existente que no esté asociada a ninguna unidad)
def test_eliminar_presentacion_sin_asociaciones(modelo_presentacion):
    mock_cursor = modelo_presentacion.conexion.cursor.return_value
    mock_cursor.fetchone.side_effect = [(1,), (0,)]
    mock_cursor.rowcount = 1

    resultado = modelo_presentacion.eliminar(1)

    assert resultado == 1
    assert mock_cursor.execute.call_count == 3
    modelo_presentacion.conexion.commit.assert_called_once()


# CP-PRE-06 (prueba negativa: rechaza una presentación que contiene solo espacios)
def test_validar_presentacion_rechaza_presentacion_con_solo_espacios(modelo_presentacion):
    resultado = modelo_presentacion.validarPresentacion("   ")

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "obligatoria" in resultado["text"]
