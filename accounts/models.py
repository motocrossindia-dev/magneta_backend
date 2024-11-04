import random

from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from datetime import datetime
import random
import string


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
    def full_name(self):
        return f"{self.first_name} {self.last_name}" or f"{self.email}"


    def generate_unique_id(self):
        # Generate zero-padded user ID
        padded_id = str(self.id).zfill(4)  # Zero-pad the ID to a length of 4

        # Generate a random alphanumeric string of 4 characters for uniqueness
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

        if self.is_distributor:
            # Create distributor user ID in the format: MAG-CITY-ID-RANDOM
            return f"MAG-{self.city.upper()}-{padded_id}-{random_suffix}"
        elif self.is_retailer:
            return f"MAG-RTL-{padded_id}-{random_suffix}"
        elif self.is_manager:
            return f"MAG-MGM-{padded_id}-{random_suffix}"
        elif self.role == "sales":  # Check if the role is sales
            return f"SL-{padded_id}-{random_suffix}"  # Format for sales role
        else:
            return f"MAG-{padded_id}-{random_suffix}"

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
