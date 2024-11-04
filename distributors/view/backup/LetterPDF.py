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
import pandas as pd

from accounts.CustomPermissions import IsDistributorPermission

logger = logging.getLogger("magneta_logger")


def header_section(p):
    p.setFont("Helvetica-Bold", 13)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(20, 800, "MOTOCROSS INDIA")
    # p.drawString(20, 785, "MAGNETA")
    p.setFillColorRGB(1, 0, 0)

    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica", 9)
    p.drawString(20, 770, "Motocross India Private Limited")
    p.drawString(20, 759, "3rd Main, Club Road, Basavnagar")
    p.drawString(20, 748, "Belagavi - 590001")
    p.drawString(20, 737, "www.motocrossindia.in | 8888222992")
    # p.drawString(20, 726, "www.magnetaicecream.in")

    image_path = os.path.join(settings.STATIC_DIR, 'download mooooo.png')
    p.drawImage(image_path, 350, 740, width=200, height=60)

    # watermark_logo = os.path.join(settings.STATIC_DIR, 'watermark_logo.png')
    # p.drawImage(watermark_logo, 50, 150, width=500, height=500)

    p.setFillColorRGB(0, 0, 0)
    p.drawString(20, 720, "________________________________________________________________________"
                          "_______________________________________")


def invoice_section(p, name, mobile, invoice_no, date):
    p.setFont("Helvetica-Bold", 11)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(260, 705, "Tax Invoice")
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(20, 695, "Bill to,")
    p.drawString(20, 685, f"Name : {name}")
    p.drawString(485, 695, f"Invoice No: ")
    p.drawString(485, 685, f"{invoice_no}")
    p.drawString(20, 674, f"{mobile}")
    # p.drawString(20, 663,
    #              str(retailer.gst) + " | State name: " + str(retailer.state) + ", Code: " + str(retailer.gst[:2]))

    p.setFont("Helvetica", 10)
    p.drawString(485, 663, f"Date: {date}")


def table_header_section(p):
    x_start = 20
    y_start = 638
    width = 555
    height = 20

    p.setFillColorRGB(0, 0, 0)

    p.rect(x_start, y_start, width, height, fill=True, stroke=False)

    p.setFont("Helvetica-Bold", 11)
    p.setFillColorRGB(1, 1, 1)
    p.drawString(30, 645, "SL no")
    p.drawString(80, 645, "Particulars")
    # p.drawString(295, 645, "Qty")
    p.drawString(320, 645, "Amount")
    p.drawString(380, 645, "GST %")
    p.drawString(420, 645, "GST Amount")
    # p.setFont("Helvetica-Bold", 8)
    # p.drawString(482, 645, f"{retailer_main_order.gst_rate}%")
    p.setFont("Helvetica-Bold", 11)
    p.drawString(495, 645, "Total Amount")


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


def table_data_section(pk, p, y_position, slno, parti, amt, gstp, gsta, ta):
    retailer_orders = RetailerOrders.objects.filter(retailer_main_order=pk)
    # retailer_orders = RetailerOrders.objects.filter(retailer_main_order=pk).order_by('-id')
    p.setFont("Helvetica", 11)
    p.setFillColorRGB(0, 0, 0)
    y_position = y_position
    for index, order in enumerate(retailer_orders, start=1):
        y_position -= 20

        p.drawString(30, y_position, str(1))
        p.drawString(80, y_position, parti)
        # p.drawString(align_x(base_x=270, float_num=order.quantity), y_position, str(order.quantity))
        p.drawString(320, y_position, str(amt))

        p.drawString(380, y_position, gstp)

        p.drawString(420, y_position,str(round(gsta, 2)))

        p.drawString(495, y_position, str(round(ta, 2)))

        if y_position <= 30:
            p.showPage()
            header_section(p=p)
            y_position = 720
            p.setFont("Helvetica", 11)
            p.setFillColorRGB(0, 0, 0)

    return y_position


def total_section(p, y_position, total):
    if y_position <= 30:
        p.showPage()
        header_section(p=p)
        y_position = 720

    p.setFont("Helvetica", 9)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(20, y_position - 45, "________________________________________________________________________"
                                      "_______________________________________")

    p.setFont("Helvetica-Bold", 11)
    p.drawString(80, y_position - 65, "Total")
    # p.drawString(align_x(base_x=380, float_num=retailer_main_order.sub_total), y_position - 25,
    #              str(retailer_main_order.sub_total))
    # p.drawString(align_x(base_x=440, float_num=retailer_main_order.gst), y_position - 25,
    #              str(retailer_main_order.gst))
    p.drawString(495, y_position - 65, str(round(total, 2)))

    p.setFont("Helvetica", 9)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(20, y_position - 70, "________________________________________________________________________"
                                      "_______________________________________")
    return y_position - 70


def footer_section(p, y_position, retailer_main_order):
    if y_position <= 120:
        p.showPage()
        header_section(p=p)
        y_position = 720

    p.setFillColorRGB(0, 0, 0)

    # Set the font to Arial
    p.setFont("Helvetica-Bold", 10)

    # Draw the text with the Rupee symbol
    p.drawString(40, y_position - 30, f"Bank Details")

    p.setFont("Helvetica", 10)
    p.drawString(40, y_position - 50, f"Motocross India Private Limited")
    p.drawString(40, y_position - 65, f"A/c no: 241705001140")
    p.drawString(40, y_position - 80, f"Bank: ICICI BANK LIMITED")
    p.drawString(40, y_position - 95, f"IFSC Code: ICIC0002417")
    p.setFont("Helvetica", 7)
    p.drawString(200, y_position - 410, f"This is Computer generated quotation and don't need any Signature.")

    # p.drawString(300, y_position - 30, "Sub Total")
    # p.drawString(470, y_position - 30, str(retailer_main_order.sub_total))
    #
    # p.setFont("Helvetica", 10)
    # p.drawString(300, y_position - 50, f"SGST@{retailer_main_order.SGST_rate}%")
    # p.drawString(470, y_position - 50, str(round(retailer_main_order.SGST, 2)))
    #
    # p.drawString(300, y_position - 70, f"CGST@{retailer_main_order.CGST_rate}%")
    # p.drawString(470, y_position - 70, str(round(retailer_main_order.CGST, 2)))
    #
    # p.drawString(300, y_position - 90, f"IGST@{retailer_main_order.IGST_rate}%")
    # p.drawString(470, y_position - 90, str(round(retailer_main_order.IGST, 2)))

    # x_start = 290
    # y_start = y_position - 117
    # width = 220
    # height = 20
    #
    # p.setFillColorRGB(1, 0, 0)
    #
    # p.rect(x_start, y_start, width, height, fill=True, stroke=False)
    #
    # p.setFont("Helvetica-Bold", 11)
    # p.setFillColorRGB(1, 1, 1)
    #
    # p.drawString(300, y_position - 112, "Total")
    # p.drawString(470, y_position - 112, str(round(retailer_main_order.grand_total, 2)))
    #
    # p.setFillColorRGB(0, 0, 0)
    # p.setFont("Helvetica", 10)
    # p.drawString(290, y_position - 125, f"Generated by {retailer_main_order.distributor}")


@api_view(['GET'])
@permission_classes([AllowAny])
def letter_pdf_temp(request):
    if request.method == 'GET':
        try:

            buffer = BytesIO()
            p = canvas.Canvas(buffer)

            header_section(p=p)

            p.setFillColorRGB(0, 0, 0)
            p.setFont("Helvetica", 11)
            p.drawString(30, 690, "The Manager")
            p.drawString(30, 676, "BSNL Office")
            p.drawString(30, 664, "Railway Station,")
            p.drawString(30, 652, "Camp Belagavi-590001")
            p.drawString(30, 600, "Subject: Request for Replacement of Lost Company SIM Card")
            p.drawString(30, 580, "Dear Sir/Madam,")

            p.drawString(30, 560, "I hope this letter finds you well. I am writing to inform you that our company, Motocross India Pvt.")
            p.drawString(30, 548, "Ltd., has recently lost one of our BSNL SIM cards. The details of the SIM card are as follows:")

            p.drawString(30, 508, "- Company Name: Motocross India Private Limited")
            p.drawString(30, 496, "- SIM Number: 9141022283")
            p.drawString(30, 482, "- Employee Authorized for Collection: Abraj Hukkeri")


            p.drawString(30, 450, "We kindly request your assistance in issuing a replacement SIM card for the above mentioned")
            p.drawString(30, 438, "number. As per company policy and for security reasons, we authorize Mr. Abraj Hukkeri, our")
            p.drawString(30, 426, "employee, to collect the replacement SIM card on our behalf. Enclosed with this letter are copies of")
            p.drawString(30, 414, "Mr. Hukkeri's identification and a letter of authorization from our company.")

            p.drawString(30, 380, "Please process this request at your earliest convenience and provide Mr. Hukkeri with the")
            p.drawString(30, 368, "replacement SIM card.")

            p.drawString(30, 300, "Thank you for your prompt attention to this matter.")

            p.drawString(30, 250, "Yours sincerely,")
            p.drawString(30, 150, "Karan Javali.")
            p.drawString(30, 138, "Founder & CEO")

            p.showPage()
            p.save()
            buffer.seek(0)
            return HttpResponse(buffer.read(), content_type='application/pdf')
            # file_name = f"tax_invoice_{retailer_main_order.id}.pdf"
            #
            # # Create a FileResponse with the PDF content
            # response = FileResponse(buffer, content_type='application/pdf')
            # response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            #
            # buffer.seek(0)
            # return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
