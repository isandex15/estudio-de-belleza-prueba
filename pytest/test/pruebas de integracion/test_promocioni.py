import secrets
import string
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.promociones import PromocionModelo


@pytest.fixture
def datos_promocion():
    modelo = PromocionModelo()
    sufijo = "".join(secrets.choice(string.ascii_lowercase) for _ in range(12))
    nombre = "Integracion Promo " + sufijo
    inicio = (date.today() + timedelta(days=1)).isoformat()
    fin = (date.today() + timedelta(days=10)).isoformat()
    cod_promo = None

    modelo.descuento = 15
    modelo.nombre_promo = nombre
    modelo.descripcion_promo = "Prueba de integración"
    modelo.imagen_promo = None
    modelo.inicio_promo = inicio
    modelo.fin_promo = fin

    try:
        assert modelo.registrar() == 1
        registro = modelo.buscar(nombre)
        assert registro is not None
        cod_promo = registro["cod_promo"]
        yield {
            "modelo": modelo,
            "cod_promo": cod_promo,
            "nombre": nombre,
            "inicio": inicio,
            "fin": fin,
        }
    finally:
        try:
            if cod_promo is not None and modelo.obtener(cod_promo):
                resultado = modelo.eliminar(cod_promo)
                if resultado != "eliminado":
                    pytest.fail("No se pudo limpiar la promoción de integración.")
        finally:
            modelo.conexion.close()


def test_registrar_y_consultar_promocion(datos_promocion):
    modelo = datos_promocion["modelo"]
    codigo = datos_promocion["cod_promo"]

    assert modelo.validarNombrePromo(datos_promocion["nombre"])["status"] is True
    assert modelo.validarDescuento("15")["status"] is True
    assert modelo.validarFechasPromo(
        datos_promocion["inicio"],
        datos_promocion["fin"],
    )["status"] is True
    assert modelo.obtener(codigo)["nombre_promo"] == datos_promocion["nombre"]
    assert any(item["cod_promo"] == codigo for item in modelo.consultar())


def test_editar_promocion_persiste_cambios(datos_promocion):
    modelo = datos_promocion["modelo"]
    nuevo_nombre = datos_promocion["nombre"] + " Editada"
    modelo.cod_promo = datos_promocion["cod_promo"]
    modelo.descuento = 20
    modelo.nombre_promo = nuevo_nombre
    modelo.descripcion_promo = "Descripción actualizada"
    modelo.imagen_promo = None
    modelo.inicio_promo = datos_promocion["inicio"]
    modelo.fin_promo = datos_promocion["fin"]
    modelo.status = 1

    assert modelo.editar() == 1
    promocion = modelo.obtener(datos_promocion["cod_promo"])
    assert promocion["nombre_promo"] == nuevo_nombre
    assert int(promocion["descuento"]) == 20
    assert promocion["descripcion_promo"] == "Descripción actualizada"


def test_eliminar_promocion(datos_promocion):
    modelo = datos_promocion["modelo"]
    codigo = datos_promocion["cod_promo"]

    assert modelo.eliminar(codigo) == "eliminado"
    assert modelo.obtener(codigo) is None