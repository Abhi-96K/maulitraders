from rest_framework import viewsets, permissions, filters
from .models import Order
from rest_framework import viewsets, permissions, filters
from .models import Order, OrderItem
from .serializers import OrderSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Product
from .cart import Cart
from .forms import OrderCreateForm

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['customer_name', 'user__email', 'id']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# Frontend Views

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    return redirect('cart-detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    cart.remove(product)
    return redirect('cart-detail')

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity, update_quantity=True)
    return redirect('cart-detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'orders/cart.html', {'cart': cart})

def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
                # If these fields are empty in form, maybe fill from user profile if available (optional enhancement)
            
            # For guests (and registered users), the form cleaned_data is already set on 'order' by form.save(commit=False)
            # We just need to ensure we don't overwrite if not intended, but form.save() handles it.
            
            # Set payment details
            order.payment_method = request.POST.get('payment_method', 'COD')
            if order.payment_method == 'COD':
                order.payment_status = 'PENDING'
            else:
                # For UPI/Netbanking, we'll assume pending until callback (simulated here)
                order.payment_status = 'PENDING'
                
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    unit_price=item['price'],
                    quantity=item['quantity'],
                    total_price=item['total_price'],
                    tax_rate=item['product'].tax_rate
                )
                # Update stock
                product = item['product']
                product.stock_quantity -= item['quantity']
                product.save()
            
            # Calculate totals
            order.total_amount = cart.get_total_price() # + tax
            order.save()
            
            # Send SMS Notification
            try:
                from maulitraders.utils.notifications import send_sms
                # Determine mobile number
                mobile = order.customer_mobile or (order.user.mobile if order.user else None)
                if mobile:
                    msg = f"Hello {order.customer_name or 'Customer'}, your order #{order.id} has been placed! Total: {order.total_amount}. We will update you shortly."
                    send_sms(mobile, msg)
            except Exception as e:
                # Don't fail the order if notification fails
                print(f"Notification Error: {e}")

            cart.clear()
            return render(request, 'orders/created.html', {'order': order})
    else:
        form = OrderCreateForm()
    return render(request, 'orders/checkout.html', {'cart': cart, 'form': form})

def invoice_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Allow access if user is admin OR if user owns the order
    if not (request.user.is_staff or order.user == request.user):
        return redirect('home') # Or 403
        
    return render(request, 'orders/invoice.html', {'order': order})
