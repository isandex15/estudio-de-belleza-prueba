from datetime import datetime
from admin.config.conexion import Conexion


class NotificacionesModelo(Conexion):

    def __init__(self):
        super().__init__()

    def consultar(self):
        cursor = self.conexion.cursor(dictionary=True)

        try:
            fecha_hoy = datetime.now().date()

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM seguridad.usuario
                WHERE cod_rol = 3
                AND fecha_registro = %s
                AND status = 1
            """, (fecha_hoy,))
            total_clientes = int(cursor.fetchone()["total"] or 0)

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM sac.servicio
                WHERE fecha = %s
                AND status = 1
            """, (fecha_hoy,))
            total_reservas = int(cursor.fetchone()["total"] or 0)

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM sac.compra
                WHERE fecha_compra = %s
                AND status = 1
            """, (fecha_hoy,))
            total_compras = int(cursor.fetchone()["total"] or 0)

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM sac.pago
                WHERE fecha_pago = %s
                AND status = 1
            """, (fecha_hoy,))
            total_pagos = int(cursor.fetchone()["total"] or 0)

            # Consulta de productos activos con stock bajo para generar notificaciones.
            cursor.execute("""
                SELECT cod_producto, nombre_producto, stock
                FROM sac.producto
                WHERE status = 1
                AND stock < 3
                ORDER BY stock ASC, nombre_producto ASC
            """)
            productos_bajo_stock = [
                {
                    "cod_producto": int(producto["cod_producto"]),
                    "nombre_producto": producto["nombre_producto"],
                    "stock": int(producto["stock"] or 0)
                }
                for producto in cursor.fetchall()
            ]
            #  PAGOS AL PERSONAL
            cursor.execute("""
                SELECT pp.cod_pago_personal,
                       CONCAT(COALESCE(u.nombre_usuario, ''), ' ', COALESCE(u.apellido_usuario, '')) AS nombre_especialista
                FROM sac.pago_personal pp
                INNER JOIN sac.servicio s ON s.cod_servicio = pp.cod_servicio
                LEFT JOIN seguridad.usuario u ON u.cedula = s.cedula_especialista
                WHERE pp.fecha_pago = %s AND pp.status = 1
                ORDER BY pp.cod_pago_personal DESC
            """, (fecha_hoy,))
            pagos_personal = cursor.fetchall()

            # MANTENIMIENTO
            cursor.execute("""
                SELECT cod_mantenimiento, nombre_archivo
                FROM seguridad.mantenimiento
                WHERE fecha = %s
                ORDER BY cod_mantenimiento DESC
            """, (fecha_hoy,))
            mantenimientos = cursor.fetchall()

            #  ACTUALIZACION DE MONEDAS
            cursor.execute("""
                SELECT actual.cod_cambio, actual.cod_moneda, m.nombre_moneda,
                       anterior.valor AS valor_anterior, actual.valor AS valor_nuevo,
                       actual.fecha AS fecha_cambio
                FROM sac.cambio actual
                INNER JOIN sac.moneda m ON m.cod_moneda = actual.cod_moneda
                LEFT JOIN (
                    SELECT c.cod_moneda, c.valor
                    FROM sac.cambio c
                    INNER JOIN (
                        SELECT cod_moneda, MAX(CONCAT(fecha, ' ', LPAD(cod_cambio, 11, '0'))) AS ultimo
                        FROM sac.cambio
                        WHERE fecha < %s
                        GROUP BY cod_moneda
                    ) anterior ON anterior.cod_moneda = c.cod_moneda
                              AND CONCAT(c.fecha, ' ', LPAD(c.cod_cambio, 11, '0')) = anterior.ultimo
                ) anterior ON anterior.cod_moneda = actual.cod_moneda
                WHERE actual.fecha = %s AND actual.valor IS NOT NULL
                ORDER BY actual.cod_cambio DESC
            """, (fecha_hoy, fecha_hoy))
            cambios_monedas = cursor.fetchall()
            for cambio in cambios_monedas:
                cambio["fecha_cambio"] = str(cambio["fecha_cambio"])
                cambio["valor_anterior"] = float(cambio["valor_anterior"] or 0)
                cambio["valor_nuevo"] = float(cambio["valor_nuevo"] or 0)

            return {
                "status": True,
                "fecha": str(fecha_hoy),
                "clientes": total_clientes,
                "reservas": [{
                    "fecha": str(fecha_hoy),
                    "total": total_reservas
                }],
                "compras": total_compras,
                "pagos": total_pagos,
                "pagos_personal": pagos_personal,
                "mantenimientos": mantenimientos,
                "monedas": cambios_monedas,
                "productos_bajo_stock": productos_bajo_stock
            }

        except Exception as error:
            print("Error al consultar notificaciones:", error)

            return {
                "status": False,
                "fecha": str(datetime.now().date()),
                "clientes": 0,
                "reservas": [],
                "compras": 0,
                "pagos": 0,
                "pagos_personal": [],
                "mantenimientos": [],
                "monedas": [],
                "productos_bajo_stock": []
            }

        finally:
            cursor.close()

    def consultarUltimaCancelacion(self):
        cursor = self.conexion.cursor(dictionary=True)

        try:
            sql = """
                SELECT s.cod_servicio, s.fecha, s.hora,
                       u.nombre_usuario, u.apellido_usuario
                FROM sac.servicio s
                INNER JOIN seguridad.usuario u
                    ON u.cedula = s.cedula
                WHERE s.status = 0
                ORDER BY s.cod_servicio DESC
                LIMIT 1
            """

            cursor.execute(sql)
            resultado = cursor.fetchone()

            if not resultado:
                return None

            return {
                "cod_servicio": int(resultado["cod_servicio"]),
                "fecha": resultado["fecha"].strftime("%Y-%m-%d")
                    if resultado["fecha"] else "",
                "hora": str(resultado["hora"])
                    if resultado["hora"] else "",
                "cliente": f'{resultado["nombre_usuario"]} '
                           f'{resultado["apellido_usuario"]}'.strip()
            }

        except Exception as error:
            print("Error consultando última cancelación:", error)
            return None

        finally:
            cursor.close()

    def consultarCancelacionesHoy(self):
        cursor = self.conexion.cursor(dictionary=True)

        try:
            fecha_hoy = datetime.now().date()

            sql = """
                SELECT s.cod_servicio, s.fecha, s.hora,
                       u.nombre_usuario, u.apellido_usuario
                FROM sac.servicio s
                INNER JOIN seguridad.usuario u
                    ON u.cedula = s.cedula
                WHERE s.status = 0
                AND s.fecha = %s
                ORDER BY s.cod_servicio DESC
            """

            cursor.execute(sql, (fecha_hoy,))
            resultados = cursor.fetchall()

            cancelaciones = []

            for resultado in resultados:
                cancelaciones.append({
                    "cod_servicio": int(resultado["cod_servicio"]),
                    "fecha": resultado["fecha"].strftime("%Y-%m-%d")
                        if resultado["fecha"] else "",
                    "hora": str(resultado["hora"])
                        if resultado["hora"] else "",
                    "cliente": f'{resultado["nombre_usuario"]} '
                               f'{resultado["apellido_usuario"]}'.strip()
                })

            return cancelaciones

        except Exception as error:
            print("Error consultando cancelaciones del día:", error)
            return []

        finally:
            cursor.close()


    def consultarEmpresaRegistrada(self):
        cursor = self.conexion.cursor(dictionary=True)

        try:
            sql = """
                SELECT COUNT(*) AS total
                FROM sac.empresa
            """

            cursor.execute(sql)
            resultado = cursor.fetchone()

            return resultado["total"] > 0

        except Exception as error:
            print("Error verificando empresa registrada:", error)
            return False

        finally:
            cursor.close()


    def consultarDevolucionesStock(self):

        import json
        import os
        from datetime import datetime
        from flask import current_app

        archivo = os.path.join(
            current_app.root_path,
            "static",
            "assets",
            "js",
            "modulos-js",
            "json-js",
            "reservas_stock.json"
        )

        if not os.path.exists(archivo):
            return []

        try:

            with open(
                archivo,
                "r",
                encoding="utf-8"
            ) as f:

                datos = json.load(f)

            fecha_hoy = str(
                datetime.now().date()
            )

            devoluciones = []

            cursor = self.conexion.cursor(
                dictionary=True
            )

            # ==========================================================
            # BUSCAR RESERVAS DE HOY SIN PAGO
            # ==========================================================

            cursor.execute("""
                SELECT
                    s.cod_servicio,
                    s.fecha,
                    s.hora,
                    CONCAT(
                        u.nombre_usuario,
                        ' ',
                        u.apellido_usuario
                    ) AS cliente
                FROM sac.servicio s
                INNER JOIN seguridad.usuario u
                    ON u.cedula = s.cedula
                WHERE s.fecha = %s
                AND s.status = 0
                AND NOT EXISTS (
                    SELECT 1
                    FROM sac.pago p
                    WHERE p.cod_servicio = s.cod_servicio
                    AND p.status = 1
                )
                ORDER BY s.cod_servicio ASC
            """, (fecha_hoy,))

            reservas_canceladas = cursor.fetchall()

            cursor.close()

            # ==========================================================
            # BUSCAR EN EL JSON
            # ==========================================================

            for reserva in reservas_canceladas:

                cod_servicio = str(
                    reserva["cod_servicio"]
                )

                datos_reserva = datos.get(
                    cod_servicio
                )

                if not datos_reserva:
                    continue

                if datos_reserva.get(
                    "fecha"
                ) != fecha_hoy:
                    continue

                devoluciones.append({
                    "cod_servicio": reserva[
                        "cod_servicio"
                    ],
                    "fecha": fecha_hoy,
                    "hora": (
                        str(reserva["hora"])
                        if reserva["hora"]
                        else ""
                    ),
                    "cliente": reserva[
                        "cliente"
                    ],
                    "productos": datos_reserva.get(
                        "productos",
                        {}
                    )
                })

            return devoluciones

        except Exception as error:

            print(
                "Error consultando devoluciones de stock:",
                error
            )

            return []