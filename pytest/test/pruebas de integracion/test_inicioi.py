
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.inicio import InicioModelo
from app import app

# python -m pytest "pytest\test\pruebas de integracion\test_inicioi.py" -v

 # python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_inicioi.py::test_registrar" -vv -s --tb=long
# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_inicioi.py::test_registrar_reserva_cliente_inexistente" -vv -s --tb=long

@pytest.fixture
def datos_reserva():
    modelo = InicioModelo()
    cursor = modelo.conexion.cursor(dictionary=True)

    fecha = date.today().isoformat()
    hora = "11:00 am"

    cursor.execute("""
        SELECT cedula
        FROM seguridad.usuario
        WHERE cod_rol = 3 AND status = 1
        LIMIT 1
    """)
    cliente = cursor.fetchone()

    cursor.execute("""
        SELECT e.cedula_especialista
        FROM especialista e
        WHERE e.status = 1
        AND NOT EXISTS (
            SELECT 1
            FROM servicio s
            WHERE s.cedula_especialista = e.cedula_especialista
            AND s.fecha = %s
            AND s.hora = %s
            AND s.status = 1
        )
        LIMIT 1
    """, (fecha, hora))
    especialista = cursor.fetchone()

    cursor.execute("""
        SELECT cod_tipo_servicio
        FROM tipo_servicio
        WHERE status = 1
        LIMIT 3
    """)
    servicios = cursor.fetchall()

    cursor.close()

    productos = modelo.obtenerProductosDisponibles()
    producto = next(
        (p for p in productos if p["stock"] >= 3),
        None
    )

    if not cliente or not especialista or len(servicios) != 3 or not producto:
        modelo.conexion.close()
        pytest.fail("No existen datos suficientes para registrar la reserva.")

    datos = {
        "modelo": modelo,
        "cedula": cliente["cedula"],
        "cedula_especialista": especialista["cedula_especialista"],
        "servicios": [s["cod_tipo_servicio"] for s in servicios],
        "cod_producto": producto["cod_producto"],
        "stock_inicial": producto["stock"],
        "cantidad": 3,
        "fecha": fecha,
        "hora": hora,
        "descripcion": "Reserva de prueba CP-INI-01"
    }

    try:
        yield datos
    finally:
       
        modelo.conexion.close()


@pytest.fixture
def reserva_registrada(datos_reserva):
    modelo = datos_reserva["modelo"]

    with app.app_context():
        resultado = modelo.registrarReserva(
            datos_reserva["cedula"],
            datos_reserva["servicios"],
            datos_reserva["fecha"],
            datos_reserva["hora"],
            datos_reserva["cedula_especialista"],
            None,
            [
                {
                    "cod_producto": datos_reserva["cod_producto"],
                    "cantidad": datos_reserva["cantidad"]
                }
            ],
            datos_reserva["descripcion"]
        )

    assert resultado["success"] is True, resultado
    assert resultado["cod_servicio"]

    return resultado["cod_servicio"]


def test_registrar(datos_reserva, reserva_registrada):
    modelo = datos_reserva["modelo"]
    cod_servicio = reserva_registrada
    cod_producto = datos_reserva["cod_producto"]

    reservas = modelo.consultarConClientes(datos_reserva["cedula"])

    reserva = next(
        (r for r in reservas if r["cod_servicio"] == cod_servicio),
        None
    )

    assert reserva is not None
    assert reserva["estado_reserva"] == 1
    assert str(reserva["fecha_reserva"]) == datos_reserva["fecha"]
    assert reserva["hora_reserva"] == datos_reserva["hora"]

    # Validar los servicios asociados.
    servicios_registrados = modelo.obtenerServiciosDeReserva(cod_servicio)

    assert servicios_registrados

    # Verificar los detalles de la reserva.
    cursor = modelo.conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT cod_tipo_servicio, cod_producto
        FROM detalle_servicio
        WHERE cod_servicio = %s
    """, (cod_servicio,))

    detalles = cursor.fetchall()

    assert len(detalles) == 3
    assert {
        detalle["cod_tipo_servicio"] for detalle in detalles
    } == set(datos_reserva["servicios"])

    assert all(
        detalle["cod_producto"] == cod_producto
        for detalle in detalles
    )

    # Verificar el conteo de productos.
    cursor.execute("""
        SELECT conteo, status
        FROM conteo_stock
        WHERE cod_producto = %s
        ORDER BY cod_conteo DESC
        LIMIT 1
    """, (cod_producto,))

    conteo = cursor.fetchone()

    assert conteo is not None
    assert conteo["conteo"] == datos_reserva["cantidad"]
    assert conteo["status"] == 1

    # Verificar el descuento del inventario.
    cursor.execute("""
        SELECT stock
        FROM producto
        WHERE cod_producto = %s
    """, (cod_producto,))

    producto = cursor.fetchone()

    assert producto is not None
    assert producto["stock"] == (
        datos_reserva["stock_inicial"] - datos_reserva["cantidad"]
    )

    cursor.close()



def test_registrar_reserva_cliente_inexistente(datos_reserva):
    modelo = datos_reserva["modelo"]

    resultado = modelo.registrarReserva(
        "999999999999",
        datos_reserva["servicios"],
        datos_reserva["fecha"],
        datos_reserva["hora"],
        datos_reserva["cedula_especialista"],
        None,
        [
            {
                "cod_producto": datos_reserva["cod_producto"],
                "cantidad": datos_reserva["cantidad"]
            }
        ],
        "Prueba de reserva con cliente inexistente"
    )

    assert resultado["success"] is False



