from flask import request, jsonify
from admin.modelo.pagospersonal import PagospersonalModelo
import re


def handle_request(ruta):
    return pagospersonal()


# PAGOS PERSONAL
def pagospersonal():
    modelo = PagospersonalModelo()
    mensaje = None

    if request.method == "POST" and request.form.get("verificar_referencia"):
        referencia_pago = request.form.get("referencia_pago", "").strip()
        return jsonify({
            "registrada": bool(referencia_pago and modelo.existe_referencia(referencia_pago))
        })

    if request.method == "POST" and request.form.get("verificar_pago_personal"):
        cod_servicio = int(request.form.get("cod_servicio", 0) or 0)
        return jsonify({
            "registrado": bool(cod_servicio and modelo.existe_pago_activo(cod_servicio))
        })

    if request.method == "POST" and request.form.get("crear_banco"):
        nombre_banco = (request.form.get("nombre_banco", "") or "").strip()
        if not nombre_banco:
            return jsonify({
                "icon": "warning",
                "title": "Banco requerido",
                "text": "Debe escribir el nombre del banco."
            })

        if len(nombre_banco) > 35:
            return jsonify({
                "icon": "warning",
                "title": "limite de caracteres alcanzado",
                "text": "limite de caracteres alcanzado"
            })

        if re.search(r"[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]", nombre_banco):
            return jsonify({
                "icon": "warning",
                "title": "Nombre inválido",
                "text": "Este campo solo permite letras."
            })

        if modelo.buscar_banco(nombre_banco):
            return jsonify({
                "icon": "warning",
                "title": "Banco duplicado",
                "text": "Ese banco ya existe en el sistema."
            })

        codigo = modelo.crear_banco(nombre_banco)
        if codigo:
            return jsonify({
                "icon": "success",
                "title": "Banco agregado",
                "text": "El banco fue registrado correctamente.",
                "cod_banco": codigo,
                "nombre_banco": nombre_banco
            })

        return jsonify({
            "icon": "error",
            "title": "Error",
            "text": modelo.ultimo_error or "No se pudo registrar el banco."
        })

    if request.method == "POST" and request.form.get("registrar"):
        errores = []

        cod_servicio = int(request.form.get("cod_servicio", 0) or 0)
        fecha_pago = request.form.get("fecha_pago", "").strip()
        hora_pago = request.form.get("hora_pago", "").strip()
        if hour := hora_pago:
            hora_pago = hour if len(hour) == 8 else (hour + ':00' if len(hour) == 5 else hour)
        porcentaje = int(request.form.get("porcentaje", 0) or 0)
        cod_banco = int(request.form.get("cod_banco", 0) or 0)
        cod_tipo_pago = int(request.form.get("cod_tipo_pago", 0) or 0)
        referencia_pago = request.form.get("referencia_pago", "").strip()
        tasa_pago = request.form.get("tasa_pago", "").strip()
        archivo_comprobante = request.files.get("comprobante_pago")
        monto_comision = modelo.calcular_comision(cod_servicio, porcentaje)

        if cod_servicio <= 0:
            errores.append("Debe seleccionar un servicio.")
        if not fecha_pago:
            errores.append("Debe indicar la fecha del pago.")
        if porcentaje <= 0:
            errores.append("El porcentaje debe ser mayor a cero.")
        if cod_banco <= 0:
            errores.append("Debe seleccionar el banco de destino.")
        if cod_tipo_pago <= 0:
            errores.append("Debe seleccionar el tipo de pago.")
        if not referencia_pago:
            errores.append("Debe indicar la referencia del pago móvil.")
        if len(referencia_pago) > 100:
            errores.append("La referencia no puede superar 100 caracteres.")
        if referencia_pago and modelo.existe_referencia(referencia_pago):
            errores.append("La referencia del pago ya está registrada.")
        if tasa_pago not in {"BCV", "Euro"}:
            errores.append("Debe seleccionar la tasa del pago.")
        if monto_comision <= 0:
            errores.append("No se pudo calcular la comisión del servicio.")

        if not archivo_comprobante or not archivo_comprobante.filename:
            errores.append("Debe adjuntar el comprobante de pago.")
        elif archivo_comprobante.mimetype not in {"image/jpeg", "image/png", "image/gif"}:
            errores.append("El comprobante debe ser una imagen JPG, PNG o GIF.")
        else:
            archivo_comprobante.stream.seek(0, 2)
            tamano = archivo_comprobante.stream.tell()
            archivo_comprobante.stream.seek(0)
            if tamano > 5 * 1024 * 1024:
                errores.append("El comprobante no puede superar 5 MB.")

        validar = modelo.validarPagoPersonal(
            cod_servicio=cod_servicio,
            fecha_pago=fecha_pago,
            hora_pago=hora_pago,
            porcentaje=porcentaje
        )

        if not validar["status"]:
            return jsonify(validar)

        if errores:
            return jsonify({
                "icon": "error",
                "title": "Error de validación",
                "text": " ".join(errores)
            })

        if modelo.existe_pago_activo(cod_servicio):
            return jsonify({
                "icon": "warning",
                "title": "Pago personal ya registrado",
                "text": "anule el anterior para registrarlo nuevamente"
            })

        try:
            modelo.cod_servicio = cod_servicio
            modelo.fecha_pago = fecha_pago
            modelo.hora_pago = hora_pago or "00:00:00"
            modelo.porcentaje = porcentaje
            modelo.status = 1
            modelo.cod_banco = cod_banco
            modelo.referencia_pago = referencia_pago or None
            modelo.tasa_pago = tasa_pago
        except ValueError as error:
            return jsonify({
                "icon": "warning",
                "title": "Dato inválido",
                "text": str(error)
            })

        if not errores and not modelo.subir_comprobante(archivo_comprobante):
            return jsonify({
                "icon": "error",
                "title": "Comprobante inválido",
                "text": "No se pudo guardar el comprobante de pago."
            })

        if modelo.registrar():
            return jsonify({
                "icon": "success",
                "title": "Pago personal registrado",
                "text": "El pago del personal se registró correctamente.",
                "notificacion": True
            })

        return jsonify({
            "icon": "error",
            "title": "Error",
            "text": modelo.ultimo_error or "No se pudo registrar el pago del personal."
        })

    if request.method == "POST" and request.form.get("anular"):
        cod_pago_personal = request.form.get("cod_pago_personal_a_anular")
        if not cod_pago_personal or not str(cod_pago_personal).isdigit():
            return jsonify({
                "icon": "warning",
                "title": "Pago inválido",
                "text": "No se recibió un pago personal válido."
            })

        resultado = modelo.anular(int(cod_pago_personal))
        if resultado:
            return jsonify({
                "icon": "success",
                "title": "Pago anulado con éxito",
                "text": "El pago personal se anuló correctamente."
            })
        return jsonify({
            "icon": "error",
            "title": "Error al anular",
            "text": modelo.ultimo_error or "El pago no existe o ya estaba anulado."
        })

    registro = modelo.consultar()
    servicios = modelo.listar_servicios()
    bancos = modelo.listar_bancos()
    tipopagos = modelo.listar_tipos_pago()
    return {
        "registro": registro,
        "servicios": servicios,
        "bancos": bancos,
        "tipopagos": tipopagos,
        "mensaje": mensaje
    }
