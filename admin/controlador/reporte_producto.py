from flask import request, send_file
from admin.modelo.producto import ProductoModelo
from admin.modelo.empresa import EmpresaModelo
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Line
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import datetime
import tempfile
import os


def footer(canvas, doc, empresa=None):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#D4AF37'))
    canvas.setLineWidth(0.8)
    canvas.line(15 * mm, 18 * mm, 195 * mm, 18 * mm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawString(18 * mm, 11 * mm, f"Sistema de Gestión • {empresa.get('nombre', 'Empresa') if empresa else 'Empresa'}")
    canvas.drawRightString(195 * mm, 11 * mm, datetime.now().strftime('%d/%m/%Y %H:%M'))
    canvas.drawCentredString(105 * mm, 6 * mm, f'Página {doc.page}')
    canvas.restoreState()


def borde(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#D4AF37'))
    canvas.setLineWidth(1.2)
    canvas.rect(10 * mm, 10 * mm, LETTER[0] - 20 * mm, LETTER[1] - 20 * mm)
    canvas.restoreState()


def _build_filters(cod_categoria, cod_marca, status, vencimiento='all', stock='all'):
    condiciones = []
    parametros = []

    if cod_categoria and cod_categoria > 0:
        condiciones.append('p.cod_categoria = %s')
        parametros.append(cod_categoria)

    if cod_marca and cod_marca > 0:
        condiciones.append('p.cod_marca = %s')
        parametros.append(cod_marca)

    if status == 'active':
        condiciones.append('p.status = 1')
    elif status == 'inactive':
        condiciones.append('p.status = 0')

    if vencimiento == 'expired':
        condiciones.append('dp.fecha_vencimiento < CURDATE()')
    elif vencimiento == 'next_30':
        condiciones.append('dp.fecha_vencimiento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)')
    elif vencimiento == 'after_30':
        condiciones.append('dp.fecha_vencimiento > DATE_ADD(CURDATE(), INTERVAL 30 DAY)')
    elif vencimiento == 'without_date':
        condiciones.append('dp.fecha_vencimiento IS NULL')

    if stock == 'empty':
        condiciones.append('p.stock = 0')
    elif stock == 'low':
        condiciones.append('p.stock BETWEEN 1 AND 5')
    elif stock == 'available':
        condiciones.append('p.stock > 5')

    where = ' AND '.join(condiciones) if condiciones else '1=1'
    return where, parametros


def _fetch_rows(modelo, sql, parametros):
    cursor = modelo.conn().cursor(dictionary=True)
    cursor.execute(sql, tuple(parametros))
    filas = cursor.fetchall()
    cursor.close()
    return filas


def _consultar_productos(modelo, cod_categoria=0, cod_marca=0, status='all', vencimiento='all', stock='all'):
    where, parametros = _build_filters(cod_categoria, cod_marca, status, vencimiento, stock)
    sql = f'''
        SELECT
            p.cod_producto,
            p.nombre_producto,
            p.precio_producto,
            p.stock,
            p.status,
            c.nombre_categoria,
            m.nombre_marca,
            u.nombre_unidad,
            COALESCE(pr.presentacion, 'N/A') AS nombre_presentacion,
            COALESCE(me.medida, 'N/A') AS nombre_medida,
            COALESCE(dp.nombre_tipo_producto, 'Sin tipo') AS nombre_tipo_producto,
            dp.fecha_vencimiento,
            DATEDIFF(dp.fecha_vencimiento, CURDATE()) AS dias_para_vencer,
            (p.precio_producto * p.stock) AS valor_inventario,
            CASE
                WHEN p.stock = 0 THEN 'Agotado'
                WHEN p.stock <= 5 THEN 'Stock bajo'
                ELSE 'Disponible'
            END AS nivel_stock
        FROM producto p
        INNER JOIN categoria c ON p.cod_categoria = c.cod_categoria
        INNER JOIN marca m ON p.cod_marca = m.cod_marca
        INNER JOIN unidad u ON p.cod_unidad = u.cod_unidad
        LEFT JOIN presentacion pr ON u.cod_presentacion = pr.cod_presentacion
        LEFT JOIN medida me ON u.cod_medida = me.cod_medida
        LEFT JOIN (
            SELECT
                dp.cod_producto,
                MIN(dp.fecha_vencimiento) AS fecha_vencimiento,
                GROUP_CONCAT(DISTINCT tp.nombre_tipo_producto ORDER BY tp.nombre_tipo_producto SEPARATOR ', ') AS nombre_tipo_producto
            FROM detalle_producto dp
            LEFT JOIN tipo_producto tp ON dp.cod_tipo_producto = tp.cod_tipo_producto
            GROUP BY dp.cod_producto
        ) dp ON p.cod_producto = dp.cod_producto
        WHERE {where}
        ORDER BY p.cod_producto DESC
    '''
    return _fetch_rows(modelo, sql, parametros)


def _consultar_resumen(modelo, cod_categoria=0, cod_marca=0, status='all', vencimiento='all', stock='all'):
    where, parametros = _build_filters(cod_categoria, cod_marca, status, vencimiento, stock)
    resumen = _fetch_rows(modelo, f'''
        SELECT
            COUNT(*) AS total_productos,
            COALESCE(SUM(p.stock), 0) AS stock_total,
            COALESCE(SUM(p.precio_producto * p.stock), 0) AS valor_inventario,
            COALESCE(AVG(p.precio_producto), 0) AS precio_promedio,
            SUM(p.stock = 0) AS agotados,
            SUM(p.stock BETWEEN 1 AND 5) AS stock_bajo,
            SUM(p.status = 1) AS activos,
            SUM(dp.fecha_vencimiento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)) AS vencen_30_dias
        FROM producto p
        LEFT JOIN (
            SELECT cod_producto, MIN(fecha_vencimiento) AS fecha_vencimiento
            FROM detalle_producto
            GROUP BY cod_producto
        ) dp ON p.cod_producto = dp.cod_producto
        WHERE {where}
    ''', parametros)
    return resumen[0] if resumen else {}


def _listar_catalogos(modelo):
    cursor = modelo.conn().cursor(dictionary=True)
    cursor.execute('SELECT cod_categoria, nombre_categoria FROM categoria ORDER BY nombre_categoria')
    categorias = cursor.fetchall()
    cursor.execute('SELECT cod_marca, nombre_marca FROM marca ORDER BY nombre_marca')
    marcas = cursor.fetchall()
    cursor.close()
    return categorias, marcas


def _etiqueta_filtro(valor, catalogo=None, llave_id='cod_categoria', llave_nombre='nombre_categoria', mapa=None):
    if valor in (None, '', 'all', 'ALL', 0, '0'):
        return 'Ninguno seleccionado'

    if catalogo:
        for item in catalogo:
            if str(item.get(llave_id)) == str(valor):
                return item.get(llave_nombre) or 'Ninguno seleccionado'

    if mapa:
        return mapa.get(str(valor), 'Ninguno seleccionado')

    return str(valor)


def _filtros_en_espanol(filtros, categorias=None, marcas=None):
    return [
        ['Categoría', _etiqueta_filtro(filtros.get('cod_categoria'), categorias, 'cod_categoria', 'nombre_categoria')],
        ['Marca', _etiqueta_filtro(filtros.get('cod_marca'), marcas, 'cod_marca', 'nombre_marca')],
        ['Estado', _etiqueta_filtro(filtros.get('status'), mapa={'active': 'Activo', 'inactive': 'Inactivo'})],
        ['Vencimiento', _etiqueta_filtro(filtros.get('vencimiento'), mapa={
            'expired': 'Vencidos',
            'next_30': 'Próximos 30 días',
            'after_30': 'Después de 30 días',
            'without_date': 'Sin fecha'
        })],
        ['Cantidad de stock', _etiqueta_filtro(filtros.get('stock'), mapa={
            'empty': 'Sin stock',
            'low': 'Stock bajo',
            'available': 'Disponible'
        })],
    ]


def _generar_pdf(empresa, listado, filtros, resumen, categorias=None, marcas=None):
    archivo = os.path.join(tempfile.gettempdir(), f'reporte_productos_{int(datetime.now().timestamp())}.pdf')
    doc = SimpleDocTemplate(
        archivo,
        pagesize=LETTER,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=22 * mm
    )
    doc.title = f"Productos - {empresa.get('nombre', 'Sistema')}"
    doc.author = empresa.get('nombre', 'Sistema')
    doc.subject = 'Reporte de productos'

    estilos = getSampleStyleSheet()

    titulo = ParagraphStyle(
        'titulo',
        parent=estilos['Heading1'],
        fontSize=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#B8860B'),
        spaceAfter=8
    )

    subtitulo = ParagraphStyle(
        'subtitulo',
        parent=estilos['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )

    normal = ParagraphStyle(
        'normal',
        parent=estilos['Normal'],
        fontSize=9
    )

    elementos = []
    logo = ''
    nombre_empresa = empresa.get('nombre') or 'Estudio MT - Salón & Estética'
    direccion_empresa = empresa.get('direccion') or 'Dirección no registrada'
    telefono_empresa = empresa.get('telefono') or 'Teléfono no registrado'
    email_empresa = empresa.get('email') or 'Correo no registrado'

    if empresa.get('logo'):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_bd = empresa.get('logo', '').lstrip('/')
        logo_path = os.path.abspath(os.path.join(base_dir, '..', '..', logo_bd))
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=42 * mm, height=42 * mm)

    header_text = f"""
    <font size="16" color="#1B365D">
        <b>{nombre_empresa}</b>
    </font>
    <br/>
    <font size="9">
        📍 {direccion_empresa}<br/>
        📞 {telefono_empresa}<br/>
        ✉ {email_empresa}
    </font>
    """

    header = Table([[logo, Paragraph(header_text, normal)]], colWidths=[45 * mm, 120 * mm])
    header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))

    elementos.append(header)
    elementos.append(Spacer(1, 8))

    line = Drawing(500, 10)
    line.add(Line(0, 5, 500, 5, strokeColor=colors.HexColor('#D4AF37'), strokeWidth=1.2))
    elementos.append(line)
    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph('REPORTE DE PRODUCTOS', titulo))
    elementos.append(Paragraph('Listado del sistema', subtitulo))
    elementos.append(Spacer(1, 10))

    resumen_data = [[
        'Fecha',
        datetime.now().strftime('%d/%m/%Y'),
        'Total',
        str(len(listado))
    ]]
    resumen_table = Table(resumen_data)
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F5')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    elementos.append(resumen_table)
    elementos.append(Spacer(1, 12))

    if filtros:
        filtros_data = _filtros_en_espanol(filtros, categorias, marcas)
        filtro_table = Table(filtros_data, hAlign='LEFT', colWidths=[40 * mm, 120 * mm])
        filtro_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9F9F9')),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elementos.append(filtro_table)
        elementos.append(Spacer(1, 12))

    data = [[
        'CÓDIGO',
        'PRODUCTO',
        'CATEGORÍA',
        'MARCA',
        'TIPO',
        'STOCK',
        'PRECIO',
        'VALOR',
        'NIVEL',
        'VENCE',
        'ESTADO'
    ]]

    for producto in listado:
        data.append([
            str(producto['cod_producto']),
            Paragraph(producto['nombre_producto'], normal),
            producto['nombre_categoria'] or 'N/A',
            producto['nombre_marca'] or 'N/A',
            producto.get('nombre_tipo_producto') or 'Sin tipo',
            str(producto['stock']),
            f"{float(producto['precio_producto']):.2f}",
            f"{float(producto.get('valor_inventario', 0) or 0):.2f}",
            producto.get('nivel_stock') or 'N/A',
            str(producto.get('fecha_vencimiento') or 'N/A'),
            'Activo' if producto['status'] == 1 else 'Inactivo',
        ])

    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F7F7')]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elementos.append(tabla)

    def first_page(canvas, doc):
        canvas.setTitle(f"Productos - {empresa.get('nombre', 'Sistema')}")
        canvas.setAuthor(empresa.get('nombre', 'Sistema'))
        canvas.setSubject('Reporte de productos')
        borde(canvas, doc)
        footer(canvas, doc, empresa)

    def later_pages(canvas, doc):
        borde(canvas, doc)
        footer(canvas, doc, empresa)

    doc.build(
        elementos,
        onFirstPage=first_page,
        onLaterPages=later_pages
    )
    return archivo


def _generar_excel(empresa, listado, filtros, resumen, categorias=None, marcas=None):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Productos'

    sheet.merge_cells('A1:G1')
    sheet['A1'] = empresa.get('nombre', 'Estudio MT - Salón & Estética')
    sheet['A1'].font = Font(bold=True, size=14)
    sheet['A1'].alignment = Alignment(horizontal='center')

    sheet['A2'] = empresa.get('direccion', 'Dirección no registrada')
    sheet['A3'] = empresa.get('telefono', 'Teléfono no registrado')
    sheet['A4'] = empresa.get('email', 'Correo no registrado')
    sheet['A5'] = datetime.now().strftime('%d-%m-%Y')

    sheet.append([])
    sheet.append(['Reporte de Productos'])
    sheet.append(['Emitido', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    sheet.append([])
    sheet.append(['Categoría', _etiqueta_filtro(filtros.get('cod_categoria'), categorias, 'cod_categoria', 'nombre_categoria')])
    sheet.append(['Marca', _etiqueta_filtro(filtros.get('cod_marca'), marcas, 'cod_marca', 'nombre_marca')])
    sheet.append(['Estado', _etiqueta_filtro(filtros.get('status'), mapa={'active': 'Activo', 'inactive': 'Inactivo'})])
    sheet.append(['Vencimiento', _etiqueta_filtro(filtros.get('vencimiento'), mapa={
        'expired': 'Vencidos',
        'next_30': 'Próximos 30 días',
        'after_30': 'Después de 30 días',
        'without_date': 'Sin fecha'
    })])
    sheet.append(['Cantidad de stock', _etiqueta_filtro(filtros.get('stock'), mapa={
        'empty': 'Sin stock',
        'low': 'Stock bajo',
        'available': 'Disponible'
    })])
    sheet.append([])
    sheet.append(['Indicador', 'Resultado'])
    sheet.append(['Productos filtrados', resumen.get('total_productos', 0)])
    sheet.append(['Unidades en inventario', resumen.get('stock_total', 0)])
    sheet.append(['Valor del inventario', float(resumen.get('valor_inventario', 0) or 0)])
    sheet.append(['Agotados', resumen.get('agotados', 0) or 0])
    sheet.append(['Stock bajo', resumen.get('stock_bajo', 0) or 0])
    sheet.append(['Vencen en 30 días', resumen.get('vencen_30_dias', 0) or 0])
    sheet.append([])
    detail_header_row = sheet.max_row + 1
    sheet.append(['Código', 'Producto', 'Categoría', 'Marca', 'Unidad', 'Presentación', 'Medida', 'Tipo', 'Stock', 'Precio', 'Valor inventario', 'Nivel', 'Vencimiento', 'Días para vencer', 'Estado'])

    for producto in listado:
        sheet.append([
            producto['cod_producto'],
            producto['nombre_producto'],
            producto['nombre_categoria'] or 'N/A',
            producto['nombre_marca'] or 'N/A',
            producto.get('nombre_unidad') or 'N/A',
            producto.get('nombre_presentacion') or 'N/A',
            producto.get('nombre_medida') or 'N/A',
            producto.get('nombre_tipo_producto') or 'Sin tipo',
            producto['stock'],
            float(producto['precio_producto']),
            float(producto.get('valor_inventario', 0) or 0),
            producto.get('nivel_stock') or 'N/A',
            producto.get('fecha_vencimiento') or 'N/A',
            producto.get('dias_para_vencer') if producto.get('dias_para_vencer') is not None else 'N/A',
            'Activo' if producto['status'] == 1 else 'Inactivo',
        ])

    for col in range(1, 16):
        cell = sheet.cell(row=detail_header_row, column=col)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='1B365D')
        cell.alignment = Alignment(horizontal='center')

    sheet.column_dimensions['A'].width = 10
    sheet.column_dimensions['B'].width = 24
    sheet.column_dimensions['C'].width = 18
    sheet.column_dimensions['D'].width = 16
    sheet.column_dimensions['E'].width = 14
    sheet.column_dimensions['F'].width = 16
    sheet.column_dimensions['G'].width = 14
    sheet.column_dimensions['H'].width = 14
    sheet.column_dimensions['I'].width = 10
    sheet.column_dimensions['J'].width = 12
    sheet.column_dimensions['K'].width = 16
    sheet.column_dimensions['L'].width = 16
    sheet.column_dimensions['M'].width = 16
    sheet.column_dimensions['N'].width = 16
    sheet.column_dimensions['O'].width = 12

    archivo = os.path.join(tempfile.gettempdir(), f'reporte_productos_{int(datetime.now().timestamp())}.xlsx')
    workbook.save(archivo)
    return archivo


def handle_request(ruta):
    modelo = ProductoModelo()

    cod_categoria_raw = request.values.get('cod_categoria', 0)
    cod_marca_raw = request.values.get('cod_marca', 0)
    status = request.values.get('status', 'all') or 'all'
    vencimiento = request.values.get('vencimiento', 'all') or 'all'
    stock = request.values.get('stock', 'all') or 'all'

    try:
        cod_categoria = int(cod_categoria_raw or 0)
    except (TypeError, ValueError):
        cod_categoria = 0

    try:
        cod_marca = int(cod_marca_raw or 0)
    except (TypeError, ValueError):
        cod_marca = 0

    filtros = {
        'cod_categoria': cod_categoria,
        'cod_marca': cod_marca,
        'status': status,
        'vencimiento': vencimiento,
        'stock': stock,
    }

    registro = _consultar_productos(modelo, cod_categoria=cod_categoria, cod_marca=cod_marca, status=status,
                                    vencimiento=vencimiento, stock=stock)
    resumen = _consultar_resumen(modelo, cod_categoria=cod_categoria, cod_marca=cod_marca, status=status,
                                 vencimiento=vencimiento, stock=stock)
    categorias, marcas = _listar_catalogos(modelo)

    if request.method == 'POST' and request.form.get('pdf'):
        empresa = EmpresaModelo().mostrar()
        empresa_data = empresa[0] if empresa else {}
        archivo = _generar_pdf(empresa_data, registro, filtros, resumen, categorias, marcas)
        return send_file(archivo, mimetype='application/pdf', as_attachment=False)

    if request.method == 'POST' and request.form.get('excel'):
        empresa = EmpresaModelo().mostrar()
        empresa_data = empresa[0] if empresa else {}
        archivo = _generar_excel(empresa_data, registro, filtros, resumen, categorias, marcas)
        return send_file(archivo, as_attachment=True, download_name='reporte_productos.xlsx')

    return {
        'registro': registro,
        'resumen': resumen,
        'categorias': categorias,
        'marcas': marcas,
        'filtros': filtros,
    }
