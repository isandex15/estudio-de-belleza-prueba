import secrets
import string

import pytest

from admin.modelo.tipopagos import TipopagosModelo


def _nombre_temporal():
    return "IT" + "".join(secrets.choice(string.ascii_lowercase) for _ in range(8))


@pytest.fixture
def datos_tipo_pago(ready_test_database):
    modelo = TipopagosModelo()
    datos = {
        "modelo": modelo,
        "nombres_creados": [],
    }
    try:
        yield datos
    finally:
        cursor = modelo.conexion.cursor()
        for nombre in datos["nombres_creados"]:
            cursor.execute(
                "DELETE FROM tipo_pago WHERE nombre_tipo_pago = %s",
                (nombre,),
            )
        modelo.conexion.commit()
        cursor.close()
        modelo.conexion.close()


@pytest.fixture
def tipo_pago_registrado(datos_tipo_pago):
    modelo = datos_tipo_pago["modelo"]
    nombre_inicial = _nombre_temporal()
    datos_tipo_pago["nombres_creados"].append(nombre_inicial)
    modelo.nombre_tipo_pago = nombre_inicial
    assert modelo.registrar() == 1
    tipo_pago = modelo.buscar(nombre_inicial)
    assert tipo_pago is not None
    assert tipo_pago["status"] == 1
    datos_tipo_pago["tipo_pago"] = tipo_pago
    return datos_tipo_pago


@pytest.fixture
def tipo_pago_editado(tipo_pago_registrado):
    modelo = tipo_pago_registrado["modelo"]
    tipo_pago = tipo_pago_registrado["tipo_pago"]
    nombre_editado = _nombre_temporal()
    tipo_pago_registrado["nombres_creados"].append(nombre_editado)
    modelo.cod_tipo_pago = tipo_pago["cod_tipo_pago"]
    modelo.nombre_tipo_pago = nombre_editado
    modelo.status = 1
    assert modelo.editar() == 1
    tipo_pago_registrado["nombre_editado"] = nombre_editado
    return tipo_pago_registrado


# CP-TP-13 (Prueba positiva de registro de tipo de pago)
def test_registrar_tipo_pago(tipo_pago_registrado):
    assert tipo_pago_registrado["tipo_pago"]["status"] == 1


# CP-TP-14 (Prueba positiva de consulta de tipo de pago)
def test_consultar_tipo_pago(tipo_pago_registrado):
    modelo = tipo_pago_registrado["modelo"]
    tipo_pago = tipo_pago_registrado["tipo_pago"]
    assert any(
        fila["cod_tipo_pago"] == tipo_pago["cod_tipo_pago"]
        for fila in modelo.consultar()
    )


# CP-TP-15 (Prueba positiva de edición de tipo de pago)
def test_editar_tipo_pago(tipo_pago_editado):
    modelo = tipo_pago_editado["modelo"]
    tipo_pago = modelo.buscar(tipo_pago_editado["nombre_editado"])
    assert tipo_pago is not None
    assert tipo_pago["cod_tipo_pago"] == tipo_pago_editado["tipo_pago"]["cod_tipo_pago"]


# CP-TP-16 (Prueba positiva de eliminación de tipo de pago)
def test_eliminar_tipo_pago(tipo_pago_registrado):
    modelo = tipo_pago_registrado["modelo"]
    tipo_pago = tipo_pago_registrado["tipo_pago"]
    assert modelo.eliminar(tipo_pago["cod_tipo_pago"]) == 1
    assert modelo.buscar(tipo_pago["nombre_tipo_pago"]) is None


# CP-TP-17 (Prueba negativa: rechaza eliminar un tipo de pago inexistente)
def test_rechazar_eliminacion_tipo_pago_inexistente(datos_tipo_pago):
    modelo = datos_tipo_pago["modelo"]
    cursor = modelo.conexion.cursor()
    cursor.execute("SELECT COALESCE(MAX(cod_tipo_pago), 0) + 1 FROM tipo_pago")
    cod_inexistente = cursor.fetchone()[0]
    cursor.close()

    assert modelo.eliminar(cod_inexistente) == -2
