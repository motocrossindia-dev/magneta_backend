import logging
import os

import fitz
from django.conf import settings
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import UserBase
from distributors.models import RetailerMainOrders
from distributors.serializers.RetailerMainOrderSerializer import GETretailerMainOrderSerializer
from sales.models import retailerTransactionDetails, salesRetailerTransactions, distributor_sales, \
    salesPersonCashInHand, transactionFromSalesToDistributor
from sales.serializers.transactionFromSalesToDistributorSerializer import transactionFromSalesToDistributorSerializer
from sales.serializers.transactionSerializer import retailerTransactionDetailsSerializer, \
    salesRetailerTransactionsSerializer, GETretailerSerializer

logger = logging.getLogger("magneta_logger")


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def collectMoney(request):
    if request.method == "GET":
        try:
            try:
                retailer = UserBase.objects.filter(is_retailer=True)
                serializer = GETretailerSerializer(retailer, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error("Exception: distributor_orders " + str(e))
                return Response(data={"Exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("error in getTransactions : ", e)
            return Response(data={"error": e}, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            print(request.data)
            retailer_id = request.data.get('retailer_id')
            amount = float(request.data.get('amount'))
            mode_of_payment = request.data.get('mode_of_payment')
            details = request.data.get('details')

            retailer = UserBase.objects.get(pk=retailer_id)
            try:
                distributor = distributor_sales.objects.get(sales_person=request.user).distributor
            except Exception as e:
                print("error in collectMoney : ", e)
                return Response(data={"error": e}, status=status.HTTP_400_BAD_REQUEST)

            try:
                salesRetailerTransactions.objects.create(
                    sales_person=request.user,
                    retailer=retailer,
                    distributor=distributor,
                    transaction_amount=amount,
                    mode_of_payment=mode_of_payment,
                    details=details
                )
                if mode_of_payment == "cash":
                    print(mode_of_payment, "mode_of_payment")
                    print(amount, "amount")
                    try:
                        salesPersonObject, created = salesPersonCashInHand.objects.get_or_create(
                            sales_person=request.user
                        )

                        if created:
                            salesPersonObject.cash_in_hand = amount
                            salesPersonObject.amount_transferred_to_distributer = 0
                            salesPersonObject.total = amount
                            salesPersonObject.save()
                        else:
                            salesPersonObject.cash_in_hand = salesPersonObject.cash_in_hand + amount
                            salesPersonObject.total = salesPersonObject.total + amount
                            salesPersonObject.save()
                    except Exception as e:
                        print("error in collectMoney : ", e)

            except Exception as e:
                print("error in collectMoney : ", e)
                return Response(data={"error": e}, status=status.HTTP_400_BAD_REQUEST)

            try:
                try:
                    transaction = retailerTransactionDetails.objects.get(retailer=retailer)
                    transaction.amount = transaction.amount + amount
                    transaction.totalSaleAmount = transaction.totalSaleAmount + amount

                    transaction.save()
                except Exception as e:
                    print(e, "error")
                    transaction = retailerTransactionDetails.objects.create(
                        retailer=retailer,
                        amount=amount,
                        totalSaleAmount=amount)
                    transaction.amount = amount
                    transaction.totalSaleAmount = amount
                    transaction.save()
                transaction, created = retailerTransactionDetails.objects.get_or_create(retailer=retailer)
                print(amount, "amount")

            except Exception as e:
                print("error in collectMoney1 : ", e)
                return Response(data={"error": e}, status=status.HTTP_400_BAD_REQUEST)
            print(transaction.amount, "transaction.amount")

            return Response(data={"success": "Successfully Collected Money from retailer", "data": transaction.amount},
                            status=status.HTTP_200_OK)
        except Exception as e:
            print("error in collectMoney2 : ", e)
            return Response(data={"error": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def distributeCollectedMoneyToOrders(request):
    try:
        order_id = request.data.get('order_id')
        amount = float(request.data.get('amount'))
        order = RetailerMainOrders.objects.get(pk=order_id)
        order.pending_amount = round(order.pending_amount - amount, 2)
        if order.pending_amount == 0.00 or order.pending_amount < 0.00:
            order.payment_status = "Paid"
            order.mode_of_payment = "cash"
            order.save()

        retailer = retailerTransactionDetails.objects.get(retailer=order.retailer)
        retailer.amount = float(retailer.amount) - amount

        if order.pending_amount < 0.00:
            return Response(data={"error": "Incorrect amount"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            retailer.save()
            order.save()
        serializer = GETretailerMainOrderSerializer(order)
        return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
    except retailerTransactionDetails.DoesNotExist:
        print("error in distributeCollectedMoneyToOrders : DoesNotExist")
        return Response(data={"error": "DoesNotExist"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print("error in distributeCollectedMoneyToOrders : ", e)
        return Response(data={"error": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def getTransactions(request):
    try:
        transactions = retailerTransactionDetails.objects.filter(sales_person=request.user).order_by('-id')[0:500]
        serializer = retailerTransactionDetailsSerializer(transactions, many=True)
        return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        print("error in getTransactions123 : ", e)
        return Response(data={"error": e}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def getSalesTransactions(request):
    try:
        transactions = salesRetailerTransactions.objects.filter(sales_person=request.user).order_by('-id')[0:500]
        # data = salesRetailerTransactionsSerializer(transactions, many=True)
        try:
            transactionSerializer = salesRetailerTransactionsSerializer(transactions, many=True)
            print(transactionSerializer.data, "transactionSerializer.data")
        except Exception as e:
            print(e, "error")
            transactionSerializer.data = []
        return Response(data=transactionSerializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print("error in getTransactions : ", e)
        return Response(data={"error": e}, status=status.HTTP_400_BAD_REQUEST)


def getUnusedAmount(retailer):
    try:
        transaction = retailerTransactionDetails.objects.get(retailer=retailer)
        return transaction.amount
    except retailerTransactionDetails.DoesNotExist:
        print("error in getUnusedAmount : DoesNotExist")
        return 0.00
    except Exception as e:
        print("error in getUnusedAmount : ", e)
        return 0.00

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def getListOfTransactionsFromSalesToDistributor(request):

    try:
        try:
            transactions = transactionFromSalesToDistributor.objects.filter(distributor=request.user).order_by('-id')
        except transactionFromSalesToDistributor.DoesNotExist:
            return Response(data={"error": "No transactions found for this user"}, status=status.HTTP_404_NOT_FOUND)
        serializer = transactionFromSalesToDistributorSerializer(transactions, many=True)
        return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        print("error in getListOfTransactionsFromSalesToDistributor : ", e)
        return Response(data={"error": e}, status=status.HTTP_400_BAD_REQUEST)


# ===============recitrive payament recipts

from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from io import BytesIO
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator


@method_decorator(xframe_options_exempt, name='dispatch')
class SalesRetailerTransactionDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def generate_receipt_pdf(self, transaction_data):
        buffer = BytesIO()

        # Set up constants
        width = 60 * mm
        height = 110 * mm
        margin = 0 * mm
        new_margin = -3 * mm
        content_width = width - (2 * margin)

        # Create the PDF object
        p = canvas.Canvas(buffer, pagesize=(width, height))

        # Load the logo image
        image_path = os.path.join(settings.STATIC_DIR, 'logo.png')

        # Calculate image position
        image_width = 30 * mm  # Adjust the image width as necessary
        image_height = (image_width * 100) / 100  # Assuming the logo has a width:height ratio of 2:3
        image_x = (width - image_width) / 2  # Centered X position
        image_y = height - image_height -new_margin  # Y position

        # Draw the logo image at the calculated position
        p.drawImage(image_path, image_x, image_y, width=image_width, height=image_height)

        # Starting position from top with consistent margin spacing
        y = image_y - 0.001 * mm  # Adjust y position after the image

        def draw_text_centered(text, y_pos, font_name="Helvetica", font_size=12):
            p.setFont(font_name, font_size)
            text_width = p.stringWidth(text, font_name, font_size)
            x = (width - text_width) / 2
            p.drawString(x, y_pos, text)
            return y_pos - (font_size + 1)  # Consistent spacing between lines

        def draw_text_line(left_text, right_text, y_pos, font_name="Helvetica", font_size=10):
            p.setFont(font_name, font_size)
            # Draw left-aligned text
            p.drawString(margin, y_pos, left_text)

            # Calculate aligned colon and right text position
            colon_x = margin + 22 * mm
            p.drawString(colon_x, y_pos, ":")
            p.drawString(colon_x + 2 * mm, y_pos, right_text)
            return y_pos - (font_size + 4)  # Consistent spacing between lines
        def draw_text_line_without(left_text, right_text, y_pos, font_name="Helvetica", font_size=10):
            p.setFont(font_name, font_size)
            # Draw left-aligned text
            p.drawString(margin, y_pos, left_text)

            # Calculate aligned colon and right text position
            colon_x = margin + 22 * mm
            p.drawString(colon_x, y_pos, "")
            p.drawString(colon_x + 2 * mm, y_pos, right_text)
            return y_pos - (font_size + 2)  # Consistent spacing between lines

        def draw_dotted_line(y_pos):
            p.setDash(1, 2)  # Set dotted line pattern
            p.line(margin, y_pos, width - margin, y_pos)
            p.setDash()  # Reset to solid line
            return y_pos - 2 * mm

        # Header
        y = draw_text_centered("MAGNETA ICECREAM", y, "Helvetica-Bold", 14)
        y = draw_text_centered("SHASHI SIDNAL FOODS PVT LTD", y, "Helvetica", 10)
        y = draw_text_centered("LX EXTENSION, MAHANTESH NAG", y, "Helvetica", 8)
        y = draw_text_centered("BELGAVI", y, "Helvetica", 8)


        # Draw dotted line after header
        y -= 0 * mm
        y = draw_dotted_line(y)
        y -= 3.5 * mm

        # Receipt title and transaction ID
        y = draw_text_centered("PAYMENT RECEIPT", y, "Helvetica-Bold", 12)
        y = draw_text_centered(f"#{transaction_data['id']}", y, "Helvetica", 12)

        # Transaction details
        y = draw_text_line("Amount", f"{transaction_data['transaction_amount']:.2f}", y)
        y = draw_text_line("Pay Type", transaction_data['mode_of_payment'].capitalize(), y)
        y = draw_text_line("Payment ID", "NA", y)

        # Format date and time
        created_date = datetime.fromisoformat(transaction_data['created'].replace('Z', '+00:00'))
        date_str = created_date.strftime("%d/%m/%Y")
        time_str = created_date.strftime("%I:%M %p")

        y = draw_text_line("Date", date_str, y)
        y = draw_text_line("Time", time_str, y)

        y -= 0 * mm  # Extra space before collector information

        # Collector information
        name = str(transaction_data.get('sales_person_name', ''))
        name_id = str(transaction_data.get('sales_person', ''))

        # Draw the "Collected by" label and collector's name on separate lines
        y = draw_text_line("Collected by", name, y)
        y -= 0 * mm  # Adjust spacing between name and name_id
        y = draw_text_line_without("", name_id, y)  # Draw name_id on the next line
        y -= 0 * mm  # Extra space before the next section


        # Draw dotted line after title
        y -= 0 * mm
        y = draw_dotted_line(y)
        y -= 2.5 * mm



        # Footer
        footer_spacing = 0.1  # Adjust this to control spacing between footer lines
        y = draw_text_centered(f"Contact us: {transaction_data['distributor']['phone_number']}", y, "Helvetica", 10)
        y -= footer_spacing
        y = draw_text_centered(transaction_data['distributor']['email'], y, "Helvetica", 10)
        y -= footer_spacing
        y = draw_text_centered("www.magnetaicecream.in", y, "Helvetica", 10)
        y -= 0.1 * mm  # Final footer offset for the bottom of the page

        # Save PDF
        p.showPage()
        p.save()

        buffer.seek(0)
        return buffer

    def get(self, request, pk):
        try:
            transaction = salesRetailerTransactions.objects.get(id=pk)
            transaction_data = salesRetailerTransactionsSerializer(transaction).data
            print(transaction_data,'=====data')
            pdf_buffer = self.generate_receipt_pdf(transaction_data)

            # Create a BytesIO stream for the image
            img_buffer = BytesIO()

            # Convert PDF buffer to image using PyMuPDF
            pdf_document = fitz.open(stream=pdf_buffer.getvalue(), filetype="pdf")

            # Check if there are any pages in the PDF document
            if pdf_document.page_count > 0:
                # Get the first page (index 0)
                page = pdf_document[0]

                # Try to render the page to an image with higher quality
                try:
                    # Set zoom for higher resolution (e.g., 2.0 means 200%)
                    zoom = 30.0  # Adjust this for desired quality (1.0 = 100%, 2.0 = 200%, etc.)
                    matrix = fitz.Matrix(zoom, zoom)  # Apply zoom to both x and y axes
                    pix = page.get_pixmap(matrix=matrix)  # Render page to an image with specified zoom

                    # Save the image to the BytesIO buffer
                    img_buffer.write(pix.tobytes("jpg"))  # Convert to PNG format
                    img_buffer.seek(0)  # Reset buffer position to the beginning
                except Exception as pixmap_error:
                    return HttpResponse(f"Error rendering page to image: {pixmap_error}", status=500)

                # Create the HTTP response for the image
                response = HttpResponse(content_type='image/png')
                response['Content-Disposition'] = f'inline; filename="receipt_{pk}.png"'
                response.write(img_buffer.getvalue())

                return response

            # response = FileResponse(
            #     pdf_buffer,
            #     content_type='application/pdf',
            #     filename=f'receipt_{pk}.pdf'
            # )
            # response['Content-Disposition'] = f'inline; filename="receipt_{pk}.pdf"'
            # return response

        except salesRetailerTransactions.DoesNotExist:
            return Response(
                {"error": "Transaction not found"},
                status=status.HTTP_404_NOT_FOUND
            )


# class SalesRetailerTransactionDetailView(generics.RetrieveAPIView):
#     queryset = salesRetailerTransactions.objects.all()
#     serializer_class = salesRetailerTransactionsSerializer
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [JWTAuthentication]