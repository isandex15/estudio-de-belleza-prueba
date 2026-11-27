import os
import uuid
from datetime import date, timedelta

from locust import HttpUser, between, task


CEDULA = os.getenv("LOCUST_CEDULA", "4723317").strip()
PASSWORD = os.getenv("LOCUST_PASSWORD", "admin123").strip()

# Ajusta estos códigos a registros activos de la base de datos de pruebas.
Nombre_marca = os.getenv("LOCUST_NOMBRE_MARCA", "Marca de prueba").strip()


CAPTCHA_CODE = "AB12CD"



class Marca(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.marcas_creadas = {}

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

    def _datos_marca(self, nombre):
        return {
            "nombre_marca": nombre,
        }

    @staticmethod
    def _nombre_prueba(prefijo):
        sufijo = "".join(
            chr(ord("A") + int(caracter, 16))
            for caracter in uuid.uuid4().hex[:8]
        )
        return f"{prefijo} {sufijo}"

    def _buscar_marca(self, nombre):
        with self.client.post(
            "/admin?ruta=marca",
            data={"buscar": nombre},
            name="Buscar tipo marca",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta de búsqueda no es JSON.")
                return None

            marca = resultado.get("datos")
            if (
                response.status_code == 200
                and resultado.get("existe")
                and marca
                and marca.get("cod_marca")
            ):
                response.success()
                return marca

            response.failure("No se encontró la marca.")
            return None

    @task(4)
    def registrar_marca(self):
        # Mantiene como máximo una marca pendiente por usuario virtual.
        if self.marcas_creadas:
            return

        nombre = self._nombre_prueba("Locust")
        datos = self._datos_marca(nombre)
        datos["registrar"] = "1"

        with self.client.post(
            "/admin?ruta=marca",
            data=datos,
            name="Registrar marca",
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

        marca = self._buscar_marca(nombre)
        if marca:
            self.marcas_creadas[marca["cod_marca"]] = nombre

    @task(3)
    def consultar_marca(self):
        with self.client.get(
            "/admin?ruta=marca",
            name="Consultar marca",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Error HTTP {response.status_code}")
            elif "/admin?ruta=login" in response.url:
                response.failure("La sesión expiró.")
            else:
                response.success()

        if self.marcas_creadas:
            nombre = next(iter(self.marcas_creadas.values()))
            self._buscar_marca(nombre)

    @task(2)
    def editar_marca(self):
        if not self.marcas_creadas:
            return

        cod_marca = next(iter(self.marcas_creadas))
        nombre = self._nombre_prueba("Edicion")
        datos = self._datos_marca(nombre)
        datos.update(
            {
                "actualizar": "1",
                "cod_marca": str(cod_marca),
                "status": "1",
            }
        )

        with self.client.post(
            "/admin?ruta=marca",
            data=datos,
            name="Editar marca",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.marcas_creadas[cod_marca] = nombre
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )

    @task(1)
    def eliminar_marca(self):
        if not self.marcas_creadas:
            return

        cod_marca = next(iter(self.marcas_creadas))
        with self.client.post(
            "/admin?ruta=marca",
            data={
                "eliminar": "1",
                "cod_marca": str(cod_marca),
            },
            name="Eliminar marca",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.marcas_creadas.pop(cod_marca)
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )