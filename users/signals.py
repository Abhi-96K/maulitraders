from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import ResellerProfile
from .utils import send_html_email, send_whatsapp_message

@receiver(pre_save, sender=ResellerProfile)
def capture_old_status(sender, instance, **kwargs):
    """
    Capture the old approval status before saving.
    """
    if instance.pk:
        try:
            old_instance = ResellerProfile.objects.get(pk=instance.pk)
            instance._old_is_approved = old_instance.is_approved
        except ResellerProfile.DoesNotExist:
            instance._old_is_approved = False
    else:
        instance._old_is_approved = False

@receiver(post_save, sender=ResellerProfile)
def send_approval_notifications(sender, instance, created, **kwargs):
    """
    Send notifications when a reseller is approved.
    """
    # Check if approval status changed from False to True
    if instance.is_approved and not getattr(instance, '_old_is_approved', False):
        print(f"DEBUG: Reseller {instance.shop_name} approved. Sending notifications...")
        
        # 1. Send HTML Email
        subject = 'Welcome to Mauli Traders! Your Shop is Approved'
        context = {
            'user': instance.user,
            'shop_name': instance.shop_name,
            'login_url': f"{settings.ALLOWED_HOSTS[0]}/login/" if settings.ALLOWED_HOSTS else "http://localhost:8000/login/"
        }
        send_html_email(subject, 'emails/reseller_approved.html', context, [instance.user.email])
        
        # 2. Send WhatsApp Message
        whatsapp_msg = (
            f"Welcome to Mauli Traders! 🌟\n\n"
            f"Dear {instance.user.first_name},\n"
            f"Your shop '{instance.shop_name}' has been approved! ✅\n\n"
            f"You can now login and access wholesale prices.\n"
            f"Login here: http://localhost:8000/login/"
        )
        send_whatsapp_message(instance.user.mobile, whatsapp_msg)
