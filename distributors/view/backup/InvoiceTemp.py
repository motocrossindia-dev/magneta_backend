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
def invoice_temp(request, pk=None):
    if request.method == 'GET':
        try:
            data = [
                {"Date": "31-03-2022", "Customer": "Vijay", "Phone Number": "6363170237", "Invoice No": "3103202210",
                 "Particulars": "Sale of two wheeler", "Amount": 84765.63, "GST%": "28%", "GST Amount": 23734.3764,
                 "Total Amount": 108500.0064},
                {"Date": "01-04-2022", "Customer": "Rajesh", "Phone Number": "9980973073", "Invoice No": "104202211",
                 "Particulars": "Sale of two wheeler", "Amount": 84765.63, "GST%": "28%", "GST Amount": 23734.3764,
                 "Total Amount": 108500.0064},
                {"Date": "30-04-2022", "Customer": "Manjunath", "Phone Number": "9591705479",
                 "Invoice No": "3004202201",
                 "Particulars": "Sale of two wheeler", "Amount": 12011.72, "GST%": "28%", "GST Amount": 3363.2816,
                 "Total Amount": 15375.0016},
                {"Date": "30-04-2022", "Customer": "Ramesh", "Phone Number": "7412589635", "Invoice No": "3004202202",
                 "Particulars": "Sale of two wheeler", "Amount": 12011.72, "GST%": "28%", "GST Amount": 3363.2816,
                 "Total Amount": 15375.0016},
                {"Date": "30-04-2022", "Customer": "Vishnu", "Phone Number": "8529634569", "Invoice No": "3004202203",
                 "Particulars": "Sale of two wheeler", "Amount": 12011.72, "GST%": "28%", "GST Amount": 3363.2816,
                 "Total Amount": 15375.0016},
                {"Date": "30-04-2022", "Customer": "Praveen", "Phone Number": "8965412307", "Invoice No": "3004202204",
                 "Particulars": "Sale of two wheeler", "Amount": 12011.72, "GST%": "28%", "GST Amount": 3363.2816,
                 "Total Amount": 15375.0016},
                {"Date": "30-06-2022", "Customer": "Akash", "Phone Number": "8965471230", "Invoice No": "3006202212",
                 "Particulars": "Sale of two wheeler", "Amount": 18984.376, "GST%": "28%", "GST Amount": 5315.62528,
                 "Total Amount": 24300.00128},
                {"Date": "30-06-2022", "Customer": "Onkar", "Phone Number": "9658741230", "Invoice No": "3006202213",
                 "Particulars": "Sale of two wheeler", "Amount": 18984.376, "GST%": "28%", "GST Amount": 5315.62528,
                 "Total Amount": 24300.00128},
                {"Date": "30-06-2022", "Customer": "Rahul", "Phone Number": "9874125631", "Invoice No": "3006202214",
                 "Particulars": "Sale of two wheeler", "Amount": 18984.376, "GST%": "28%", "GST Amount": 5315.62528,
                 "Total Amount": 24300.00128},
                {"Date": "30-06-2022", "Customer": "Pranay", "Phone Number": "6985471235", "Invoice No": "3006202215",
                 "Particulars": "Sale of two wheeler", "Amount": 18984.376, "GST%": "28%", "GST Amount": 5315.62528,
                 "Total Amount": 24300.00128},
                {"Date": "30-06-2022", "Customer": "Karan", "Phone Number": "9658632147", "Invoice No": "3006202216",
                 "Particulars": "Sale of two wheeler", "Amount": 18984.376, "GST%": "28%", "GST Amount": 5315.62528,
                 "Total Amount": 24300.00128},
                {"Date": "31-10-2022", "Customer": "Ikhalas", "Phone Number": "9988225631", "Invoice No": "3110202217",
                 "Particulars": "Sale of two wheeler", "Amount": 23437.5, "GST%": "28%", "GST Amount": 6562.5,
                 "Total Amount": 30000},
                {"Date": "31-10-2022", "Customer": "Shreya", "Phone Number": "8879652314", "Invoice No": "3110202218",
                 "Particulars": "Sale of two wheeler", "Amount": 23437.5, "GST%": "28%", "GST Amount": 6562.5,
                 "Total Amount": 30000},
                {"Date": "31-10-2022", "Customer": "Ganesh", "Phone Number": "9977584632", "Invoice No": "3110202219",
                 "Particulars": "Sale of two wheeler", "Amount": 23437.5, "GST%": "28%", "GST Amount": 6562.5,
                 "Total Amount": 30000},
                {"Date": "31-10-2022", "Customer": "Vishal", "Phone Number": "8965471230", "Invoice No": "3110202220",
                 "Particulars": "Sale of two wheeler", "Amount": 23437.5, "GST%": "28%", "GST Amount": 6562.5,
                 "Total Amount": 30000},
                {"Date": "31-10-2022", "Customer": "Virat", "Phone Number": "9658741562", "Invoice No": "3110202221",
                 "Particulars": "Sale of two wheeler", "Amount": 23437.5, "GST%": "28%", "GST Amount": 6562.5,
                 "Total Amount": 30000},
                {"Date": "30-11-2022", "Customer": "Prathmesh", "Phone Number": "9968321472",
                 "Invoice No": "3011202201",
                 "Particulars": "Service & Labour Charges", "Amount": 1824.58, "GST%": "18%", "GST Amount": 328.4244,
                 "Total Amount": 2153.0044},
                {"Date": "30-11-2022", "Customer": "Shubham", "Phone Number": "9977587705", "Invoice No": "3011202202",
                 "Particulars": "Service & Labour Charges", "Amount": 16050, "GST%": "18%", "GST Amount": 2889,
                 "Total Amount": 18939},
                {"Date": "30-12-2022", "Customer": "krishna", "Phone Number": "8632541756", "Invoice No": "3012202221",
                 "Particulars": "Service & Labour Charges", "Amount": 13628, "GST%": "18%", "GST Amount": 2453.04,
                 "Total Amount": 16081.04},
                {"Date": "31-01-2023", "Customer": "Akshay", "Phone Number": "8965471238", "Invoice No": "3101202322",
                 "Particulars": "Oil Change", "Amount": 447, "GST%": "18%", "GST Amount": 80.46,
                 "Total Amount": 527.46},
                {"Date": "31-01-2023", "Customer": "Piyush", "Phone Number": "9658741230", "Invoice No": "3101202323",
                 "Particulars": "Washing ", "Amount": 447, "GST%": "18%", "GST Amount": 80.46, "Total Amount": 527.46},
                {"Date": "31-01-2023", "Customer": "Arush", "Phone Number": "8896547123", "Invoice No": "3101202324",
                 "Particulars": "Washing ", "Amount": 447, "GST%": "18%", "GST Amount": 80.46, "Total Amount": 527.46},
                {"Date": "31-01-2023", "Customer": "Rohit", "Phone Number": "9864712305", "Invoice No": "3101202325",
                 "Particulars": "Servicing ", "Amount": 447, "GST%": "18%", "GST Amount": 80.46,
                 "Total Amount": 527.46},
                {"Date": "31-01-2023", "Customer": "Abhjeet", "Phone Number": "9874125821", "Invoice No": "3101202326",
                 "Particulars": "Servicing ", "Amount": 447, "GST%": "18%", "GST Amount": 80.46,
                 "Total Amount": 527.46},
                {"Date": "28-02-2023", "Customer": "Abhishek", "Phone Number": "9977448523", "Invoice No": "2802202327",
                 "Particulars": "Engine work (KTM RC 200)", "Amount": 19500, "GST%": "18%", "GST Amount": 3510,
                 "Total Amount": 23010},
                {"Date": "28-02-2023", "Customer": "Arun", "Phone Number": "8874512693", "Invoice No": "2802202328",
                 "Particulars": "Engine work (Activa )", "Amount": 9199.7, "GST%": "18%", "GST Amount": 1655.946,
                 "Total Amount": 10855.646},
                {"Date": "28-02-2023", "Customer": "Raju", "Phone Number": "9987452103", "Invoice No": "2802202329",
                 "Particulars": "Engine work (Splender)", "Amount": 9199.7, "GST%": "18%", "GST Amount": 1655.946,
                 "Total Amount": 10855.646},
                {"Date": "31-03-2023", "Customer": "Bhushan", "Phone Number": "9987452103", "Invoice No": "3103202330",
                 "Particulars": "Sale of two wheeler", "Amount": 15690.1, "GST%": "28%", "GST Amount": 4393.228,
                 "Total Amount": 20083.328},
                {"Date": "01-04-2023", "Customer": "Mukesh", "Phone Number": "7854123058", "Invoice No": "3103202331",
                 "Particulars": "Sale of two wheeler", "Amount": 15690.1, "GST%": "28%", "GST Amount": 4393.228,
                 "Total Amount": 20083.328},
                {"Date": "02-04-2023", "Customer": "Shushanth", "Phone Number": "8965741230",
                 "Invoice No": "3103202332",
                 "Particulars": "Sale of two wheeler", "Amount": 15690.1, "GST%": "28%", "GST Amount": 4393.228,
                 "Total Amount": 20083.328},
                {"Date": "03-04-2023", "Customer": "Mathew", "Phone Number": "6985471230", "Invoice No": "3103202333",
                 "Particulars": "Sale of two wheeler", "Amount": 15690.1, "GST%": "28%", "GST Amount": 4393.228,
                 "Total Amount": 20083.328},
                {"Date": "04-04-2023", "Customer": "Aman", "Phone Number": "9874545867", "Invoice No": "3103202334",
                 "Particulars": "Sale of two wheeler", "Amount": 15690.1, "GST%": "28%", "GST Amount": 4393.228,
                 "Total Amount": 20083.328},
                {"Date": "05-04-2023", "Customer": "Sachin", "Phone Number": "9743257037", "Invoice No": "3103202335",
                 "Particulars": "Sale of two wheeler", "Amount": 15690.1, "GST%": "28%", "GST Amount": 4393.228,
                 "Total Amount": 20083.328}
            ]

            retailer_main_order = RetailerMainOrders.objects.get(id=pk)

            # retailer = UserBase.objects.get(id=retailer_main_order.retailer_id)
            # gst = GST.objects.get(id=1)
            # if retailer.gst[:2] == "29":
            #     cgst = gst.cgst
            #     sgst = gst.sgst
            #     igst = 0
            # else:
            #     cgst = 0
            #     sgst = 0
            #     igst = gst.igst
            buffer = BytesIO()
            p = canvas.Canvas(buffer)


            j = 0
            for i in data:
                header_section(p=p)
                print(i, type(i), i['Date'])
                j += 1
                invoice_section(p=p, name=i['Customer'], mobile=i['Phone Number'], invoice_no=i['Invoice No'], date=i['Date'])

                table_header_section(p=p)

                y_position = 640

                y_position = table_data_section(pk=pk, p=p, y_position=y_position, slno=j, parti=i['Particulars'],
                                                amt=i['Amount'], gstp=i['GST%'], gsta=i['GST Amount'],
                                                ta=i['Total Amount'])

                y_position = total_section(p=p, y_position=y_position, total=i['Total Amount'])

                footer_section(p=p, y_position=y_position, retailer_main_order=retailer_main_order)

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
