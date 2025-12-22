from django.db import models
from orders.models import Order

class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    pdf_file = models.FileField(upload_to='invoices/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
        ('BANK', 'Bank Transfer'),
        ('CARD', 'Card'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.amount} via {self.method}"
