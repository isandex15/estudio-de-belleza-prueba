
import sys
from pathlib import Path
from uuid import uuid4

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.unidad import UnidadModelo

# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_unidadi.py::test_registrar_unidad" -vv -s --tb=long
# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_unidadi.py::test_editar_unidad" -vv -s --tb=long
# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_unidadi.py::test_registrar_unidad_sin_presentacion" -vv -s --tb=long
# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_unidadi.py::test_registrar_unidad_sin_medida" -vv -s --tb=long

# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_unidadi.py::test_editar_nombre_unidad" -vv -s --tb=long
# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_unidadi.py::test_editar_nombre_unidad_conservando_datos" -vv -s --tb=long

@pytest.fixture
def datos_unidad():
    modelo = UnidadModelo()

    presentaciones = modelo.obtener_presentaciones()
    medidas = modelo.obtener_medidas()

    if len(presentaciones) < 2 or len(medidas) < 2:
        modelo.conexion.close()
        pytest.fail(
            "Se requieren al menos dos presentaciones y dos medidas."
        )

    unidades_creadas = []

    datos = {
        "modelo": modelo,
        "cod_presentacion": presentaciones[0]["cod_presentacion"],
        "cod_medida": medidas[0]["cod_medida"],
        "segunda_presentacion": presentaciones[1]["cod_presentacion"],
        "segunda_medida": medidas[1]["cod_medida"],
        "unidades_creadas": unidades_creadas,
    }

    try:
        yield datos
    finally:
        for cod_unidad in unidades_creadas:
            modelo.conexion.commit()
            resultado = modelo.sp_eliminar_unidad(cod_unidad)

            if resultado != 1:
                modelo.conexion.rollback()
                modelo.conexion.close()
                pytest.fail(
                    f"No se pudo eliminar la unidad de prueba {cod_unidad}."
                )

        modelo.conexion.close()


@pytest.fixture
def unidad_registrada(datos_unidad):
    modelo = datos_unidad["modelo"]
    nombre = str(uuid4().int)[:12]

    modelo.nombre_unidad = nombre
    modelo.cod_presentacion = datos_unidad["cod_presentacion"]
    modelo.cod_medida = datos_unidad["cod_medida"]

    resultado = modelo.registrar()
    assert resultado == 1

    unidad = next(
        (
            u for u in modelo.consultar()
            if u["nombre_unidad"] == nombre
            and u["cod_presentacion"] == datos_unidad["cod_presentacion"]
            and u["cod_medida"] == datos_unidad["cod_medida"]
        ),
        None
    )

    assert unidad is not None

    datos_unidad["unidades_creadas"].append(unidad["cod_unidad"])

    return unidad["cod_unidad"]


# CP-UNI-01 (prueba positiva: Registra correctamente una unidad)
def test_registrar_unidad(datos_unidad, unidad_registrada):
    modelo = datos_unidad["modelo"]

    unidad = next(
        (
            u for u in modelo.consultar()
            if u["cod_unidad"] == unidad_registrada
        ),
        None
    )

    assert unidad is not None
    assert unidad["cod_presentacion"] == datos_unidad["cod_presentacion"]
    assert unidad["cod_medida"] == datos_unidad["cod_medida"]
    assert unidad["status"] == 1


# CP-UNI-02 (prueba positiva: Edita la presentación y medida de una unidad)
def test_editar_unidad(datos_unidad, unidad_registrada):
    modelo = datos_unidad["modelo"]
    cod_unidad = unidad_registrada

    unidad = next(
        (
            u for u in modelo.consultar()
            if u["cod_unidad"] == cod_unidad
        ),
        None
    )

    assert unidad is not None

    modelo.cod_unidad = cod_unidad
    modelo.nombre_unidad = unidad["nombre_unidad"]
    modelo.cod_presentacion = datos_unidad["segunda_presentacion"]
    modelo.cod_medida = datos_unidad["segunda_medida"]
    modelo.status = unidad["status"]

    resultado = modelo.editar()
    assert resultado == 1

    unidad_editada = next(
        (
            u for u in modelo.consultar()
            if u["cod_unidad"] == cod_unidad
        ),
        None
    )

    assert unidad_editada is not None
    assert unidad_editada["cod_presentacion"] == datos_unidad["segunda_presentacion"]
    assert unidad_editada["cod_medida"] == datos_unidad["segunda_medida"]
    assert unidad_editada["status"] == 1


# CP-UNI-03 (prueba negativa: Intenta registrar una unidad sin presentación)
def test_registrar_unidad_sin_presentacion(datos_unidad):
    modelo = datos_unidad["modelo"]

    modelo.nombre_unidad = str(uuid4().int)[:1]
    modelo.cod_presentacion = None
    modelo.cod_medida = datos_unidad["cod_medida"]

    resultado = modelo.registrar()

    assert resultado == 0


# CP-UNI-04 (prueba negativa: Intenta registrar una unidad sin medida)
def test_registrar_unidad_sin_medida(datos_unidad):
    modelo = datos_unidad["modelo"]

    modelo.nombre_unidad = str(uuid4().int)[:1]
    modelo.cod_presentacion = datos_unidad["cod_presentacion"]
    modelo.cod_medida = None

    resultado = modelo.registrar()

    assert resultado == 0

    
def test_editar_nombre_unidad(datos_unidad, unidad_registrada):
    modelo = datos_unidad["modelo"]
    cod_unidad = unidad_registrada

    modelo.cod_unidad = cod_unidad
    modelo.nombre_unidad = str(uuid4().int)[:12]
    modelo.cod_presentacion = datos_unidad["cod_presentacion"]
    modelo.cod_medida = datos_unidad["cod_medida"]
    modelo.status = 1

    assert modelo.editar() == 1

    unidad_editada = next(
        u for u in modelo.consultar()
        if u["cod_unidad"] == cod_unidad
    )

    assert unidad_editada["nombre_unidad"] == modelo.nombre_unidad
    modelo = datos_unidad["modelo"]
    cod_unidad = unidad_registrada

    modelo.nombre_unidad = str(uuid4().int)[:12]
    modelo.cod_presentacion = datos_unidad["cod_presentacion"]
    modelo.cod_medida = datos_unidad["cod_medida"]
    modelo.status = 1

    assert modelo.editar() == 1

    unidad_editada = next(
        u for u in modelo.consultar()
        if u["cod_unidad"] == cod_unidad
    )

    assert unidad_editada["nombre_unidad"] == modelo.nombre_unidad
    assert unidad_editada["cod_presentacion"] == datos_unidad["cod_presentacion"]
    assert unidad_editada["cod_medida"] == datos_unidad["cod_medida"]


def test_editar_nombre_unidad_conservando_datos(datos_unidad, unidad_registrada):
    modelo = datos_unidad["modelo"]
    cod_unidad = unidad_registrada

    modelo.cod_unidad = cod_unidad
    modelo.nombre_unidad = str(uuid4().int)[:12]
    modelo.cod_presentacion = datos_unidad["cod_presentacion"]
    modelo.cod_medida = datos_unidad["cod_medida"]
    modelo.status = 1

    assert modelo.editar() == 1

    unidad_editada = next(
        u for u in modelo.consultar()
        if u["cod_unidad"] == cod_unidad
    )

    assert unidad_editada["nombre_unidad"] == modelo.nombre_unidad
    assert unidad_editada["cod_presentacion"] == datos_unidad["cod_presentacion"]
    assert unidad_editada["cod_medida"] == datos_unidad["cod_medida"]    