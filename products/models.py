from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    display_order = models.IntegerField(default=0, help_text="Order in lists (lower numbers come first)")

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    sku = models.CharField(max_length=50, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    unit = models.CharField(max_length=20, help_text="e.g., kg, pcs, box")
    units_per_box = models.PositiveIntegerField(default=1, help_text="For bulk calculation")
    
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="For profit calculation")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, help_text="GST %")
    
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_threshold = models.PositiveIntegerField(default=10)
    
    description = models.TextField(blank=True)
    warranty_info = models.CharField(max_length=255, blank=True, null=True)
    has_exchange_policy = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Show in Featured Products on Home Page")
    display_order = models.IntegerField(default=0, help_text="Order in lists (lower numbers come first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.product.name}"

class StockAdjustmentLog(models.Model):
    REASON_CHOICES = [
        ('NEW_STOCK', 'New Stock Arrived'),
        ('DAMAGED', 'Damaged/Expired'),
        ('CORRECTION', 'Inventory Correction'),
        ('RETURN', 'Customer Return'),
        ('OTHER', 'Other'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_logs')
    quantity_change = models.IntegerField(help_text="Positive for addition, negative for reduction")
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name}: {self.quantity_change} ({self.reason})"

class ProductNotification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='notifications')
    email = models.EmailField()
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, null=True, blank=True)
    is_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.email} on {self.product.name}"
