import logging
from datetime import timedelta

from django.db.models import Sum
from django.http import FileResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import UserBase
from distributors.invoice_utils import generate_invoice
from distributors.models import RetailerMainOrders
from orders.models import GST

logger = logging.getLogger("magneta_logger")


def safe_str(value):
    return '' if value is None else str(value)


def header_section(p):
    p.setFont("Helvetica-Bold", 13)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(20, 800, "SHASHI SIDNAL FOODS PVT LTD")
    p.drawString(20, 785, "MAGNETA")
    p.setFillColorRGB(1, 0, 0)

    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica", 9)
    p.drawString(20, 770, "Survey No. 43/2, Village: Sanikopa,")
    p.drawString(20, 759, "Taluka: Bailhongal, BELAGAVI, KARNATAKA - 591102.")
    p.drawString(20, 748, "GSTIN: 29AAMCS5943H1ZS | State Name : Karnataka, Code : 29")
    p.drawString(20, 737, "Phone: 9035054529 | Email: info@magnetaicecream.in")
    p.drawString(20, 726, "www.magnetaicecream.in")

    image_path = os.path.join(settings.STATIC_DIR, 'logo.png')
    p.drawImage(image_path, 460, 720, width=100, height=100)

    watermark_logo = os.path.join(settings.STATIC_DIR, 'watermark_logo.png')
    p.drawImage(watermark_logo, 50, 150, width=500, height=500)

    p.setFillColorRGB(1, 0, 0)
    p.drawString(20, 720, "________________________________________________________________________"
                          "_______________________________________")


def invoice_section(p, retailer_main_order, retailer):
    p.setFont("Helvetica-Bold", 11)
    p.setFillColorRGB(1, 0, 0)
    # p.drawString(260, 705, "Tax Invoice")
    if retailer_main_order.mode_of_payment in ['Credit', 'credit', 'CREDIT']:
        p.drawString(260, 700, "Tax Invoice")
    else:
        header_tax_invoice = "Tax Invoice" if retailer_main_order.mode_of_payment not in ['stn','free sample'] else retailer_main_order.mode_of_payment
        p.drawString(260, 705, header_tax_invoice.upper())
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(20, 695, "Bill to,")
    p.drawString(485, 695, "Invoice No: ")
    p.drawString(20, 685, safe_str(retailer.first_name) + " " + safe_str(retailer.last_name)+safe_str(retailer.enterprise_name) + " (" + safe_str(retailer.user_id)+")")
    p.drawString(485, 685, safe_str(retailer_main_order.order_number))
    p.drawString(20, 674, safe_str(retailer.phone_number) + " | " + safe_str(retailer.email))

    new_gst = retailer.gst if retailer.gst[2:11] != "XXXXX0000" else "NA"
    new_state = retailer.state if retailer.state is not None else "NA"

    p.drawString(20, 663,
                 safe_str(new_gst) + " | State name: " + safe_str(new_state) + ", Code: " + safe_str(
                     retailer.gst[:2]))
    p.setFont("Helvetica", 10)
    p.drawString(485, 663, "Date: " + safe_str(retailer_main_order.order_date))


def table_header_section(p, retailer_main_order):
    x_start = 20
    y_start = 638
    width = 555
    height = 20

    p.setFillColorRGB(1, 0, 0)

    p.rect(x_start, y_start, width, height, fill=True, stroke=False)

    p.setFont("Helvetica-Bold", 11)
    p.setFillColorRGB(1, 1, 1)
    p.drawString(30, 645, "#")
    p.drawString(50, 645, "Item Name")
    p.drawString(245, 645, "Qty")
    p.drawString(280, 645, "Unit")#new
    p.drawString(338, 645, "Price/Unit")


    p.drawString(400, 645, "Discount")

    # p.drawString(465, 645, "GST")
    # p.setFont("Helvetica-Bold", 8)
    # p.drawString(490, 645, f"{retailer_main_order.gst_rate}%")
    p.setFont("Helvetica-Bold", 11)


    p.drawString(528, 645, "Amount")


def align_x(base_x, float_num):
    int_num = str(round(float(float_num)))
    num_digits = len(int_num)

    if num_digits == 7:
        return base_x
    elif num_digits == 6:
        return base_x + 6
    elif num_digits == 5:
        return base_x + 12
    elif num_digits == 4:
        return base_x + 18
    elif num_digits == 3:
        return base_x + 24
    elif num_digits == 2:
        return base_x + 30
    elif num_digits == 1:
        return base_x + 36
    else:
        return base_x


def table_data_section(p, y_position,data):
    p.setFont("Helvetica", 11)
    p.setFillColorRGB(0, 0, 0)
    y_position = y_position
    for index, order in enumerate(data, start=1):
        y_position -= 20

        p.drawString(30, y_position, str(index))
        p.drawString(50, y_position, str(order['name']))
        p.drawString(align_x(base_x=220, float_num=order['quantity']), y_position, str(order['quantity']))
        p.drawString(280, y_position, f"Box ({order['carton_size']})")


        p.drawString(align_x(base_x=320, float_num=order['carton_base_price']), y_position, str(order['carton_base_price']))


        p.drawString(410, y_position, f"{order['discount_amount']} ({order['product_discount']}%)")


        # p.drawString(align_x(base_x=445, float_num=order['gst_price']), y_position, str(order['gst_price']))

        p.drawString(align_x(base_x=515, float_num=order['discounted_price']), y_position, str(order['discounted_price']))

        if y_position <= 30:
            p.showPage()
            header_section(p=p)
            y_position = 720
            p.setFont("Helvetica", 11)
            p.setFillColorRGB(0, 0, 0)

    return y_position


def total_section(p, y_position,data):
    if y_position <= 30:
        p.showPage()
        header_section(p=p)
        y_position = 720

    p.setFont("Helvetica", 9)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(20, y_position - 10, "________________________________________________________________________"
                                      "_______________________________________")

    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y_position - 25, "Total")

    # p.drawString(align_x(base_x=380, float_num=data['total_discounted_price']),
    #              y_position - 25,str(data['total_discounted_price']))
    # p.drawString(align_x(base_x=445, float_num=data['total_gst_amount']), y_position - 25,
    #              str(data['total_gst_amount']))

    p.drawString(align_x(base_x=515, float_num=data['total_discounted_price']),
                 y_position - 25,str(data['total_discounted_price']))

    p.setFont("Helvetica", 9)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(20, y_position - 30, "________________________________________________________________________"
                                      "_______________________________________")
    return y_position - 30


def footer_section(p, y_position, data):
    if y_position <= 120:
        p.showPage()
        header_section(p=p)
        y_position = 720

    p.setFillColorRGB(0, 0, 0)

    # Set the font to Arial
    p.setFont("Helvetica-Bold", 10)

    # Draw the text with the Rupee symbol
    p.drawString(40, y_position - 30, f"Description")

    p.setFont("Helvetica", 10)
    p.drawString(40, y_position - 50, f"Generated by {data['generated_by']}")

    p.drawString(300, y_position - 30, "Sub Total")
    p.drawString(470, y_position - 30, str(data['total_discounted_price']))

    p.drawString(300, y_position - 45, f"INVOICE DISCOUNT@{data['discount_percentage']}%")
    p.drawString(470, y_position - 45, "- "+str(data['invoice_discount_amount']))

    p.setFont("Helvetica", 10)
    p.drawString(300, y_position - 60, f"SGST@{data['sgst_rate']}%")
    p.drawString(470, y_position - 60, str(data['sgst']))

    p.drawString(300, y_position - 75, f"CGST@{data['cgst_rate']}%")
    p.drawString(470, y_position - 75, str(data['cgst']))

    p.drawString(300, y_position - 90, f"IGST@{data['igst_rate']}%")
    p.drawString(470, y_position - 90, str(data['igst']))




    x_start = 290
    y_start = y_position - 117
    width = 220
    height = 20

    p.setFillColorRGB(1, 0, 0)

    p.rect(x_start, y_start, width, height, fill=True, stroke=False)

    p.setFont("Helvetica-Bold", 11)
    p.setFillColorRGB(1, 1, 1)

    p.drawString(300, y_position - 112, "Total")
    p.drawString(470, y_position - 112, str(data['grand_total']))

    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica", 12)
    p.drawString(230, y_position - 150, "This is computer generated bill")


