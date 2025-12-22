from django.contrib import admin
from .models import Invoice

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'order', 'created_at']
    search_fields = ['invoice_number', 'order__id']
    readonly_fields = ['created_at']

admin.site.register(Invoice, InvoiceAdmin)
