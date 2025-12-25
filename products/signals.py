from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, ProductNotification

@receiver(post_save, sender=Product)
def send_stock_notification(sender, instance, **kwargs):
    if instance.stock_quantity > 0:
        # Find unnotified users
        notifications = ProductNotification.objects.filter(product=instance, is_notified=False)
        
        if notifications.exists():
            emails = [n.email for n in notifications]
            
            subject = f"Good News! {instance.name} is back in stock!"
            message = f"Hello,\n\nThe product '{instance.name}' you were interested in is now back in stock at Mauli Traders.\n\nHurry up and order now before it runs out again!\n\nLink: {settings.SITE_URL}/products/{instance.slug}/"
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    emails,
                    fail_silently=True,
                )
                
                # Mark as notified
                notifications.update(is_notified=True)
                print(f"Sent stock notification to {len(emails)} users for {instance.name}")
            except Exception as e:
                print(f"Failed to send stock notification: {e}")
