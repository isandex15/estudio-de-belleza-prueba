
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.inicio import InicioModelo

# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_reservaclientei.py::test_registrar_reserva_cliente" -vv -s --tb=long

# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_reservaclientei.py::test_registrar_reserva_cliente_inexistente" -vv -s --tb=long

# python -m pytest "pytest\test\pruebas de integracion\test_reservaclientei.py" -v


@pytest.fixture
def datos_reserva():
    modelo = InicioModelo()
    cursor = modelo.conexion.cursor()

    cursor.execute("""
        SELECT
            (SELECT cedula
             FROM seguridad.usuario
             WHERE cod_rol=3 AND status=1
             LIMIT 1),
            (SELECT cedula_especialista
             FROM sac.especialista
             WHERE status=1
             LIMIT 1),
            (SELECT cod_tipo_servicio
             FROM sac.tipo_servicio
             WHERE status=1
             LIMIT 1)
    """)

    datos = cursor.fetchone()
    cursor.close()

    assert datos is not None
    assert all(dato is not None for dato in datos)

    reserva = {
        "modelo": modelo,
        "cedula": datos[0],
        "especialista": datos[1],
        "servicio": [datos[2]],
        "fecha": date.today(),
        "hora": "09:00 AM"
    }

    yield reserva

    modelo.conexion.close()


# CP-RESC-0: Registrar una reserva de cliente.
def test_registrar_reserva_cliente(datos_reserva):
    resultado = datos_reserva["modelo"].registrarReservadeclientes(
        datos_reserva["cedula"],
        datos_reserva["servicio"],
        datos_reserva["fecha"],
        datos_reserva["hora"],
        datos_reserva["especialista"]
    )

    assert resultado["success"] is True
    assert resultado["cod_servicio"] > 0


# CP-RESC-0: Rechazar el registro con un cliente inexistente.
def test_registrar_reserva_cliente_inexistente(datos_reserva):
    resultado = datos_reserva["modelo"].registrarReservadeclientes(
        "999999999999",
        datos_reserva["servicio"],
        datos_reserva["fecha"],
        datos_reserva["hora"],
        datos_reserva["especialista"]
    )

    assert resultado["success"] is False

