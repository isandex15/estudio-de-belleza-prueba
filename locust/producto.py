import os
import uuid
from datetime import date, timedelta

from locust import HttpUser, between, task


CEDULA = os.getenv("LOCUST_CEDULA", "4723317").strip()
PASSWORD = os.getenv("LOCUST_PASSWORD", "admin123").strip()

# Ajusta estos códigos a registros activos de la base de datos de pruebas.
COD_CATEGORIA = os.getenv("LOCUST_COD_CATEGORIA", "4")
COD_MARCA = os.getenv("LOCUST_COD_MARCA", "4")
COD_UNIDAD = os.getenv("LOCUST_COD_UNIDAD", "7")
COD_TIPO_PRODUCTO = os.getenv("LOCUST_COD_TIPO_PRODUCTO", "3")

CAPTCHA_CODE = "AB12CD"
PRECIO = "10.00"
STOCK = "1"


class Producto(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.productos_creados = {}

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

    def _datos_producto(self, nombre):
        return {
            "nombre_producto": nombre,
            "precio_producto": PRECIO,
            "stock": STOCK,
            "cod_categoria": COD_CATEGORIA,
            "cod_marca": COD_MARCA,
            "cod_unidad": COD_UNIDAD,
            "cod_presentacion": os.getenv("LOCUST_COD_PRESENTACION", "1"),
            "cod_medida": os.getenv("LOCUST_COD_MEDIDA", "1"),
            "fecha_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
            "cod_tipo_producto": COD_TIPO_PRODUCTO,
        }

    def _buscar_producto(self, nombre):
        with self.client.post(
            "/admin?ruta=producto",
            data={"buscar": nombre},
            name="Buscar producto",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta de búsqueda no es JSON.")
                return None

            producto = resultado.get("datos")
            if (
                response.status_code == 200
                and resultado.get("existe")
                and producto
                and producto.get("cod_producto")
            ):
                response.success()
                return producto

            response.failure("No se encontró el producto.")
            return None

    @task(5)
    def registrar_producto(self):
        # Mantiene como máximo un producto pendiente por usuario virtual.
        if self.productos_creados:
            return

        nombre = f"L{uuid.uuid4().hex[:8]}"
        datos = self._datos_producto(nombre)
        datos["registrar"] = "1"

        with self.client.post(
            "/admin?ruta=producto",
            data=datos,
            name="Registrar producto",
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

        producto = self._buscar_producto(nombre)
        if producto:
            self.productos_creados[producto["cod_producto"]] = nombre

    @task(3)
    def consultar_producto(self):
        with self.client.get(
            "/admin?ruta=producto",
            name="Consultar productos",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Error HTTP {response.status_code}")
            elif "/admin?ruta=login" in response.url:
                response.failure("La sesión expiró.")
            else:
                response.success()

        if self.productos_creados:
            nombre = next(iter(self.productos_creados.values()))
            self._buscar_producto(nombre)

    @task(2)
    def editar_producto(self):
        if not self.productos_creados:
            return

        cod_producto = next(iter(self.productos_creados))
        nombre = f"E{uuid.uuid4().hex[:8]}"
        datos = self._datos_producto(nombre)
        datos.update(
            {
                "actualizar": "1",
                "cod_producto": str(cod_producto),
                "status": "1",
            }
        )

        with self.client.post(
            "/admin?ruta=producto",
            data=datos,
            name="Editar producto",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.productos_creados[cod_producto] = nombre
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )

    @task(1)
    def eliminar_producto(self):
        if not self.productos_creados:
            return

        cod_producto = next(iter(self.productos_creados))
        with self.client.post(
            "/admin?ruta=producto",
            data={
                "eliminar": "1",
                "cod_producto": str(cod_producto),
            },
            name="Eliminar producto",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.productos_creados.pop(cod_producto)
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )