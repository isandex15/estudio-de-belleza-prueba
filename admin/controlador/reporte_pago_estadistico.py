from flask import request, send_file
from admin.modelo.pagos import PagosModelo
from admin.modelo.empresa import EmpresaModelo
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Line
from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from datetime import datetime
import tempfile
import os


def _logo_path():
    return os.path.abspath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', '..', 'static', 'Logo SAC.jpeg'
    ))


def _empresa_dato(empresa, campo, predeterminado=''):
    return str((empresa or {}).get(campo) or predeterminado)


def _empresa_logo_path(empresa):
    logo = _empresa_dato(empresa, 'logo')
    if not logo:
        return _logo_path()
    ruta = os.path.abspath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', '..', logo
    )) if not os.path.isabs(logo) else logo
    return ruta if os.path.exists(ruta) else _logo_path()


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.grey)
    canvas.drawString(15 * mm, 12 * mm, 'Sistema de Gestión | Reporte generado automáticamente')
    canvas.drawRightString(195 * mm, 12 * mm, f'Página {doc.page}')
    canvas.restoreState()


def borde(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.lightgrey)
    canvas.setLineWidth(1)
    canvas.rect(20 * mm, 20 * mm, LETTER[0] - 40 * mm, LETTER[1] - 40 * mm)
    canvas.restoreState()


def _build_filters(desde, hasta, cod_tipo_pago, status, cedula_especialista=0, cedula_cliente=0):
    condiciones = []
    parametros = []

    if desde:
        condiciones.append('p.fecha_pago >= %s')
        parametros.append(desde)

    if hasta:
        condiciones.append('p.fecha_pago <= %s')
        parametros.append(hasta)

    if cod_tipo_pago and cod_tipo_pago > 0:
        condiciones.append('dp.cod_tipo_pago = %s')
        parametros.append(cod_tipo_pago)

    if cedula_especialista and int(cedula_especialista) > 0:
        condiciones.append('s.cedula_especialista = %s')
        parametros.append(int(cedula_especialista))

    if cedula_cliente:
        condiciones.append('s.cedula = %s')
        parametros.append(str(cedula_cliente))

    if status == 'active':
        condiciones.append('p.status = 1')
    elif status == 'anulado':
        condiciones.append('p.status = 0')

    where = ' AND '.join(condiciones) if condiciones else '1=1'
    return where, parametros


def _fetch_scalar(modelo, sql, parametros):
    cursor = modelo.conexion.cursor(dictionary=True)
    cursor.execute(sql, tuple(parametros))
    fila = cursor.fetchone()
    cursor.close()
    return fila


def _fetch_rows(modelo, sql, parametros):
    cursor = modelo.conexion.cursor(dictionary=True)
    cursor.execute(sql, tuple(parametros))
    filas = cursor.fetchall()
    cursor.close()
    return filas


def _consultar_pagos_personal(modelo, desde=None, hasta=None, status='all', cedula_especialista=0):
    condiciones = []
    parametros = []

    if desde:
        condiciones.append('pp.fecha_pago >= %s')
        parametros.append(desde)
    if hasta:
        condiciones.append('pp.fecha_pago <= %s')
        parametros.append(hasta)
    if cedula_especialista and int(cedula_especialista) > 0:
        condiciones.append('s.cedula_especialista = %s')
        parametros.append(int(cedula_especialista))
    if status == 'active':
        condiciones.append('pp.status = 1')
    elif status == 'anulado':
        condiciones.append('pp.status = 0')

    where = ' AND '.join(condiciones) if condiciones else '1=1'
    return _fetch_rows(modelo, f'''
        SELECT
            pp.cod_pago_personal,
            pp.fecha_pago,
            pp.referencia_pago,
            pp.comprobante,
            pp.status,
            s.cod_servicio,
            CONCAT(COALESCE(u.nombre_usuario, ''), ' ', COALESCE(u.apellido_usuario, '')) AS nombre_especialista,
            COALESCE(b.nombre_banco, 'Sin banco') AS nombre_banco,
            COALESCE(
                fn_calcular_comision_servicio(
                    COALESCE((
                        SELECT SUM(GREATEST(CAST(ds.cantidad_servicio AS DECIMAL(10,2)), 1) * ts.precio)
                        FROM detalle_servicio ds
                        LEFT JOIN tipo_servicio ts ON ts.cod_tipo_servicio = ds.cod_tipo_servicio
                        WHERE ds.cod_servicio = s.cod_servicio
                    ), 0),
                    pp.porcentaje
                ),
                0
            ) AS monto_pagado
        FROM pago_personal pp
        INNER JOIN servicio s ON s.cod_servicio = pp.cod_servicio
        LEFT JOIN seguridad.usuario u ON u.cedula = s.cedula_especialista
        LEFT JOIN banco b ON b.cod_banco = pp.cod_banco
        WHERE {where}
        ORDER BY pp.fecha_pago DESC, pp.cod_pago_personal DESC
    ''', parametros)


def _consultar_estadisticas(modelo, desde=None, hasta=None, cod_tipo_pago=0, status='all', cedula_especialista=0, cedula_cliente=''):
    where, parametros = _build_filters(
        desde, hasta, cod_tipo_pago, status, cedula_especialista, cedula_cliente
    )

    total_pagos = _fetch_scalar(modelo, f'''
        SELECT COUNT(DISTINCT p.cod_pago) AS total_pagos
        FROM pago p
        LEFT JOIN detalle_pago dp ON dp.cod_pago = p.cod_pago
        LEFT JOIN servicio s ON p.cod_servicio = s.cod_servicio
        WHERE {where}
    ''', parametros) or {}

    ingresos = _fetch_scalar(modelo, f'''
        SELECT
            COALESCE(SUM(p.monto), 0) AS ingresos_totales,
            COALESCE(AVG(p.monto), 0) AS pago_promedio,
            COALESCE(MAX(p.fecha_pago), NULL) AS fecha_maxima,
            COALESCE(MIN(p.fecha_pago), NULL) AS fecha_minima
        FROM pago p
        LEFT JOIN detalle_pago dp ON dp.cod_pago = p.cod_pago
        LEFT JOIN servicio s ON p.cod_servicio = s.cod_servicio
        WHERE {where}
    ''', parametros) or {}

    estado = _fetch_scalar(modelo, f'''
        SELECT
            COALESCE(SUM(p.status = 1), 0) AS pagos_activos,
            COALESCE(SUM(p.status = 0), 0) AS pagos_anulados,
            COALESCE(ROUND((SUM(p.status = 0) / NULLIF(COUNT(p.cod_pago), 0)) * 100, 2), 0) AS tasa_cancelacion
        FROM pago p
        LEFT JOIN detalle_pago dp ON dp.cod_pago = p.cod_pago
        LEFT JOIN servicio s ON p.cod_servicio = s.cod_servicio
        WHERE {where}
    ''', parametros) or {}

    pagos_por_tipo = _fetch_rows(modelo, f'''
        SELECT
            COALESCE(tp.cod_tipo_pago, 0) AS cod_tipo_pago,
            COALESCE(tp.nombre_tipo_pago, 'Sin tipo') AS nombre_tipo_pago,
            COUNT(DISTINCT p.cod_pago) AS total_pagos,
            COALESCE(SUM(p.monto), 0) AS ingresos
        FROM pago p
        LEFT JOIN detalle_pago dp ON dp.cod_pago = p.cod_pago
        LEFT JOIN tipo_pago tp ON tp.cod_tipo_pago = dp.cod_tipo_pago
        LEFT JOIN servicio s ON p.cod_servicio = s.cod_servicio
        WHERE {where}
        GROUP BY tp.cod_tipo_pago, tp.nombre_tipo_pago
        ORDER BY ingresos DESC
    ''', parametros)

    pagos_por_moneda = _fetch_rows(modelo, f'''
        SELECT
            COALESCE(m.cod_moneda, 0) AS cod_moneda,
            COALESCE(m.nombre_moneda, 'Bs') AS nombre_moneda,
            COUNT(DISTINCT p.cod_pago) AS total_pagos,
            COALESCE(SUM(p.monto), 0) AS ingresos
        FROM pago p
        LEFT JOIN detalle_pago dp ON dp.cod_pago = p.cod_pago
        LEFT JOIN moneda m ON m.cod_moneda = COALESCE(dp.cod_moneda, 1)
        LEFT JOIN servicio s ON p.cod_servicio = s.cod_servicio
        WHERE {where}
        GROUP BY m.cod_moneda, m.nombre_moneda
        ORDER BY ingresos DESC
    ''', parametros)

    pagos_por_mes = _fetch_rows(modelo, f'''
        SELECT
            DATE_FORMAT(p.fecha_pago, '%b %Y') AS periodo,
            COUNT(DISTINCT p.cod_pago) AS total_pagos,
            COALESCE(SUM(p.monto), 0) AS ingresos
        FROM pago p
        LEFT JOIN detalle_pago dp ON dp.cod_pago = p.cod_pago
        LEFT JOIN servicio s ON p.cod_servicio = s.cod_servicio
        WHERE {where}
        GROUP BY YEAR(p.fecha_pago), MONTH(p.fecha_pago)
        ORDER BY YEAR(p.fecha_pago), MONTH(p.fecha_pago)
        LIMIT 12
    ''', parametros)

    ingresos_por_especialista = _fetch_rows(modelo, f'''
        SELECT
            u.cedula,
            CONCAT(COALESCE(u.nombre_usuario, ''), ' ', COALESCE(u.apellido_usuario, '')) AS nombre_especialista,
            COUNT(DISTINCT p.cod_pago) AS total_pagos,
            COALESCE(SUM(p.monto), 0) AS ingresos,
            MIN(p.fecha_pago) AS fecha_inicio,
            MAX(p.fecha_pago) AS fecha_fin
        FROM pago p
        INNER JOIN servicio s ON p.cod_servicio = s.cod_servicio
        INNER JOIN seguridad.usuario u ON s.cedula_especialista = u.cedula
        LEFT JOIN detalle_pago dp ON dp.cod_pago = p.cod_pago
        WHERE {where}
        GROUP BY u.cedula, u.nombre_usuario, u.apellido_usuario
        ORDER BY ingresos DESC
        LIMIT 10
    ''', parametros)

    resumen_especialista_mes = _fetch_rows(modelo, f'''
        SELECT
            CONCAT(COALESCE(u.nombre_usuario, ''), ' ', COALESCE(u.apellido_usuario, '')) AS nombre_especialista,
            DATE_FORMAT(p.fecha_pago, '%b %Y') AS periodo,
            COUNT(DISTINCT p.cod_pago) AS total_pagos,
            COALESCE(SUM(p.monto), 0) AS ingresos,
            SUM(p.status = 0) AS pagos_cancelados,
            ROUND((SUM(p.status = 0) / NULLIF(COUNT(p.cod_pago), 0)) * 100, 2) AS tasa_cancelacion
        FROM pago p
        INNER JOIN servicio s ON p.cod_servicio = s.cod_servicio
        INNER JOIN seguridad.usuario u ON s.cedula_especialista = u.cedula
        LEFT JOIN detalle_pago dp ON dp.cod_pago = p.cod_pago
        WHERE {where}
        GROUP BY u.cedula, u.nombre_usuario, u.apellido_usuario, YEAR(p.fecha_pago), MONTH(p.fecha_pago)
        ORDER BY YEAR(p.fecha_pago), MONTH(p.fecha_pago), ingresos DESC
        LIMIT 12
    ''', parametros)

    top_clientes = _fetch_rows(modelo, f'''
        SELECT
            u.cedula,
            u.nombre_usuario AS nombre_cliente,
            COUNT(DISTINCT p.cod_pago) AS total_pagos,
            COALESCE(SUM(p.monto), 0) AS ingresos
        FROM pago p
        INNER JOIN servicio s ON p.cod_servicio = s.cod_servicio
        LEFT JOIN seguridad.usuario u ON s.cedula = u.cedula
        LEFT JOIN detalle_pago dp ON dp.cod_pago = p.cod_pago
        WHERE {where}
        GROUP BY u.cedula, u.nombre_usuario
        ORDER BY ingresos DESC
        LIMIT 5
    ''', parametros)

    ultimos_pagos = _fetch_rows(modelo, f'''
        SELECT
            p.cod_pago,
            p.fecha_pago,
            p.monto,
            p.status,
            p.comprobante_pago,
            s.cod_servicio,
            COALESCE(
                (
                    SELECT GROUP_CONCAT(
                        DISTINCT ts.nombre_servicio
                        ORDER BY ts.nombre_servicio
                        SEPARATOR ', '
                    )
                    FROM detalle_servicio ds
                    INNER JOIN tipo_servicio ts
                        ON ts.cod_tipo_servicio = ds.cod_tipo_servicio
                    WHERE ds.cod_servicio = s.cod_servicio
                ),
                NULLIF(TRIM(s.descripcion), ''),
                'Servicio'
            ) AS servicio,
            u.nombre_usuario AS cliente,
            COALESCE(tp.nombre_tipo_pago, 'N/A') AS tipo_pago,
            COALESCE(m.nombre_moneda, 'Bs') AS moneda
        FROM pago p
        INNER JOIN servicio s ON p.cod_servicio = s.cod_servicio
        LEFT JOIN seguridad.usuario u ON s.cedula = u.cedula
        LEFT JOIN detalle_pago dp ON dp.cod_pago = p.cod_pago
        LEFT JOIN tipo_pago tp ON tp.cod_tipo_pago = dp.cod_tipo_pago
        LEFT JOIN moneda m ON m.cod_moneda = COALESCE(dp.cod_moneda, 1)
        WHERE {where}
        ORDER BY p.fecha_pago DESC
        LIMIT 10
    ''', parametros)

    total_dias = 1
    if ingresos.get('fecha_minima') and ingresos.get('fecha_maxima'):
        try:
            total_dias = max(1, (datetime.strptime(ingresos['fecha_maxima'], '%Y-%m-%d') - datetime.strptime(ingresos['fecha_minima'], '%Y-%m-%d')).days + 1)
        except Exception:
            total_dias = 1

    return {
        'total_pagos': int(total_pagos.get('total_pagos') or 0),
        'ingresos_totales': float(ingresos.get('ingresos_totales') or 0.0),
        'pago_promedio': float(ingresos.get('pago_promedio') or 0.0),
        'promedio_por_dia': float(ingresos.get('ingresos_totales') or 0.0) / total_dias,
        'pagos_activos': int(estado.get('pagos_activos') or 0),
        'pagos_anulados': int(estado.get('pagos_anulados') or 0),
        'tasa_cancelacion': float(estado.get('tasa_cancelacion', 0.0) or 0.0),
        'pagos_por_tipo': pagos_por_tipo,
        'pagos_por_moneda': pagos_por_moneda,
        'pagos_por_mes': pagos_por_mes,
        'ingresos_por_especialista': ingresos_por_especialista,
        'resumen_especialista_mes': resumen_especialista_mes,
        'top_clientes': top_clientes,
        'ultimos_pagos': ultimos_pagos,
    }


def _generar_pdf(empresa, estadisticas, filtros):
    archivo = os.path.join(tempfile.gettempdir(), f'reporte_pagos_estadistico_{int(datetime.now().timestamp())}.pdf')
    doc = SimpleDocTemplate(
        archivo,
        pagesize=LETTER,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm
    )
    styles = getSampleStyleSheet()

    empresa_style = ParagraphStyle(
        'empresa', parent=styles['Heading1'], fontName='Helvetica-Bold',
        fontSize=18, leading=20, textColor=colors.HexColor('#1B365D'), alignment=TA_LEFT
    )
    titulo_style = ParagraphStyle(
        'titulo', parent=styles['Heading1'], fontName='Helvetica-Bold',
        fontSize=18, textColor=colors.HexColor('#B8860B'), alignment=TA_CENTER, spaceAfter=4
    )
    subtitulo_style = ParagraphStyle(
        'subtitulo', parent=styles['Normal'], fontName='Helvetica', fontSize=10,
        textColor=colors.grey, alignment=TA_CENTER
    )

    normal_style = ParagraphStyle(
        "normal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14
    )

    elementos = []

    logo = ''
    logo_path = _empresa_logo_path(empresa)
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=42 * mm, height=42 * mm)

    nombre_empresa = _empresa_dato(empresa, 'nombre')
    direccion_empresa = _empresa_dato(empresa, 'direccion')
    telefono_empresa = _empresa_dato(empresa, 'telefono')
    correo_empresa = _empresa_dato(empresa, 'email')

    empresa_html = f"""
        <font size="18" color="#1B365D"><b>{nombre_empresa}</b></font><br/><br/>
        <font size="10"><b>Dirección:</b> {direccion_empresa}<br/>
        <b>Teléfono:</b> {telefono_empresa}<br/>
        <b>Correo:</b> {correo_empresa}</font>
    """
    encabezado = Table([[logo, Paragraph(empresa_html, normal_style)]], colWidths=[48 * mm, 120 * mm])
    encabezado.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
    ]))
    elementos.append(encabezado)

    linea = Drawing(520, 12)
    linea.add(Line(0, 5, 520, 5, strokeColor=colors.HexColor('#D4AF37'), strokeWidth=2))
    elementos.extend([linea, Spacer(1, 12)])
    elementos.append(Paragraph('REPORTE ESTADÍSTICO DE PAGOS', titulo_style))
    elementos.append(Paragraph('Análisis de pagos registrados en el sistema administrativo.', subtitulo_style))
    if filtros.get('nombre_especialista'):
        elementos.append(Paragraph(f"Especialista seleccionado: {filtros['nombre_especialista']}", subtitulo_style))
    if filtros.get('nombre_cliente'):
        elementos.append(Paragraph(f"Cliente seleccionado: {filtros['nombre_cliente']}", subtitulo_style))
    if filtros.get('detalle_especialista'):
        elementos.append(Paragraph('Reporte de pagos al especialista seleccionado', subtitulo_style))
    elementos.append(Paragraph(f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y')}", subtitulo_style))
    elementos.append(Spacer(1, 10))

    metrics_data = [
        ['Métrica', 'Valor'],
        ['Total de pagos', str(estadisticas['total_pagos'])],
        ['Ingresos totales', f"{estadisticas['ingresos_totales']:.2f}"],
        ['Pagos anulados', str(estadisticas['pagos_anulados'])],
    ]
    if not filtros.get('cedula_cliente'):
        metrics_data.insert(3, ['Pago promedio', f"{estadisticas['pago_promedio']:.2f}"])
    metrics_table = Table(metrics_data, hAlign='LEFT', colWidths=[80 * mm, 65 * mm])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))
    elementos.extend([metrics_table, Spacer(1, 12)])

    if filtros.get('detalle_especialista'):
        elementos.append(Paragraph('Detalle de pagos al especialista', styles['Heading3']))
        detalle_data = [['Fecha', 'Referencia', 'Banco', 'Pago', 'Comprobante', 'Estado']]
        for item in estadisticas['pagos_personal']:
            comprobante = 'Sin comprobante'
            if item['comprobante']:
                ruta_comprobante = os.path.abspath(os.path.join(
                    os.path.dirname(__file__), '..', '..', 'static', item['comprobante']
                ))
                if os.path.exists(ruta_comprobante):
                    comprobante = Image(ruta_comprobante, width=28 * mm, height=20 * mm, kind='proportional')
                else:
                    comprobante = os.path.basename(item['comprobante'])
            detalle_data.append([
                str(item['fecha_pago']),
                str(item['referencia_pago'] or 'Sin referencia'),
                item['nombre_banco'],
                f"{float(item['monto_pagado'] or 0):.2f}",
                comprobante,
                'Activo' if item['status'] == 1 else 'Anulado'
            ])
        if len(detalle_data) == 1:
            detalle_data.append(['Sin datos', '', '', '', '', ''])
        detalle_table = Table(
            detalle_data,
            hAlign='LEFT',
            colWidths=[25 * mm, 35 * mm, 32 * mm, 22 * mm, 35 * mm, 22 * mm],
            repeatRows=1
        )
        detalle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        elementos.extend([detalle_table, Spacer(1, 12)])

    if filtros.get('cedula_especialista') and estadisticas['resumen_especialista_mes']:
        elementos.append(Paragraph('Ganancia del especialista por mes', styles['Heading3']))
        especialista_mes_data = [['Periodo', 'Pagos', 'Ingresos', 'Cancelados']]
        for item in estadisticas['resumen_especialista_mes']:
            especialista_mes_data.append([
                item['periodo'],
                item['total_pagos'],
                f"{item['ingresos']:.2f}",
                item['pagos_cancelados']
            ])
        especialista_mes_table = Table(
            especialista_mes_data,
            hAlign='LEFT',
            colWidths=[55 * mm, 35 * mm, 45 * mm, 35 * mm],
            repeatRows=1
        )
        especialista_mes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        elementos.extend([especialista_mes_table, Spacer(1, 12)])

    if filtros.get('detalle_especialista'):
        elementos.append(Paragraph('Pagos realizados al especialista', styles['Heading3']))
        personal_data = [['Fecha', 'Referencia', 'Banco', 'Monto', 'Comprobante', 'Estado']]
        for item in estadisticas['pagos_personal']:
            comprobante = 'Sin comprobante'
            if item['comprobante']:
                comprobante_path = os.path.abspath(os.path.join(
                    os.path.dirname(__file__), '..', '..', 'static', item['comprobante']
                ))
                if os.path.exists(comprobante_path):
                    comprobante = Image(comprobante_path, width=30 * mm, height=22 * mm, kind='proportional')
                else:
                    comprobante = os.path.basename(item['comprobante'])
            personal_data.append([
                str(item['fecha_pago']),
                item['referencia_pago'] or 'Sin referencia',
                item['nombre_banco'],
                f"{float(item['monto_pagado'] or 0):.2f}",
                comprobante,
                'Activo' if item['status'] == 1 else 'Anulado'
            ])
        if len(personal_data) == 1:
            personal_data.append(['Sin datos', '', '', '', '', ''])
        personal_table = Table(personal_data, hAlign='LEFT', colWidths=[25 * mm, 40 * mm, 35 * mm, 25 * mm, 35 * mm, 22 * mm], repeatRows=1)
        personal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        elementos.extend([personal_table, Spacer(1, 12)])

    if not filtros.get('cedula_cliente') and estadisticas['pagos_por_tipo']:
        elementos.append(Paragraph('Pagos por tipo', styles['Heading3']))
        tipo_data = [['Tipo', 'Pagos', 'Ingresos']]
        for item in estadisticas['pagos_por_tipo']:
            tipo_data.append([item['nombre_tipo_pago'], item['total_pagos'], f"{item['ingresos']:.2f}"])
        tipo_table = Table(tipo_data, hAlign='LEFT', colWidths=[75 * mm, 35 * mm, 45 * mm], repeatRows=1)
        tipo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        elementos.extend([tipo_table, Spacer(1, 12)])

    if not filtros.get('cedula_cliente') and estadisticas['pagos_por_moneda']:
        elementos.append(Paragraph('Pagos por moneda', styles['Heading3']))
        moneda_data = [['Moneda', 'Pagos', 'Ingresos']]
        for item in estadisticas['pagos_por_moneda']:
            moneda_data.append([item['nombre_moneda'], item['total_pagos'], f"{item['ingresos']:.2f}"])
        moneda_table = Table(moneda_data, hAlign='LEFT', colWidths=[75 * mm, 35 * mm, 45 * mm], repeatRows=1)
        moneda_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        elementos.extend([moneda_table, Spacer(1, 12)])

    if not filtros.get('cedula_cliente') and estadisticas['top_clientes']:
        elementos.append(Paragraph('Top clientes', styles['Heading3']))
        clientes_data = [['Cliente', 'Pagos', 'Ingresos']]
        for cliente in estadisticas['top_clientes']:
            clientes_data.append([cliente['nombre_cliente'], cliente['total_pagos'], f"{cliente['ingresos']:.2f}"])
        clientes_table = Table(clientes_data, hAlign='LEFT', colWidths=[90 * mm, 35 * mm, 40 * mm], repeatRows=1)
        clientes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        elementos.extend([clientes_table, Spacer(1, 12)])

    if filtros.get('cedula_cliente') and estadisticas['ultimos_pagos']:
        elementos.append(Paragraph('Información de pagos', styles['Heading3']))
        detalle_data = [['Servicio', 'Fecha', 'Monto', 'Tipo', 'Moneda', 'Comprobante', 'Estado']]
        for pago in estadisticas['ultimos_pagos']:
            comprobante = 'Sin comprobante'
            if pago['comprobante_pago']:
                comprobante_path = os.path.abspath(os.path.join(
                    os.path.dirname(__file__), '..', '..', 'static', pago['comprobante_pago']
                ))
                if os.path.exists(comprobante_path):
                    comprobante = Image(
                        comprobante_path,
                        width=22 * mm,
                        height=18 * mm,
                        kind='proportional'
                    )
                else:
                    comprobante = os.path.basename(pago['comprobante_pago'])
            detalle_data.append([
                Paragraph(str(pago['servicio'] or 'Servicio'), styles['Normal']),
                str(pago['fecha_pago']),
                f"{float(pago['monto'] or 0):.2f}",
                Paragraph(str(pago['tipo_pago'] or 'N/A'), styles['Normal']),
                Paragraph(str(pago['moneda'] or 'Bs'), styles['Normal']),
                comprobante,
                'Activo' if pago['status'] == 1 else 'Anulado'
            ])
        detalle_table = Table(
            detalle_data,
            hAlign='LEFT',
            colWidths=[38 * mm, 23 * mm, 20 * mm, 25 * mm, 20 * mm, 28 * mm, 20 * mm],
            repeatRows=1
        )
        detalle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        elementos.extend([detalle_table, Spacer(1, 12)])

    doc.build(
        elementos,
        onFirstPage=lambda c, d: (borde(c, d), footer(c, d)),
        onLaterPages=lambda c, d: (borde(c, d), footer(c, d))
    )
    return archivo


def _generar_excel(empresa, estadisticas, filtros):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Estadísticas'

    logo_path = _empresa_logo_path(empresa)
    if os.path.exists(logo_path):
        logo = ExcelImage(logo_path)
        logo.width = 75
        logo.height = 60
        sheet.add_image(logo, 'B1')

    sheet.merge_cells('A6:C6')
    sheet['A6'] = _empresa_dato(empresa, 'nombre')
    sheet['A6'].font = Font(bold=True, size=14)
    sheet['A6'].alignment = Alignment(horizontal='center')
    for row, value in enumerate([
        f"Dirección: {_empresa_dato(empresa, 'direccion')}",
        f"Teléfono: {_empresa_dato(empresa, 'telefono')}",
        f"Correo: {_empresa_dato(empresa, 'email')}",
        datetime.now().strftime('%d-%m-%Y'),
    ], start=7):
        sheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
        sheet.cell(row=row, column=1).value = value
        sheet.cell(row=row, column=1).alignment = Alignment(horizontal='center')

    sheet.row_dimensions[1].height = 50
    sheet.row_dimensions[2].height = 8
    sheet.row_dimensions[3].height = 8
    sheet.row_dimensions[4].height = 8
    sheet.row_dimensions[5].height = 8
    sheet.row_dimensions[6].height = 22
    gold_border = Border(bottom=Side(style='medium', color='D4AF37'))
    for cell in sheet[10]:
        cell.border = gold_border
    sheet['A10'].font = Font(italic=True, color='777777')

    sheet.append([])
    sheet.append(['Reporte Estadístico de Pagos'])
    sheet.merge_cells('A12:C12')
    sheet['A12'].font = Font(bold=True, size=14, color='B8860B')
    sheet['A12'].alignment = Alignment(horizontal='center')
    sheet.append(['Emitido', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    sheet.append([])
    sheet.append(['Métrica', 'Valor'])
    sheet.append(['Total de pagos', estadisticas['total_pagos']])
    sheet.append(['Ingresos totales', float(estadisticas['ingresos_totales'])])
    if not filtros.get('cedula_cliente'):
        sheet.append(['Pago promedio', float(estadisticas['pago_promedio'])])
    sheet.append(['Pagos anulados', estadisticas['pagos_anulados']])
    sheet.append([])

    if not filtros.get('cedula_cliente'):
        tipo_sheet = workbook.create_sheet('Pagos por tipo')
        tipo_sheet.append(['Tipo', 'Pagos', 'Ingresos'])
        for item in estadisticas['pagos_por_tipo']:
            tipo_sheet.append([item['nombre_tipo_pago'], item['total_pagos'], float(item['ingresos'])])

        moneda_sheet = workbook.create_sheet('Pagos por moneda')
        moneda_sheet.append(['Moneda', 'Pagos', 'Ingresos'])
        for item in estadisticas['pagos_por_moneda']:
            moneda_sheet.append([item['nombre_moneda'], item['total_pagos'], float(item['ingresos'])])

    if filtros.get('cedula_cliente'):
        detalle_sheet = workbook.create_sheet('Detalle de pagos')
        detalle_sheet.append(['Servicio', 'Fecha', 'Monto', 'Estado'])
        for item in estadisticas['ultimos_pagos']:
            detalle_sheet.append([
                f"{item['cod_servicio']} - {item['servicio'] or 'Servicio'}",
                item['fecha_pago'],
                float(item['monto'] or 0),
                'Activo' if item['status'] == 1 else 'Anulado'
            ])

    top_sheet = None
    if not filtros.get('cedula_cliente'):
        top_sheet = workbook.create_sheet('Top clientes')
        top_sheet.append(['Cliente', 'Pagos', 'Ingresos'])
        for item in estadisticas['top_clientes']:
            top_sheet.append([item['nombre_cliente'], item['total_pagos'], float(item['ingresos'])])

    personal_sheet = None
    if filtros.get('detalle_especialista'):
        personal_sheet = workbook.create_sheet('Pagos al especialista')
        personal_sheet.append(['Fecha', 'Referencia', 'Banco', 'Monto pagado', 'Comprobante', 'Estado'])
        for item in estadisticas['pagos_personal']:
            personal_sheet.append([
                item['fecha_pago'],
                item['referencia_pago'] or 'Sin referencia',
                item['nombre_banco'],
                float(item['monto_pagado'] or 0),
                'Disponible' if item['comprobante'] else 'Sin comprobante',
                'Activo' if item['status'] == 1 else 'Anulado'
            ])

    sheets_to_style = [sheet]
    if not filtros.get('cedula_cliente'):
        sheets_to_style.extend([tipo_sheet, moneda_sheet, top_sheet])
    if filtros.get('cedula_cliente'):
        sheets_to_style.append(detalle_sheet)
    if personal_sheet:
        sheets_to_style.append(personal_sheet)
    for sheet_to_style in sheets_to_style:
        if sheet_to_style.title == 'Estadísticas':
            header_row = 15
        else:
            header_row = 1

        for col in range(1, 4):
            cell = sheet_to_style.cell(row=header_row, column=col)
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill('solid', fgColor='1B365D')
            cell.alignment = Alignment(horizontal='center')

        sheet_to_style.column_dimensions['A'].width = 24
        sheet_to_style.column_dimensions['B'].width = 14
        sheet_to_style.column_dimensions['C'].width = 16
        if sheet_to_style.title == 'Pagos al especialista':
            sheet_to_style.column_dimensions['C'].width = 20
            sheet_to_style.column_dimensions['D'].width = 16
            sheet_to_style.column_dimensions['E'].width = 20
            sheet_to_style.column_dimensions['F'].width = 14

    archivo = os.path.join(tempfile.gettempdir(), f'reporte_pagos_estadistico_{int(datetime.now().timestamp())}.xlsx')
    workbook.save(archivo)
    return archivo


def _listar_especialistas(modelo):
    cursor = modelo.conexion.cursor(dictionary=True)
    cursor.execute('''
        SELECT
            e.cedula_especialista,
            CONCAT(COALESCE(u.nombre_usuario, ''), ' ', COALESCE(u.apellido_usuario, '')) AS nombre_especialista
        FROM sac.especialista e
        INNER JOIN seguridad.usuario u ON u.cedula = e.cedula_especialista
        WHERE e.status = 1
        ORDER BY u.nombre_usuario, u.apellido_usuario
    ''')
    especialistas = cursor.fetchall()
    cursor.close()
    return especialistas


def _listar_clientes(modelo):
    cursor = modelo.conexion.cursor(dictionary=True)
    cursor.execute('''
        SELECT DISTINCT
            s.cedula,
            COALESCE(
                NULLIF(TRIM(CONCAT(COALESCE(u.nombre_usuario, ''), ' ', COALESCE(u.apellido_usuario, ''))), ''),
                CONCAT('Cliente ', s.cedula)
            ) AS nombre_cliente
        FROM pago p
        INNER JOIN servicio s ON s.cod_servicio = p.cod_servicio
        LEFT JOIN seguridad.usuario u ON u.cedula = s.cedula
        ORDER BY u.nombre_usuario, u.apellido_usuario
    ''')
    clientes = cursor.fetchall()
    cursor.close()
    return clientes


def _generar_pdf_especialista(empresa, pagos, desde, hasta):
    archivo = os.path.join(tempfile.gettempdir(), f'reporte_especialista_{int(datetime.now().timestamp())}.pdf')
    doc = SimpleDocTemplate(archivo, pagesize=LETTER, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=25 * mm, bottomMargin=25 * mm)
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle('titulo_especialista', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=17, textColor=colors.HexColor('#B8860B'), alignment=TA_CENTER)
    normal = ParagraphStyle('normal_especialista', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12)
    elementos = []
    logo_path = _empresa_logo_path(empresa)
    logo = Image(logo_path, width=42 * mm, height=42 * mm) if os.path.exists(logo_path) else ''
    empresa_html = f"<font size='16' color='#1B365D'><b>{_empresa_dato(empresa, 'nombre')}</b></font><br/><br/><b>Dirección:</b> {_empresa_dato(empresa, 'direccion')}<br/><b>Teléfono:</b> {_empresa_dato(empresa, 'telefono')}<br/><b>Correo:</b> {_empresa_dato(empresa, 'email')}"
    encabezado = Table([[logo, Paragraph(empresa_html, normal)]], colWidths=[48 * mm, 120 * mm])
    encabezado.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    elementos.extend([encabezado, Spacer(1, 8), Paragraph('REPORTE DETALLADO DE PAGOS AL ESPECIALISTA', titulo), Paragraph(f'Período: {desde or "Todos"} al {hasta or "Todos"}', normal), Spacer(1, 12)])
    nombre = pagos[0]['nombre_especialista'] if pagos else 'Sin pagos registrados'
    total = sum(float(item['monto_pagado'] or 0) for item in pagos)
    elementos.append(Paragraph(f'<b>Especialista:</b> {nombre}<br/><b>Total pagado:</b> {total:.2f}<br/><b>Cantidad de pagos:</b> {len(pagos)}', normal))
    elementos.append(Spacer(1, 10))
    datos = [['Fecha', 'Referencia', 'Banco', 'Monto', 'Comprobante', 'Estado']]
    for item in pagos:
        comprobante = 'Sin comprobante'
        if item['comprobante']:
            ruta = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static', item['comprobante']))
            comprobante = Image(ruta, width=25 * mm, height=18 * mm, kind='proportional') if os.path.exists(ruta) else os.path.basename(item['comprobante'])
        datos.append([str(item['fecha_pago']), str(item['referencia_pago'] or 'Sin referencia'), item['nombre_banco'], f"{float(item['monto_pagado'] or 0):.2f}", comprobante, 'Activo' if item['status'] == 1 else 'Anulado'])
    if len(datos) == 1:
        datos.append(['Sin datos', '', '', '', '', ''])
    tabla = Table(datos, colWidths=[25 * mm, 35 * mm, 32 * mm, 22 * mm, 35 * mm, 22 * mm], repeatRows=1)
    tabla.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('GRID', (0, 0), (-1, -1), 0.25, colors.grey), ('FONTSIZE', (0, 0), (-1, -1), 7), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    elementos.append(tabla)
    doc.build(elementos, onFirstPage=lambda canvas, document: (borde(canvas, document), footer(canvas, document)), onLaterPages=lambda canvas, document: (borde(canvas, document), footer(canvas, document)))
    return archivo


def _generar_pdf_especialista(empresa, pagos, desde, hasta):
    archivo = os.path.join(tempfile.gettempdir(), f'reporte_especialista_{int(datetime.now().timestamp())}.pdf')
    doc = SimpleDocTemplate(archivo, pagesize=LETTER, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=25 * mm, bottomMargin=25 * mm)
    styles = getSampleStyleSheet()
    titulo = ParagraphStyle('titulo_especialista', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=17, textColor=colors.HexColor('#B8860B'), alignment=TA_CENTER)
    normal = ParagraphStyle('normal_especialista', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12)
    elementos = []
    logo_path = _empresa_logo_path(empresa)
    logo = Image(logo_path, width=42 * mm, height=42 * mm) if os.path.exists(logo_path) else ''
    empresa_html = f"<font size='16' color='#1B365D'><b>{_empresa_dato(empresa, 'nombre')}</b></font><br/><br/><b>Dirección:</b> {_empresa_dato(empresa, 'direccion')}<br/><b>Teléfono:</b> {_empresa_dato(empresa, 'telefono')}<br/><b>Correo:</b> {_empresa_dato(empresa, 'email')}"
    encabezado = Table([[logo, Paragraph(empresa_html, normal)]], colWidths=[48 * mm, 120 * mm])
    encabezado.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    elementos.extend([encabezado, Spacer(1, 8), Paragraph('REPORTE DETALLADO DE PAGOS AL ESPECIALISTA', titulo), Paragraph(f'Período: {desde or "Todos"} al {hasta or "Todos"}', normal), Spacer(1, 12)])
    nombre = pagos[0]['nombre_especialista'] if pagos else 'Sin pagos registrados'
    total = sum(float(item['monto_pagado'] or 0) for item in pagos)
    elementos.append(Paragraph(f'<b>Especialista:</b> {nombre}<br/><b>Total pagado:</b> {total:.2f}<br/><b>Cantidad de pagos:</b> {len(pagos)}', normal))
    elementos.append(Spacer(1, 10))
    datos = [['Fecha', 'Referencia', 'Banco', 'Monto', 'Comprobante', 'Estado']]
    for item in pagos:
        comprobante = 'Sin comprobante'
        if item['comprobante']:
            ruta = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static', item['comprobante']))
            comprobante = Image(ruta, width=25 * mm, height=18 * mm, kind='proportional') if os.path.exists(ruta) else os.path.basename(item['comprobante'])
        datos.append([str(item['fecha_pago']), str(item['referencia_pago'] or 'Sin referencia'), item['nombre_banco'], f"{float(item['monto_pagado'] or 0):.2f}", comprobante, 'Activo' if item['status'] == 1 else 'Anulado'])
    if len(datos) == 1:
        datos.append(['Sin datos', '', '', '', '', ''])
    tabla = Table(datos, colWidths=[25 * mm, 35 * mm, 32 * mm, 22 * mm, 35 * mm, 22 * mm], repeatRows=1)
    tabla.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('GRID', (0, 0), (-1, -1), 0.25, colors.grey), ('FONTSIZE', (0, 0), (-1, -1), 7), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    elementos.append(tabla)
    doc.build(elementos, onFirstPage=lambda canvas, document: (borde(canvas, document), footer(canvas, document)), onLaterPages=lambda canvas, document: (borde(canvas, document), footer(canvas, document)))
    return archivo


def handle_request(ruta):
    modelo = PagosModelo()

    desde = request.form.get('desde') or request.args.get('desde')
    hasta = request.form.get('hasta') or request.args.get('hasta')
    try:
        cod_tipo_pago = int(request.form.get('cod_tipo_pago') or request.args.get('cod_tipo_pago') or 0)
    except (TypeError, ValueError):
        cod_tipo_pago = 0
    status = request.form.get('status') or request.args.get('status') or 'all'
    try:
        cedula_especialista = int(
            request.form.get('cedula_especialista')
            or request.args.get('cedula_especialista')
            or 0
        )
    except (TypeError, ValueError):
        cedula_especialista = 0
    cedula_cliente = (request.form.get('cedula_cliente') or request.args.get('cedula_cliente') or '').strip()

    if request.method == 'POST' and request.form.get('pdf_especialista') and cedula_especialista > 0:
        pagos = _consultar_pagos_personal(modelo, desde, hasta, status, cedula_especialista)
        empresa = EmpresaModelo().mostrar()
        empresa_data = empresa[0] if empresa else {}
        archivo = _generar_pdf_especialista(empresa_data, pagos, desde, hasta)
        return send_file(archivo, mimetype='application/pdf', as_attachment=False)

    filtros = {
        'desde': desde or '',
        'hasta': hasta or '',
        'cod_tipo_pago': cod_tipo_pago,
        'status': status,
        'cedula_especialista': cedula_especialista,
        'cedula_cliente': cedula_cliente,
    }

    estadisticas = _consultar_estadisticas(
        modelo,
        desde=desde,
        hasta=hasta,
        cod_tipo_pago=cod_tipo_pago,
        status=status,
        cedula_especialista=cedula_especialista,
        cedula_cliente=cedula_cliente,
    )
    tipopagos = modelo.listar_tipos_pago()
    especialistas = _listar_especialistas(modelo)
    clientes = _listar_clientes(modelo)
    filtros['nombre_especialista'] = next(
        (item['nombre_especialista'] for item in especialistas
         if int(item['cedula_especialista']) == cedula_especialista),
        ''
    )
    filtros['nombre_cliente'] = next(
        (item['nombre_cliente'] for item in clientes
         if str(item['cedula']) == cedula_cliente),
        ''
    )

    if request.method == 'POST' and request.form.get('pdf'):
        empresa = EmpresaModelo().mostrar()
        empresa_data = empresa[0] if empresa else {}
        archivo = _generar_pdf(empresa_data, estadisticas, filtros)
        return send_file(archivo, mimetype='application/pdf', as_attachment=False)

    if request.method == 'POST' and request.form.get('excel'):
        empresa = EmpresaModelo().mostrar()
        empresa_data = empresa[0] if empresa else {}
        archivo = _generar_excel(empresa_data, estadisticas, filtros)
        return send_file(archivo, as_attachment=True, download_name='reporte_pagos_estadistico.xlsx')

    return {
        'estadisticas': estadisticas,
        'tipopagos': tipopagos,
        'especialistas': especialistas,
        'clientes': clientes,
        'filtros': filtros,
    }
