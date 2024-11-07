# views.py
import calendar
from datetime import datetime

import django_filters
from django import forms
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import UserTargetAmount, UserBase, Role
from accounts.serializers.AccountsUserTargetAmount import UserTargetAmountSerializer, UsersSerializer


class DateInput(forms.DateInput):
    input_type = 'date'  # This will use the HTML5 date picker

class UserTargetAmountFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(field_name='user__id', lookup_expr='exact')
    status = django_filters.ChoiceFilter(choices=UserTargetAmount.STATUS_CHOICES)
    start_date = django_filters.DateFilter(field_name='start_date', lookup_expr='gte', widget=DateInput(attrs={'class': 'form-control'}))
    end_date = django_filters.DateFilter(field_name='end_date', lookup_expr='lte', widget=DateInput(attrs={'class': 'form-control'}))
    target_amount = django_filters.NumberFilter(field_name='target_amount', lookup_expr='exact')
    achieved_amount = django_filters.NumberFilter(field_name='achieved_amount', lookup_expr='gte')
    month_year = django_filters.CharFilter(method='filter_month_year')

    class Meta:
        model = UserTargetAmount
        fields = ['user', 'status', 'start_date', 'end_date', 'target_amount', 'achieved_amount','month_year']

    def filter_month_year(self, queryset, name, value):
        try:
            # Parse month-year string (e.g., "2-2024")
            month, year = map(int, value.split('-'))

            # Calculate start and end dates for the given month
            start_date = datetime(year, month, 1).date()
            _, last_day = calendar.monthrange(year, month)
            end_date = datetime(year, month, last_day).date()

            # Filter queryset for the month range
            return queryset.filter(
                start_date__gte=start_date,
                end_date__lte=end_date
            )
        except (ValueError, TypeError):
            return queryset.none()  # Return empty queryset if invalid format
class UserTargetAmountViewSet(viewsets.ModelViewSet):
    queryset = UserTargetAmount.objects.all()
    serializer_class = UserTargetAmountSerializer
    authentication_classes = [JWTAuthentication]

    # Add the filter backend and filter class
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserTargetAmountFilter

    def get_queryset(self):
        return UserTargetAmount.objects.all().order_by('-start_date')





class UsersViewSet(viewsets.ModelViewSet):
    queryset = UserBase.objects.all()
    serializer_class = UsersSerializer
    authentication_classes = [JWTAuthentication]


    @action(detail=False, methods=['get'])
    def retailer(self, request):
        """
        Custom action for retailer role.
        """
        retailers = UserBase.objects.filter(is_retailer=True)
        serializer = self.get_serializer(retailers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def sales(self, request):
        """
        Custom action for retrieving users with the 'sales' role,
        excluding those with a pending target amount status.
        """
        # Fetch the Role instance for "sales"
        sales_role = get_object_or_404(Role, role="sales")

        # Filter users with the 'sales' role and exclude those with pending target amounts
        sales_users = UserBase.objects.filter(
            role=sales_role
        ).exclude(user_target_amounts__status='pending')

        # Serialize and return the data
        serializer = self.get_serializer(sales_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
