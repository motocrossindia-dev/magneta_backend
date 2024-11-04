# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4, landscape
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import mm
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
#
#
# def generate_comprehensive_stock_pdf(stock_record):
#     # Register fonts
#     pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
#     pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
#
#     # Page setup
#     page_width, page_height = landscape(A4)
#     filename = f"stock_report_{stock_record.id}_{stock_record.date}.pdf"
#
#     # Margins
#     left_margin = 15 * mm
#     right_margin = 15 * mm
#     top_margin = 2 * mm
#     bottom_margin = 20 * mm
#
#     doc = SimpleDocTemplate(filename, pagesize=landscape(A4),
#                             leftMargin=left_margin, rightMargin=right_margin,
#                             topMargin=top_margin, bottomMargin=bottom_margin)
#     elements = []
#
#     # Styles
#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         'Title',
#         parent=styles['Title'],
#         fontName='VeraBd',
#         fontSize=12,
#         leading=22,
#         alignment=1,
#         spaceAfter=2 * mm,
#     )
#
#     header_style = ParagraphStyle(
#         'Header',
#         fontName='VeraBd',
#         fontSize=6,
#         leading=11,
#         alignment=1,
#     )
#
#     data_style = ParagraphStyle(
#         'Data',
#         fontName='Vera',
#         fontSize=8,
#         leading=11,
#         alignment=1,
#     )
#
#     # Title
#     elements.append(Paragraph(f"Comprehensive Stock Report for {stock_record.date}", title_style))
#
#     # Explicitly check for physical stock
#     records = stock_record.product_stock_records.all().select_related('product')
#     show_physical_stock = False
#     for record in records:
#         if hasattr(record, 'physical_stock') and record.physical_stock is not None:
#             show_physical_stock = True
#             break
#
#     # Create headers
#     headers = [
#         [Paragraph('PRODUCTION DETAILS', header_style)] + [''] * (15 if show_physical_stock else 14),
#         [Paragraph(h, header_style) for h in [
#             'S.NO', 'SKU', 'Vol*nos', 'MRP', 'Lit Factor', 'Op.Stock in Units', 'Op.Stock in Lits',
#             'Production in Units', 'Production in Lits', 'Sales in Units', 'Sales in Lits', 'Cls.Stock in Units',
#             'Cls.Stock in Lits', 'Returns', 'Damage'
#         ]]
#     ]
#
#     # Add Physical Stock header if needed
#     if show_physical_stock:
#         headers[1].append(Paragraph('Physical Stock', header_style))
#
#     # Prepare data rows
#     data = []
#     comments_data = []
#
#     for count, record in enumerate(records, start=1):
#         row = [
#             Paragraph(str(count), data_style),
#             Paragraph(str(record.product.product_name), data_style),
#             Paragraph(str(record.volume_nos), data_style),
#             Paragraph(f"{record.mrp}", data_style),
#             Paragraph(f"{record.lit_factor}", data_style),
#             Paragraph(f"{record.opening_stock_units}", data_style),
#             Paragraph(f"{record.opening_stock_lits}", data_style),
#             Paragraph(f"{record.production_units}", data_style),
#             Paragraph(f"{record.production_lits}", data_style),
#             Paragraph(f"{record.sales_units}", data_style),
#             Paragraph(f"{record.sales_lits}", data_style),
#             Paragraph(f"{record.closing_stock_units}", data_style),
#             Paragraph(f"{record.closing_stock_lits}", data_style),
#             Paragraph(f"{record.return_in_units}", data_style),
#             Paragraph(f"{record.damage_in_units}", data_style),
#         ]
#
#         # Add physical stock value if present
#         if show_physical_stock:
#             physical_stock_value = getattr(record, 'physical_stock', 0)
#             row.append(Paragraph(f"{physical_stock_value}", data_style))
#
#         data.append(row)
#
#         # Add comments if present
#         if hasattr(record, 'comments') and record.comments:
#             comments_data.append([
#                 Paragraph(str(record.product.id), data_style),
#                 Paragraph(str(record.product.product_name), data_style),
#                 Paragraph(str(record.comments), data_style)
#             ])
#
#     # Calculate table dimensions
#     table_width = page_width - left_margin - right_margin
#
#     # Define column widths
#     fixed_width_cols = [12 * mm, 45 * mm, 18 * mm, 18 * mm, 18 * mm]  # S.NO, SKU, Vol*nos, MRP, Lit Factor
#     fixed_width_total = sum(fixed_width_cols)
#     remaining_width = table_width - fixed_width_total
#     num_flexible_cols = 11 if show_physical_stock else 10  # Adjusted for physical stock
#     flexible_col_width = remaining_width / num_flexible_cols
#
#     col_widths = fixed_width_cols + [flexible_col_width] * num_flexible_cols
#
#     # Create and style main table
#     table = Table(headers + data, repeatRows=2, colWidths=col_widths)
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
#         ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('FONTNAME', (0, 0), (-1, 1), 'VeraBd'),
#         ('FONTSIZE', (0, 0), (-1, 1), 9),
#         ('BOTTOMPADDING', (0, 0), (-1, 1), 1 * mm),
#         ('TOPPADDING', (0, 0), (-1, 1), 1 * mm),
#         ('SPAN', (0, 0), (-1, 0)),
#         ('BACKGROUND', (0, 2), (-1, -1), colors.white),
#         ('TEXTCOLOR', (0, 2), (-1, -1), colors.black),
#         ('FONTNAME', (0, 2), (-1, -1), 'Vera'),
#         ('FONTSIZE', (0, 2), (-1, -1), 9),
#         ('TOPPADDING', (0, 2), (-1, -1), 1 * mm),
#         ('BOTTOMPADDING', (0, 2), (-1, -1), 1 * mm),
#         ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#     ]))
#
#     elements.append(KeepTogether(table))
#     elements.append(Spacer(1, 15 * mm))
#
#     # Add comments table if there are comments
#     if comments_data:
#         comments_header = [[Paragraph(h, header_style) for h in ['Product ID', 'Product Name', 'Comments']]]
#         comments_table = Table(comments_header + comments_data, repeatRows=1,
#                                colWidths=[35 * mm, 55 * mm, table_width - 90 * mm])
#         comments_table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('FONTNAME', (0, 0), (-1, 0), 'VeraBd'),
#             ('FONTSIZE', (0, 0), (-1, 0), 9),
#             ('BOTTOMPADDING', (0, 0), (-1, 0), 3 * mm),
#             ('TOPPADDING', (0, 0), (-1, 0), 3 * mm),
#             ('BACKGROUND', (0, 1), (-1, -1), colors.white),
#             ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
#             ('FONTNAME', (0, 1), (-1, -1), 'Vera'),
#             ('FONTSIZE', (0, 1), (-1, -1), 9),
#             ('TOPPADDING', (0, 1), (-1, -1), 2 * mm),
#             ('BOTTOMPADDING', (0, 1), (-1, -1), 2 * mm),
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ]))
#         elements.append(KeepTogether(comments_table))
#
#     # Add page numbers
#     def add_page_number(canvas, doc):
#         page_num = canvas.getPageNumber()
#         text = f"Page {page_num}"
#         canvas.saveState()
#         canvas.setFont("Vera", 9)
#         canvas.drawRightString(page_width - right_margin, bottom_margin / 2, text)
#         canvas.restoreState()
#
#     doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#     return filename
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4, landscape
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import mm
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
#
#
# def generate_comprehensive_stock_pdf(stock_record):
#     pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
#     pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
#
#     page_width, page_height = landscape(A4)
#     filename = f"stock_report_{stock_record.id}_{stock_record.date}.pdf"
#
#     # Increase margins for better spacing
#     left_margin = 15 * mm
#     right_margin = 15 * mm
#     top_margin = 2 * mm
#     bottom_margin = 20 * mm
#
#     doc = SimpleDocTemplate(filename, pagesize=landscape(A4),
#                             leftMargin=left_margin, rightMargin=right_margin,
#                             topMargin=top_margin, bottomMargin=bottom_margin)
#     elements = []
#
#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         'Title',
#         parent=styles['Title'],
#         fontName='VeraBd',
#         fontSize=12,
#         leading=22,
#         alignment=1,
#         spaceAfter=2 * mm,
#     )
#
#     def create_title():
#         return Paragraph(f"Comprehensive Stock Report for {stock_record.date}", title_style)
#
#     elements.append(create_title())
#
#     show_physical_stock = any(record.physical_stock != 0 for record in stock_record.product_stock_records.all())
#
#     header_style = ParagraphStyle(
#         'Header',
#         fontName='VeraBd',
#         fontSize=6,
#         leading=11,
#         alignment=1,
#     )
#
#     data_style = ParagraphStyle(
#         'Data',
#         fontName='Vera',
#         fontSize=8,
#         leading=11,
#         alignment=1,
#     )
#
#     def create_headers():
#         headers = [
#             [Paragraph('PRODUCTION DETAILS', header_style)] + [''] * (11 if show_physical_stock else 10),
#             [Paragraph(h, header_style) for h in [
#                 'S.NO', 'SKU', 'Vol*nos', 'MRP', 'Op.Stock', 'Production',
#                 'Returns', 'Damage', 'Sales', 'Cls.Stock', 'Physical Stock'
#             ]]
#         ]
#         if not show_physical_stock:
#             headers[1].pop()  # Remove Physical Stock header if not needed
#         return headers
#
#     data = []
#     comments_data = []
#     records = stock_record.product_stock_records.all().select_related('product')
#     for count, record in enumerate(records, start=1):
#         row = [
#             Paragraph(str(count), data_style),
#             Paragraph(record.product.product_name, data_style),
#             Paragraph(str(record.volume_nos), data_style),
#             Paragraph(f"{record.mrp}", data_style),
#             Paragraph(f"{record.opening_stock_units}", data_style),
#             Paragraph(f"{record.production_units}", data_style),
#             Paragraph(f"{record.return_in_units}", data_style),
#             Paragraph(f"{record.damage_in_units}", data_style),
#             Paragraph(f"{record.sales_units}", data_style),
#             Paragraph(f"{record.closing_stock_units}", data_style),
#         ]
#         if show_physical_stock:
#             row.append(Paragraph(f"{record.physical_stock}", data_style))
#         data.append(row)
#
#         if record.comments:
#             comments_data.append([
#                 Paragraph(str(record.product.id), data_style),
#                 Paragraph(record.product.product_name, data_style),
#                 Paragraph(record.comments, data_style)
#             ])
#
#     # Calculate available width for the table
#     table_width = page_width - left_margin - right_margin
#
#     # Define column widths with more space
#     fixed_width_cols = [12 * mm, 45 * mm, 18 * mm, 18 * mm]  # S.NO, SKU, Vol*nos, MRP
#     fixed_width_total = sum(fixed_width_cols)
#     remaining_width = table_width - fixed_width_total
#     num_flexible_cols = 7 if show_physical_stock else 6
#     flexible_col_width = remaining_width / num_flexible_cols
#
#     col_widths = fixed_width_cols + [flexible_col_width] * num_flexible_cols
#
#     table = Table(create_headers() + data, repeatRows=2, colWidths=col_widths)
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
#         ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('FONTNAME', (0, 0), (-1, 1), 'VeraBd'),
#         ('FONTSIZE', (0, 0), (-1, 1), 9),
#         ('BOTTOMPADDING', (0, 0), (-1, 1), 1 * mm),
#         ('TOPPADDING', (0, 0), (-1, 1), 1 * mm),
#         ('SPAN', (0, 0), (-1, 0)),
#         ('BACKGROUND', (0, 2), (-1, -1), colors.white),
#         ('TEXTCOLOR', (0, 2), (-1, -1), colors.black),
#         ('FONTNAME', (0, 2), (-1, -1), 'Vera'),
#         ('FONTSIZE', (0, 2), (-1, -1), 9),
#         ('TOPPADDING', (0, 2), (-1, -1), 1 * mm),
#         ('BOTTOMPADDING', (0, 2), (-1, -1), 1 * mm),
#         ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#     ]))
#
#     elements.append(KeepTogether(table))
#     elements.append(Spacer(1, 15 * mm))  # Increased spacing after main table
#
#     if comments_data:
#         comments_header = [[Paragraph(h, header_style) for h in ['Product ID', 'Product Name', 'Comments']]]
#         comments_table_data = comments_header + comments_data
#         comments_table = Table(comments_table_data, repeatRows=1,
#                                colWidths=[35 * mm, 55 * mm, table_width - 90 * mm])
#         comments_table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('FONTNAME', (0, 0), (-1, 0), 'VeraBd'),
#             ('FONTSIZE', (0, 0), (-1, 0), 9),
#             ('BOTTOMPADDING', (0, 0), (-1, 0), 3 * mm),
#             ('TOPPADDING', (0, 0), (-1, 0), 3 * mm),
#             ('BACKGROUND', (0, 1), (-1, -1), colors.white),
#             ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
#             ('FONTNAME', (0, 1), (-1, -1), 'Vera'),
#             ('FONTSIZE', (0, 1), (-1, -1), 9),
#             ('TOPPADDING', (0, 1), (-1, -1), 2 * mm),
#             ('BOTTOMPADDING', (0, 1), (-1, -1), 2 * mm),
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ]))
#         elements.append(KeepTogether(comments_table))
#
#     def add_page_number(canvas, doc):
#         page_num = canvas.getPageNumber()
#         text = f"Page {page_num}"
#         canvas.saveState()
#         canvas.setFont("Vera", 9)
#         canvas.drawRightString(page_width - right_margin, bottom_margin / 2, text)
#         canvas.restoreState()
#
#     doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#
#     return filename
#


# # # <editor-fold desc=" old formart">
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def generate_comprehensive_stock_pdf(stock_record):
    pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
    pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))

    page_width, page_height = landscape(A4)
    filename = f"stock_report_{stock_record.id}_{stock_record.date}.pdf"

    # Increase margins for better spacing
    left_margin = 15 * mm
    right_margin = 15 * mm
    top_margin = 2 * mm
    bottom_margin = 20 * mm

    doc = SimpleDocTemplate(filename, pagesize=landscape(A4),
                            leftMargin=left_margin, rightMargin=right_margin,
                            topMargin=top_margin, bottomMargin=bottom_margin)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='VeraBd',
        fontSize=12,
        leading=22,
        alignment=1,
        spaceAfter=2 * mm,
    )

    def create_title():
        return Paragraph(f"Comprehensive Stock Report for {stock_record.date}", title_style)

    elements.append(create_title())

    show_physical_stock = any(record.physical_stock != 0 for record in stock_record.product_stock_records.all())

    header_style = ParagraphStyle(
        'Header',
        fontName='VeraBd',
        fontSize=6,
        leading=11,
        alignment=1,
    )

    data_style = ParagraphStyle(
        'Data',
        fontName='Vera',
        fontSize=8,
        leading=11,
        alignment=1,
    )

    def create_headers():
        headers = [
            [Paragraph('PRODUCTION DETAILS', header_style)] + [''] * (15 if show_physical_stock else 14),
            [Paragraph(h, header_style) for h in [
                'S.NO', 'SKU', 'Vol*nos', 'MRP', 'Lit Factor', 'Op.Stock in Units', 'Op.Stock in Lits',
                'Production in Units', 'Production in Lits', 'Sales in Units', 'Sales in Lits', 'Cls.Stock in Units',
                'Cls.Stock in Lits','Returns', 'Damage',
            ]]
        ]
        if show_physical_stock:
            headers[1].append(Paragraph('Physical Stock', header_style))
        return headers

    data = []
    comments_data = []
    records = stock_record.product_stock_records.all().select_related('product')
    for count, record in enumerate(records, start=1):
        row = [
            Paragraph(str(count), data_style),
            Paragraph(record.product.product_name, data_style),
            Paragraph(str(record.volume_nos), data_style),
            Paragraph(f"{record.mrp}", data_style),
            Paragraph(f"{record.lit_factor}", data_style),
            Paragraph(f"{record.opening_stock_units}", data_style),
            Paragraph(f"{record.opening_stock_lits}", data_style),
            Paragraph(f"{record.production_units}", data_style),
            Paragraph(f"{record.production_lits}", data_style),
            Paragraph(f"{record.sales_units}", data_style),
            Paragraph(f"{record.sales_lits}", data_style),
            Paragraph(f"{record.closing_stock_units}", data_style),
            Paragraph(f"{record.closing_stock_lits}", data_style),
            Paragraph(f"{record.return_in_units}", data_style),
            Paragraph(f"{record.damage_in_units}", data_style),
        ]
        if show_physical_stock:
            row.append(Paragraph(f"{record.physical_stock}", data_style))
        data.append(row)

        if record.comments:
            comments_data.append([
                Paragraph(str(record.product.id), data_style),
                Paragraph(record.product.product_name, data_style),
                Paragraph(record.comments, data_style)
            ])

    # Calculate available width for the table
    table_width = page_width - left_margin - right_margin

    # Define column widths with more space
    fixed_width_cols = [12 * mm, 45 * mm, 18 * mm, 18 * mm, 18 * mm]  # S.NO, SKU, Vol*nos, MRP, Lit Factor
    fixed_width_total = sum(fixed_width_cols)
    remaining_width = table_width - fixed_width_total
    num_flexible_cols = 8 if show_physical_stock else 7
    flexible_col_width = remaining_width / num_flexible_cols

    col_widths = fixed_width_cols + [flexible_col_width] * num_flexible_cols

    table = Table(create_headers() + data, repeatRows=2, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 1), 'VeraBd'),
        ('FONTSIZE', (0, 0), (-1, 1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 1), 1 * mm),
        ('TOPPADDING', (0, 0), (-1, 1), 1 * mm),
        ('SPAN', (0, 0), (-1, 0)),
        ('BACKGROUND', (0, 2), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 2), (-1, -1), colors.black),
        ('FONTNAME', (0, 2), (-1, -1), 'Vera'),
        ('FONTSIZE', (0, 2), (-1, -1), 9),
        ('TOPPADDING', (0, 2), (-1, -1), 1 * mm),
        ('BOTTOMPADDING', (0, 2), (-1, -1), 1 * mm),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(KeepTogether(table))
    elements.append(Spacer(1, 15 * mm))  # Increased spacing after main table

    if comments_data:
        comments_header = [[Paragraph(h, header_style) for h in ['Product ID', 'Product Name', 'Comments']]]
        comments_table_data = comments_header + comments_data
        comments_table = Table(comments_table_data, repeatRows=1,
                               colWidths=[35 * mm, 55 * mm, table_width - 90 * mm])
        comments_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'VeraBd'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 3 * mm),
            ('TOPPADDING', (0, 0), (-1, 0), 3 * mm),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Vera'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 2 * mm),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 2 * mm),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(KeepTogether(comments_table))

    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.saveState()
        canvas.setFont("Vera", 9)
        canvas.drawRightString(page_width - right_margin, bottom_margin / 2, text)
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

    return filename
# # # </editor-fold>



# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4, landscape
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import mm
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
#
#
# def generate_comprehensive_stock_pdf(stock_record):
#     pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
#     pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
#
#     page_width, page_height = landscape(A4)
#     filename = f"stock_report_{stock_record.id}_{stock_record.date}.pdf"
#
#     # Adjust margins for landscape orientation
#     left_margin = 10 * mm
#     right_margin = 10 * mm
#     top_margin = 15 * mm
#     bottom_margin = 15 * mm
#
#     doc = SimpleDocTemplate(filename, pagesize=landscape(A4),
#                             leftMargin=left_margin, rightMargin=right_margin,
#                             topMargin=top_margin, bottomMargin=bottom_margin)
#     elements = []
#
#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         'Title',
#         parent=styles['Title'],
#         fontName='VeraBd',
#         fontSize=16,
#         leading=18,
#         alignment=1,
#         spaceAfter=5 * mm,
#     )
#
#     def create_title():
#         return Paragraph(f"Comprehensive Stock Report for {stock_record.date}", title_style)
#
#     elements.append(create_title())
#
#     show_physical_stock = any(record.physical_stock != 0 for record in stock_record.product_stock_records.all())
#
#     header_style = ParagraphStyle(
#         'Header',
#         fontName='VeraBd',
#         fontSize=8,
#         leading=10,
#         alignment=1,
#     )
#
#     data_style = ParagraphStyle(
#         'Data',
#         fontName='Vera',
#         fontSize=8,
#         leading=10,
#         alignment=1,
#     )
#
#     def create_headers():
#         headers = [
#             [Paragraph('PRODUCTION DETAILS', header_style)] + [''] * (13 if show_physical_stock else 12),
#             [Paragraph(h, header_style) for h in [
#                 'S.NO', 'SKU', 'Vol*nos', 'MRP', 'Lit Factor', 'Op.Stock in Units', 'Op.Stock in Lits',
#                 'Production in Units', 'Production in Lits', 'Sales in Units', 'Sales in Lits', 'Cls.Stock in Units',
#                 'Cls.Stock in Lits'
#             ]]
#         ]
#         if show_physical_stock:
#             headers[1].append(Paragraph('Physical Stock', header_style))
#         return headers
#
#     data = []
#     comments_data = []
#     records = stock_record.product_stock_records.all().select_related('product')
#     for count, record in enumerate(records, start=1):
#         row = [
#             Paragraph(str(count), data_style),
#             Paragraph(record.product.product_name, data_style),
#             Paragraph(str(record.volume_nos), data_style),
#             Paragraph(f"{record.mrp}", data_style),
#             Paragraph(f"{record.lit_factor}", data_style),
#             Paragraph(f"{record.opening_stock_units}", data_style),
#             Paragraph(f"{record.opening_stock_lits}", data_style),
#             Paragraph(f"{record.production_units}", data_style),
#             Paragraph(f"{record.production_lits}", data_style),
#             Paragraph(f"{record.sales_units}", data_style),
#             Paragraph(f"{record.sales_lits}", data_style),
#             Paragraph(f"{record.closing_stock_units}", data_style),
#             Paragraph(f"{record.closing_stock_lits}", data_style),
#         ]
#         if show_physical_stock:
#             row.append(Paragraph(f"{record.physical_stock}", data_style))
#         data.append(row)
#
#         if record.comments:
#             comments_data.append([
#                 Paragraph(str(record.product.id), data_style),
#                 Paragraph(record.product.product_name, data_style),
#                 Paragraph(record.comments, data_style)
#             ])
#
#     # Calculate available width for the table
#     table_width = page_width - left_margin - right_margin
#
#     # Define column widths
#     fixed_width_cols = [10 * mm, 40 * mm, 15 * mm, 15 * mm, 15 * mm]  # S.NO, SKU, Vol*nos, MRP, Lit Factor
#     fixed_width_total = sum(fixed_width_cols)
#     remaining_width = table_width - fixed_width_total
#     num_flexible_cols = 8 if show_physical_stock else 7
#     flexible_col_width = remaining_width / num_flexible_cols
#
#     col_widths = fixed_width_cols + [flexible_col_width] * num_flexible_cols
#
#     table = Table(create_headers() + data, repeatRows=2, colWidths=col_widths)
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
#         ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('FONTNAME', (0, 0), (-1, 1), 'VeraBd'),
#         ('FONTSIZE', (0, 0), (-1, 1), 8),
#         ('BOTTOMPADDING', (0, 0), (-1, 1), 3 * mm),
#         ('TOPPADDING', (0, 0), (-1, 1), 3 * mm),
#         ('SPAN', (0, 0), (-1, 0)),
#         ('BACKGROUND', (0, 2), (-1, -1), colors.white),
#         ('TEXTCOLOR', (0, 2), (-1, -1), colors.black),
#         ('FONTNAME', (0, 2), (-1, -1), 'Vera'),
#         ('FONTSIZE', (0, 2), (-1, -1), 8),
#         ('TOPPADDING', (0, 2), (-1, -1), 2 * mm),
#         ('BOTTOMPADDING', (0, 2), (-1, -1), 2 * mm),
#         ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#     ]))
#
#     elements.append(KeepTogether(table))
#     elements.append(Spacer(1, 10 * mm))
#
#     if comments_data:
#         comments_header = [[Paragraph(h, header_style) for h in ['Product ID', 'Product Name', 'Comments']]]
#         comments_table_data = comments_header + comments_data
#         comments_table = Table(comments_table_data, repeatRows=1,
#                                colWidths=[30 * mm, 50 * mm, table_width - 80 * mm])
#         comments_table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('FONTNAME', (0, 0), (-1, 0), 'VeraBd'),
#             ('FONTSIZE', (0, 0), (-1, 0), 8),
#             ('BOTTOMPADDING', (0, 0), (-1, 0), 2 * mm),
#             ('TOPPADDING', (0, 0), (-1, 0), 2 * mm),
#             ('BACKGROUND', (0, 1), (-1, -1), colors.white),
#             ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
#             ('FONTNAME', (0, 1), (-1, -1), 'Vera'),
#             ('FONTSIZE', (0, 1), (-1, -1), 8),
#             ('TOPPADDING', (0, 1), (-1, -1), 1 * mm),
#             ('BOTTOMPADDING', (0, 1), (-1, -1), 1 * mm),
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
#         ]))
#         elements.append(KeepTogether(comments_table))
#
#     def add_page_number(canvas, doc):
#         page_num = canvas.getPageNumber()
#         text = f"Page {page_num}"
#         canvas.saveState()
#         canvas.setFont("Vera", 8)
#         canvas.drawRightString(page_width - right_margin, bottom_margin / 2, text)
#         canvas.restoreState()
#
#     doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#
#     return filename
# # ==============================
# # from reportlab.lib import colors
# # from reportlab.lib.pagesizes import A4
# # from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# # from reportlab.lib.units import mm
# # from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# #
# #
# # def generate_comprehensive_stock_pdf(stock_record):
# #     page_width, page_height = A4
# #     filename = f"stock_report_{stock_record.id}_{stock_record.date}.pdf"
# #     doc = SimpleDocTemplate(filename, pagesize=A4,
# #                             leftMargin=15 * mm, rightMargin=15 * mm,
# #                             topMargin=20 * mm, bottomMargin=20 * mm)
# #     elements = []
# #
# #     styles = getSampleStyleSheet()
# #     title_style = ParagraphStyle(
# #         'Title',
# #         parent=styles['Title'],
# #         fontSize=16,
# #         leading=20,
# #         alignment=1,
# #         spaceAfter=10 * mm,
# #     )
# #     elements.append(Paragraph(f"Comprehensive Stock Report for {stock_record.date}", title_style))
# #
# #     show_physical_stock = any(record.physical_stock != 0 for record in stock_record.product_stock_records.all())
# #
# #     headers = [
# #         ['PRODUCTION DETAILS'] + [''] * (15 if show_physical_stock else 14),
# #         ['S.NO', 'SKU', 'Vol*nos', 'MRP', 'Lit Factor', 'Op.Stock in Units', 'Op.Stock in Lits',
# #          'Production in Units', 'Production in Lits', 'Prdn in Value', 'Sales in Units', 'Sales in Lits',
# #          'Sales in Value', 'Cls.Stock in Units', 'Cls.Stock in Lits', 'Cls.Stock in Value']
# #     ]
# #     if show_physical_stock:
# #         headers[1].append('Physical Stock')
# #
# #     data = []
# #     comments_data = []
# #     records = stock_record.product_stock_records.all().select_related('product')
# #     for count, record in enumerate(records, start=1):
# #         row = [
# #             count,
# #             record.product.product_name,
# #             record.volume_nos,
# #             str(record.mrp),
# #             str(record.lit_factor),
# #             str(record.opening_stock_units),
# #             str(record.opening_stock_lits),
# #             str(record.production_units),
# #             str(record.production_lits),
# #             str(record.production_value),
# #             str(record.sales_units),
# #             str(record.sales_lits),
# #             str(record.sales_value),
# #             str(record.closing_stock_units),
# #             str(record.closing_stock_lits),
# #             str(record.closing_stock_value),
# #         ]
# #         if show_physical_stock:
# #             row.append(str(record.physical_stock))
# #         data.append(row)
# #
# #         if record.comments:
# #             comments_data.append([
# #                 record.product.id,
# #                 record.product.product_name,
# #                 record.comments
# #             ])
# #
# #     all_data = headers + data
# #
# #     table_width = page_width - 30 * mm  # Subtracting left and right margins
# #     col_widths = [10 * mm] + [(table_width - 10 * mm) / (16 if show_physical_stock else 15)] * (
# #         16 if show_physical_stock else 15)
# #
# #     table = Table(all_data, repeatRows=2, colWidths=col_widths)
# #     table.setStyle(TableStyle([
# #         ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
# #         ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
# #         ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
# #         ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
# #         ('FONTSIZE', (0, 0), (-1, 1), 8),
# #         ('BOTTOMPADDING', (0, 0), (-1, 1), 3 * mm),
# #         ('TOPPADDING', (0, 0), (-1, 1), 3 * mm),
# #         ('SPAN', (0, 0), (-1, 0)),
# #         ('BACKGROUND', (0, 2), (-1, -1), colors.white),
# #         ('TEXTCOLOR', (0, 2), (-1, -1), colors.black),
# #         ('ALIGN', (0, 2), (-1, -1), 'CENTER'),
# #         ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
# #         ('FONTSIZE', (0, 2), (-1, -1), 8),
# #         ('TOPPADDING', (0, 2), (-1, -1), 1 * mm),
# #         ('BOTTOMPADDING', (0, 2), (-1, -1), 1 * mm),
# #         ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
# #         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
# #         ('WORDWRAP', (0, 0), (-1, -1), True),
# #     ]))
# #
# #     elements.append(table)
# #     elements.append(Spacer(1, 15 * mm))
# #
# #     if comments_data:
# #         comments_header = [['Product ID', 'Product Name', 'Comments']]
# #         comments_table_data = comments_header + comments_data
# #         comments_table = Table(comments_table_data, repeatRows=1,
# #                                colWidths=[30 * mm, 60 * mm, page_width - 120 * mm])
# #         comments_table.setStyle(TableStyle([
# #             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
# #             ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
# #             ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
# #             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
# #             ('FONTSIZE', (0, 0), (-1, 0), 9),
# #             ('BOTTOMPADDING', (0, 0), (-1, 0), 3 * mm),
# #             ('BACKGROUND', (0, 1), (-1, -1), colors.white),
# #             ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
# #             ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
# #             ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
# #             ('FONTSIZE', (0, 1), (-1, -1), 8),
# #             ('TOPPADDING', (0, 1), (-1, -1), 1 * mm),
# #             ('BOTTOMPADDING', (0, 1), (-1, -1), 1 * mm),
# #             ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
# #             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
# #             ('WORDWRAP', (0, 0), (-1, -1), True),
# #         ]))
# #         elements.append(comments_table)
# #
# #     doc.build(elements)
# #
# #     return filename
# # # ==========================================
# # # from reportlab.lib import colors
# # # from reportlab.lib.pagesizes import A4, landscape
# # # from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# # # from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# # # from reportlab.lib.units import mm
# # # from StockReport.models import StockRecord
# # #
# # #
# # # def generate_alternative_stock_pdf(stock_record):
# # #     page_width, page_height = landscape(A4)
# # #     filename = f"stock_report_{stock_record.id}_{stock_record.date}.pdf"
# # #     doc = SimpleDocTemplate(filename, pagesize=landscape(A4),
# # #                             leftMargin=15 * mm, rightMargin=15 * mm,
# # #                             topMargin=20 * mm, bottomMargin=20 * mm)
# # #     elements = []
# # #
# # #     styles = getSampleStyleSheet()
# # #     title_style = ParagraphStyle(
# # #         'Title',
# # #         parent=styles['Title'],
# # #         fontSize=16,
# # #         leading=20,
# # #         alignment=1,
# # #         spaceAfter=10 * mm,
# # #     )
# # #     elements.append(Paragraph(f"Comprehensive Stock Report for {stock_record.date}", title_style))
# # #
# # #     # Main stock table
# # #     main_headers = [
# # #         'S.NO', 'SKU', 'Vol*nos', 'MRP', 'Lit Factor', 'Op.Stock', 'Production', 'Sales', 'Cls.Stock'
# # #     ]
# # #
# # #     main_data = [main_headers]
# # #
# # #     records = stock_record.product_stock_records.all().select_related('product')
# # #     for count, record in enumerate(records, start=1):
# # #         row = [
# # #             count,
# # #             record.product.product_name,
# # #             record.volume_nos,
# # #             f"{record.mrp:.2f}",
# # #             f"{record.lit_factor:.2f}",
# # #             f"{record.opening_stock_units} / {record.opening_stock_lits:.2f}L",
# # #             f"{record.production_units} / {record.production_lits:.2f}L / {record.production_value:.2f}",
# # #             f"{record.sales_units} / {record.sales_lits:.2f}L / {record.sales_value:.2f}",
# # #             f"{record.closing_stock_units} / {record.closing_stock_lits:.2f}L / {record.closing_stock_value:.2f}"
# # #         ]
# # #         main_data.append(row)
# # #
# # #     col_widths = [20 * mm, 40 * mm, 25 * mm, 20 * mm, 25 * mm, 35 * mm, 45 * mm, 45 * mm, 45 * mm]
# # #     main_table = Table(main_data, repeatRows=1, colWidths=col_widths)
# # #     main_table.setStyle(TableStyle([
# # #         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
# # #         ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
# # #         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
# # #         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
# # #         ('FONTSIZE', (0, 0), (-1, 0), 10),
# # #         ('BOTTOMPADDING', (0, 0), (-1, 0), 5 * mm),
# # #         ('BACKGROUND', (0, 1), (-1, -1), colors.white),
# # #         ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
# # #         ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
# # #         ('FONTSIZE', (0, 1), (-1, -1), 8),
# # #         ('TOPPADDING', (0, 1), (-1, -1), 3 * mm),
# # #         ('BOTTOMPADDING', (0, 1), (-1, -1), 3 * mm),
# # #         ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
# # #         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
# # #         ('WORDWRAP', (0, 0), (-1, -1), True),
# # #     ]))
# # #
# # #     elements.append(main_table)
# # #     elements.append(Spacer(1, 20 * mm))
# # #
# # #     # Comments table
# # #     comments_data = [['Product ID', 'Product Name', 'Comments']]
# # #     for record in records:
# # #         if record.comments:
# # #             comments_data.append([
# # #                 record.product.id,
# # #                 record.product.product_name,
# # #                 record.comments
# # #             ])
# # #
# # #     if len(comments_data) > 1:
# # #         comments_table = Table(comments_data, repeatRows=1,
# # #                                colWidths=[30 * mm, 60 * mm, page_width - 120 * mm])
# # #         comments_table.setStyle(TableStyle([
# # #             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
# # #             ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
# # #             ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
# # #             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
# # #             ('FONTSIZE', (0, 0), (-1, 0), 10),
# # #             ('BOTTOMPADDING', (0, 0), (-1, 0), 5 * mm),
# # #             ('BACKGROUND', (0, 1), (-1, -1), colors.white),
# # #             ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
# # #             ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
# # #             ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
# # #             ('FONTSIZE', (0, 1), (-1, -1), 8),
# # #             ('TOPPADDING', (0, 1), (-1, -1), 3 * mm),
# # #             ('BOTTOMPADDING', (0, 1), (-1, -1), 3 * mm),
# # #             ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
# # #             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
# # #             ('WORDWRAP', (0, 0), (-1, -1), True),
# # #         ]))
# # #         elements.append(comments_table)
# # #
# # #     doc.build(elements)
# # #     return filename
# # # ================================================
# # # from reportlab.lib import colors
# # # from reportlab.lib.pagesizes import landscape, A3
# # # from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# # # from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# # # from reportlab.lib.units import inch
# # # from StockReport.models import StockRecord
# # #
# # #
# # #
# # # # ========================
# # # # PDF Generation Function
# # #
# # # def generate_comprehensive_stock_pdf(stock_record):
# # #     page_width, page_height = landscape(A3)
# # #     filename = f"stock_report_{stock_record.id}_{stock_record.date}.pdf"
# # #     doc = SimpleDocTemplate(filename, pagesize=(page_width, page_height),
# # #                             leftMargin=0.25 * inch, rightMargin=0.25 * inch,
# # #                             topMargin=0.5 * inch, bottomMargin=0.5 * inch)
# # #     elements = []
# # #
# # #     styles = getSampleStyleSheet()
# # #     title_style = ParagraphStyle(
# # #         'Title',
# # #         parent=styles['Title'],
# # #         fontSize=14,
# # #         leading=16,
# # #         alignment=1,  # Center alignment
# # #     )
# # #     elements.append(Paragraph(f"Comprehensive Stock Report for {stock_record.date}", title_style))
# # #     elements.append(Spacer(1, 0.1 * inch))
# # #
# # #     headers = [
# # #         ['PRODUCTION DETAILS', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',],
# # #         ['S.NO','SKU', 'Vol*nos', 'MRP', 'Lit Factor', 'Op.Stock in Units', 'Op.Stock in Lits',
# # #          'Production in Units',
# # #         'Production in Lits', 'Prdn in Value', 'Sales in Units', 'Sales in Lits', 'Sales in Value',
# # #          'Cls.Stock in Units', 'Cls.Stock in Lits', 'Cls.Stock in Value', 'Physical Stock']
# # #     ]
# # #
# # #     data = []
# # #     comments_data = []
# # #     records = stock_record.product_stock_records.all().select_related('product')
# # #     count = 1
# # #     for record in records:
# # #         data.append([
# # #             count,
# # #             record.product.product_name,
# # #             record.volume_nos,
# # #             str(record.mrp),
# # #             str(record.lit_factor),
# # #             str(record.opening_stock_units),
# # #             str(record.opening_stock_lits),
# # #             str(record.production_units),
# # #             str(record.production_lits),
# # #             str(record.production_value),
# # #             str(record.sales_units),
# # #             str(record.sales_lits),
# # #             str(record.sales_value),
# # #             str(record.closing_stock_units),
# # #             str(record.closing_stock_lits),
# # #             str(record.closing_stock_value),
# # #             str(record.physical_stock),
# # #         ])
# # #         if record.comments:
# # #             comments_data.append([
# # #                 record.product.id,
# # #                 record.product.product_name,
# # #                 record.comments
# # #             ])
# # #         count += 1
# # #
# # #     all_data = headers + data
# # #
# # #     table_width = page_width - 0.5 * inch
# # #     col_widths = [1.2 * inch] + [((table_width - 1.2 * inch) / 17)] * 17
# # #
# # #     table = Table(all_data, repeatRows=2, colWidths=col_widths)
# # #     table.setStyle(TableStyle([
# # #         ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
# # #         ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
# # #         ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
# # #         ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
# # #         ('FONTSIZE', (0, 0), (-1, 1), 6),
# # #         ('BOTTOMPADDING', (0, 0), (-1, 1), 4),
# # #         ('SPAN', (0, 0), (-1, 0)),
# # #         ('BACKGROUND', (0, 2), (-1, -1), colors.white),
# # #         ('TEXTCOLOR', (0, 2), (-1, -1), colors.black),
# # #         ('ALIGN', (0, 2), (-1, -1), 'CENTER'),
# # #         ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
# # #         ('FONTSIZE', (0, 2), (-1, -1), 6),
# # #         ('TOPPADDING', (0, 2), (-1, -1), 1),
# # #         ('BOTTOMPADDING', (0, 2), (-1, -1), 1),
# # #         ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
# # #         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
# # #         ('WORDWRAP', (0, 0), (-1, -1), True),
# # #     ]))
# # #
# # #     elements.append(table)
# # #     elements.append(Spacer(1, 0.2 * inch))
# # #
# # #     if comments_data:
# # #         comments_header = [['Product ID', 'Product Name', 'Comments']]
# # #         comments_table_data = comments_header + comments_data
# # #         comments_table = Table(comments_table_data, repeatRows=1)
# # #         comments_table.setStyle(TableStyle([
# # #             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
# # #             ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
# # #             ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
# # #             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
# # #             ('FONTSIZE', (0, 0), (-1, 0), 8),
# # #             ('BACKGROUND', (0, 1), (-1, -1), colors.white),
# # #             ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
# # #             ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
# # #             ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
# # #             ('FONTSIZE', (0, 1), (-1, -1), 8),
# # #             ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
# # #             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
# # #             ('WORDWRAP', (0, 0), (-1, -1), True),
# # #         ]))
# # #         elements.append(comments_table)
# # #
# # #     doc.build(elements)
# # #
# # #     return filename
# # #
# #
# # # ========================
# #
# # # def generate_comprehensive_stock_pdf(stock_record):
# # #     # Use A2 size for more width
# # #     page_width, page_height = landscape(A3)
# # #     filename = f"stock_report_{stock_record.id}_{stock_record.date}.pdf"
# # #     doc = SimpleDocTemplate(filename, pagesize=(page_width, page_height),
# # #                             leftMargin=0.25 * inch, rightMargin=0.25 * inch,
# # #                             topMargin=0.5 * inch, bottomMargin=0.5 * inch)
# # #     elements = []
# # #
# # #     styles = getSampleStyleSheet()
# # #     title_style = ParagraphStyle(
# # #         'Title',
# # #         parent=styles['Title'],
# # #         fontSize=14,
# # #         leading=16,
# # #         alignment=1,  # Center alignment
# # #     )
# # #     elements.append(Paragraph(f"Comprehensive Stock Report for {stock_record.date}", title_style))
# # #     elements.append(Spacer(1, 0.1 * inch))
# # #
# # #     # Prepare data for the main table
# # #     headers = [
# # #         ['PRODUCTION DETAILS', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',],
# # #         ['S.NO','SKU', 'Vol*nos', 'MRP', 'Lit Factor', 'Op.Stock in Units', 'Op.Stock in Lits', 'Production in Units',
# # #          'Production in Lits', 'Prdn in Value', 'Sales in Units', 'Sales in Lits', 'Sales in Value',
# # #          'Cls.Stock in Units', 'Cls.Stock in Lits', 'Cls.Stock in Value', 'Physical Stock']
# # #     ]
# # #
# # #     data = []
# # #     comments_data = []
# # #     records = stock_record.stock_record.all().select_related('product')
# # #     count=1
# # #     for record in records:
# # #         data.append([
# # #             count,
# # #             record.product.product_name,
# # #             record.volume_nos,
# # #             str(record.mrp),
# # #             str(record.lit_factor),
# # #             str(record.opening_stock_units),
# # #             str(record.opening_stock_lits),
# # #             str(record.production_units),
# # #             str(record.production_lits),
# # #             str(record.production_value),
# # #             str(record.sales_units),
# # #             str(record.sales_lits),
# # #             str(record.sales_value),
# # #             str(record.closing_stock_units),
# # #             str(record.closing_stock_lits),
# # #             str(record.closing_stock_value),
# # #             str(record.physical_stock),
# # #
# # #         ])
# # #         if record.comments:
# # #             comments_data.append([
# # #                 record.product.id,
# # #                 record.product.product_name,
# # #                 record.comments
# # #             ])
# # #         count=count+1
# # #     # Combine headers and data
# # #     all_data = headers + data
# # #
# # #     # Calculate fixed column widths
# # #     table_width = page_width - 0.5 * inch  # Total width minus margins
# # #     col_widths = [1.2 * inch] + [((table_width - 1.2 * inch) / 17)] * 17  # First column wider, rest equal
# # #
# # #     # Create the main table
# # #     table = Table(all_data, repeatRows=2, colWidths=col_widths)
# # #     table.setStyle(TableStyle([
# # #         # Header styles
# # #         ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
# # #         ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
# # #         ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
# # #         ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
# # #         ('FONTSIZE', (0, 0), (-1, 1), 6),  # Smaller font size for headers
# # #         ('BOTTOMPADDING', (0, 0), (-1, 1), 4),
# # #         ('SPAN', (0, 0), (-1, 0)),  # Span the first row
# # #
# # #         # Data styles
# # #         ('BACKGROUND', (0, 2), (-1, -1), colors.white),
# # #         ('TEXTCOLOR', (0, 2), (-1, -1), colors.black),
# # #         ('ALIGN', (0, 2), (-1, -1), 'CENTER'),
# # #         ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
# # #         ('FONTSIZE', (0, 2), (-1, -1), 6),  # Smaller font size for data
# # #         ('TOPPADDING', (0, 2), (-1, -1), 1),
# # #         ('BOTTOMPADDING', (0, 2), (-1, -1), 1),
# # #
# # #         # Global styles
# # #         ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
# # #         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
# # #         ('WORDWRAP', (0, 0), (-1, -1), True),
# # #     ]))
# # #
# # #     elements.append(table)
# # #     elements.append(Spacer(1, 0.2 * inch))
# # #
# # #     # Create the comments table if there are any comments
# # #     if comments_data:
# # #         comments_header = [['Product ID', 'Product Name', 'Comments']]
# # #         comments_table_data = comments_header + comments_data
# # #         comments_table = Table(comments_table_data, repeatRows=1)
# # #         comments_table.setStyle(TableStyle([
# # #             # Header styles
# # #             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
# # #             ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
# # #             ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
# # #             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
# # #             ('FONTSIZE', (0, 0), (-1, 0), 8),
# # #
# # #             # Data styles
# # #             ('BACKGROUND', (0, 1), (-1, -1), colors.white),
# # #             ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
# # #             ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
# # #             ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
# # #             ('FONTSIZE', (0, 1), (-1, -1), 8),
# # #
# # #             # Global styles
# # #             ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
# # #             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
# # #             ('WORDWRAP', (0, 0), (-1, -1), True),
# # #         ]))
# # #         elements.append(comments_table)
# # #
# # #     # Generate the PDF
# # #     doc.build(elements)
# # #
# # #     return filename
# # # from reportlab.lib import colors
# # # from reportlab.lib.pagesizes import landscape, A3
# # # from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# # # from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# # # from reportlab.lib.units import inch
# # # from StockReport.models import StockRecord
# # #
# # #
# # # def generate_comprehensive_stock_pdf(stock_record):
# # #     # Use A2 size for more width
# # #     page_width, page_height = landscape(A3)
# # #     filename = f"stock_report_{stock_record.id}_{stock_record.date}.pdf"
# # #     doc = SimpleDocTemplate(filename, pagesize=(page_width, page_height),
# # #                             leftMargin=0.25 * inch, rightMargin=0.25 * inch,
# # #                             topMargin=0.5 * inch, bottomMargin=0.5 * inch)
# # #     elements = []
# # #
# # #     styles = getSampleStyleSheet()
# # #     title_style = ParagraphStyle(
# # #         'Title',
# # #         parent=styles['Title'],
# # #         fontSize=14,
# # #         leading=16,
# # #         alignment=1,  # Center alignment
# # #     )
# # #     elements.append(Paragraph(f"Comprehensive Stock Report for {stock_record.date}", title_style))
# # #     elements.append(Spacer(1, 0.1 * inch))
# # #
# # #     # Prepare data for the table
# # #     headers = [
# # #         ['PRODUCTION DETAILS', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
# # #         ['SKU', 'Vol*nos', 'MRP', 'Lit Factor', 'Op.Stock in Units', 'Op.Stock in Lits', 'Production in Units',
# # #          'Production in Lits', 'Prdn in Value', 'Sales in Units', 'Sales in Lits', 'Sales in Value',
# # #          'Cls.Stock in Units', 'Cls.Stock in Lits', 'Cls.Stock in Value', 'Physical Stock', 'Comments']
# # #     ]
# # #
# # #     data = []
# # #     records = stock_record.stock_record.all().select_related('product')
# # #     for record in records:
# # #         data.append([
# # #             record.product.product_name,
# # #             record.volume_nos,
# # #             str(record.mrp),
# # #             str(record.lit_factor),
# # #             str(record.opening_stock_units),
# # #             str(record.opening_stock_lits),
# # #             str(record.production_units),
# # #             str(record.production_lits),
# # #             str(record.production_value),
# # #             str(record.sales_units),
# # #             str(record.sales_lits),
# # #             str(record.sales_value),
# # #             str(record.closing_stock_units),
# # #             str(record.closing_stock_lits),
# # #             str(record.closing_stock_value),
# # #
# # #             str(record.physical_stock),
# # #             record.comments
# # #         ])
# # #
# # #     # Combine headers and data
# # #     all_data = headers + data
# # #
# # #     # Calculate fixed column widths
# # #     table_width = page_width - 0.5 * inch  # Total width minus margins
# # #     col_widths = [1.2 * inch] + [((table_width - 1.2 * inch) / 17)] * 17  # First column wider, rest equal
# # #
# # #     # Create the table
# # #     table = Table(all_data, repeatRows=2, colWidths=col_widths)
# # #     table.setStyle(TableStyle([
# # #         # Header styles
# # #         ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
# # #         ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
# # #         ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
# # #         ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
# # #         ('FONTSIZE', (0, 0), (-1, 1), 6),  # Smaller font size for headers
# # #         ('BOTTOMPADDING', (0, 0), (-1, 1), 4),
# # #         ('SPAN', (0, 0), (-1, 0)),  # Span the first row
# # #
# # #         # Data styles
# # #         ('BACKGROUND', (0, 2), (-1, -1), colors.white),
# # #         ('TEXTCOLOR', (0, 2), (-1, -1), colors.black),
# # #         ('ALIGN', (0, 2), (-1, -1), 'CENTER'),
# # #         ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
# # #         ('FONTSIZE', (0, 2), (-1, -1), 6),  # Smaller font size for data
# # #         ('TOPPADDING', (0, 2), (-1, -1), 1),
# # #         ('BOTTOMPADDING', (0, 2), (-1, -1), 1),
# # #
# # #         # Global styles
# # #         ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
# # #         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
# # #         ('WORDWRAP', (0, 0), (-1, -1), True),
# # #     ]))
# # #
# # #     elements.append(table)
# # #
# # #     # Generate the PDF
# # #     doc.build(elements)
# # #
# # #     return filename
# # # from reportlab.lib import colors
# # # from reportlab.lib.pagesizes import landscape, A3
# # # from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# # # from reportlab.lib.styles import getSampleStyleSheet
# # # from StockReport.models import StockRecord
# # #
# # # def generate_comprehensive_stock_pdf(stock_record):
# # #     """
# # #     Generate a comprehensive PDF report of ProductStockRecords associated with a specific StockRecord.
# # #
# # #     Args:
# # #     stock_record (StockRecord): The StockRecord instance to generate the report for.
# # #     """
# # #     filename = f"stock_report_{stock_record.id}_{stock_record.date}.pdf"
# # #     doc = SimpleDocTemplate(filename, pagesize=landscape(A3))
# # #     elements = []
# # #
# # #     styles = getSampleStyleSheet()
# # #     elements.append(Paragraph(f"Comprehensive Stock Report for {stock_record.date}", styles['Title']))
# # #     elements.append(Spacer(1, 20))
# # #
# # #     # Fetch data
# # #     records = stock_record.stock_record.all().select_related('product', 'opening_stock')
# # #
# # #     # Prepare data for the table
# # #     data = [
# # #         ['Product', 'Opening Stock Date', 'Opening Stock Units', 'Opening Stock Liters',
# # #          'Volume', 'MRP', 'Lit Factor', 'Production Units', 'Production Liters', 'Production Value',
# # #          'Sales Units', 'Sales Liters', 'Sales Value',
# # #          'Closing Stock Units', 'Closing Stock Liters', 'Closing Stock Value',
# # #          'Units per Crate', 'Physical Stock', 'Comments']
# # #     ]
# # #
# # #     for record in records:
# # #         data.append([
# # #             record.product.product_name,
# # #             str(record.opening_stock.date),
# # #             str(record.opening_stock.stock_units),
# # #             str(record.opening_stock.stock_lits),
# # #             record.volume_nos,
# # #             str(record.mrp),
# # #             str(record.lit_factor),
# # #             str(record.production_units),
# # #             str(record.production_lits),
# # #             str(record.production_value),
# # #             str(record.sales_units),
# # #             str(record.sales_lits),
# # #             str(record.sales_value),
# # #             str(record.closing_stock_units),
# # #             str(record.closing_stock_lits),
# # #             str(record.closing_stock_value),
# # #             str(record.units_per_crate),
# # #             str(record.physical_stock),
# # #             record.comments
# # #         ])
# # #
# # #     # Create the table
# # #     table = Table(data, repeatRows=1)
# # #     table.setStyle(TableStyle([
# # #         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
# # #         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
# # #         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
# # #         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
# # #         ('FONTSIZE', (0, 0), (-1, 0), 8),
# # #         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
# # #         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
# # #         ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
# # #         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
# # #         ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
# # #         ('FONTSIZE', (0, 1), (-1, -1), 7),
# # #         ('TOPPADDING', (0, 1), (-1, -1), 4),
# # #         ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
# # #         ('GRID', (0, 0), (-1, -1), 1, colors.black),
# # #         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
# # #         ('WORDWRAP', (0, 0), (-1, -1), True),
# # #     ]))
# # #
# # #     elements.append(table)
# # #
# # #     # Generate the PDF
# # #     doc.build(elements)
# # #
# # #     return filename