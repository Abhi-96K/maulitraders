from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customer_name', 'total_amount', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'order_type', 'created_at']
    search_fields = ['id', 'customer_name', 'user__email', 'user__username']
    inlines = [OrderItemInline]
    readonly_fields = ['total_amount', 'tax_amount', 'created_at']

admin.site.register(Order, OrderAdmin)
