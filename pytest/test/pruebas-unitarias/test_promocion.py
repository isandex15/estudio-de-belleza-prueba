import sys
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

#python -m pytest .\Estudio-attelier\pytest\test\test_promocion.py -q
#python -m pytest .\Estudio-attelier\pytest\test\test_promocion.py::test_registrar_promocion -vv
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import admin.config.conexion as conexion_module
from admin.modelo.promociones import PromocionModelo


@pytest.fixture
def modelo_promocion(monkeypatch):
    fake_conn = MagicMock()
    fake_conn.is_connected.return_value = True
    monkeypatch.setattr(
        conexion_module.mysql.connector,
        "connect",
        lambda **kwargs: fake_conn,
    )
    return PromocionModelo()


def test_validar_nombre_promo_acepta_nombre_valido(modelo_promocion):
    resultado = modelo_promocion.validarNombrePromo("Promo Verano 2026")

    assert resultado["status"] is True


def test_validar_nombre_promo_rechaza_nombre_vacio(modelo_promocion):
    resultado = modelo_promocion.validarNombrePromo("   ")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_nombre_promo_rechaza_caracteres_especiales(modelo_promocion):
    resultado = modelo_promocion.validarNombrePromo("Promo-Verano")

    assert resultado["status"] is False
    assert resultado["title"] == "Dato inválido"


def test_validar_nombre_promo_rechaza_nombre_muy_largo(modelo_promocion):
    resultado = modelo_promocion.validarNombrePromo("P" * 101)

    assert resultado["status"] is False
    assert resultado["title"] == "Nombre muy largo"


def test_validar_descripcion_promo_acepta_descripcion_valida(modelo_promocion):
    resultado = modelo_promocion.validarDescripcionPromo("Descuento de temporada")

    assert resultado["status"] is True


def test_validar_descripcion_promo_rechaza_descripcion_muy_larga(modelo_promocion):
    resultado = modelo_promocion.validarDescripcionPromo("D" * 251)

    assert resultado["status"] is False
    assert resultado["title"] == "Descripción muy larga"


def test_validar_descuento_acepta_porcentaje_valido(modelo_promocion):
    resultado = modelo_promocion.validarDescuento("25")

    assert resultado["status"] is True


def test_validar_descuento_rechaza_valor_vacio(modelo_promocion):
    resultado = modelo_promocion.validarDescuento("")

    assert resultado["status"] is False
    assert resultado["title"] == "Campo vacío"


def test_validar_descuento_rechaza_valor_no_numerico(modelo_promocion):
    resultado = modelo_promocion.validarDescuento("veinte")

    assert resultado["status"] is False
    assert resultado["title"] == "Dato inválido"


def test_validar_descuento_rechaza_mas_de_tres_digitos(modelo_promocion):
    resultado = modelo_promocion.validarDescuento("1000")

    assert resultado["status"] is False
    assert resultado["title"] == "Descuento inválido"


def test_validar_descuento_rechaza_mayor_a_cien(modelo_promocion):
    resultado = modelo_promocion.validarDescuento("101")

    assert resultado["status"] is False
    assert resultado["title"] == "Descuento inválido"


def test_validar_fechas_promo_acepta_rango_valido(modelo_promocion):
    inicio = date.today() + timedelta(days=1)
    fin = inicio + timedelta(days=7)

    resultado = modelo_promocion.validarFechasPromo(
        inicio.isoformat(),
        fin.isoformat(),
    )

    assert resultado["status"] is True


def test_validar_fechas_promo_rechaza_fechas_vacias(modelo_promocion):
    resultado = modelo_promocion.validarFechasPromo("", "")

    assert resultado["status"] is False
    assert resultado["title"] == "Fechas requeridas"


def test_validar_fechas_promo_rechaza_formato_invalido(modelo_promocion):
    resultado = modelo_promocion.validarFechasPromo("fecha", "fecha")

    assert resultado["status"] is False
    assert resultado["title"] == "Fechas inválidas"


def test_validar_fechas_promo_rechaza_inicio_anterior_a_hoy(modelo_promocion):
    ayer = date.today() - timedelta(days=1)
    manana = date.today() + timedelta(days=1)

    resultado = modelo_promocion.validarFechasPromo(
        ayer.isoformat(),
        manana.isoformat(),
    )

    assert resultado["status"] is False
    assert resultado["title"] == "Fecha inválida"


def test_validar_fechas_promo_rechaza_fin_anterior_a_inicio(modelo_promocion):
    inicio = date.today() + timedelta(days=2)
    fin = inicio - timedelta(days=1)

    resultado = modelo_promocion.validarFechasPromo(
        inicio.isoformat(),
        fin.isoformat(),
    )

    assert resultado["status"] is False
    assert resultado["title"] == "Fecha inválida"


