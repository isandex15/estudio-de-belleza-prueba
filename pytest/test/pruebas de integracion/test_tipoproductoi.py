import secrets
import string
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.tipoproducto import TipoProductoModelo


@pytest.fixture
def datos_tipo_producto():
    modelo = TipoProductoModelo()
    sufijo = "".join(secrets.choice(string.ascii_lowercase) for _ in range(12))
    nombre = "Integracion " + sufijo
    cod_tipo_producto = None

    try:
        assert modelo.validarNombreTipoProducto(nombre)["status"] is True
        modelo.nombre_tipo_producto = nombre
        resultado = modelo.registrar()
        assert resultado["status"] is True
        registro = modelo.buscar(nombre)
        assert registro is not None
        cod_tipo_producto = registro["cod_tipo_producto"]
        yield {
            "modelo": modelo,
            "cod_tipo_producto": cod_tipo_producto,
            "nombre": nombre,
        }
    finally:
        try:
            if cod_tipo_producto is not None:
                cursor = modelo.conexion.cursor(dictionary=True)
                cursor.execute(
                    "SELECT cod_tipo_producto FROM tipo_producto WHERE cod_tipo_producto = %s",
                    (cod_tipo_producto,),
                )
                existe = cursor.fetchone()
                cursor.close()
                if existe and not modelo.eliminar(cod_tipo_producto)["status"]:
                    pytest.fail("No se pudo limpiar el tipo de producto de integración.")
        finally:
            modelo.conexion.close()


def test_registrar_y_consultar_tipo_producto(datos_tipo_producto):
    modelo = datos_tipo_producto["modelo"]
    codigo = datos_tipo_producto["cod_tipo_producto"]

    assert any(item["cod_tipo_producto"] == codigo for item in modelo.consultar())
    registro = modelo.buscar(datos_tipo_producto["nombre"])
    assert registro["cod_tipo_producto"] == codigo


def test_editar_tipo_producto_persiste_cambios(datos_tipo_producto):
    modelo = datos_tipo_producto["modelo"]
    nuevo_nombre = datos_tipo_producto["nombre"] + " Editado"
    modelo.cod_tipo_producto = datos_tipo_producto["cod_tipo_producto"]
    modelo.nombre_tipo_producto = nuevo_nombre
    modelo.status = 1

    resultado = modelo.editar()

    assert resultado["status"] is True
    registro = modelo.buscar(nuevo_nombre)
    assert registro is not None
    assert registro["cod_tipo_producto"] == datos_tipo_producto["cod_tipo_producto"]


def test_eliminar_tipo_producto_sin_productos_asociados(datos_tipo_producto):
    modelo = datos_tipo_producto["modelo"]
    codigo = datos_tipo_producto["cod_tipo_producto"]

    resultado = modelo.eliminar(codigo)

    assert resultado["status"] is True
    assert modelo.buscar(datos_tipo_producto["nombre"]) is None