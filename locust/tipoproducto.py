import os
import uuid
from datetime import date, timedelta

from locust import HttpUser, between, task


CEDULA = os.getenv("LOCUST_CEDULA", "4723317").strip()
PASSWORD = os.getenv("LOCUST_PASSWORD", "admin123").strip()

# Ajusta estos códigos a registros activos de la base de datos de pruebas.
Nombre_producto = os.getenv("LOCUST_NOMBRE_PRODUCTO", "Producto de prueba").strip()


CAPTCHA_CODE = "AB12CD"



class TipoProducto(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.tipos_productos_creados = {}

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

    def _datos_tipo_producto(self, nombre):
        return {
            "nombre_tipo_producto": nombre,
        }

    @staticmethod
    def _nombre_prueba(prefijo):
        sufijo = "".join(
            chr(ord("A") + int(caracter, 16))
            for caracter in uuid.uuid4().hex[:8]
        )
        return f"{prefijo} {sufijo}"

    def _buscar_tipo_producto(self, nombre):
        with self.client.post(
            "/admin?ruta=tipoproducto",
            data={"buscar": nombre},
            name="Buscar tipo de producto",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta de búsqueda no es JSON.")
                return None

            tipo_producto = resultado.get("datos")
            if (
                response.status_code == 200
                and resultado.get("existe")
                and tipo_producto
                and tipo_producto.get("cod_tipo_producto")
            ):
                response.success()
                return tipo_producto

            response.failure("No se encontró el tipo de producto.")
            return None

    @task(4)
    def registrar_tipo_producto(self):
        # Mantiene como máximo un tipo de producto pendiente por usuario virtual.
        if self.tipos_productos_creados:
            return

        nombre = self._nombre_prueba("Locust")
        datos = self._datos_tipo_producto(nombre)
        datos["registrar"] = "1"

        with self.client.post(
            "/admin?ruta=tipoproducto",
            data=datos,
            name="Registrar tipo de producto",
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

        tipo_producto = self._buscar_tipo_producto(nombre)
        if tipo_producto:
            self.tipos_productos_creados[tipo_producto["cod_tipo_producto"]] = nombre

    @task(3)
    def consultar_tipo_producto(self):
        with self.client.get(
            "/admin?ruta=tipoproducto",
            name="Consultar tipos de producto",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Error HTTP {response.status_code}")
            elif "/admin?ruta=login" in response.url:
                response.failure("La sesión expiró.")
            else:
                response.success()

        if self.tipos_productos_creados:
            nombre = next(iter(self.tipos_productos_creados.values()))
            self._buscar_tipo_producto(nombre)

    @task(2)
    def editar_tipo_producto(self):
        if not self.tipos_productos_creados:
            return

        cod_tipo_producto = next(iter(self.tipos_productos_creados))
        nombre = self._nombre_prueba("Edicion")
        datos = self._datos_tipo_producto(nombre)
        datos.update(
            {
                "actualizar": "1",
                "cod_tipo_producto": str(cod_tipo_producto),
                "status": "1",
            }
        )

        with self.client.post(
            "/admin?ruta=tipoproducto",
            data=datos,
            name="Editar tipo de producto",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.tipos_productos_creados[cod_tipo_producto] = nombre
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )

    @task(1)
    def eliminar_tipo_producto(self):
        if not self.tipos_productos_creados:
            return

        cod_tipo_producto = next(iter(self.tipos_productos_creados))
        with self.client.post(
            "/admin?ruta=tipoproducto",
            data={
                "eliminar": "1",
                "cod_tipo_producto": str(cod_tipo_producto),
            },
            name="Eliminar tipo de producto",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.tipos_productos_creados.pop(cod_tipo_producto)
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )