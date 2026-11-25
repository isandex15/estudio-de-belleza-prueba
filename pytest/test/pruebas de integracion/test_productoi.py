import secrets
import string
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.producto import ProductoModelo


@pytest.fixture
def datos_producto():
    modelo = ProductoModelo()
    cursor = modelo.conn().cursor(dictionary=True)
    referencias = {}
    tablas = {
        "cod_categoria": "SELECT cod_categoria FROM categoria WHERE status = 1 LIMIT 1",
        "cod_marca": "SELECT cod_marca FROM marca WHERE status = 1 LIMIT 1",
        "cod_unidad": "SELECT cod_unidad FROM unidad WHERE status = 1 LIMIT 1",
        "cod_tipo_producto": (
            "SELECT cod_tipo_producto FROM tipo_producto WHERE status = 1 LIMIT 1"
        ),
    }
    faltan_referencias = False
    try:
        for campo, sql in tablas.items():
            cursor.execute(sql)
            fila = cursor.fetchone()
            if not fila:
                faltan_referencias = True
                break
            referencias[campo] = fila[campo]
    finally:
        cursor.close()

    if faltan_referencias:
        modelo.conexion.close()
        pytest.skip(
            "La prueba de producto requiere categoría, marca, unidad "
            "y tipo de producto activos."
        )

    sufijo = "".join(secrets.choice(string.ascii_lowercase) for _ in range(12))
    nombre = "ProductoIntegracion" + sufijo
    vencimiento = (date.today() + timedelta(days=30)).isoformat()
    modelo.nombre_producto = nombre
    modelo.precio_producto = 17.25
    modelo.stock = 6
    modelo.cod_categoria = referencias["cod_categoria"]
    modelo.cod_marca = referencias["cod_marca"]
    modelo.cod_unidad = referencias["cod_unidad"]
    modelo.cod_tipo_producto = referencias["cod_tipo_producto"]
    modelo.fecha_vencimiento = vencimiento
    cod_producto = None

    try:
        assert modelo.validarNombreProducto(nombre)["status"] is True
        assert modelo.validarPrecio("17.25")["status"] is True
        assert modelo.validarStock("6")["status"] is True
        assert modelo.validarFechaVencimiento(vencimiento)["status"] is True
        assert modelo.registrar() == 1
        registro = modelo.buscar(nombre)
        assert registro is not None
        cod_producto = registro["cod_producto"]
        yield {
            "modelo": modelo,
            "cod_producto": cod_producto,
            "nombre": nombre,
            "vencimiento": vencimiento,
            **referencias,
        }
    finally:
        try:
            if cod_producto is not None and modelo.obtener(cod_producto):
                resultado = modelo.eliminar(cod_producto)
                if resultado != "eliminado":
                    pytest.fail("No se pudo limpiar el producto de integración.")
        finally:
            modelo.conexion.close()


def test_registrar_y_consultar_producto(datos_producto):
    modelo = datos_producto["modelo"]
    codigo = datos_producto["cod_producto"]

    assert any(item["cod_producto"] == codigo for item in modelo.consultar())
    registro = modelo.obtener(codigo)
    assert registro["nombre_producto"] == datos_producto["nombre"]
    assert float(registro["precio_producto"]) == 17.25
    assert registro["cod_categoria"] == datos_producto["cod_categoria"]


def test_editar_producto_persiste_cambios(datos_producto):
    modelo = datos_producto["modelo"]
    nuevo_nombre = datos_producto["nombre"] + " Editado"
    modelo.cod_producto = datos_producto["cod_producto"]
    modelo.nombre_producto = nuevo_nombre
    modelo.precio_producto = 22.50
    modelo.cod_categoria = datos_producto["cod_categoria"]
    modelo.cod_marca = datos_producto["cod_marca"]
    modelo.cod_unidad = datos_producto["cod_unidad"]
    modelo.cod_tipo_producto = datos_producto["cod_tipo_producto"]
    modelo.fecha_vencimiento = datos_producto["vencimiento"]
    modelo.status = 1

    assert modelo.editar() == 1
    registro = modelo.obtener(datos_producto["cod_producto"])
    assert registro["nombre_producto"] == nuevo_nombre
    assert float(registro["precio_producto"]) == 22.50


def test_eliminar_producto_sin_compras_asociadas(datos_producto):
    modelo = datos_producto["modelo"]
    codigo = datos_producto["cod_producto"]

    assert modelo.eliminar(codigo) == "eliminado"
    assert modelo.obtener(codigo) is None