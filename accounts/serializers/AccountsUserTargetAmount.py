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


def convert_date_format(date_str):
    """
    Converts a date string in the format 'YYYY-MM-DD' to the format 'MM YY'.

    Parameters:
    date_str (str): The date string in the format 'YYYY-MM-DD'.

    Returns:
    str: The date string in the format 'MM YY'.
    """
    year, month, _ = date_str.split('-')
    return f"{month}-{year[-2:]}"


# print(convert_date_format("2024-03-01"))
class UserTargetAmountSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.first_name')
    user_enterprise_name = serializers.ReadOnlyField(source='user.enterprise_name')
    user_id = serializers.IntegerField()
    month_year = serializers.CharField(write_only=True)  # Changed to CharField to handle the format

    class Meta:
        model = UserTargetAmount
        fields = ['id', 'user', 'user_id', 'month_year', 'target_amount', 'start_date', 'end_date', 'status','user_enterprise_name']

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
        # Check if month_year was provided in validated_data
        month_year_str = validated_data.get('month_year', None)
        if month_year_str:
            print(month_year_str,'============year put',)
            data=convert_date_format(str(month_year_str))
            print(data,'================')
            # Convert month_year string to date and set start and end dates
            validated_data['month_year'] = self.validate_month_year(convert_date_format(str(month_year_str)))
            self.set_start_end_dates(validated_data)

        # Update fields on the instance
        for attr, value in validated_data.items():
            if attr != 'user_id':  # Exclude user_id from being updated
                setattr(instance, attr, value)

        # Save the instance to persist changes
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['month_year'] = instance.start_date.strftime('%m-%Y')
        return data
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
