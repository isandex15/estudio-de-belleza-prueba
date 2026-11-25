import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.proveedor import ProveedorModelo


@pytest.fixture
def datos_proveedor():
    modelo = ProveedorModelo()
    cursor = modelo.conexion.cursor()
    cedula = None
    try:
        for _ in range(20):
            candidata = str(random.SystemRandom().randint(10_000_000, 99_999_999))
            cursor.execute(
                "SELECT COUNT(*) FROM proveedor WHERE cedula = %s",
                (candidata,),
            )
            if cursor.fetchone()[0] == 0:
                cedula = candidata
                break
    finally:
        cursor.close()

    if cedula is None:
        modelo.conexion.close()
        pytest.skip("No se pudo generar una cédula libre para el proveedor.")

    datos = {
        "modelo": modelo,
        "cedula": cedula,
        "nombre": "ProveedorIntegracion",
        "apellido": "Pruebas",
        "rif": "J" + cedula,
        "telefono": "04" + cedula,
        "correo": "proveedor" + cedula + "@example.test",
    }

    try:
        for metodo, valor in [
            (modelo.validarCedula, datos["cedula"]),
            (modelo.validarNombre, datos["nombre"]),
            (modelo.validarApellido, datos["apellido"]),
            (modelo.validarRif, datos["rif"]),
            (modelo.validarTelefono, datos["telefono"]),
            (modelo.validarCorreo, datos["correo"]),
        ]:
            assert metodo(valor)["status"] is True
        modelo.cedula = datos["cedula"]
        modelo.nombre = datos["nombre"]
        modelo.apellido = datos["apellido"]
        modelo.rif = datos["rif"]
        modelo.telefono = datos["telefono"]
        modelo.correo = datos["correo"]
        assert modelo.registrar() == 1
        registro = modelo.buscar(cedula)
        assert registro is not None
        datos["cod_proveedor"] = registro["cod_proveedor"]
        yield datos
    finally:
        try:
            registro = modelo.buscar(cedula)
            if registro:
                resultado = modelo.eliminar(registro["cod_proveedor"])
                if resultado != "eliminado":
                    pytest.fail("No se pudo limpiar el proveedor de integración.")
        finally:
            modelo.conexion.close()


def test_registrar_y_consultar_proveedor(datos_proveedor):
    modelo = datos_proveedor["modelo"]
    codigo = datos_proveedor["cod_proveedor"]

    assert any(item["cod_proveedor"] == codigo for item in modelo.consultar())
    registro = modelo.buscar(datos_proveedor["cedula"])
    assert registro["nombre"] == datos_proveedor["nombre"]
    assert registro["rif"] == datos_proveedor["rif"]


def test_editar_proveedor_persiste_cambios(datos_proveedor):
    modelo = datos_proveedor["modelo"]
    modelo.cod_proveedor = datos_proveedor["cod_proveedor"]
    modelo.cedula = datos_proveedor["cedula"]
    modelo.nombre = "ProveedorActualizado"
    modelo.apellido = "Integracion"
    modelo.rif = datos_proveedor["rif"]
    modelo.telefono = datos_proveedor["telefono"]
    modelo.correo = datos_proveedor["correo"]
    modelo.status = 1

    assert modelo.editar() == 1
    registro = modelo.buscar(datos_proveedor["cedula"])
    assert registro["nombre"] == "ProveedorActualizado"
    assert registro["apellido"] == "Integracion"


def test_eliminar_proveedor_sin_compras_asociadas(datos_proveedor):
    modelo = datos_proveedor["modelo"]
    codigo = datos_proveedor["cod_proveedor"]

    assert modelo.eliminar(codigo) == "eliminado"
    assert modelo.buscar(datos_proveedor["cedula"]) is None