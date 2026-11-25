import secrets
import string
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.marca import MarcaModelo


@pytest.fixture
def datos_marca():
    modelo = MarcaModelo()
    sufijo = "".join(secrets.choice(string.ascii_lowercase) for _ in range(12))
    nombre = "Integracion " + sufijo
    cod_marca = None

    try:
        assert modelo.validarNombreMarca(nombre)["status"] is True
        assert modelo.validarStatus("1")["status"] is True
        modelo.nombre_marca = nombre
        assert modelo.registrar() == 1
        registro = modelo.buscar(nombre)
        assert registro is not None
        cod_marca = registro["cod_marca"]
        yield {
            "modelo": modelo,
            "cod_marca": cod_marca,
            "nombre": nombre,
        }
    finally:
        try:
            if cod_marca is not None:
                cursor = modelo.conexion.cursor(dictionary=True)
                cursor.execute(
                    "SELECT cod_marca FROM marca WHERE cod_marca = %s",
                    (cod_marca,),
                )
                existe = cursor.fetchone()
                cursor.close()
                if existe and modelo.eliminar(cod_marca) != "eliminado":
                    pytest.fail("No se pudo limpiar la marca de integración.")
        finally:
            modelo.conexion.close()


def test_registrar_y_consultar_marca(datos_marca):
    modelo = datos_marca["modelo"]
    codigo = datos_marca["cod_marca"]

    assert any(item["cod_marca"] == codigo for item in modelo.consultar())
    registro = modelo.buscar(datos_marca["nombre"])
    assert registro["cod_marca"] == codigo


def test_editar_marca_persiste_cambios(datos_marca):
    modelo = datos_marca["modelo"]
    nuevo_nombre = datos_marca["nombre"] + " Editada"
    modelo.cod_marca = datos_marca["cod_marca"]
    modelo.nombre_marca = nuevo_nombre
    modelo.status = 1

    assert modelo.editar() == 1
    registro = modelo.buscar(nuevo_nombre)
    assert registro is not None
    assert registro["cod_marca"] == datos_marca["cod_marca"]


def test_eliminar_marca_sin_productos_asociados(datos_marca):
    modelo = datos_marca["modelo"]
    codigo = datos_marca["cod_marca"]

    assert modelo.eliminar(codigo) == "eliminado"
    assert modelo.buscar(datos_marca["nombre"]) is None