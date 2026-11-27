import os
import sys
from pathlib import Path

import mysql.connector
import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from admin.config.config import DB_HOST, DB_NAME, DB_PASS, DB_SEGURIDAD_NAME, DB_USER


_REQUIRED_ROUTINES = {
    ("sp_registrar_pago_completo", "PROCEDURE"),
    ("sp_respaldar_mantenimiento", "PROCEDURE"),
    ("fn_calcular_comision_servicio", "FUNCTION"),
    ("fn_calcular_total_pago_personal", "FUNCTION"),
}


@pytest.fixture(scope="session")
def integration_test_database():
    isolated_ci_mysql = (
        os.getenv("GITHUB_ACTIONS") == "true"
        and os.getenv("CI_MYSQL_SERVICE") == "true"
        and DB_HOST == "127.0.0.1"
        and DB_NAME == "sac"
        and DB_SEGURIDAD_NAME == "seguridad"
    )
    isolated_test_databases = (
        DB_NAME == "sac_test" and DB_SEGURIDAD_NAME == "seguridad_test"
    )
    if not (isolated_ci_mysql or isolated_test_databases):
        pytest.fail(
            "Pruebas detenidas por seguridad: usa sac_test/seguridad_test o "
            "el servicio MySQL efímero configurado en GitHub Actions."
        )

    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
    )
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT ROUTINE_NAME, ROUTINE_TYPE
            FROM information_schema.ROUTINES
            WHERE ROUTINE_SCHEMA = %s
            """,
            (DB_NAME,),
        )
        available_routines = set(cursor.fetchall())
        missing_routines = sorted(_REQUIRED_ROUTINES - available_routines)

        cursor.execute(
            """
            SELECT TABLE_NAME, COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s
              AND (
                    (TABLE_NAME = 'banco' AND COLUMN_NAME = 'nombre_banco')
                 OR (TABLE_NAME = 'pago_personal' AND COLUMN_NAME = 'referencia_pago')
              )
            """,
            (DB_NAME,),
        )
        available_columns = set(cursor.fetchall())
        required_columns = {
            ("banco", "nombre_banco"),
            ("pago_personal", "referencia_pago"),
        }
        missing_columns = sorted(required_columns - available_columns)

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'usuario'
            """,
            (DB_SEGURIDAD_NAME,),
        )
        security_schema_available = cursor.fetchone()[0] == 1
        cursor.close()
    finally:
        connection.close()

    if missing_routines or missing_columns or not security_schema_available:
        details = []
        if missing_routines:
            details.append(f"rutinas faltantes: {missing_routines}")
        if missing_columns:
            details.append(f"columnas faltantes: {missing_columns}")
        if not security_schema_available:
            details.append(
                "no se encuentra la tabla de usuarios en la base de seguridad de pruebas"
            )
        pytest.fail(
            "Prepara el esquema de integración importando "
            f"db/integration_test_schema.sql y los procedimientos requeridos. "
            f"{'; '.join(details)}"
        )


@pytest.fixture
def ready_test_database(integration_test_database):
    return None
