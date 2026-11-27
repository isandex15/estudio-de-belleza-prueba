import os
import uuid
from datetime import date, timedelta

from locust import HttpUser, between, task


CEDULA = os.getenv("LOCUST_CEDULA", "4723317").strip()
PASSWORD = os.getenv("LOCUST_PASSWORD", "admin123").strip()

# Ajusta estos códigos a registros activos de la base de datos de pruebas.
Nombre_categoria = os.getenv("LOCUST_NOMBRE_CATEGORIA", "Categoría de prueba").strip()


CAPTCHA_CODE = "AB12CD"



class Categoria(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.categorias_creadas = {}

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

    def _datos_categoria(self, nombre):
        return {
            "nombre_categoria": nombre,
        }

    @staticmethod
    def _nombre_prueba(prefijo):
        sufijo = "".join(
            chr(ord("A") + int(caracter, 16))
            for caracter in uuid.uuid4().hex[:8]
        )
        return f"{prefijo} {sufijo}"

    def _buscar_categoria(self, nombre):
        with self.client.post(
            "/admin?ruta=categoria",
            data={"buscar": nombre},
            name="Buscar tipo categoria",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta de búsqueda no es JSON.")
                return None

            categoria = resultado.get("datos")
            if (
                response.status_code == 200
                and resultado.get("existe")
                and categoria
                and categoria.get("cod_categoria")
            ):
                response.success()
                return categoria

            response.failure("No se encontró la categoria.")
            return None

    @task(4)
    def registrar_categoria(self):
        # Mantiene como máximo una categoria pendiente por usuario virtual.
        if self.categorias_creadas:
            return

        nombre = self._nombre_prueba("Locust")
        datos = self._datos_categoria(nombre)
        datos["registrar"] = "1"

        with self.client.post(
            "/admin?ruta=categoria",
            data=datos,
            name="Registrar categoria",
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

        categoria = self._buscar_categoria(nombre)
        if categoria:
            self.categorias_creadas[categoria["cod_categoria"]] = nombre

    @task(3)
    def consultar_categoria(self):
        with self.client.get(
            "/admin?ruta=categoria",
            name="Consultar categoria",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Error HTTP {response.status_code}")
            elif "/admin?ruta=login" in response.url:
                response.failure("La sesión expiró.")
            else:
                response.success()

        if self.categorias_creadas:
            nombre = next(iter(self.categorias_creadas.values()))
            self._buscar_categoria(nombre)

    @task(2)
    def editar_categoria(self):
        if not self.categorias_creadas:
            return

        cod_categoria = next(iter(self.categorias_creadas))
        nombre = self._nombre_prueba("Edicion")
        datos = self._datos_categoria(nombre)
        datos.update(
            {
                "actualizar": "1",
                "cod_categoria": str(cod_categoria),
                "status": "1",
            }
        )

        with self.client.post(
            "/admin?ruta=categoria",
            data=datos,
            name="Editar categoria",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.categorias_creadas[cod_categoria] = nombre
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )

    @task(1)
    def eliminar_categoria(self):
        if not self.categorias_creadas:
            return

        cod_categoria = next(iter(self.categorias_creadas))
        with self.client.post(
            "/admin?ruta=categoria",
            data={
                "eliminar": "1",
                "cod_categoria": str(cod_categoria),
            },
            name="Eliminar categoria",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.categorias_creadas.pop(cod_categoria)
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )