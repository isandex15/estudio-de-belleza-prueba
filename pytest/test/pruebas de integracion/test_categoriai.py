import secrets
import string
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.categorias import CategoriaModelo


@pytest.fixture
def datos_categoria():
    modelo = CategoriaModelo()
    sufijo = "".join(secrets.choice(string.ascii_lowercase) for _ in range(12))
    nombre = "Integracion " + sufijo
    cod_categoria = None

    try:
        assert modelo.validarNombreCategoria(nombre)["status"] is True
        assert modelo.validarStatus("1")["status"] is True
        modelo.nombre_categoria = nombre
        assert modelo.registrar() == 1
        registro = modelo.buscar(nombre)
        assert registro is not None
        cod_categoria = registro["cod_categoria"]
        yield {
            "modelo": modelo,
            "cod_categoria": cod_categoria,
            "nombre": nombre,
        }
    finally:
        try:
            if cod_categoria is not None:
                cursor = modelo.conexion.cursor(dictionary=True)
                cursor.execute(
                    "SELECT cod_categoria FROM categoria WHERE cod_categoria = %s",
                    (cod_categoria,),
                )
                existe = cursor.fetchone()
                cursor.close()
                if existe and modelo.eliminar(cod_categoria) != "eliminado":
                    pytest.fail("No se pudo limpiar la categoría de integración.")
        finally:
            modelo.conexion.close()


def test_registrar_y_consultar_categoria(datos_categoria):
    modelo = datos_categoria["modelo"]
    codigo = datos_categoria["cod_categoria"]

    assert any(item["cod_categoria"] == codigo for item in modelo.consultar())
    registro = modelo.buscar(datos_categoria["nombre"])
    assert registro["cod_categoria"] == codigo


def test_editar_categoria_persiste_cambios(datos_categoria):
    modelo = datos_categoria["modelo"]
    nuevo_nombre = datos_categoria["nombre"] + " Editada"
    modelo.cod_categoria = datos_categoria["cod_categoria"]
    modelo.nombre_categoria = nuevo_nombre
    modelo.status = 1

    assert modelo.editar() == 1
    registro = modelo.buscar(nuevo_nombre)
    assert registro is not None
    assert registro["cod_categoria"] == datos_categoria["cod_categoria"]


def test_eliminar_categoria_sin_productos_asociados(datos_categoria):
    modelo = datos_categoria["modelo"]
    codigo = datos_categoria["cod_categoria"]

    assert modelo.eliminar(codigo) == "eliminado"
    assert modelo.buscar(datos_categoria["nombre"]) is None