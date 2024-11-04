import logging
import os

from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.template.loader import render_to_string
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from bs4 import BeautifulSoup
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import UserBase
from distributors.models import RetailerMainOrders, RetailerOrders
from orders.models import Order, MainOrders, GST

from accounts.CustomPermissions import IsDistributorPermission

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

    image_path = os.path.join(settings.STATIC_ROOT, 'logo.png')
    p.drawImage(image_path, 460, 720, width=100, height=100)

    watermark_logo = os.path.join(settings.STATIC_ROOT, 'watermark_logo.png')
    p.drawImage(watermark_logo, 50, 150, width=500, height=500)

    p.setFillColorRGB(1, 0, 0)
    p.drawString(20, 720, "________________________________________________________________________"
                          "_______________________________________")


def invoice_section(p, retailer_main_order, retailer):
    p.setFont("Helvetica-Bold", 11)
    p.setFillColorRGB(1, 0, 0)
    # p.drawString(260, 705, "Tax Invoice")
    if retailer_main_order.mode_of_payment in ['Credit', 'credit', 'CREDIT']:
        p.drawString(260, 700, "Proforma Invoice")
    else:
        p.drawString(260, 705, "Tax Invoice")
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(20, 695, "Bill to,")
    p.drawString(20, 685, safe_str(retailer.first_name) + " " + safe_str(retailer.last_name))
    p.drawString(485, 695, "Invoice No: ")
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
    p.drawString(295, 645, "Qty")
    p.drawString(338, 645, "Unit")
    p.drawString(387, 645, "Price/Unit")
    p.drawString(460, 645, "GST")
    p.setFont("Helvetica-Bold", 8)
    p.drawString(482, 645, f"{retailer_main_order.gst_rate}%")
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


def table_data_section(pk, p, y_position):
    retailer_orders = RetailerOrders.objects.filter(retailer_main_order=pk)
    # retailer_orders = RetailerOrders.objects.filter(retailer_main_order=pk).order_by('-id')
    p.setFont("Helvetica", 11)
    p.setFillColorRGB(0, 0, 0)
    y_position = y_position
    for index, order in enumerate(retailer_orders, start=1):
        y_position -= 20

        p.drawString(30, y_position, str(index))
        p.drawString(50, y_position, str(order.product_name))
        p.drawString(align_x(base_x=270, float_num=order.quantity), y_position, str(order.quantity))
        p.drawString(340, y_position, f"Box ({order.carton_size})")

        p.drawString(align_x(base_x=380, float_num=order.price_per_carton), y_position, str(order.price_per_carton))

        p.drawString(align_x(base_x=440, float_num=order.gst), y_position, str(order.gst))

        p.drawString(align_x(base_x=515, float_num=order.amount), y_position, str(order.amount))

        if y_position <= 30:
            p.showPage()
            header_section(p=p)
            y_position = 720
            p.setFont("Helvetica", 11)
            p.setFillColorRGB(0, 0, 0)

    return y_position


def total_section(p, y_position, retailer_main_order):
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
    # p.drawString(align_x(base_x=380, float_num=retailer_main_order.sub_total), y_position - 25,
    #              str(retailer_main_order.sub_total))
    p.drawString(align_x(base_x=440, float_num=retailer_main_order.gst), y_position - 25,
                 str(retailer_main_order.gst))
    p.drawString(align_x(base_x=515, float_num=round(retailer_main_order.grand_total, 2)), y_position - 25,
                 str(round(retailer_main_order.grand_total, 2)))

    p.setFont("Helvetica", 9)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(20, y_position - 30, "________________________________________________________________________"
                                      "_______________________________________")
    return y_position - 30


def footer_section(p, y_position, retailer_main_order):
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
    p.drawString(40, y_position - 50, f"Generated by {retailer_main_order.distributor}")

    p.drawString(300, y_position - 30, "Sub Total")
    p.drawString(470, y_position - 30, str(retailer_main_order.sub_total))

    p.setFont("Helvetica", 10)
    p.drawString(300, y_position - 50, f"SGST@{retailer_main_order.SGST_rate}%")
    p.drawString(470, y_position - 50, str(round(retailer_main_order.SGST, 2)))

    p.drawString(300, y_position - 70, f"CGST@{retailer_main_order.CGST_rate}%")
    p.drawString(470, y_position - 70, str(round(retailer_main_order.CGST, 2)))

    p.drawString(300, y_position - 90, f"IGST@{retailer_main_order.IGST_rate}%")
    p.drawString(470, y_position - 90, str(round(retailer_main_order.IGST, 2)))

    x_start = 290
    y_start = y_position - 117
    width = 220
    height = 20

    p.setFillColorRGB(1, 0, 0)

    p.rect(x_start, y_start, width, height, fill=True, stroke=False)

    p.setFont("Helvetica-Bold", 11)
    p.setFillColorRGB(1, 1, 1)

    p.drawString(300, y_position - 112, "Total")
    p.drawString(470, y_position - 112, str(round(retailer_main_order.grand_total, 2)))

    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica", 12)
    p.drawString(230, y_position - 150, "This is computer generated bill")


@api_view(['GET'])
@permission_classes([AllowAny])
def tax_invoice(request, pk=None):
    print("tax_invoice--->1234", pk)
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

            y_position = table_data_section(pk=pk, p=p, y_position=y_position)

            y_position = total_section(p=p, y_position=y_position, retailer_main_order=retailer_main_order)

            footer_section(p=p, y_position=y_position, retailer_main_order=retailer_main_order)

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
