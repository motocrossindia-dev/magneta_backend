from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import UserBase
from sales.models import distributor_sales, salesPersonCashInHand, transactionFromSalesToDistributor
from sales.serializers.cashInHandSerializer import GetCashInHandSerializer, GetCashInHandWithTodaysCollectionSerializer
from sales.serializers.distributor_salesSerializer import DistributorSalesSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_sales_by_distributor(request):
    try:
        print(request.user)
        if request.user:
            if not request.user.is_distributor:
                return Response(data={"msg": "Only distributors can access this information"},
                                status=status.HTTP_403_FORBIDDEN)
            sales = distributor_sales.objects.filter(distributor_id=request.user.id)
            if not sales.exists():
                return Response(data={"msg": "No sales records found for the given distributor."},
                                status=status.HTTP_404_NOT_FOUND)

            serializer = DistributorSalesSerializer(sales, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data={"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Cash in Hand of Sales Person

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def getCashInHand(request):
    if request.user.is_distributor and request.user.role.role == 'sales':
        try:
            transactions = salesPersonCashInHand.objects.filter(sales_person=request.user).first()
            serializer = GetCashInHandWithTodaysCollectionSerializer(transactions)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print("error in getCashInhand : ", e)
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    elif request.user.is_distributor and not request.user.role.role == 'sales':
        try:

            sales = distributor_sales.objects.filter(distributor=request.user)
            sales_persons_list = sales.values_list('sales_person', flat=True)
            sales_persons = salesPersonCashInHand.objects.filter(sales_person__in=sales_persons_list)
            serializer = GetCashInHandSerializer(sales_persons, many=True)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print("error in getCashInhand : ", e)
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(data={"error": "Only sales can access this information"}, status=status.HTTP_403_FORBIDDEN)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def transferCashInHand(request):
    try:
        sales_person_id = request.data.get('sales_person_id')
        try:
            salesPerson=UserBase.objects.get(id=sales_person_id)
            print(salesPerson, "salesPerson")
            transactions = salesPersonCashInHand.objects.get(sales_person=salesPerson)
        except salesPersonCashInHand.DoesNotExist:
            return Response(data={"error": "Doesnt exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        print(transactions.cash_in_hand)
        if transactions.cash_in_hand < float(request.data.get('amount')):
            return Response(data={"error": "Insufficient cash in hand"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            transactions.cash_in_hand = float(transactions.cash_in_hand) - float(request.data.get('amount'))
            transactions.amount_transferred_to_distributer = float(transactions.amount_transferred_to_distributer) + float(
                request.data.get('amount'))
            transactions.save()
            try:
                transactionFromSalesToDistributor.objects.create(
                    sales_person=transactions.sales_person,
                    distributor=request.user,
                    amount=float(request.data.get('amount')),
                )
            except Exception as e:
                print(e)
            serializer = GetCashInHandSerializer(transactions)
            return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(data={"error": e}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print("error in transferCashInHand : ", e)
        return Response(data={"error": e}, status=status.HTTP_400_BAD_REQUEST)


def get_total_transactions(request):
    try:
        transactions = salesPersonCashInHand.objects.all()
        serializer = GetCashInHandSerializer(transactions, many=True)
        return Response(data={"data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        print("error in get_total_transactions : ", e)
        return Response(data={"error": e}, status=status.HTTP_400_BAD_REQUEST)