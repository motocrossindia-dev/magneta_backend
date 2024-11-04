from django.db import models


class AppVersionNumber(models.Model):
    latest_version = models.CharField(max_length=10)
    base_version = models.CharField(max_length=10, blank=True, null=True)
    force_update = models.BooleanField(default=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "update   "

    def __str__(self):
        return self.latest_version


class PartnerAppVersionNumber(models.Model):
    latest_version = models.CharField(max_length=10)
    base_version = models.CharField(max_length=10, blank=True, null=True)
    force_update = models.BooleanField(default=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Partner Android Version Number"

    def __str__(self):
        return self.latest_version


class IphoneAppVersionNumber(models.Model):
    latest_version = models.CharField(max_length=10)
    base_version = models.CharField(max_length=10, blank=True, null=True)
    force_update = models.BooleanField(default=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Customer IOS Version Number"

    def __str__(self):
        return self.latest_version


class IphonePartnerAppVersionNumber(models.Model):
    latest_version = models.CharField(max_length=10)
    base_version = models.CharField(max_length=10, blank=True, null=True)
    force_update = models.BooleanField(default=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Partner IOS Version Number"

    def __str__(self):
        return self.latest_version
