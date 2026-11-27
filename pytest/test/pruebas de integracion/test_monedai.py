import secrets
import string

import pytest

from admin.modelo.moneda import MonedaModelo


def _nombre_temporal():
    return "IT" + "".join(secrets.choice(string.ascii_lowercase) for _ in range(8))


@pytest.fixture
def datos_moneda(ready_test_database):
    modelo = MonedaModelo()
    datos = {
        "modelo": modelo,
        "nombres_creados": [],
    }
    try:
        yield datos
    finally:
        cursor = modelo.conexion.cursor()
        for nombre in datos["nombres_creados"]:
            cursor.execute("DELETE FROM moneda WHERE nombre_moneda = %s", (nombre,))
        modelo.conexion.commit()
        cursor.close()
        modelo.conexion.close()


@pytest.fixture
def moneda_registrada(datos_moneda):
    modelo = datos_moneda["modelo"]
    nombre_inicial = _nombre_temporal()
    datos_moneda["nombres_creados"].append(nombre_inicial)
    modelo.nombre_moneda = nombre_inicial
    assert modelo.registrar() == 1
    moneda = modelo.buscar(nombre_inicial)
    assert moneda is not None
    assert moneda["status"] == 1
    datos_moneda["moneda"] = moneda
    return datos_moneda


@pytest.fixture
def moneda_editada(moneda_registrada):
    modelo = moneda_registrada["modelo"]
    moneda = moneda_registrada["moneda"]
    nombre_editado = _nombre_temporal()
    moneda_registrada["nombres_creados"].append(nombre_editado)
    modelo.cod_moneda = moneda["cod_moneda"]
    modelo.nombre_moneda = nombre_editado
    modelo.status = 1
    assert modelo.editar() == 1
    moneda_registrada["nombre_editado"] = nombre_editado
    return moneda_registrada


# CP-MON-15 (Prueba positiva de registro de moneda)
def test_registrar_moneda(moneda_registrada):
    assert moneda_registrada["moneda"]["status"] == 1


# CP-MON-16 (Prueba positiva de consulta de moneda)
def test_consultar_moneda(moneda_registrada):
    modelo = moneda_registrada["modelo"]
    moneda = moneda_registrada["moneda"]
    assert any(
        fila["cod_moneda"] == moneda["cod_moneda"]
        for fila in modelo.consultar()
    )


# CP-MON-17 (Prueba positiva de edición de moneda)
def test_editar_moneda(moneda_editada):
    modelo = moneda_editada["modelo"]
    moneda = modelo.buscar(moneda_editada["nombre_editado"])
    assert moneda is not None
    assert moneda["cod_moneda"] == moneda_editada["moneda"]["cod_moneda"]


# CP-MON-18 (Prueba positiva de eliminación de moneda)
def test_eliminar_moneda(moneda_registrada):
    modelo = moneda_registrada["modelo"]
    moneda = moneda_registrada["moneda"]
    assert modelo.eliminar(moneda["cod_moneda"]) == 1
    assert modelo.buscar(moneda["nombre_moneda"]) is None


# CP-MON-19 (Prueba negativa: rechaza eliminar una moneda inexistente)
def test_rechazar_eliminacion_moneda_inexistente(datos_moneda):
    modelo = datos_moneda["modelo"]
    cursor = modelo.conexion.cursor()
    cursor.execute("SELECT COALESCE(MAX(cod_moneda), 0) + 1 FROM moneda")
    cod_inexistente = cursor.fetchone()[0]
    cursor.close()

    assert modelo.eliminar(cod_inexistente) == -2
