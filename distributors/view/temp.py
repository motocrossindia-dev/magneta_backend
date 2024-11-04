import logging
import os

from django.conf import settings
from django.http import HttpResponse
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


def header_section(p):
    p.setFont("Helvetica-Bold", 13)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(20, 800, "SHASHI SIDNAL FOODS PVT LTD")
    p.drawString(20, 785, "MAGNETA")
    p.setFillColorRGB(1, 0, 0)

    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica", 9)
    p.drawString(20, 770, "Survey No. 43/2, Village: Sanikopa,")
    p.drawString(20, 760, "Taluka: Bailhongal,")
    p.drawString(20, 750, "BELAGAVI")
    p.drawString(20, 740, "GSTIN/UIN: 29AAMCS5943H1ZS")
    p.drawString(20, 730, "State Name : Karnataka, Code : 29")
    p.drawString(20, 720, "Phone: 9035054529")
    p.drawString(20, 710, "Email: magnetaicecream@gmail.com")
    p.drawString(20, 700, "GSTIN: 29AAMCS5943H1ZS")
    p.drawString(20, 690, "State Name : Karnataka, Code : 29")

    ####################################################################################################################

    from PIL import Image

    # Open the logo image
    logo_path = os.path.join(settings.STATIC_DIR, 'logo.png')
    logo = Image.open(logo_path)

    # Adjust transparency (alpha channel) of the image
    logo = logo.convert("RGBA")
    logo_with_alpha = Image.new("RGBA", logo.size, (255, 255, 255, 0))
    alpha = 0.1  # Set the transparency level (0.0 to 1.0)
    logo = Image.blend(logo_with_alpha, logo, alpha)

    # Save the adjusted image temporarily
    temp_logo_path = os.path.join(settings.STATIC_DIR, 'temp_logo.png')
    logo.save(temp_logo_path)

    # Draw the adjusted logo image onto the canvas
    p.drawImage(temp_logo_path, 460, 700, width=100, height=100)

    # Clean up temporary image file
    # os.remove(temp_logo_path)

    ####################################################################################################################

    p.setFillColorRGB(1, 0, 0)
    p.drawString(20, 685, "________________________________________________________________________"
                          "_______________________________________")


def invoice_section(p, retailer_main_order, retailer):
    p.setFont("Helvetica-Bold", 11)
    p.setFillColorRGB(1, 0, 0)
    p.drawString(260, 670, "Tax Invoice")

    # p.setFont("Helvetica-Bold", 30)
    # p.setFillColor(colors.lightgrey)  # Light grey color for watermark
    # p.rotate(45)  # Rotate the canvas to draw watermark diagonally
    # p.drawString(150, -320, "WATERMARK")  # Adjust the position of watermark as needed
    # p.rotate(-45)  # Rotate the canvas back to normal

    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(20, 660, "Bill to,")
    p.drawString(485, 660, "Invoice Details,")
    p.drawString(20, 646, str(retailer.first_name) + " " + str(retailer.last_name))
    p.drawString(485, 646, "Invoice No: " + str(retailer_main_order.id))
    p.setFont("Helvetica", 10)
    p.drawString(20, 633, str(retailer.phone_number))
    p.drawString(485, 633, "Date: " + str(retailer_main_order.order_date))


def table_header_section(p, cgst, sgst, igst):
    x_start = 40  # X-coordinate for the starting point of the rectangle
    y_start = 605  # Y-coordinate for the starting point of the rectangle
    width = 510  # Width of the rectangle
    height = 20  # Height of the rectangle

    # Set the fill color to red
    p.setFillColorRGB(1, 0, 0)  # Red color in RGB

    # Draw the rectangle
    p.rect(x_start, y_start, width, height, fill=True, stroke=False)

    p.setFont("Helvetica-Bold", 11)
    p.setFillColorRGB(1, 1, 1)
    p.drawString(50, 611, "#")
    p.drawString(80, 611, "Item Name")
    p.drawString(230, 611, "Quantity")
    p.drawString(300, 611, "Unit")
    p.drawString(340, 611, "Price/Unit")
    p.drawString(410, 611, f"GST({cgst + sgst + igst}%)")
    p.drawString(490, 611, "Amount")


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

            table_header_section(p=p, cgst=cgst, sgst=sgst, igst=igst)

            p.setFont("Helvetica-Bold", 30)
            p.setFillColor(colors.red)  # Light grey color for watermark
            p.rotate(45)  # Rotate the canvas to draw watermark diagonally
            p.drawString(200, 500, "WATERMARK")  # Adjust the position of watermark as needed
            p.rotate(-45)



            retailer_orders = RetailerOrders.objects.filter(retailer_main_order=pk)
            p.setFont("Helvetica", 11)
            p.setFillColorRGB(0, 0, 0)
            y_position = 400
            for index, order in enumerate(retailer_orders, start=1):
                y_position -= 15

                p.drawString(50, y_position, str(index))
                p.drawString(80, y_position, str(order.product_name))
                p.drawString(230, y_position, str(order.quantity))
                p.drawString(300, y_position, "Box")
                p.drawString(340, y_position, str(order.sum))
                p.drawString(410, y_position, str(order.gst))
                p.drawString(490, y_position, str(order.amount))

            p.setFont("Helvetica", 9)
            p.setFillColorRGB(0, 0, 0)
            p.drawString(40, y_position - 10, "________________________________________________________________________"
                                              "______________________________")

            p.setFont("Helvetica-Bold", 10)
            p.drawString(80, y_position - 23, "Total")
            p.drawString(340, y_position - 23, str(retailer_main_order.sub_total))
            p.drawString(410, y_position - 23, str(retailer_main_order.gst))
            p.drawString(490, y_position - 23, str(round(retailer_main_order.grand_total, 2)))

            p.setFont("Helvetica", 9)
            p.setFillColorRGB(0, 0, 0)
            p.drawString(40, y_position - 30, "________________________________________________________________________"
                                              "______________________________")
            p.showPage()  # Move to the next page

            ############################################################################################################

            p.setFont("Helvetica-Bold", 13)
            p.setFillColorRGB(0, 0, 0)
            p.drawString(40, 800, "SHASHI SIDNAL FOODS PVT LTD")
            p.drawString(40, 785, "MAGNETA")
            p.setFillColorRGB(1, 0, 0)

            p.setFillColorRGB(0, 0, 0)
            p.setFont("Helvetica", 9)
            p.drawString(40, 770, "Survey No. 43/2, Village: Sanikopa,")
            p.drawString(40, 760, "Taluka: Bailhongal,")
            p.drawString(40, 750, "BELAGAVI")
            p.drawString(40, 740, "GSTIN/UIN: 29AAMCS5943H1ZS")
            p.drawString(40, 730, "State Name : Karnataka, Code : 29")
            p.drawString(40, 720, "Phone: 9035054529")
            p.drawString(40, 710, "Email: magnetaicecream@gmail.com")
            p.drawString(40, 700, "GSTIN: 29AAMCS5943H1ZS")
            p.drawString(40, 690, "State Name : Karnataka, Code : 29")
            image_path1 = os.path.join(settings.STATIC_DIR, 'logo.png')
            image_path = image_path1  # Replace with the path to your image
            p.drawImage(image_path, 450, 700, width=100, height=100)

            p.setFillColorRGB(1, 0, 0)
            p.drawString(40, 685, "________________________________________________________________________"
                                  "______________________________")

            p.setFillColorRGB(0, 0, 0)
            p.setFont("Helvetica", 9)

            image_path1 = os.path.join(settings.STATIC_DIR, 'logo.png')
            image_path = image_path1  # Replace with the path to your image
            p.drawImage(image_path, 450, 700, width=100, height=100)

            # Set the font to Arial
            p.setFont("Helvetica-Bold", 10)

            # Draw the text with the Rupee symbol
            p.drawString(40, 670, f"Description")

            p.drawString(300, 670, "Sub Total")
            p.drawString(470, 670, str(retailer_main_order.sub_total))

            p.setFont("Helvetica", 10)
            p.drawString(40, 650, "22-credit due to raspberry duet bill")
            p.drawString(300, 650, f"SGST@{sgst}%")
            p.drawString(470, 650, str(round(retailer_main_order.SGST, 2)))

            p.drawString(300, 630, f"CGST@{cgst}%")
            p.drawString(470, 630, str(round(retailer_main_order.CGST, 2)))

            p.drawString(300, 610, f"IGST@{igst}%")
            p.drawString(470, 610, str(round(retailer_main_order.IGST, 2)))

            x_start = 290  # X-coordinate for the starting point of the rectangle
            y_start = 580  # Y-coordinate for the starting point of the rectangle
            width = 220  # Width of the rectangle
            height = 20  # Height of the rectangle

            # Set the fill color to red
            p.setFillColorRGB(1, 0, 0)  # Red color in RGB

            # Draw the rectangle
            p.rect(x_start, y_start, width, height, fill=True, stroke=False)

            p.setFont("Helvetica-Bold", 11)
            p.setFillColorRGB(1, 1, 1)

            p.drawString(300, 586, "Total")
            p.drawString(470, 586, str(round(retailer_main_order.grand_total, 2)))

            p.showPage()
            p.save()
            buffer.seek(0)
            return HttpResponse(buffer.read(), content_type='application/pdf')
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
