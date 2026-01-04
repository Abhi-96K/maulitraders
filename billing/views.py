from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from products.models import Product
from orders.models import Order, OrderItem
import json
from django.core.files.base import ContentFile
from .models import Invoice, Order
from .serializers import InvoiceSerializer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
import uuid
from decimal import Decimal

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def generate(self, request):
        order_id = request.data.get('order_id')
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        if hasattr(order, 'invoice'):
            return Response({"message": "Invoice already exists", "invoice_id": order.invoice.id})

        # Generate PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Header
        p.setFont("Helvetica-Bold", 20)
        p.drawString(50, height - 50, "Mauli Traders")
        
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 70, "Building Materials & Hardware")
        p.drawString(50, height - 85, "Marathwada Region")
        p.drawString(50, height - 100, "GSTIN: 27ABCDE1234F1Z5") # Mock GSTIN
        
        # Invoice Details
        invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        p.drawString(400, height - 50, f"INVOICE #: {invoice_number}")
        p.drawString(400, height - 70, f"Date: {order.created_at.strftime('%Y-%m-%d')}")
        
        # Customer Details
        p.drawString(50, height - 140, "Bill To:")
        if order.user:
            p.drawString(50, height - 155, f"{order.user.first_name} {order.user.last_name}")
            p.drawString(50, height - 170, f"Mobile: {order.user.mobile}")
        else:
            p.drawString(50, height - 155, f"{order.customer_name}")
            p.drawString(50, height - 170, f"Mobile: {order.customer_mobile}")

        # Table Header
        y = height - 220
        p.line(50, y, 550, y)
        p.drawString(50, y + 5, "Item")
        p.drawString(300, y + 5, "Qty")
        p.drawString(350, y + 5, "Price")
        p.drawString(450, y + 5, "Total")
        p.line(50, y + 20, 550, y + 20)
        
        # Items
        y -= 20
        for item in order.items.all():
            p.drawString(50, y, f"{item.product.name}")
            p.drawString(300, y, str(item.quantity))
            p.drawString(350, y, str(item.unit_price))
            p.drawString(450, y, str(item.total_price))
            y -= 20
            
        # Totals
        y -= 20
        p.line(50, y, 550, y)
        p.drawString(350, y - 20, "Subtotal:")
        p.drawString(450, y - 20, str(order.total_amount - order.tax_amount))
        
        p.drawString(350, y - 40, "Tax:")
        p.drawString(450, y - 40, str(order.tax_amount))
        
        p.setFont("Helvetica-Bold", 14)
        p.drawString(350, y - 70, "Total:")
        p.drawString(450, y - 70, str(order.total_amount))
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        
        invoice = Invoice.objects.create(
            order=order,
            invoice_number=invoice_number,
        )
        invoice.pdf_file.save(f"{invoice_number}.pdf", ContentFile(buffer.getvalue()))
        
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def pos_view(request):
    if request.method == 'POST':
        # Handle Order Creation
        try:
            cart_data = json.loads(request.POST.get('cart_data'))
            customer_name = request.POST.get('customer_name', 'Walk-in Customer')
            customer_mobile = request.POST.get('customer_mobile', '')
            payment_method = request.POST.get('payment_method', 'CASH')
            
            if not cart_data:
                messages.error(request, "Cart is empty!")
                return redirect('pos')

            from django.db import transaction
            
            with transaction.atomic():
                # Check for gst_applied in POST
                gst_applied = request.POST.get('gst_applied') == 'on'
                
                # Create Order
                order = Order.objects.create(
                    user=None, # Walk-in
                    created_by=request.user,
                    customer_name=customer_name,
                    customer_mobile=customer_mobile,
                    order_type='POS',
                    status='COMPLETED', # POS orders are instant
                    payment_method=payment_method,
                    payment_status='COMPLETED',
                    gst_applied=gst_applied
                )
                
                subtotal_amount = 0
                
                for item in cart_data:
                    product = Product.objects.get(id=item['id'])
                    quantity = int(item['quantity'])
                    
                    if product.stock_quantity < quantity:
                        raise Exception(f"Insufficient stock for {product.name}. Available: {product.stock_quantity}")

                    price = product.retail_price # Use retail price for now
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=price,
                        tax_rate=18.00 if gst_applied else 0.00, 
                        total_price=price * quantity
                    )
                    
                    # Update Stock
                    product.stock_quantity -= quantity
                    product.save()
                    
                    subtotal_amount += price * quantity
                
                # Financial Calculations
                if gst_applied:
                    tax_amount = subtotal_amount * Decimal('0.18')
                    total_amount = subtotal_amount + tax_amount
                else:
                    tax_amount = 0
                    total_amount = subtotal_amount
                    
                order.tax_amount = tax_amount
                order.total_amount = total_amount
                order.save()
            
            messages.success(request, f"Order #{order.id} created successfully!")
            return redirect('invoice', order_id=order.id)
            
        except Exception as e:
            messages.error(request, f"Error creating order: {str(e)}")
            return redirect('pos')

    # GET request - Show POS Interface
    products = Product.objects.filter(is_active=True)
    return render(request, 'billing/pos.html', {'products': products})
