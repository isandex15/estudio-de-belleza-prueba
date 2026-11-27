import json
import os
from datetime import date

from locust import HttpUser, between, task


# Estos datos son los de una cuenta de prueba. Se leen del entorno para no
# guardar contraseñas en el archivo.
CEDULA = os.getenv("LOCUST_CEDULA", "4723317").strip()
PASSWORD = os.getenv("LOCUST_PASSWORD", "admin123").strip()

# En login.py, el CAPTCHA de prueba usa este código cuando app.testing=True.
CAPTCHA_CODE = "AB12CD"

# Datos de ejemplo: reemplaza estos códigos por un proveedor y producto
# existentes en tu base de datos de pruebas.
COD_PROVEEDOR = int(os.getenv("LOCUST_COD_PROVEEDOR", "2"))
COD_PRODUCTO = int(os.getenv("LOCUST_COD_PRODUCTO", "7"))
CANTIDAD = 1
PRECIO = 10.00


class Compra(HttpUser):
    # Pausa aleatoria entre tareas de este usuario virtual (en segundos).
    wait_time = between(1, 5)

    def on_start(self):
        self.codigos_compra = []

        # Locust conserva las cookies de self.client entre peticiones;
        # así se conserva la sesión después de iniciar sesión.
        if not CEDULA or not PASSWORD:
            raise RuntimeError("Define LOCUST_CEDULA y LOCUST_PASSWORD.")

        url_login = "/admin?ruta=login"

        self.client.post(url_login, data={"generar_captcha": "1"})

        captcha = self.client.post(
            url_login,
            data={
                "verificar_captcha": "1",
                "respuesta": CAPTCHA_CODE,
            },
        )
        if not captcha.json().get("verificado"):
            raise RuntimeError(
                "No se verificó el CAPTCHA. Usa app.testing=True para la prueba."
            )

        login = self.client.post(
            url_login,
            data={
                "login": "1",
                "cedula": CEDULA,
                "password": PASSWORD,
            },
        )
        if login.json().get("icon") != "success":
            raise RuntimeError(login.json().get("text", "No se pudo iniciar sesión."))

    @task(5)
    def registrar_compra(self):
        # El controlador espera estos campos del formulario. "productos" es
        # una lista convertida a JSON porque el servidor la lee con json.loads.
        datos = {
            "registrar": "1",
            "fecha_compra": date.today().isoformat(),
            "cod_proveedor": str(COD_PROVEEDOR),
            "total": str(CANTIDAD * PRECIO),
            "productos": json.dumps(
                [
                    {
                        "cod_producto": COD_PRODUCTO,
                        "cantidad": CANTIDAD,
                        "precio": PRECIO,
                    }
                ]
            ),
        }

        with self.client.post(
            "/admin?ruta=compra",
            data=datos,
            name="Registrar compra",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except json.JSONDecodeError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                cod_compra = resultado.get("cod_compra")
                if cod_compra:
                    self.codigos_compra.append(cod_compra)
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )

    @task(3)
    def consultar_compras(self):
        with self.client.get(
            "/admin?ruta=compra",
            name="Consultar compras",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Error HTTP {response.status_code}")
            elif "/admin?ruta=login" in response.url:
                response.failure("La sesión expiró.")
            else:
                response.success()

        if not self.codigos_compra:
            return

        cod_compra = self.codigos_compra[-1]
        with self.client.get(
            "/admin?ruta=compra",
            params={
                "detalle_compra": "1",
                "cod_compra": cod_compra,
            },
            name="Consultar detalle de compra",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except json.JSONDecodeError:
                response.failure("La respuesta del detalle no es JSON.")
                return

            if response.status_code == 200 and resultado.get("compra"):
                response.success()
            else:
                response.failure("No se encontró el detalle de la compra.")

    @task(2)
    def eliminar_compra(self):
        if not self.codigos_compra:
            return

        cod_compra = self.codigos_compra[0]
        with self.client.post(
            "/admin?ruta=compra",
            data={
                "eliminar": "1",
                "cod_compra": str(cod_compra),
            },
            name="Eliminar compra",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except json.JSONDecodeError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.codigos_compra.pop(0)
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )
