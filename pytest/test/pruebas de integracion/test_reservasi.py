
import sys
from pathlib import Path
from datetime import datetime, timedelta

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.reservas import ReservasModelo


# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_reservasi.py::test_editar_reserva_y_disponibilidad" -vv -s --tb=long

# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_reservasi.py::test_eliminar_reserva_activa" -vv -s --tb=long

# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_reservasi.py::test_eliminar_reserva_cancelada" -vv -s --tb=long

@pytest.fixture
def datos_reserva():
    modelo = ReservasModelo()
    cursor = modelo.conexion.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                s.cod_servicio,
                s.fecha,
                s.hora,
                s.cedula_especialista,
                s.status
            FROM sac.servicio s
            INNER JOIN sac.disponibilidad_especialista d
                ON d.fecha_disponibilidad = s.fecha
                AND d.hora_disponibilidad = s.hora
                AND d.cedula_especialista = s.cedula_especialista
            WHERE s.fecha = CURDATE()
            AND s.status = 1
            ORDER BY s.hora
            LIMIT 1
        """)

        reserva = cursor.fetchone()

        if not reserva:
            pytest.skip(
                "No existe una reserva activa de hoy con disponibilidad correspondiente."
            )

        yield {
            "modelo": modelo,
            "cod_servicio": reserva["cod_servicio"],
            "fecha_anterior": reserva["fecha"],
            "hora_anterior": reserva["hora"],
            "especialista": reserva["cedula_especialista"]
        }

    finally:
        cursor.close()
        modelo.conexion.close()


def test_editar_reserva_y_disponibilidad(datos_reserva):
    modelo = datos_reserva["modelo"]

    cod_servicio = datos_reserva["cod_servicio"]
    fecha_anterior = datos_reserva["fecha_anterior"]
    hora_anterior = datos_reserva["hora_anterior"]
    especialista = datos_reserva["especialista"]

    # Convertir la hora y sumarle 30 minutos
    hora_convertida = datetime.strptime(hora_anterior, "%I:%M %p")
    hora_nueva = (
        hora_convertida + timedelta(minutes=30)
    ).strftime("%I:%M %p").lower()

    # Editar la reserva
    modelo.cod_servicio = cod_servicio
    modelo.fecha_reserva = fecha_anterior
    modelo.hora_reserva = hora_nueva
    modelo.status = 0

    resultado = modelo.editar()

    assert resultado == 1

    cursor = modelo.conexion.cursor(dictionary=True)

    try:
        # Comprobar los cambios en la reserva
        cursor.execute("""
            SELECT fecha, hora, status
            FROM sac.servicio
            WHERE cod_servicio = %s
        """, (cod_servicio,))

        reserva_actualizada = cursor.fetchone()

        assert reserva_actualizada is not None
        assert reserva_actualizada["fecha"] == fecha_anterior
        assert reserva_actualizada["hora"] == hora_nueva
        assert reserva_actualizada["status"] == 0

        # Comprobar los cambios en la disponibilidad
        cursor.execute("""
            SELECT
                fecha_disponibilidad,
                hora_disponibilidad,
                status
            FROM sac.disponibilidad_especialista
            WHERE fecha_disponibilidad = %s
            AND hora_disponibilidad = %s
            AND cedula_especialista = %s
        """, (fecha_anterior, hora_nueva, especialista))

        disponibilidad_actualizada = cursor.fetchone()

        assert disponibilidad_actualizada is not None
        assert disponibilidad_actualizada["fecha_disponibilidad"] == fecha_anterior
        assert disponibilidad_actualizada["hora_disponibilidad"] == hora_nueva
        assert disponibilidad_actualizada["status"] == 0

    finally:
        cursor.close()

# CP-RES-02 (prueba positiva: Elimina una reserva cancelada y elimina su disponibilidad correspondiente)

def test_eliminar_reserva_cancelada():
    modelo = ReservasModelo()

    try:
        cursor = modelo.conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.cod_servicio
            FROM sac.servicio s
            INNER JOIN sac.disponibilidad_especialista d
                ON d.fecha_disponibilidad = s.fecha
                AND d.hora_disponibilidad = s.hora
                AND d.cedula_especialista = s.cedula_especialista
            WHERE s.status = 0
            ORDER BY s.cod_servicio
            LIMIT 1
        """)
        reserva = cursor.fetchone()
        cursor.close()

        assert reserva is not None

        cod_servicio = reserva["cod_servicio"]

        resultado = modelo.eliminar(cod_servicio)
        assert resultado == "eliminado"

        cursor = modelo.conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.status,
                   d.cedula_especialista AS disponibilidad
            FROM sac.servicio s
            LEFT JOIN sac.disponibilidad_especialista d
                ON d.fecha_disponibilidad = s.fecha
                AND d.hora_disponibilidad = s.hora
                AND d.cedula_especialista = s.cedula_especialista
            WHERE s.cod_servicio = %s
        """, (cod_servicio,))
        reserva_actual = cursor.fetchone()
        cursor.close()

        assert reserva_actual is not None
        assert reserva_actual["status"] == 2
        assert reserva_actual["disponibilidad"] is None

    finally:
        modelo.conexion.close()






# CP-RES-03 (prueba negativa: Rechaza la eliminación de una reserva activa)

def test_eliminar_reserva_activa():
    modelo = ReservasModelo()

    try:
        cursor = modelo.conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT cod_servicio
            FROM sac.servicio
            WHERE status = 1
            ORDER BY cod_servicio
            LIMIT 1
        """)
        reserva = cursor.fetchone()
        cursor.close()

        assert reserva is not None

        cod_servicio = reserva["cod_servicio"]

        resultado = modelo.eliminar(cod_servicio)
        assert resultado == "activo"

        cursor = modelo.conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT status
            FROM sac.servicio
            WHERE cod_servicio = %s
        """, (cod_servicio,))
        reserva_actual = cursor.fetchone()
        cursor.close()

        assert reserva_actual is not None
        assert reserva_actual["status"] == 1

    finally:
        modelo.conexion.close()