@api_view(['GET'])
@permission_classes([AllowAny])
def tax_invoice(request, pk=None):
    if request.method == 'GET':
        try:
            retailer_main_order = RetailerMainOrders.objects.get(id=pk)

            retailer = UserBase.objects.get(id=retailer_main_order.retailer_id)
            gst = GST.objects.get(id=1)
            if retailer.gst[:2] == "29":
                cgst = gst.cgst
                sgst = gst.sgst
                igst = 0
            else:
                cgst = 0
                sgst = 0
                igst = gst.igst
            buffer = BytesIO()
            p = canvas.Canvas(buffer)

            header_section(p=p)

            invoice_section(p=p, retailer_main_order=retailer_main_order, retailer=retailer)
            table_header_section(p=p, retailer_main_order=retailer_main_order)
            y_position = 640
            invoice_data = generate_invoice(retailer_main_order)
            print(invoice_data, '=============main order data')
            y_position = table_data_section(p=p, y_position=y_position,data=invoice_data.get('products',[]))
            y_position = total_section(p=p, y_position=y_position, data=invoice_data.get('totals',{}))
            footer_section(p=p, y_position=y_position,data=invoice_data.get('totals',{}))
            p.showPage()
            p.save()
            buffer.seek(0)
            # return HttpResponse(buffer.read(), content_type='application/pdf')
            file_name = f"tax_invoice_{retailer_main_order.id}.pdf"

            # Create a FileResponse with the PDF content
            response = FileResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'

            buffer.seek(0)
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# =======================pdf tax invoice short===========
# <editor-fold desc="pdf report tax invoice with barcode ">
import os
from io import BytesIO
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from django.conf import settings
import fitz  # PyMuPDF


def generate_receipt_pdf(request, pk):
    try:
        retailer_main_order = get_object_or_404(RetailerMainOrders, id=pk)
        main_data = generate_invoice(retailer_main_order)

        # Create buffer and set up page size
        buffer = BytesIO()
        width = 60 * mm  # Slightly wider for better layout
        height = 150 * mm
        new_margin = -3 * mm

        p = canvas.Canvas(buffer, pagesize=(width, height))

        # Load the logo image
        image_path = os.path.join(settings.STATIC_DIR, 'logo.png')

        # Calculate image position
        image_width = 30 * mm
        image_height = (image_width * 100) / 100  # Adjust this ratio as necessary
        image_x = (width - image_width) / 2
        image_y = height - image_height - new_margin

        # Draw the logo image
        p.drawImage(image_path, image_x, image_y, width=image_width, height=image_height)

        # Starting position from top
        y = image_y - 0.001 * mm

        def draw_dotted_line(y_pos):
            p.setDash(1, 2)  # Dotted line pattern
            p.line(0, y_pos, width, y_pos)
            p.setDash()  # Reset to solid line
            return y_pos - 2 * mm

        def draw_wrapped_text(p, text, x, y, max_width, font_name="Helvetica", font_size=8, padding=0, margin=0):
            p.setFont(font_name, font_size)
            words = text.split(' ')
            line = ''
            # Adjust y for the margin
            y -= margin

            # Iterate through each word in the text
            for word in words:
                # Test the current line with the next word
                test_line = line + (word if not line else ' ' + word)
                if p.stringWidth(test_line, font_name, font_size) < max_width - 2 * padding:  # Account for padding
                    line = test_line  # Add the word to the current line
                else:
                    # Draw the current line and reset for the new line
                    p.drawString(x + padding, y, line)  # Adjust x for padding
                    y -= font_size + 2  # Move down for the next line (adjust space as needed)
                    line = word  # Start new line with the current word

            # Draw any remaining text in the last line
            if line:
                p.drawString(x + padding, y, line)  # Adjust x for padding

        # Company details
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width / 2, y, 'MAGNETA ICECREAM')
        y -= 6 * mm
        p.setFont("Helvetica", 8)
        p.drawCentredString(width / 2, y, 'SHASHI SIDNAL FOODS PVT LTD')
        y -= 4 * mm
        p.drawCentredString(width / 2, y, 'MM EXTENSION, MAHANTESH NAGAR,')
        y -= 4 * mm
        p.drawCentredString(width / 2, y, 'BELGAVI')

        # Draw dotted line after header
        y -= 3 * mm
        y = draw_dotted_line(y)
        y -= 1.5 * mm

        # Tax Invoice header
        y -= 2 * mm
        p.setFont("Helvetica-Bold", 10)
        p.drawCentredString(width / 2, y, "TAX INVOICE")
        y -= 5 * mm
        p.drawCentredString(width / 2, y, f"#{retailer_main_order.order_number}")

        # Details section
        left_col = 1 * mm
        right_col = 30 * mm
        y -= 1 * mm
        p.setFont("Helvetica", 8)

        # SubTotal
        y -= 5 * mm
        p.drawString(left_col, y, "SubTotal")
        p.drawString(right_col - 5 * mm, y, ":")
        p.drawString(right_col, y, f"{main_data['totals']['grand_total']}")

        # Prepare the invoice items
        invoice_items = [
            {'label': f"DISCOUNT {main_data['totals']['discount_percentage']}%",
             'amount': main_data['totals']['invoice_discounted_amount']},
            {'label': f"SGST {main_data['totals']['sgst_rate']}%", 'amount': main_data['totals']['sgst']},
            {'label': f"CGST {main_data['totals']['cgst_rate']}%", 'amount': main_data['totals']['cgst']},
            {'label': f"GST {main_data['totals']['igst_rate']}%", 'amount': main_data['totals']['igst']},
        ]

        # Filter out items with amount 0
        filtered_items = [item for item in invoice_items if item['amount'] > 0]

        # Draw the items dynamically
        for item in filtered_items:
            y -= 5 * mm
            p.drawString(left_col, y, item['label'])
            p.drawString(right_col - 5 * mm, y, ":")
            p.drawString(right_col, y, f"{item['amount']}")

        # Date & Time
        y -= 5 * mm
        p.drawString(left_col, y, "Date & Time")
        p.drawString(right_col - 5 * mm, y, ":")
        date_str = retailer_main_order.created.strftime("%d/%m/%Y")
        time_str = retailer_main_order.created.strftime("%I:%M %p")
        p.drawString(right_col, y, date_str)
        y -= 4 * mm
        p.drawString(right_col, y, time_str)

        # Generated by
        y -= 4 * mm
        p.drawString(left_col, y, "Generated by")
        p.drawString(right_col - 5 * mm, y, ":")
        p.drawString(right_col, y, retailer_main_order.distributor.first_name)


        # # Decrease font size for user ID
        p.setFont("Helvetica", 6)  # Smaller font size for user ID
        user_id_text = f"({retailer_main_order.distributor.user_id})"
        y -= 1 * mm  # Move down for the user ID

        # # Use the draw_wrapped_text function to handle wrapping
        draw_wrapped_text(p, user_id_text, right_col, y, max_width=0.2 * mm, font_name="Helvetica", font_size=6, padding=2,margin=1)


        # QR Code
        y -= 32 * mm  # Adjust space before the QR code

        # Get the base URL dynamically from the request
        base_url = f"{request.scheme}://{request.get_host()}"
        order_id = retailer_main_order.id
        dynamic_url = f"{base_url}/distributors/retailer_order/{order_id}/"

        # Create the QR data string
        qr_data = dynamic_url  # Just the URL for better scanning
        qr_code = QrCodeWidget(qr_data)
        qr_code.barWidth = 30 * mm
        qr_code.barHeight = 30 * mm
        qr_code.barLevel = 'M'
        d = Drawing(30 * mm, 30 * mm)
        d.add(qr_code)
        qr_x = (width - 30 * mm) / 2  # Center the QR code
        renderPDF.draw(d, p, qr_x, y)

        # Add "Scan for invoice" text below the QR code
        y -= 2 * mm  # Move down after the QR code
        p.setFont("Helvetica", 8)
        p.drawCentredString(width / 2, y, "Scan for invoice")

        # Dotted line after footer
        y -= 1.8 * mm
        y = draw_dotted_line(y)
        y -= 1.5 * mm

        # Contact information
        p.setFont("Helvetica", 7)
        p.drawCentredString(width / 2, y, f"Contact us: {retailer_main_order.distributor.phone_number}")
        y -= 3 * mm
        p.drawCentredString(width / 2, y, f"{retailer_main_order.distributor.email}")
        y -= 3 * mm
        p.drawCentredString(width / 2, y, "www.magnetaicecream.in")

        # Close and return PDF
        p.showPage()
        p.save()
        pdf = buffer.getvalue()
        buffer.close()

        # Create a buffer to store the image
        img_buffer = BytesIO()

        # Convert PDF to image using PyMuPDF
        pdf_document = fitz.open(stream=pdf, filetype="pdf")
        page = pdf_document[0]  # Get the first page

        # Set zoom for higher resolution (e.g., 2.0 means 200%)
        zoom = 3.0  # Adjust for desired quality
        matrix = fitz.Matrix(zoom, zoom)  # Apply zoom to both x and y axes
        pix = page.get_pixmap(matrix=matrix)  # Render page to an image with specified zoom

        # Save the image to the buffer
        img_buffer.write(pix.tobytes("png"))  # Convert to PNG format
        img_buffer.seek(0)  # Reset buffer pointer

        # Create the HTTP response for the image
        response = HttpResponse(content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="receipt_{retailer_main_order.order_number}.png"'
        response.write(img_buffer.getvalue())
        return response

    except RetailerMainOrders.DoesNotExist:
        raise Http404("Order not found")
    except Exception as e:
        return HttpResponse(f"Error generating receipt: {str(e)}", status=500)
# </editor-fold>


# <editor-fold desc="old">
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
#
# class DistributorStatsAPIView(APIView):
#     permission_classes = []
#     authentication_classes = [JWTAuthentication]
#
#     def get(self, request, *args, **kwargs):
#         user = request.user
#
#         # Ensure the user is a distributor
#         if not hasattr(user, 'is_distributor') or not user.is_distributor:
#             return Response({"detail": "User is not a distributor"}, status=403)
#
#         # Retrieve distributor-specific stats
#         stats = {
#             "total_amount": 0.0,
#             "total_pending_amount": 0.0,
#             "total_receivable_amount": 0.0,
#             "target_amount": 0.0,
#             "today_bills_count": 0.0,
#             "current_month_target_amount": 0.0,
#             "previous_month_target_amount": 0.0,
#         }
#
#         # Get all orders for this distributor
#         orders = RetailerMainOrders.objects.filter(distributor=user)
#         # Calculate total pending and bill amounts for the distributor
#         if orders.exists():
#             t_amount=orders.first().total_bill_amount()
#             p_amount=orders.first().total_pending_amount()
#             r_amount=t_amount-p_amount
#             # Calculate the total pending amount
#             stats["total_amount"] +=orders.first().total_bill_amount()
#             stats["total_pending_amount"] += orders.first().total_pending_amount()
#             stats["total_receivable_amount"] = r_amount
#
#             # Ensure t_amount is defined with a valid number
#             # t_amount = t_amount if 't_amount' in locals() and t_amount else 0
#             stats["target_amount"]=user.total_target_amount
#
#             # stats["target_amount"] = (t_amount/user.user_target_amounts.target_amount)/100
#             stats["total_bills"] = orders.first().total_order_count()
#             stats["current_month_target_amount"] = {
#                 "target": round(int(user.current_month_target_amount)),
#                 "amount": round(int(user.current_month_achieved_amount)),
#                 "status": (str(round((user.current_month_achieved_amount / user.current_month_target_amount) * 100)) + '%' if user.current_month_target_amount > 0 else '0')
#             }
#             stats["previous_month_target_amount"] = {
#                 "target": round(int(user.previous_month_target_amount)),
#                 "amount": round(int(user.previous_month_achieved_amount)),
#                 "status": (str(round((user.previous_month_achieved_amount / user.previous_month_target_amount) * 100)) + '%' if user.previous_month_target_amount > 0 else '0')
#             }
#         return Response(stats, status=200)
# # </editor-fold>

#
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

def get_distributor_amounts(distributor):
    """
    Calculate total bill amount, current month achieved amount, and previous month achieved amount
    for a specific retailer, excluding cancelled orders.

    Args:
        distributor: Distributor object

    Returns:
        dict: Contains current_month_amount and previous_month_amount
    """
    # Get current date and first day of current month
    today = timezone.now()
    current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Calculate previous month's start and end dates
    previous_month_end = current_month_start - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)

    # Base query for active orders
    base_query = RetailerMainOrders.objects.filter(distributor=distributor).exclude(payment_status="cancelled")

    # Aggregate current and previous month amounts
    current_month_amount = base_query.filter(created__gte=current_month_start).aggregate(total=Sum('grand_total'))['total'] or 0
    previous_month_amount = base_query.filter(created__gte=previous_month_start, created__lte=previous_month_end).aggregate(total=Sum('grand_total'))['total'] or 0

    return {
        'current_month_amount': current_month_amount,
        'previous_month_amount': previous_month_amount
    }

class DistributorStatsAPIView(APIView):
    permission_classes = []
    authentication_classes = [JWTAuthentication]


    def get(self, request, *args, **kwargs):
        user = request.user

        # Ensure the user is a distributor
        if not hasattr(user, 'is_distributor') or not user.is_distributor:
            return Response({"detail": "User is not a distributor"}, status=403)

        # Retrieve distributor-specific stats
        stats = {
            "total_amount": 0.0,
            "total_pending_amount": 0.0,
            "total_receivable_amount": 0.0,
            "target_amount": 0.0,
            "today_bills_count": 0.0,
            "current_month_target_amount": 0.0,
            "previous_month_target_amount": 0.0,
        }

        # Get all orders for this distributor
        orders = RetailerMainOrders.objects.filter(distributor=user)
        # Calculate total pending and bill amounts for the distributor
        if orders.exists():
            t_amount=orders.first().total_bill_amount()
            p_amount=orders.first().total_pending_amount()
            r_amount=t_amount-p_amount
            # Calculate the total pending amount
            stats["total_amount"] +=orders.first().total_bill_amount()
            stats["total_pending_amount"] += orders.first().total_pending_amount()
            stats["total_receivable_amount"] = r_amount


            # amount collectds
            achieved_amount=get_distributor_amounts(orders.first().distributor)

            current_month_collected_amount=achieved_amount['current_month_amount'] or 0
            previous_month_collected_amount=achieved_amount['previous_month_amount'] or 0

            # # Ensure t_amount is defined with a valid number
            # t_amount = t_amount if 't_amount' in locals() and t_amount else 0

            # stats["target_amount"] = (t_amount/user.user_target_amounts.target_amount)/100
            stats["total_bills"] = orders.first().total_order_count()

            stats["current_month_target_amount"] = {
                "target": round(int(user.current_month_target_amount)),
                "amount": round(int(current_month_collected_amount)),
                "status": (str(round((current_month_collected_amount / user.current_month_target_amount) * 100)) + '%'
                           if user.current_month_target_amount > 0 else '0')
            }
            stats["previous_month_target_amount"] = {
                "target": round(int(user.previous_month_target_amount)),
                "amount": round(int(previous_month_collected_amount)),
                "status": (str(round((previous_month_collected_amount / user.previous_month_target_amount) * 100)) + '%'
                           if user.previous_month_target_amount > 0 else '0')
            }
        return Response(stats, status=200)



