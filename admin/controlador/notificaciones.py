from flask import request, jsonify
from admin.modelo.notificaciones import NotificacionesModelo
from admin.modelo.inicio import InicioModelo


def handle_request():

    modelo = NotificacionesModelo()
    modelo_inicio = InicioModelo()

    # =====================================================
    # DEVOLUCIÓN DE STOCK - 08:00 PM
    # =====================================================
    if request.args.get("devolucion_stock") == "1":

        from datetime import datetime

        ahora = datetime.now()

        if ahora.hour >= 20:

            devoluciones = (
                modelo_inicio.procesar_reservas_8pm()
            )

        else:

            devoluciones = []

        return jsonify({
            "status": True,
            "devoluciones": devoluciones
        })

    # =====================================================
    # EMPRESA
    # =====================================================

    if request.args.get("empresa") == "1":

        empresa_registrada = (
            modelo.consultarEmpresaRegistrada()
        )

        return jsonify({
            "status": True,
            "empresa_registrada": empresa_registrada
        })

    # =====================================================
    # CANCELACIONES
    # =====================================================

    if request.args.get("cancelacion") == "1":

        ultima = (
            modelo.consultarUltimaCancelacion()
        )

        cancelaciones_hoy = (
            modelo.consultarCancelacionesHoy()
        )

        return jsonify({
            "status": True,
            "ultima": ultima,
            "cancelaciones": cancelaciones_hoy
        })

    # =====================================================
    # NOTIFICACIONES GENERALES
    # =====================================================

    datos = modelo.consultar()

    if datos:

        return jsonify({
            "status": True,
            "fecha": datos["fecha"],
            "reservas": datos["reservas"],
            "clientes": datos["clientes"],
            "pagos": datos["pagos"],
            "pagos_personal": datos.get("pagos_personal", []),
            "mantenimientos": datos.get("mantenimientos", []),
            "monedas": datos.get("monedas", []),
            "compras": datos["compras"],
            "productos_bajo_stock": datos["productos_bajo_stock"]
        })

    return jsonify({
        "status": False,
        "mensaje": (
            "No se pudieron consultar "
            "las notificaciones."
        )
    }), 500