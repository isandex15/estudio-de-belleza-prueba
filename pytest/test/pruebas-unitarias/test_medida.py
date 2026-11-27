import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.unidadmedida import UnidadmedidaModelo

# python -m pytest ".\pytest\test\puebas unitarias\test_medida.py::test_validar_medida_rechaza_medida_vacia" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_medida.py::test_registrar_medida" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_medida.py::test_editar_medida" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_medida.py::test_validar_medida_rechaza_numeros" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_medida.py::test_editar_estado_medida" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_medida.py::test_eliminar_medida_asociada" -q
# python -m pytest ".\pytest\test\puebas unitarias\test_medida.py::test_eliminar_medida_sin_asociaciones" -q

# python -m pytest ".\pytest\test\puebas unitarias\test_medida.py" -q


@pytest.fixture
def modelo_medida(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(conexion_module.mysql.connector, "connect", lambda **kwargs: fake_conn)
    return UnidadmedidaModelo()


# CP-MED-0 (prueba negativa: rechaza el registro con unidad de medida vacía)
def test_validar_medida_rechaza_medida_vacia(modelo_medida):
    resultado = modelo_medida.validarMedida("")

    assert resultado["status"] is False
    assert resultado["icon"] == "warning"
    assert "obligatoria" in resultado["text"]


# CP-MED-0 (prueba positiva: registra una unidad de medida correctamente) 
def test_registrar_medida(monkeypatch, modelo_medida):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    monkeypatch.setattr(modelo_medida, "conexion", mock_conn)

    modelo_medida.medida = "Kilogramo"

    resultado = modelo_medida.registrar()

    assert resultado == 1

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO medida (medida, status) VALUES (%s, 1)",
        ("Kilogramo",)
    )

    mock_conn.commit.assert_called_once()    



# CP-MED-0 (prueba positiva: edita una unidad de medida correctamente) 
def test_editar_medida(monkeypatch, modelo_medida):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    monkeypatch.setattr(modelo_medida, "conexion", mock_conn)

    modelo_medida.cod_medida = 1
    modelo_medida.medida = "Litro"
    modelo_medida.status = 1

    resultado = modelo_medida.editar()

    assert resultado == 1

    sql, parametros = mock_cursor.execute.call_args[0]

    assert parametros == ("Litro", 1, 1)



# CP-MED-0 (prueba negativa: rechaza el registro de una unidad de medida con números)
def test_validar_medida_rechaza_numeros(modelo_medida):
    resultado = modelo_medida.validarMedida("Metro2")

    assert resultado["status"] is False
    assert resultado["title"] == "Dato inválido"


# CP-MED-0 (prueba positiva: edita el estado de una unidad de medida existente)
def test_editar_estado_medida(modelo_medida):
    modelo_medida.cod_medida = 1
    modelo_medida.medida = "Kilogramo"
    modelo_medida.status = 0

    resultado = modelo_medida.editar()

    assert resultado == 1
    modelo_medida.conexion.commit.assert_called_once()


# CP-MED-0(prueba negativa: impide eliminar una unidad de medida asociada a una unidad)
def test_eliminar_medida_asociada(modelo_medida):
    mock_cursor = modelo_medida.conexion.cursor.return_value
    mock_cursor.fetchone.side_effect = [(1,), (2,)]

    resultado = modelo_medida.eliminar(1)

    assert resultado == -2
    assert mock_cursor.execute.call_count == 2
    modelo_medida.conexion.commit.assert_not_called()


# CP-MED-0 (prueba positiva: elimina una unidad de medida existente que no esté asociada a ninguna unidad)
def test_eliminar_medida_sin_asociaciones(modelo_medida):
    mock_cursor = modelo_medida.conexion.cursor.return_value
    mock_cursor.fetchone.side_effect = [(1,), (0,)]
    mock_cursor.rowcount = 1

    resultado = modelo_medida.eliminar(1)

    assert resultado == 1
    assert mock_cursor.execute.call_count == 3
    modelo_medida.conexion.commit.assert_called_once()



    