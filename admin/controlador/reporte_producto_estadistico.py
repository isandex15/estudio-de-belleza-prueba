from flask import request, send_file
from admin.modelo.producto import ProductoModelo
from admin.modelo.empresa import EmpresaModelo
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
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


def _build_filters(cod_producto, cod_categoria, cod_marca, status, stock_min=None, stock_max=None, precio_min=None, precio_max=None):
    condiciones = []
    parametros = []

    if cod_producto and cod_producto > 0:
        condiciones.append('p.cod_producto = %s')
        parametros.append(cod_producto)

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

    if stock_min is not None:
        condiciones.append('p.stock >= %s')
        parametros.append(stock_min)

    if stock_max is not None:
        condiciones.append('p.stock <= %s')
        parametros.append(stock_max)

    if precio_min is not None:
        condiciones.append('p.precio_producto >= %s')
        parametros.append(precio_min)

    if precio_max is not None:
        condiciones.append('p.precio_producto <= %s')
        parametros.append(precio_max)

    where = ' AND '.join(condiciones) if condiciones else '1=1'
    return where, parametros


def _fetch_scalar(modelo, sql, parametros):
    cursor = modelo.conn().cursor(dictionary=True)
    cursor.execute(sql, tuple(parametros))
    fila = cursor.fetchone()
    cursor.close()
    return fila


def _fetch_rows(modelo, sql, parametros):
    cursor = modelo.conn().cursor(dictionary=True)
    cursor.execute(sql, tuple(parametros))
    filas = cursor.fetchall()
    cursor.close()
    return filas


def _consultar_estadisticas(modelo, cod_producto=0, cod_categoria=0, cod_marca=0, status='all', stock_min=None, stock_max=None, precio_min=None, precio_max=None):
    where, parametros = _build_filters(cod_producto, cod_categoria, cod_marca, status, stock_min, stock_max, precio_min, precio_max)

    resumen = _fetch_scalar(modelo, f'''
        SELECT
            COUNT(*) AS total_productos,
            COALESCE(SUM(stock), 0) AS stock_total,
            COALESCE(SUM(precio_producto * stock), 0) AS valor_total,
            SUM(stock <= 5) AS stock_bajo
        FROM producto p
        WHERE {where}
    ''', parametros) or {}

    por_categoria = _fetch_rows(modelo, f'''
        SELECT
            c.cod_categoria,
            c.nombre_categoria,
            COUNT(*) AS total_productos,
            COALESCE(SUM(p.stock), 0) AS stock_total
        FROM producto p
        INNER JOIN categoria c ON p.cod_categoria = c.cod_categoria
        WHERE {where}
        GROUP BY c.cod_categoria, c.nombre_categoria
        ORDER BY stock_total DESC
    ''', parametros)

    por_marca = _fetch_rows(modelo, f'''
        SELECT
            m.cod_marca,
            m.nombre_marca,
            COUNT(*) AS total_productos,
            COALESCE(SUM(p.stock), 0) AS stock_total
        FROM producto p
        INNER JOIN marca m ON p.cod_marca = m.cod_marca
        WHERE {where}
        GROUP BY m.cod_marca, m.nombre_marca
        ORDER BY stock_total DESC
    ''', parametros)

    stock_bajo = _fetch_rows(modelo, f'''
        SELECT
            p.cod_producto,
            p.nombre_producto,
            p.stock,
            p.precio_producto
        FROM producto p
        WHERE {where} AND p.stock <= 5
        ORDER BY p.stock ASC, p.cod_producto DESC
        LIMIT 10
    ''', parametros)

    ultimos_productos = _fetch_rows(modelo, f'''
        SELECT
            p.cod_producto,
            p.nombre_producto,
            p.stock,
            p.precio_producto,
            p.status,
            c.nombre_categoria,
            m.nombre_marca
        FROM producto p
        INNER JOIN categoria c ON p.cod_categoria = c.cod_categoria
        INNER JOIN marca m ON p.cod_marca = m.cod_marca
        WHERE {where}
        ORDER BY p.cod_producto DESC
        LIMIT 10
    ''', parametros)

    return {
        'total_productos': int(resumen.get('total_productos') or 0),
        'stock_total': float(resumen.get('stock_total') or 0.0),
        'valor_total': float(resumen.get('valor_total') or 0.0),
        'stock_bajo': int(resumen.get('stock_bajo') or 0),
        'por_categoria': por_categoria,
        'por_marca': por_marca,
        'stock_bajo_items': stock_bajo,
        'ultimos_productos': ultimos_productos,
    }


def _listar_catalogos(modelo):
    cursor = modelo.conn().cursor(dictionary=True)
    cursor.execute('SELECT cod_producto, nombre_producto FROM producto ORDER BY nombre_producto')
    productos = cursor.fetchall()
    cursor.execute('SELECT cod_categoria, nombre_categoria FROM categoria ORDER BY nombre_categoria')
    categorias = cursor.fetchall()
    cursor.execute('SELECT cod_marca, nombre_marca FROM marca ORDER BY nombre_marca')
    marcas = cursor.fetchall()
    cursor.close()
    return productos, categorias, marcas


def _etiqueta_filtro(valor, catalogo=None, llave_id=None, llave_nombre=None, mapa=None):
    if valor in (None, '', 'all', 'ALL', 0, '0'):
        return 'Ninguno seleccionado'

    if catalogo and llave_id and llave_nombre:
        for item in catalogo:
            if str(item.get(llave_id)) == str(valor):
                return item.get(llave_nombre) or 'Ninguno seleccionado'

    if mapa:
        return mapa.get(str(valor), 'Ninguno seleccionado')

    return str(valor)


def _filtros_en_espanol(filtros, productos=None, categorias=None, marcas=None):
    stock_min = filtros.get('stock_min')
    stock_max = filtros.get('stock_max')
    precio_min = filtros.get('precio_min')
    precio_max = filtros.get('precio_max')
    return [
        ['Producto', _etiqueta_filtro(filtros.get('cod_producto'), productos, 'cod_producto', 'nombre_producto')],
        ['Categoría', _etiqueta_filtro(filtros.get('cod_categoria'), categorias, 'cod_categoria', 'nombre_categoria')],
        ['Marca', _etiqueta_filtro(filtros.get('cod_marca'), marcas, 'cod_marca', 'nombre_marca')],
        ['Estado', _etiqueta_filtro(filtros.get('status'), mapa={'active': 'Activo', 'inactive': 'Inactivo'})],
        ['Stock mínimo', stock_min if stock_min is not None else 'Sin mínimo'],
        ['Stock máximo', stock_max if stock_max is not None else 'Sin máximo'],
        ['Precio mínimo', f'{precio_min:.2f}' if precio_min is not None else 'Sin mínimo'],
        ['Precio máximo', f'{precio_max:.2f}' if precio_max is not None else 'Sin máximo'],
    ]


def _generar_pdf(empresa, estadisticas, filtros, productos=None, categorias=None, marcas=None):
    archivo = os.path.join(tempfile.gettempdir(), f'reporte_productos_estadistico_{int(datetime.now().timestamp())}.pdf')
    doc = SimpleDocTemplate(
        archivo,
        pagesize=LETTER,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=22 * mm
    )
    doc.title = f"Productos estadísticos - {empresa.get('nombre', 'Sistema')}"
    doc.author = empresa.get('nombre', 'Sistema')
    doc.subject = 'Reporte estadístico de productos'

    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle(
        'titulo_estadistico',
        parent=estilos['Heading1'],
        fontSize=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#B8860B'),
        spaceAfter=8
    )
    subtitulo = ParagraphStyle(
        'subtitulo_estadistico',
        parent=estilos['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    normal = ParagraphStyle(
        'normal_estadistico',
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

    elementos.append(Paragraph('REPORTE ESTADÍSTICO DE PRODUCTOS', titulo))
    elementos.append(Paragraph('Resumen estadístico del sistema', subtitulo))
    elementos.append(Spacer(1, 10))

    resumen_data = [[
        'Fecha',
        datetime.now().strftime('%d/%m/%Y'),
        'Productos',
        str(estadisticas['total_productos'])
    ]]
    resumen_table = Table(resumen_data)
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F5')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    elementos.append(resumen_table)
    elementos.append(Spacer(1, 12))

    filtros_data = _filtros_en_espanol(filtros, productos, categorias, marcas)
    filtros_table = Table(filtros_data, hAlign='LEFT', colWidths=[40 * mm, 120 * mm])
    filtros_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9F9F9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elementos.extend([filtros_table, Spacer(1, 12)])

    metrics_data = [
        ['Métrica', 'Valor'],
        ['Total de productos', str(estadisticas['total_productos'])],
        ['Stock total', f"{estadisticas['stock_total']:.2f}"],
        ['Valor total', f"{estadisticas['valor_total']:.2f}"],
        ['Productos con stock bajo', str(estadisticas['stock_bajo'])],
    ]
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

    if estadisticas['por_categoria']:
        elementos.append(Paragraph('Por categoría', estilos['Heading3']))
        categoria_data = [['Categoría', 'Productos', 'Stock']]
        for item in estadisticas['por_categoria']:
            categoria_data.append([item['nombre_categoria'], item['total_productos'], f"{item['stock_total']:.2f}"])
        categoria_table = Table(categoria_data, hAlign='LEFT', colWidths=[75 * mm, 35 * mm, 45 * mm], repeatRows=1)
        categoria_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        elementos.extend([categoria_table, Spacer(1, 12)])

    if estadisticas['por_marca']:
        elementos.append(Paragraph('Por marca', estilos['Heading3']))
        marca_data = [['Marca', 'Productos', 'Stock']]
        for item in estadisticas['por_marca']:
            marca_data.append([item['nombre_marca'], item['total_productos'], f"{item['stock_total']:.2f}"])
        marca_table = Table(marca_data, hAlign='LEFT', colWidths=[75 * mm, 35 * mm, 45 * mm], repeatRows=1)
        marca_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        elementos.extend([marca_table, Spacer(1, 12)])

    doc.build(
        elementos,
        onFirstPage=lambda c, d: (borde(c, d), footer(c, d)),
        onLaterPages=lambda c, d: (borde(c, d), footer(c, d))
    )
    return archivo


def _generar_excel(empresa, estadisticas, filtros, productos=None, categorias=None, marcas=None):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Estadísticas'

    sheet.merge_cells('A1:B1')
    sheet['A1'] = empresa.get('nombre', 'Estudio MT')
    sheet['A1'].font = Font(bold=True, size=14)
    sheet['A1'].alignment = Alignment(horizontal='center')

    sheet['A2'] = empresa.get('direccion', '')
    sheet['A3'] = empresa.get('telefono', '')
    sheet['A4'] = empresa.get('email', '')
    sheet['A5'] = datetime.now().strftime('%d-%m-%Y')

    sheet.append([])
    sheet.append(['Reporte Estadístico de Productos'])
    sheet.append(['Emitido', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    sheet.append([])
    for etiqueta, valor in _filtros_en_espanol(filtros, productos, categorias, marcas):
        sheet.append([etiqueta, valor])
    metric_header_row = sheet.max_row + 2
    sheet.append([])
    sheet.append(['Métrica', 'Valor'])
    sheet.append(['Total de productos', estadisticas['total_productos']])
    sheet.append(['Stock total', float(estadisticas['stock_total'])])
    sheet.append(['Valor total', float(estadisticas['valor_total'])])
    sheet.append(['Productos con stock bajo', estadisticas['stock_bajo']])
    sheet.append([])

    categoria_sheet = workbook.create_sheet('Por categoría')
    categoria_sheet.append(['Categoría', 'Productos', 'Stock'])
    for item in estadisticas['por_categoria']:
        categoria_sheet.append([item['nombre_categoria'], item['total_productos'], float(item['stock_total'])])

    marca_sheet = workbook.create_sheet('Por marca')
    marca_sheet.append(['Marca', 'Productos', 'Stock'])
    for item in estadisticas['por_marca']:
        marca_sheet.append([item['nombre_marca'], item['total_productos'], float(item['stock_total'])])

    stock_sheet = workbook.create_sheet('Stock bajo')
    stock_sheet.append(['Código', 'Producto', 'Stock', 'Precio'])
    for item in estadisticas['stock_bajo_items']:
        stock_sheet.append([item['cod_producto'], item['nombre_producto'], item['stock'], float(item.get('precio_producto') or 0)])

    for sheet_to_style in [sheet, categoria_sheet, marca_sheet, stock_sheet]:
        if sheet_to_style.title == 'Estadísticas':
            header_row = metric_header_row
        else:
            header_row = 1

        for col in range(1, 4):
            cell = sheet_to_style.cell(row=header_row, column=col)
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = PatternFill('solid', fgColor='1B365D')
            cell.alignment = Alignment(horizontal='center')

        sheet_to_style.column_dimensions['A'].width = 24
        sheet_to_style.column_dimensions['B'].width = 18
        sheet_to_style.column_dimensions['C'].width = 14
        sheet_to_style.column_dimensions['D'].width = 16

    archivo = os.path.join(tempfile.gettempdir(), f'reporte_productos_estadistico_{int(datetime.now().timestamp())}.xlsx')
    workbook.save(archivo)
    return archivo


def handle_request(ruta):
    modelo = ProductoModelo()

    def obtener_entero(nombre):
        try:
            return int(request.values.get(nombre, 0) or 0)
        except (TypeError, ValueError):
            return 0

    def obtener_decimal(nombre):
        try:
            valor = request.values.get(nombre, '')
            return float(valor) if valor not in (None, '') else None
        except (TypeError, ValueError):
            return None

    cod_producto = obtener_entero('cod_producto')
    cod_categoria = obtener_entero('cod_categoria')
    cod_marca = obtener_entero('cod_marca')
    status = request.values.get('status', 'all') or 'all'
    stock_min = obtener_entero('stock_min') if request.values.get('stock_min', '') != '' else None
    stock_max = obtener_entero('stock_max') if request.values.get('stock_max', '') != '' else None
    precio_min = obtener_decimal('precio_min')
    precio_max = obtener_decimal('precio_max')

    if stock_min is not None and stock_max is not None and stock_min > stock_max:
        stock_min, stock_max = stock_max, stock_min

    if precio_min is not None and precio_max is not None and precio_min > precio_max:
        precio_min, precio_max = precio_max, precio_min

    filtros = {
        'cod_producto': cod_producto,
        'cod_categoria': cod_categoria,
        'cod_marca': cod_marca,
        'status': status,
        'stock_min': stock_min,
        'stock_max': stock_max,
        'precio_min': precio_min,
        'precio_max': precio_max,
    }

    estadisticas = _consultar_estadisticas(
        modelo,
        cod_producto=cod_producto,
        cod_categoria=cod_categoria,
        cod_marca=cod_marca,
        status=status,
        stock_min=stock_min,
        stock_max=stock_max,
        precio_min=precio_min,
        precio_max=precio_max,
    )
    productos, categorias, marcas = _listar_catalogos(modelo)

    if request.method == 'POST' and request.form.get('pdf'):
        empresa = EmpresaModelo().mostrar()
        empresa_data = empresa[0] if empresa else {}
        archivo = _generar_pdf(empresa_data, estadisticas, filtros, productos, categorias, marcas)
        return send_file(archivo, mimetype='application/pdf', as_attachment=False)

    if request.method == 'POST' and request.form.get('excel'):
        empresa = EmpresaModelo().mostrar()
        empresa_data = empresa[0] if empresa else {}
        archivo = _generar_excel(empresa_data, estadisticas, filtros, productos, categorias, marcas)
        return send_file(archivo, as_attachment=True, download_name='reporte_productos_estadistico.xlsx')

    return {
        'estadisticas': estadisticas,
        'productos': productos,
        'categorias': categorias,
        'marcas': marcas,
        'filtros': filtros,
    }