def test_validar_imagen_promo_acepta_imagen_sin_archivo(modelo_promocion):
    resultado = modelo_promocion.validarImagenPromo(None)

    assert resultado["status"] is True


def test_validar_imagen_promo_acepta_extension_permitida(modelo_promocion):
    imagen = SimpleNamespace(filename="promo.PNG")

    resultado = modelo_promocion.validarImagenPromo(imagen)

    assert resultado["status"] is True


def test_validar_imagen_promo_rechaza_extension_no_permitida(modelo_promocion):
    imagen = SimpleNamespace(filename="promo.gif")

    resultado = modelo_promocion.validarImagenPromo(imagen)

    assert resultado["status"] is False
    assert resultado["title"] == "Formato inválido"


def test_registrar_promocion(modelo_promocion):
    mock_cursor = modelo_promocion.conexion.cursor.return_value
    modelo_promocion.descuento = "25"
    modelo_promocion.nombre_promo = "Promo Verano"
    modelo_promocion.descripcion_promo = "Descuento de temporada"
    modelo_promocion.imagen_promo = "promo.png"
    modelo_promocion.inicio_promo = "2026-12-01"
    modelo_promocion.fin_promo = "2026-12-31"

    resultado = modelo_promocion.registrar()

    assert resultado == 1
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == (
        "25",
        "Promo Verano",
        "Descuento de temporada",
        "promo.png",
        "2026-12-01",
        "2026-12-31",
    )
    modelo_promocion.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_consultar_promociones(modelo_promocion):
    mock_cursor = modelo_promocion.conexion.cursor.return_value
    promociones = [{"cod_promo": 3, "nombre_promo": "Promo Verano"}]
    mock_cursor.fetchall.return_value = promociones

    resultado = modelo_promocion.consultar()

    assert resultado == promociones
    mock_cursor.execute.assert_called_once()
    assert "FROM promocion" in mock_cursor.execute.call_args.args[0]
    mock_cursor.close.assert_called_once()


def test_obtener_promocion_por_codigo(modelo_promocion):
    mock_cursor = modelo_promocion.conexion.cursor.return_value
    promocion = {"cod_promo": 3, "nombre_promo": "Promo Verano"}
    mock_cursor.fetchone.return_value = promocion

    resultado = modelo_promocion.obtener(3)

    assert resultado == promocion
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == (3,)
    mock_cursor.close.assert_called_once()


def test_buscar_promocion_por_nombre(modelo_promocion):
    mock_cursor = modelo_promocion.conexion.cursor.return_value
    promocion = {"cod_promo": 3, "nombre_promo": "Promo Verano"}
    mock_cursor.fetchone.return_value = promocion

    resultado = modelo_promocion.buscar("Promo Verano")

    assert resultado == promocion
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == ("Promo Verano",)
    mock_cursor.close.assert_called_once()


def test_editar_promocion(modelo_promocion):
    mock_cursor = modelo_promocion.conexion.cursor.return_value
    modelo_promocion.descuento = "30"
    modelo_promocion.nombre_promo = "Promo Actualizada"
    modelo_promocion.descripcion_promo = "Nueva descripción"
    modelo_promocion.imagen_promo = "actualizada.png"
    modelo_promocion.inicio_promo = "2026-12-01"
    modelo_promocion.fin_promo = "2026-12-31"
    modelo_promocion.status = 1
    modelo_promocion.cod_promo = 3

    resultado = modelo_promocion.editar()

    assert resultado == 1
    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args.args[1] == (
        "30",
        "Promo Actualizada",
        "Nueva descripción",
        "actualizada.png",
        "2026-12-01",
        "2026-12-31",
        1,
        3,
    )
    modelo_promocion.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_promocion_sin_servicios_asociados(modelo_promocion):
    mock_cursor = modelo_promocion.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 0}

    resultado = modelo_promocion.eliminar(3)

    assert resultado == "eliminado"
    assert mock_cursor.execute.call_count == 2
    assert mock_cursor.execute.call_args_list[0].args[1] == (3,)
    assert mock_cursor.execute.call_args_list[1].args[1] == (3,)
    modelo_promocion.conexion.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_eliminar_promocion_con_servicios_asociados_no_la_borra(modelo_promocion):
    mock_cursor = modelo_promocion.conexion.cursor.return_value
    mock_cursor.fetchone.return_value = {"total": 2}

    resultado = modelo_promocion.eliminar(3)

    assert resultado == "existe_servicio"
    mock_cursor.execute.assert_called_once()
    modelo_promocion.conexion.commit.assert_not_called()
    mock_cursor.close.assert_called_once()