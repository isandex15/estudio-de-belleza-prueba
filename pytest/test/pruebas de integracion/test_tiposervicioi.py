import secrets
import string
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.tiposervicios import TiposervicioModelo


@pytest.fixture
def datos_tipo_servicio():
    modelo = TiposervicioModelo()
    sufijo = "".join(secrets.choice(string.ascii_lowercase) for _ in range(12))
    nombre = "Integracion " + sufijo
    cod_tipo_servicio = None

    try:
        assert modelo.validarNombreServicio(nombre)["status"] is True
        assert modelo.validarPrecio("35.50")["status"] is True
        modelo.nombre_servicio = nombre
        modelo.precio = 35.50
        assert modelo.registrar() == 1
        registro = modelo.buscar(nombre)
        assert registro is not None
        cod_tipo_servicio = registro["cod_tipo_servicio"]
        yield {
            "modelo": modelo,
            "cod_tipo_servicio": cod_tipo_servicio,
            "nombre": nombre,
        }
    finally:
        try:
            if cod_tipo_servicio is not None:
                cursor = modelo.conexion.cursor(dictionary=True)
                cursor.execute(
                    "SELECT cod_tipo_servicio FROM tipo_servicio WHERE cod_tipo_servicio = %s",
                    (cod_tipo_servicio,),
                )
                existe = cursor.fetchone()
                cursor.close()
                if existe and modelo.eliminar(cod_tipo_servicio) != "eliminado":
                    pytest.fail("No se pudo limpiar el tipo de servicio de integración.")
        finally:
            modelo.conexion.close()


def test_registrar_y_consultar_tipo_servicio(datos_tipo_servicio):
    modelo = datos_tipo_servicio["modelo"]
    codigo = datos_tipo_servicio["cod_tipo_servicio"]

    assert any(item["cod_tipo_servicio"] == codigo for item in modelo.consultar())
    registro = modelo.buscar(datos_tipo_servicio["nombre"])
    assert registro["cod_tipo_servicio"] == codigo
    assert float(registro["precio"]) == 35.5


def test_editar_tipo_servicio_persiste_cambios(datos_tipo_servicio):
    modelo = datos_tipo_servicio["modelo"]
    nuevo_nombre = datos_tipo_servicio["nombre"] + " Editado"
    modelo.cod_tipo_servicio = datos_tipo_servicio["cod_tipo_servicio"]
    modelo.nombre_servicio = nuevo_nombre
    modelo.precio = 42.75
    modelo.status = 1

    assert modelo.editar() == 1
    registro = modelo.buscar(nuevo_nombre)
    assert registro is not None
    assert float(registro["precio"]) == 42.75


def test_eliminar_tipo_servicio_sin_detalles_asociados(datos_tipo_servicio):
    modelo = datos_tipo_servicio["modelo"]
    codigo = datos_tipo_servicio["cod_tipo_servicio"]

    assert modelo.eliminar(codigo) == "eliminado"
    assert modelo.buscar(datos_tipo_servicio["nombre"]) is None
