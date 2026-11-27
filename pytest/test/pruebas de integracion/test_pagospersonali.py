from datetime import date, datetime
import secrets

import pytest

from admin.config.config import DB_SEGURIDAD_NAME
from admin.modelo.pagospersonal import PagospersonalModelo


@pytest.fixture
def datos_pago_personal(ready_test_database):
    modelo = PagospersonalModelo()
    cursor = modelo.conexion.cursor(dictionary=True)
    cursor.execute(
        f"""
        SELECT s.cod_servicio
        FROM servicio s
        INNER JOIN {DB_SEGURIDAD_NAME}.usuario u
            ON u.cedula = s.cedula
        WHERE s.status = 1
          AND NOT EXISTS (
              SELECT 1
              FROM pago_personal pp
              WHERE pp.cod_servicio = s.cod_servicio
          )
        ORDER BY s.cod_servicio
        LIMIT 1
        """
    )
    servicio = cursor.fetchone()
    cursor.close()

    if not servicio:
        modelo.conexion.close()
        pytest.fail(
            "La base de datos de pruebas requiere un servicio activo "
            "sin pagos de personal."
        )

    sufijo = secrets.token_hex(6).upper()
    nombre_banco = f"IT{sufijo}"
    referencia = f"IT-{sufijo}"
    cod_banco = modelo.crear_banco(nombre_banco)
    if not cod_banco:
        modelo.conexion.close()
        pytest.fail("No se pudo crear el banco temporal para la prueba.")

    datos = {
        "modelo": modelo,
        "cod_servicio": servicio["cod_servicio"],
        "cod_banco": cod_banco,
        "nombre_banco": nombre_banco,
        "referencia": referencia,
    }

    try:
        yield datos
    finally:
        cursor = modelo.conexion.cursor()
        cursor.execute(
            "DELETE FROM pago_personal WHERE referencia_pago = %s",
            (datos["referencia"],),
        )
        cursor.execute(
            "DELETE FROM banco WHERE cod_banco = %s",
            (datos["cod_banco"],),
        )
        modelo.conexion.commit()
        cursor.close()
        modelo.conexion.close()


@pytest.fixture
def pago_personal_registrado(datos_pago_personal):
    modelo = datos_pago_personal["modelo"]
    modelo.fecha_pago = date.today().isoformat()
    modelo.hora_pago = datetime.now().strftime("%H:%M:%S")
    modelo.porcentaje = 25
    modelo.status = 1
    modelo.cod_servicio = datos_pago_personal["cod_servicio"]
    modelo.comprobante = "integracion_personal.png"
    modelo.cod_banco = datos_pago_personal["cod_banco"]
    modelo.referencia_pago = datos_pago_personal["referencia"]

    assert modelo.registrar() is True
    cursor = modelo.conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT cod_pago_personal, status, cod_servicio, cod_banco
        FROM pago_personal
        WHERE referencia_pago = %s
        """,
        (datos_pago_personal["referencia"],),
    )
    pago = cursor.fetchone()
    cursor.close()
    assert pago is not None
    datos_pago_personal["pago"] = pago
    return datos_pago_personal


# CP-PP-16 (Prueba positiva de registro de pago personal)
def test_registrar_pago_personal(pago_personal_registrado):
    datos = pago_personal_registrado
    pago = datos["pago"]

    assert pago["status"] == 1
    assert pago["cod_servicio"] == datos["cod_servicio"]
    assert pago["cod_banco"] == datos["cod_banco"]


# CP-PP-17 (Prueba positiva de consulta y cálculo de comisión de pago personal)
def test_consultar_y_calcular_comision_pago_personal(pago_personal_registrado):
    datos = pago_personal_registrado
    modelo = datos["modelo"]
    pago = datos["pago"]

    registros = modelo.consultar()
    registro = next(
        item
        for item in registros
        if item["cod_pago_personal"] == pago["cod_pago_personal"]
    )
    assert float(registro["monto_a_pagar"]) >= 0
    assert modelo.calcular_comision(datos["cod_servicio"], 25) >= 0


# CP-PP-18 (Prueba positiva de anulación de pago personal)
def test_anular_pago_personal(pago_personal_registrado):
    datos = pago_personal_registrado
    modelo = datos["modelo"]
    cod_pago_personal = datos["pago"]["cod_pago_personal"]

    assert modelo.anular(cod_pago_personal) is True

    cursor = modelo.conexion.cursor()
    cursor.execute(
        "SELECT status FROM pago_personal WHERE cod_pago_personal = %s",
        (cod_pago_personal,),
    )
    estado = cursor.fetchone()
    cursor.close()
    assert estado[0] == 0


# CP-PP-19 (Prueba negativa: rechaza anular nuevamente un pago personal)
def test_rechazar_anulacion_repetida_pago_personal(pago_personal_registrado):
    datos = pago_personal_registrado
    modelo = datos["modelo"]
    cod_pago_personal = datos["pago"]["cod_pago_personal"]

    assert modelo.anular(cod_pago_personal) is True
    assert modelo.anular(cod_pago_personal) is False
