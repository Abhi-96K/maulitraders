from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Order
from maulitraders.utils.whatsapp import send_whatsapp_message
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Order)
def cache_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Order)
def send_status_update_notification(sender, instance, created, **kwargs):
    if created:
        return # Handled in view
    
    old_status = getattr(instance, '_old_status', None)
    new_status = instance.status
    
    if old_status != new_status:
        mobile = instance.customer_mobile or (instance.user.mobile if instance.user else None)
        
        if mobile:
            if not mobile.startswith('+'):
                mobile = f"+91{mobile.strip()}"
                
            msg = None
            if new_status == 'CONFIRMED':
                msg = f"Order #{instance.id} Confirmed! We are processing your order."
            elif new_status == 'SHIPPED':
                msg = f"Good news! Your Order #{instance.id} has been shipped. It will reach you soon."
            elif new_status == 'DELIVERED':
                msg = f"Order #{instance.id} Delivered. Thank you for shopping with Mauli Traders!"
            elif new_status == 'CANCELLED':
                msg = f"Order #{instance.id} has been cancelled."
            
            if msg:
                send_whatsapp_message(mobile, msg)
