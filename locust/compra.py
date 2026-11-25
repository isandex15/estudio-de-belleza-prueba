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
COD_PROVEEDOR = 2
COD_PRODUCTO = 7
CANTIDAD = 1
PRECIO = 10.00


class Compra(HttpUser):
    # Pausa aleatoria entre tareas de este usuario virtual (en segundos).
    wait_time = between(1, 5)

    def on_start(self):
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

    @task
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
            resultado = response.json()

            if response.status_code == 200 and resultado.get("icon") == "success":
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )
