import random
import string
from datetime import datetime
from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be assigned to is_superuser=True')
        return self.create_user(email, password=password, **other_fields)

    def create_user(self, email, password, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))
        email = self.normalize_email(email)
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user


class Role(models.Model):
    role = models.CharField(max_length=30, unique=True, blank=False, null=False)

    def __str__(self):
        return f"{self.role}"


class UserBase(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=255, null=True, blank=True)
    enterprise_name = models.CharField(max_length=255, null=True, blank=True, default='magneta')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    aadhar = models.CharField(max_length=100, null=True, blank=True)
    pan = models.CharField(max_length=15, null=True, blank=True)
    gst = models.CharField(max_length=50, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_image/', default='default/profile_default.png',
                                        null=True, blank=True)

    # Contact Data
    phone_number = models.CharField(max_length=20, unique=True, blank=False, null=False)
    emergency_phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True)

    # Address Data
    Address = models.TextField(max_length=500, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=255, null=True, blank=True)

    # user status
    otp = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name='status')
    is_staff = models.BooleanField(default=False)

    is_retailer = models.BooleanField(default=False)
    is_distributor = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_store_manager = models.BooleanField(default=False)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='user_role')
    default_password = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    class Meta:
        verbose_name_plural = "Accounts"

    @property
    def total_target_amount(self):
        return self.user_target_amounts.aggregate(Sum('target_amount'))['target_amount__sum'] or 0.0

    #
    # @property
    # def daily_summary(self):
    #     today = timezone.now().date()
    #     return self._get_summary(today, today)
    #
    # @property
    # def current_month_summary(self):
    #     today = timezone.now().date()
    #     start_of_month = today.replace(day=1)
    #     return self._get_summary(start_of_month, today)
    #
    # @property
    # def previous_month_summary(self):
    #     today = timezone.now().date()
    #     first_of_this_month = today.replace(day=1)
    #     last_of_previous_month = first_of_this_month - timedelta(days=1)
    #     start_of_previous_month = last_of_previous_month.replace(day=1)
    #     return self._get_summary(start_of_previous_month, last_of_previous_month)
    #
    # ### Helper methods ###
    #
    # def _get_summary(self, start_date, end_date):
    #     # Filter `UserTargetAmount` for the specified date range and user
    #     user_target_amounts = UserTargetAmount.objects.filter(
    #         user=self,
    #         start_date__gte=start_date,
    #         end_date__lte=end_date
    #     )
    #
    #     # Aggregate the achieved and target amounts
    #     achieved_amount = user_target_amounts.aggregate(
    #         models.Sum('achieved_amount')
    #     )['achieved_amount__sum'] or 0.0
    #
    #     target_amount = user_target_amounts.aggregate(
    #         models.Sum('target_amount')
    #     )['target_amount__sum'] or 0.0
    #
    #     # Calculate achievement percentage
    #     achievement_percentage = self._calculate_percentage(achieved_amount, target_amount)
    #
    #     # Return the summary as a dictionary
    #     return {
    #         "amount": target_amount,
    #         "achieve_amount": achieved_amount,
    #         "status": achievement_percentage,
    #     }
    #     # # Return the summary as a dictionary
    #     # return {
    #     #     "target_amount": target_amount,
    #     #     "achieved_amount": achieved_amount,
    #     #     "achievement_percentage": achievement_percentage,
    #     # }
    #
    # def _calculate_percentage(self, achieved, target):
    #     if target and target > 0:
    #         return (achieved / target) * 100
    #     return 0.0
    # @property
    # def current_month_achieved_amount(self):
    #     # Get the first day of the current month
    #     first_day_of_current_month = timezone.now().replace(day=1)
    #     # Filter achieved amounts created in the current month
    #     current_month_records = self.user_target_amounts.filter(
    #         created_at__gte=first_day_of_current_month
    #     )
    #     # Sum up the achieved amounts for the current month
    #     return sum(record.achieved_amount for record in current_month_records if record.achieved_amount is not None)

    # @property
    # def previous_month_achieved_amount(self):
    #     # Get the first day of the current month
    #     first_day_of_current_month = timezone.now().replace(day=1)
    #     # Calculate the first day of the previous month
    #     first_day_of_previous_month = (first_day_of_current_month - timedelta(days=1)).replace(day=1)
    #     # Filter achieved amounts created in the previous month
    #     previous_month_records = self.user_target_amounts.filter(
    #         created_at__gte=first_day_of_previous_month,
    #         created_at__lt=first_day_of_current_month
    #     )
    #     # Sum up the achieved amounts for the previous month
    #     return sum(record.achieved_amount for record in previous_month_records if record.achieved_amount is not None)

    @property
    def current_month_target_amount(self):
        # Get the first day of the current month
        first_day_of_current_month = timezone.now().replace(day=1)
        # Filter target amounts created in the current month
        current_month_records = self.user_target_amounts.filter(
            created_at__gte=first_day_of_current_month
        )
        # Sum up the target amounts for the current month
        return sum(record.target_amount for record in current_month_records if record.target_amount is not None)

    @property
    def previous_month_target_amount(self):
        # Get the first day of the current month
        first_day_of_current_month = timezone.now().replace(day=1)
        # Calculate the first day of the previous month
        first_day_of_previous_month = (first_day_of_current_month - timedelta(days=1)).replace(day=1)
        # Filter target amounts created in the previous month
        previous_month_records = self.user_target_amounts.filter(
            created_at__gte=first_day_of_previous_month,
            created_at__lt=first_day_of_current_month
        )
        # Sum up the target amounts for the previous month
        return sum(record.target_amount for record in previous_month_records if record.target_amount is not None)


    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}" or f"{self.email}"

    def generate_unique_id(self):
        # Generate zero-padded user ID
        padded_id = str(self.id).zfill(4)  # Zero-pad the ID to a length of 4

        # Generate a random alphanumeric string of 4 characters for uniqueness
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

        if self.is_distributor:
            # Create distributor user ID in the format: MAG-CITY-ID-RANDOM
            return f"MAG-{self.enterprise_name}{self.city.upper()}-{padded_id}-{random_suffix}"
        elif self.is_retailer:
            return f"MAG-RTL-{self.enterprise_name}-{padded_id}-{random_suffix}"
        elif self.is_manager:
            return f"MAG-MGM-{self.enterprise_name}-{padded_id}-{random_suffix}"
        elif self.role == "sales":  # Check if the role is sales
            return f"SL-{self.enterprise_name}-{padded_id}-{random_suffix}"  # Format for sales role
        else:
            return f"MAG-{self.enterprise_name}-{padded_id}-{random_suffix}"

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)
        self.user_id = self.generate_unique_id()
        super().save(*args, **kwargs)
        # if not self.user_id:
        #
        # if self.is_distributor:
        #     prefix = "magnet-dst-"
        # elif self.is_retailer:
        #     prefix = "magnet-rtl-"
        # elif self.is_manager:
        #     prefix = "magnet-mgm-"
        # # elif self.role=="sales":
        #     # prefix =f"SL-{padded_id}-{random_suffix}"
        # else:
        #     prefix = "magnet-"
        # user_id = prefix + str(self.id).zfill(4)
        # self.user_id = generate_unique_id()
        # super().save(*args, **kwargs)
        # else:
        #     super().save(*args, **kwargs)

        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt', 'argon2')):
            # Manually hash the password before saving
            print(self.password)
            self.password = make_password(self.password)
            print(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Otp(models.Model):
    otp = models.CharField(max_length=10)
    user = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='otp_entries')

    def __str__(self):
        return f"{self.user}"


class CompanyInformation(models.Model):
    pan = models.CharField(max_length=10)
    legal_name = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=255)
    gstin = models.CharField(max_length=15)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.legal_name}"


class RolesPermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    user = models.ForeignKey(UserBase, related_name='roles', on_delete=models.PROTECT)
    permission = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.role} {self.permission}"

    class Meta:
        unique_together = ('user', 'permission')


class UserTargetAmount(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='user_target_amounts')
    target_amount = models.FloatField(null=True, blank=True, help_text="distributor for given to sales person")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    # achieved_amount = models.FloatField(default=0.0, help_text="Total amount achieved by user")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.end_date:
            # Convert end_date to timezone-aware datetime
            end_datetime = timezone.make_aware(
                datetime.combine(self.end_date, datetime.min.time())
            )

            # Now compare with timezone.now() since both are timezone-aware
            if end_datetime < timezone.now():
                self.status = 'completed'
            else:
                self.status = 'pending'

        super(UserTargetAmount, self).save(*args, **kwargs)


    #
    # # <editor-fold desc="old">
    # @property
    # def daily_summary(self):
    #     today = timezone.now().date()
    #     achieved_amount = self._get_achieved_amount(today, today)
    #     return {
    #         "target_amount": self.target_amount,
    #         "achieved_amount": achieved_amount,
    #         "achievement_percentage": self._calculate_percentage(achieved_amount, self.target_amount),
    #     }
    # 
    # @property
    # def current_month_summary(self):
    #     today = timezone.now().date()
    #     start_of_month = today.replace(day=1)
    #     achieved_amount = self._get_achieved_amount(start_of_month, today)
    #     return {
    #         "target_amount": self.target_amount,
    #         "achieved_amount": achieved_amount,
    #         "achievement_percentage": self._calculate_percentage(achieved_amount, self.target_amount),
    #     }
    # 
    # @property
    # def previous_month_summary(self):
    #     today = timezone.now().date()
    #     first_of_this_month = today.replace(day=1)
    #     last_of_previous_month = first_of_this_month - timedelta(days=1)
    #     start_of_previous_month = last_of_previous_month.replace(day=1)
    #     achieved_amount = self._get_achieved_amount(start_of_previous_month, last_of_previous_month)
    #     return {
    #         "target_amount": self.target_amount,
    #         "achieved_amount": achieved_amount,
    #         "achievement_percentage": self._calculate_percentage(achieved_amount, self.target_amount),
    #     }
    # 
    # ### Helper methods ###
    # 
    # def _get_achieved_amount(self, start_date, end_date):
    #     # Aggregate achieved amount within the specified dates for the same user
    #     return UserTargetAmount.objects.filter(
    #         user=self.user,
    #         start_date__gte=start_date,
    #         end_date__lte=end_date
    #     ).aggregate(models.Sum('achieved_amount'))['achieved_amount__sum'] or 0.0
    # 
    # def _calculate_percentage(self, achieved, target):
    #     if target and target > 0:
    #         return (achieved / target) * 100
    #     return 0.0
    # # </editor-fold>
    # 

    def __str__(self):
        return f"{self.user}"


# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.db.models import Sum
#
# @receiver(post_save, sender=UserTargetAmount)
# def update_achieved_amount(sender, instance, created, **kwargs):
#     """
#     Update the achieved amount whenever a UserTargetAmount instance is created or updated.
#     """
#     # Check if the instance is being created or updated
#     if created:
#         # For new instance, calculate achieved_amount
#         achieved_amount = UserTargetAmount.objects.filter(
#             user=instance.user,
#             start_date__lte=instance.end_date,
#             end_date__gte=instance.start_date,
#             status='completed'  # Ensure we include only 'completed' statuses
#         ).aggregate(Sum('achieved_amount'))['achieved_amount__sum'] or 0.0
#     else:
#         # For updated instance, recalculate achieved_amount based on new values
#         achieved_amount = UserTargetAmount.objects.filter(
#             user=instance.user,
#             start_date__lte=instance.end_date,
#             end_date__gte=instance.start_date,
#             status='completed'
#         ).aggregate(Sum('achieved_amount'))['achieved_amount__sum'] or 0.0
#
#     # Update the achieved_amount if it has changed
#     if instance.achieved_amount != achieved_amount:
#         instance.achieved_amount = achieved_amount
#         instance.save(update_fields=['achieved_amount'])  # Save only the updated field


