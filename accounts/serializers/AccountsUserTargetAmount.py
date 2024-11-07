# serializers.py
from rest_framework import serializers
from rest_framework import serializers
from datetime import datetime
import calendar

from accounts.models import UserTargetAmount, UserBase


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBase
        fields = ('enterprise_name', 'first_name','id')


class UserTargetAmountSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.first_name')
    user_id = serializers.IntegerField()
    month_year = serializers.CharField(write_only=True)  # Changed to CharField to handle the format

    class Meta:
        model = UserTargetAmount
        fields = ['id', 'user', 'user_id', 'month_year', 'target_amount', 'start_date', 'end_date', 'status']

    def validate_month_year(self, value):
        try:
            # Parse the month-year string like "2-2024"
            month, year = map(int, value.split('-'))
            return datetime(year, month, 1).date()
        except (ValueError, TypeError):
            raise serializers.ValidationError("Invalid month_year format. Use MM-YYYY format (e.g., 2-2024)")

    def validate(self, data):
        if 'target_amount' not in self.initial_data and self.context['request'].method == 'POST':
            raise serializers.ValidationError({"target_amount": "This field is required"})
        return data

    def set_start_end_dates(self, validated_data):
        month_year = validated_data.pop('month_year', None)
        if month_year:
            # month_year is now a date object from validate_month_year
            start_date = month_year
            _, last_day = calendar.monthrange(month_year.year, month_year.month)
            end_date = datetime(month_year.year, month_year.month, last_day).date()
            validated_data['start_date'] = start_date
            validated_data['end_date'] = end_date

    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        self.set_start_end_dates(validated_data)

        return UserTargetAmount.objects.create(
            user_id=user_id,
            start_date=validated_data.get('start_date'),
            end_date=validated_data.get('end_date'),
            target_amount=validated_data.get('target_amount', 0),  # Default to 0 if not provided
            status='pending'  # Set default status
        )

    def update(self, instance, validated_data):
        # First set start and end dates
        self.set_start_end_dates(validated_data)

        # Update fields on the instance
        for attr, value in validated_data.items():
            if attr != 'user_id':  # Skip updating user_id
                setattr(instance, attr, value)

        # Save the instance (this will trigger the save method with timezone handling)
        instance.save()
        return instance
# class UserTargetAmountSerializer(serializers.ModelSerializer):
#     user = serializers.ReadOnlyField(source='user.first_name')
#     user_id = serializers.IntegerField(write_only=True)
#     month_year = serializers.DateField(format='%m-%Y', input_formats=['%m-%Y'], write_only=True)
#
#     class Meta:
#         model = UserTargetAmount
#         fields = '__all__'
#         read_only_fields = ['start_date', 'end_date', 'created_at', 'updated_at']
#
#     def set_start_end_dates(self, validated_data):
#         # Extract `month_year` if it exists
#         month_year = validated_data.pop('month_year', None)
#
#         if month_year:
#             # Calculate the first and last day of the specified month
#             start_date = datetime(month_year.year, month_year.month, 1)
#             _, last_day = calendar.monthrange(month_year.year, month_year.month)
#             end_date = datetime(month_year.year, month_year.month, last_day)
#
#             # Add the calculated dates to validated data
#             validated_data['start_date'] = start_date
#             validated_data['end_date'] = end_date
#
#     def create(self, validated_data):
#         # Set start and end dates based on `month_year`
#         self.set_start_end_dates(validated_data)
#         return super().create(validated_data)
#
#     def update(self, instance, validated_data):
#         # Set start and end dates based on `month_year`
#         self.set_start_end_dates(validated_data)
#         return super().update(instance, validated_data)
