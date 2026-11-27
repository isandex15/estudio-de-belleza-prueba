import os
import uuid
from datetime import date, timedelta

from locust import HttpUser, between, task


CEDULA = os.getenv("LOCUST_CEDULA", "4723317").strip()
PASSWORD = os.getenv("LOCUST_PASSWORD", "admin123").strip()

# Ajusta estos códigos a registros activos de la base de datos de pruebas.
Nombre_servicio = os.getenv("LOCUST_NOMBRE_SERVICIO", "Servicio de prueba").strip()
precio = os.getenv("LOCUST_PRECIO", "10000").strip()


CAPTCHA_CODE = "AB12CD"



class TipoServicios(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.tipos_servicios_creados = {}

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

    def _datos_tipo_servicio(self, nombre):
        return {
            "nombre_servicio": nombre,
            "precio": precio,
        }

    @staticmethod
    def _nombre_prueba(prefijo):
        sufijo = "".join(
            chr(ord("A") + int(caracter, 16))
            for caracter in uuid.uuid4().hex[:8]
        )
        return f"{prefijo} {sufijo}"

    def _buscar_tipo_servicio(self, nombre):
        with self.client.post(
            "/admin?ruta=tiposervicio",
            data={"buscar": nombre},
            name="Buscar tipo de servicios",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta de búsqueda no es JSON.")
                return None

            tipo_servicio = resultado.get("datos")
            if (
                response.status_code == 200
                and resultado.get("existe")
                and tipo_servicio
                and tipo_servicio.get("cod_tipo_servicio")
            ):
                response.success()
                return tipo_servicio

            response.failure("No se encontró el tipo de servicio.")
            return None

    @task(4)
    def registrar_tipo_servicio(self):
        # Mantiene como máximo un tipo de servicio pendiente por usuario virtual.
        if self.tipos_servicios_creados:
            return

        nombre = self._nombre_prueba("Locust")
        datos = self._datos_tipo_servicio(nombre)
        datos["registrar"] = "1"

        with self.client.post(
            "/admin?ruta=tiposervicio",
            data=datos,
            name="Registrar tipo de servicio",
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

        tipo_servicio = self._buscar_tipo_servicio(nombre)
        if tipo_servicio:
            self.tipos_servicios_creados[tipo_servicio["cod_tipo_servicio"]] = nombre

    @task(3)
    def consultar_tipo_servicio(self):
        with self.client.get(
            "/admin?ruta=tiposervicio",
            name="Consultar tipos de servicio",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Error HTTP {response.status_code}")
            elif "/admin?ruta=login" in response.url:
                response.failure("La sesión expiró.")
            else:
                response.success()

        if self.tipos_servicios_creados:
            nombre = next(iter(self.tipos_servicios_creados.values()))
            self._buscar_tipo_servicio(nombre)

    @task(2)
    def editar_tipo_servicio(self):
        if not self.tipos_servicios_creados:
            return

        cod_tipo_servicio = next(iter(self.tipos_servicios_creados))
        nombre = self._nombre_prueba("Edicion")
        datos = self._datos_tipo_servicio(nombre)
        datos.update(
            {
                "actualizar": "1",
                "cod_tipo_servicio": str(cod_tipo_servicio),
                "status": "1",
            }
        )

        with self.client.post(
            "/admin?ruta=tiposervicio",
            data=datos,
            name="Editar tipo de servicio",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.tipos_servicios_creados[cod_tipo_servicio] = nombre
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )

    @task(1)
    def eliminar_tipo_servicio(self):
        if not self.tipos_servicios_creados:
            return

        cod_tipo_servicio = next(iter(self.tipos_servicios_creados))
        with self.client.post(
            "/admin?ruta=tiposervicio",
            data={
                "eliminar": "1",
                "cod_tipo_servicio": str(cod_tipo_servicio),
            },
            name="Eliminar tipo de servicio",
            catch_response=True,
        ) as response:
            try:
                resultado = response.json()
            except ValueError:
                response.failure("La respuesta no es JSON.")
                return

            if response.status_code == 200 and resultado.get("icon") == "success":
                self.tipos_servicios_creados.pop(cod_tipo_servicio)
                response.success()
            else:
                response.failure(
                    resultado.get("text", f"Error HTTP {response.status_code}")
                )