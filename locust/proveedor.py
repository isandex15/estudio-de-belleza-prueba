import os
import uuid

from locust import HttpUser, between, task


CEDULA = os.getenv("LOCUST_CEDULA", "4723317").strip()
PASSWORD = os.getenv("LOCUST_PASSWORD", "admin123").strip()
CAPTCHA_CODE = "AB12CD"


class Proveedor(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.proveedores_creados = {}

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
    def _datos_proveedor():
        cedula = f"{uuid.uuid4().int % 100000000:08d}"
        return {
            "cedula": cedula,
            "nombre": "Locust",
            "apellido": "Prueba",
            "rif": f"J{cedula}",
            "telefono": f"04{cedula}",
            "correo": f"locust{cedula}@example.test",
        }

    def _buscar_proveedor(self, cedula):
        with self.client.post(
            "/admin?ruta=proveedor",
            data={"buscar": cedula},
            name="Buscar proveedor",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta de búsqueda no es JSON.")
                return None

            proveedor = resultado.get("datos")
            if (
                response.status_code == 200
                and resultado.get("existe")
                and proveedor
                and proveedor.get("cod_proveedor")
            ):
                response.success()
                return proveedor

            response.failure("No se encontró el proveedor.")
            return None

    @task(5)
    def registrar_proveedor(self):
        if self.proveedores_creados:
            return

        datos = self._datos_proveedor()
        payload = datos.copy()
        payload["registrar"] = "1"

        with self.client.post(
            "/admin?ruta=proveedor",
            data=payload,
            name="Registrar proveedor",
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

        proveedor = self._buscar_proveedor(datos["cedula"])
        if proveedor:
            self.proveedores_creados[proveedor["cod_proveedor"]] = datos

    @task(3)
    def consultar_proveedores(self):
        with self.client.get(
            "/admin?ruta=proveedor",
            name="Consultar proveedores",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Error HTTP {response.status_code}")
            elif "/admin?ruta=login" in response.url:
                response.failure("La sesión expiró.")
            else:
                response.success()

        if self.proveedores_creados:
            datos = next(iter(self.proveedores_creados.values()))
            self._buscar_proveedor(datos["cedula"])

    @task(2)
    def editar_proveedor(self):
        if not self.proveedores_creados:
            return

        cod_proveedor = next(iter(self.proveedores_creados))
        datos = self.proveedores_creados[cod_proveedor].copy()
        datos.update(
            {
                "actualizar": "1",
                "cod_proveedor": str(cod_proveedor),
                "nombre": "Editado",
                "status": "1",
            }
        )

        with self.client.post(
            "/admin?ruta=proveedor",
            data=datos,
            name="Editar proveedor",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                datos.pop("actualizar")
                datos.pop("cod_proveedor")
                datos.pop("status")
                self.proveedores_creados[cod_proveedor] = datos
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )

    @task(1)
    def eliminar_proveedor(self):
        if not self.proveedores_creados:
            return

        cod_proveedor = next(iter(self.proveedores_creados))
        with self.client.post(
            "/admin?ruta=proveedor",
            data={
                "eliminar": "1",
                "cod_proveedor": str(cod_proveedor),
            },
            name="Eliminar proveedor",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.proveedores_creados.pop(cod_proveedor)
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )
