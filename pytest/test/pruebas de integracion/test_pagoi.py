from datetime import date
import secrets

import pytest

from admin.config.config import DB_SEGURIDAD_NAME
from admin.modelo.pagos import PagosModelo


def _nombre_archivo():
    return "integracion_" + secrets.token_hex(6) + ".png"


@pytest.fixture
def datos_pago(ready_test_database):
    modelo = PagosModelo()
    cursor = modelo.conexion.cursor(dictionary=True)
    cursor.execute(
        f"""
        SELECT
            s.cod_servicio,
            (
                SELECT cod_tipo_pago
                FROM tipo_pago
                WHERE status = 1
                ORDER BY cod_tipo_pago
                LIMIT 1
            ) AS cod_tipo_pago,
            (
                SELECT cod_moneda
                FROM moneda
                WHERE status = 1
                ORDER BY cod_moneda
                LIMIT 1
            ) AS cod_moneda
        FROM servicio s
        WHERE s.status = 1
          AND EXISTS (
              SELECT 1
              FROM {DB_SEGURIDAD_NAME}.usuario u
              WHERE u.cedula = s.cedula
          )
          AND EXISTS (
              SELECT 1
              FROM detalle_servicio ds
              WHERE ds.cod_servicio = s.cod_servicio
          )
          AND NOT EXISTS (
              SELECT 1
              FROM pago p
              WHERE p.cod_servicio = s.cod_servicio
          )
          AND EXISTS (SELECT 1 FROM tipo_pago WHERE status = 1)
          AND EXISTS (SELECT 1 FROM moneda WHERE status = 1)
        ORDER BY s.cod_servicio
        LIMIT 1
        """
    )
    fila = cursor.fetchone()
    cursor.close()

    if not fila:
        modelo.conexion.close()
        pytest.fail(
            "La base de datos de pruebas requiere un servicio activo con "
            "detalles, sin pagos y con un tipo de pago y una moneda activos."
        )

    monto = modelo.obtener_monto_servicio(fila["cod_servicio"])
    if not monto or monto <= 0:
        modelo.conexion.close()
        pytest.fail("El servicio elegido debe tener un monto mayor a cero.")

    datos = {
        "modelo": modelo,
        "cod_servicio": fila["cod_servicio"],
        "cod_tipo_pago": fila["cod_tipo_pago"],
        "cod_moneda": fila["cod_moneda"],
        "monto": monto,
        "comprobante": _nombre_archivo(),
    }

    try:
        yield datos
    finally:
        cursor = modelo.conexion.cursor()
        cursor.execute(
            "SELECT cod_pago FROM pago WHERE comprobante_pago = %s",
            (datos["comprobante"],),
        )
        codigos_pago = [row[0] for row in cursor.fetchall()]
        for cod_pago in codigos_pago:
            cursor.execute(
                "DELETE FROM detalle_pago WHERE cod_pago = %s",
                (cod_pago,),
            )
            cursor.execute("DELETE FROM pago WHERE cod_pago = %s", (cod_pago,))
        modelo.conexion.commit()
        cursor.close()
        modelo.conexion.close()


@pytest.fixture
def pago_registrado(datos_pago):
    modelo = datos_pago["modelo"]
    modelo.cod_servicio = datos_pago["cod_servicio"]
    modelo.fecha_pago = date.today().isoformat()
    modelo.monto = datos_pago["monto"]
    modelo.cod_tipo_pago = datos_pago["cod_tipo_pago"]
    modelo.cod_moneda = datos_pago["cod_moneda"]
    modelo.comprobante_pago = datos_pago["comprobante"]

    resultado = modelo.registrar_con_detalle()
    assert resultado["success"] is True, resultado

    pagos = modelo.consultar_por_servicio(datos_pago["cod_servicio"])
    assert len(pagos) == 1
    datos_pago["pago"] = pagos[0]
    return datos_pago


# CP-PAG-08 (Prueba positiva de registro de pago)
def test_registrar_pago(pago_registrado):
    datos = pago_registrado
    modelo = datos["modelo"]
    pago = datos["pago"]
    assert pago["status"] == 1

    cursor = modelo.conexion.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT cantidad, cod_tipo_pago, cod_moneda
        FROM detalle_pago
        WHERE cod_pago = %s
        """,
        (pago["cod_pago"],),
    )
    detalle = cursor.fetchone()
    cursor.close()
    assert int(detalle["cantidad"]) == 1
    assert detalle["cod_tipo_pago"] == datos["cod_tipo_pago"]
    assert detalle["cod_moneda"] == datos["cod_moneda"]


# CP-PAG-09 (Prueba positiva de consulta de pago)
def test_consultar_pago(pago_registrado):
    datos = pago_registrado
    modelo = datos["modelo"]
    cod_pago = datos["pago"]["cod_pago"]

    pagos = modelo.consultar_por_servicio(datos["cod_servicio"])
    assert len(pagos) == 1
    assert pagos[0]["cod_pago"] == cod_pago
    assert any(pago["cod_pago"] == cod_pago for pago in modelo.consultar())


# CP-PAG-10 (Prueba negativa de rechazo de pago duplicado)
def test_rechazar_pago_duplicado(pago_registrado):
    datos = pago_registrado
    modelo = datos["modelo"]

    resultado_duplicado = modelo.registrar_con_detalle()
    assert resultado_duplicado["success"] is False
    assert len(modelo.consultar_por_servicio(datos["cod_servicio"])) == 1


# CP-PAG-11 (Prueba positiva de anulación de pago)
def test_anular_pago(pago_registrado):
    datos = pago_registrado
    modelo = datos["modelo"]
    cod_pago = datos["pago"]["cod_pago"]

    assert modelo.anular(cod_pago) is True
    pagos = modelo.consultar_por_servicio(datos["cod_servicio"])
    assert pagos[0]["status"] == 0
