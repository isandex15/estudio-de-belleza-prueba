import os
import uuid
from datetime import date, timedelta

from locust import HttpUser, between, task


CEDULA = os.getenv("LOCUST_CEDULA", "4723317").strip()
PASSWORD = os.getenv("LOCUST_PASSWORD", "admin123").strip()
CAPTCHA_CODE = "AB12CD"


class Promocion(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.promociones_creadas = {}

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

    @staticmethod
    def _datos_promocion(prefijo):
        inicio = date.today() + timedelta(days=1)
        nombre = f"{prefijo} {uuid.uuid4().hex[:8].upper()}"
        return {
            "nombre_promo": nombre,
            "descripcion_promo": "Promocion automatizada de prueba Locust",
            "descuento": "15",
            "inicio_promo": inicio.isoformat(),
            "fin_promo": (inicio + timedelta(days=30)).isoformat(),
        }

    def _buscar_promocion(self, nombre):
        with self.client.post(
            "/admin?ruta=promocion",
            data={"buscar": nombre},
            name="Buscar promoción",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta de búsqueda no es JSON.")
                return None

            promocion = resultado.get("datos")
            if (
                response.status_code == 200
                and resultado.get("existe")
                and promocion
                and promocion.get("cod_promo")
            ):
                response.success()
                return promocion

            response.failure("No se encontró la promoción.")
            return None

    @task(5)
    def registrar_promocion(self):
        if self.promociones_creadas:
            return

        datos = self._datos_promocion("Locust")
        payload = datos.copy()
        payload["registrar"] = "1"

        with self.client.post(
            "/admin?ruta=promocion",
            data=payload,
            name="Registrar promoción",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code != 200 or resultado.get("icon") != "success":
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )
                return

            response.success()

        promocion = self._buscar_promocion(datos["nombre_promo"])
        if promocion:
            self.promociones_creadas[promocion["cod_promo"]] = datos

    @task(3)
    def consultar_promociones(self):
        with self.client.get(
            "/admin?ruta=promocion",
            name="Consultar promociones",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Error HTTP {response.status_code}")
            elif "/admin?ruta=login" in response.url:
                response.failure("La sesión expiró.")
            else:
                response.success()

        if self.promociones_creadas:
            datos = next(iter(self.promociones_creadas.values()))
            self._buscar_promocion(datos["nombre_promo"])

    @task(2)
    def editar_promocion(self):
        if not self.promociones_creadas:
            return

        cod_promo = next(iter(self.promociones_creadas))
        datos = self._datos_promocion("Editada")
        payload = datos.copy()
        payload.update(
            {
                "actualizar": "1",
                "cod_promo": str(cod_promo),
                "status": "1",
            }
        )

        with self.client.post(
            "/admin?ruta=promocion",
            data=payload,
            name="Editar promoción",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.promociones_creadas[cod_promo] = datos
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )

    @task(1)
    def eliminar_promocion(self):
        if not self.promociones_creadas:
            return

        cod_promo = next(iter(self.promociones_creadas))
        with self.client.post(
            "/admin?ruta=promocion",
            data={
                "eliminar": "1",
                "cod_promo": str(cod_promo),
            },
            name="Eliminar promoción",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.promociones_creadas.pop(cod_promo)
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )
