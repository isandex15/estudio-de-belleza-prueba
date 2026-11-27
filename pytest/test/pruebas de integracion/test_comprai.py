import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.compra import CompraModelo

#& "C:\xampp\htdocs\Estudio-attelier\Estudio-attelier\.venv\Scripts\python.exe" -m pytest "C:\xampp\htdocs\Estudio-attelier\Estudio-attelier\pytest\pruebas de integracion\test_comprai.py::test_registrar" -vv -s --tb=long
#& "C:\xampp\htdocs\Estudio-attelier\Estudio-attelier\.venv\Scripts\python.exe" -m pytest "C:\xampp\htdocs\Estudio-attelier\Estudio-attelier\pytest\pruebas de integracion\test_comprai.py::test_editar_compra" -vv -s --tb=long
#& "C:\xampp\htdocs\Estudio-attelier\Estudio-attelier\.venv\Scripts\python.exe" -m pytest "C:\xampp\htdocs\Estudio-attelier\Estudio-attelier\pytest\pruebas de integracion\test_comprai.py::test_cancelar_compra" -vv -s --tb=long
@pytest.fixture
def datos_compra():
    modelo = CompraModelo()
    cursor = modelo.conn().cursor(dictionary=True)

    cursor.execute(
        """
        SELECT cod_proveedor
        FROM proveedor
        WHERE status = 1
        ORDER BY cod_proveedor
        LIMIT 1
        """
    )
    proveedor = cursor.fetchone()

    cursor.execute(
        """
        SELECT cod_producto, stock
        FROM producto
        WHERE status = 1
        ORDER BY cod_producto
        LIMIT 1
        """
    )
    producto = cursor.fetchone()

    cursor.execute(
        """
        SELECT cedula
        FROM seguridad.usuario
        WHERE status = 1
        ORDER BY cedula
        LIMIT 1
        """
    )
    usuario = cursor.fetchone()
    cursor.close()

    if not proveedor or not producto or not usuario:
        modelo.conexion.close()
        pytest.fail(
            "La base de datos de pruebas requiere un proveedor, un producto "
            "y un usuario activos."
        )

    compras_creadas = []
    datos = {
        "modelo": modelo,
        "cod_proveedor": proveedor["cod_proveedor"],
        "cod_producto": producto["cod_producto"],
        "stock_inicial": producto["stock"],
        "cedula": usuario["cedula"],
        "compras_creadas": compras_creadas,
    }

    try:
        yield datos
    finally:
        for cod_compra in compras_creadas:
            compra = modelo.obtener(cod_compra)
            if compra and compra["status"] == 1:
                resultado = modelo.eliminar(cod_compra, datos["cedula"])
                if resultado != "cancelado":
                    modelo.conexion.close()
                    pytest.fail(
                        f"No se pudo cancelar la compra de prueba {cod_compra}."
                    )

        modelo.conexion.close()


@pytest.fixture
def compra_registrada(datos_compra):
    modelo = datos_compra["modelo"]
    _exigir_procedimientos_compra(modelo)
    fecha = date.today().isoformat()
    cod_compra = modelo.registrar_completa(
        fecha,
        datos_compra["cod_proveedor"],
        [
            {
                "cod_producto": datos_compra["cod_producto"],
                "cantidad": 2,
                "precio": 11,
            }
        ],
        datos_compra["cedula"],
    )
    assert cod_compra
    datos_compra["compras_creadas"].append(cod_compra)
    return cod_compra


def test_registrar(datos_compra, compra_registrada):
    modelo = datos_compra["modelo"]
    cod_compra = compra_registrada
    cod_producto = datos_compra["cod_producto"]

    assert modelo.validarFechaCompra(date.today().isoformat())["status"] is True
    assert modelo.validarProveedor(str(datos_compra["cod_proveedor"]))["status"] is True
    assert modelo.validarTotal("22")["status"] is True
    assert modelo.validarProductos(
        [{"cod_producto": cod_producto, "cantidad": 2, "precio": 11}]
    )["status"] is True

    compra_registrada = modelo.obtener(cod_compra)
    detalle_registrado = modelo.obtener_detalle_compra(cod_compra)
    assert compra_registrada["status"] == 1
    assert float(compra_registrada["total"]) == 22
    assert len(detalle_registrado) == 1
    assert detalle_registrado[0]["cod_producto"] == cod_producto
    assert detalle_registrado[0]["cantidad"] == 2
    assert detalle_registrado[0]["precio_unitario"] == 11
    assert _obtener_stock(modelo, cod_producto) == datos_compra["stock_inicial"] + 2




def test_cancelar_compra(datos_compra, compra_registrada):
    modelo = datos_compra["modelo"]
    cod_compra = compra_registrada
    cod_producto = datos_compra["cod_producto"]

    assert modelo.eliminar(cod_compra, datos_compra["cedula"]) == "cancelado"
    compra_cancelada = modelo.obtener(cod_compra)
    assert compra_cancelada["status"] == 0
    assert _obtener_stock(modelo, cod_producto) == datos_compra["stock_inicial"]


def test_consultar_compras_y_catalogos_desde_base_de_datos(datos_compra):
    modelo = datos_compra["modelo"]

    assert isinstance(modelo.consultar(), list)
    assert any(
        proveedor["cod_proveedor"] == datos_compra["cod_proveedor"]
        for proveedor in modelo.listar_proveedores()
    )
    assert any(
        producto["cod_producto"] == datos_compra["cod_producto"]
        for producto in modelo.listar_productos()
    )


def test_validar_total_invalido_no_registra_compra(datos_compra):
    modelo = datos_compra["modelo"]

    resultado = modelo.validarTotal("0")

    assert resultado["status"] is False
    assert resultado["title"] == "Total inválido"


def _obtener_stock(modelo, cod_producto):
    cursor = modelo.conn().cursor()
    cursor.execute(
        "SELECT stock FROM producto WHERE cod_producto = %s",
        (cod_producto,),
    )
    fila = cursor.fetchone()
    cursor.close()
    assert fila is not None
    return fila[0]


def _exigir_procedimientos_compra(modelo):
    cursor = modelo.conn().cursor()
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.ROUTINES
        WHERE ROUTINE_SCHEMA = DATABASE()
          AND ROUTINE_TYPE = 'PROCEDURE'
          AND ROUTINE_NAME IN (
              'sp_registrar_compra_completa',
              'sp_cancelar_compra'
          )
        """
    )
    cantidad = cursor.fetchone()[0]
    cursor.close()

    if cantidad != 2:
        pytest.skip(
            "La base de datos no tiene instalados los procedimientos "
            "sp_registrar_compra_completa y sp_cancelar_compra. "
            "Ejecute db/procedimientoscompras.sql antes de esta prueba."
        )
