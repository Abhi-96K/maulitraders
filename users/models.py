from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        RESELLER = 'RESELLER', _('Reseller')
        CUSTOMER = 'CUSTOMER', _('Customer')

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    mobile = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    
    # Override email to be unique
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'mobile']

    def __str__(self):
        return self.email

class ResellerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='reseller_profile')
    shop_name = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    business_address = models.TextField()
    is_approved = models.BooleanField(default=False)
    
    # Documents
    gst_certificate = models.FileField(upload_to='reseller_docs/gst/', blank=True, null=True)
    kyc_document = models.FileField(upload_to='reseller_docs/kyc/', blank=True, null=True)
    shop_image = models.ImageField(upload_to='reseller_docs/shop/', blank=True, null=True)

    def __str__(self):
        return f"{self.shop_name} ({self.user.email})"

class OTPVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.otp}"

