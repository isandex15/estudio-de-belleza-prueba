
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.modelo.permisos import PermisosModelo

# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_permisosi.py::test_registrar_permisos" -vv -s --tb=long
# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_permisosi.py::test_eliminar_permiso_asociado" -vv -s --tb=long
# python -m pytest "C:\xampp\htdocs\Estudio-attelier\pytest\test\pruebas de integracion\test_permisosi.py::test_buscar_permisos_vacios" -vv -s --tb=long

@pytest.fixture
def datos_permisos():
    modelo = PermisosModelo()
    cursor = modelo.conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT cod_rol
        FROM seguridad.rol
        WHERE status = 1
        ORDER BY cod_rol
        LIMIT 1 OFFSET 1
    """)
    rol = cursor.fetchone()

    if not rol:
        cursor.close()
        modelo.conexion.close()
        pytest.fail("La base de datos requiere un segundo rol activo.")

    cod_rol = rol["cod_rol"]

    cursor.execute("""
        SELECT
            m.cod_modulo,
            a.cod_accion
        FROM seguridad.modulos m
        CROSS JOIN seguridad.acciones a
        LEFT JOIN seguridad.permiso p
            ON p.cod_modulo = m.cod_modulo
           AND p.cod_accion = a.cod_accion
        LEFT JOIN seguridad.rol_permiso rp
            ON rp.cod_permiso = p.cod_permiso
           AND rp.cor_rol = %s
        WHERE rp.cod_permiso IS NULL
          AND (p.cod_permiso IS NULL OR p.status = 1)
        ORDER BY m.cod_modulo, a.cod_accion
        LIMIT 6
    """, (cod_rol,))
    permisos = cursor.fetchall()
    cursor.close()

    if len(permisos) != 6:
        modelo.conexion.close()
        pytest.fail(
            "La base de datos requiere seis combinaciones de módulos "
            "y acciones que no estén asignadas al segundo rol activo."
        )

    permisos_creados = []

    datos = {
        "modelo": modelo,
        "cod_rol": cod_rol,
        "permisos": permisos,
        "permisos_creados": permisos_creados,
    }

    try:
        yield datos
    finally:
        for cod_permiso in permisos_creados:
            cursor = modelo.conexion.cursor()
            cursor.execute("""
                UPDATE seguridad.permiso
                SET status = 0
                WHERE cod_permiso = %s
            """, (cod_permiso,))
            modelo.conexion.commit()
            cursor.close()

        modelo.conexion.close()


@pytest.fixture
def permisos_registrados(datos_permisos):
    modelo = datos_permisos["modelo"]
    cod_rol = datos_permisos["cod_rol"]

    permisos = {}

    for permiso in datos_permisos["permisos"]:
        cod_modulo = permiso["cod_modulo"]
        cod_accion = permiso["cod_accion"]

        permisos.setdefault(cod_modulo, {})[cod_accion] = 1

    resultado = modelo.registrar(cod_rol, permisos)
    assert resultado == 1

    cursor = modelo.conexion.cursor()
    cursor.execute("""
        SELECT p.cod_permiso
        FROM seguridad.permiso p
        INNER JOIN seguridad.rol_permiso rp
            ON rp.cod_permiso = p.cod_permiso
        WHERE rp.cor_rol = %s
          AND p.status = 1
    """, (cod_rol,))

    datos_permisos["permisos_creados"].extend(
        fila[0] for fila in cursor.fetchall()
    )
    cursor.close()

    return permisos

# CP-PER-0:registrar correctamente los permisos de un rol activo.
def test_registrar_permisos(datos_permisos, permisos_registrados):
    modelo = datos_permisos["modelo"]
    cod_rol = datos_permisos["cod_rol"]

    cursor = modelo.conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.cod_modulo, p.cod_accion
        FROM seguridad.rol_permiso rp
        INNER JOIN seguridad.permiso p
            ON p.cod_permiso = rp.cod_permiso
        WHERE rp.cor_rol = %s
          AND p.status = 1
    """, (cod_rol,))
    permisos_bd = cursor.fetchall()
    cursor.close()

    pares_registrados = {
        (p["cod_modulo"], p["cod_accion"])
        for p in permisos_bd
    }

    pares_esperados = {
        (modulo, accion)
        for modulo, acciones in permisos_registrados.items()
        for accion in acciones
    }

    assert len(pares_esperados) == 6
    assert pares_esperados.issubset(pares_registrados)


# CP-PER-0: Rechazar la eliminación de un permiso asociado a un rol.
def test_eliminar_permiso_asociado():
    modelo = PermisosModelo()

    try:
        permisos = modelo.consultar()

        permiso_encontrado = None

        for registro in permisos:
            if registro["status_permisos"] == 1 and registro["cod_permiso"]:
                permiso_encontrado = int(
                    registro["cod_permiso"].split("|")[0]
                )
                break

        resultado = modelo.eliminar(permiso_encontrado)

        assert resultado == "tiene_permisos"

    finally:
        modelo.conexion.close()

# CP-PER-0: Rechazar la búsqueda de permisos con una lista vacía de módulos y acciones.
def test_buscar_permisos_vacios():
    modelo = PermisosModelo()

    try:
        resultado = modelo.buscar_permisos(1, [])

        assert resultado is False

    finally:
        modelo.conexion.close()



# CP-PER-03 (prueba positiva: Evitar duplicar permisos asociados a un rol)

def test_no_duplicar_permisos_del_rol(datos_permisos, permisos_registrados):
    modelo = datos_permisos["modelo"]
    cod_rol = datos_permisos["cod_rol"]

    permisos_lista = [
        f"{modulo}-{accion}"
        for modulo, acciones in permisos_registrados.items()
        for accion in acciones
    ]

    assert modelo.registrar(cod_rol, permisos_registrados) == 1
    assert modelo.registrar(cod_rol, permisos_registrados) == 1

    assert modelo.buscar_permisos(cod_rol, permisos_lista) is False

    cursor = modelo.conexion.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM seguridad.rol_permiso rp
        INNER JOIN seguridad.permiso p
            ON p.cod_permiso = rp.cod_permiso
        WHERE rp.cor_rol = %s
          AND CONCAT(p.cod_modulo, '-', p.cod_accion) IN (
              '6-3', '6-4', '7-1', '7-2', '7-3', '7-4'
          )
    """, (cod_rol,))

    cantidad = cursor.fetchone()[0]
    cursor.close()

    assert cantidad == len(permisos_lista)