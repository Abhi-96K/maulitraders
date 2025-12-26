from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from products.models import Category, Product, Brand
from orders.models import Order

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_active=True, is_featured=True).prefetch_related('images')[:20]
    brands = Brand.objects.all()
    return render(request, 'core/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'brands': brands
    })

def product_list(request):
    products = Product.objects.filter(is_active=True).prefetch_related('images')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    # Read selected filters from the GET request (safe, simple values)
    selected_category = request.GET.get('category', '')
    if selected_category:
        products = products.filter(category__slug=selected_category)
        
    selected_brand = request.GET.get('brand', '')
    if selected_brand:
        products = products.filter(brand__slug=selected_brand)
        
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    return render(request, 'core/product_list.html', {
        'products': products,
        'categories': categories,
        'brands': brands,
        'selected_category': selected_category,
        'selected_brand': selected_brand,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    return render(request, 'core/product_detail.html', {
        'product': product,
        'related_products': related_products
    })

from users.forms import UserUpdateForm, ResellerProfileUpdateForm
from users.models import CustomUser

@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    user_form = UserUpdateForm(instance=request.user)
    reseller_form = None
    
    if request.user.role == CustomUser.Role.RESELLER:
        try:
            reseller_form = ResellerProfileUpdateForm(instance=request.user.reseller_profile)
        except:
            pass
            
    return render(request, 'core/dashboard.html', {
        'orders': orders,
        'user_form': user_form,
        'reseller_form': reseller_form
    })

def contact(request):
    return render(request, 'core/contact.html')

def support(request):
    return render(request, 'core/support.html')

def suggestions(request):
    return render(request, 'core/suggestions.html')

def terms(request):
    return render(request, 'core/terms.html')

def about(request):
    return render(request, 'core/about.html')

@user_passes_test(lambda u: u.is_staff)
@user_passes_test(lambda u: u.is_staff)
def analytics_view(request):
    from django.utils import timezone
    from django.db.models import Sum, F, Count, ExpressionWrapper, DecimalField
    from django.db.models.functions import TruncDate
    from orders.models import Order, OrderItem
    from products.models import Product
    import datetime
    import json

    now = timezone.now()
    today = now.date()
    this_month = now.month
    this_year = now.year
    last_30_days = now - datetime.timedelta(days=30)

    # --- KPI Cards ---
    # Helper to calculate profit
    def calculate_profit(orders):
        profit = 0
        for order in orders:
            for item in order.items.all():
                if item.product:
                    cost = item.product.cost_price * item.quantity
                    revenue = item.total_price
                    profit += (revenue - cost)
        return profit

    daily_orders = Order.objects.filter(created_at__date=today).exclude(status='CANCELLED')
    daily_sales = daily_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    daily_profit = calculate_profit(daily_orders)

    monthly_orders = Order.objects.filter(created_at__month=this_month, created_at__year=this_year).exclude(status='CANCELLED')
    monthly_sales = monthly_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_profit = calculate_profit(monthly_orders)

    yearly_orders = Order.objects.filter(created_at__year=this_year).exclude(status='CANCELLED')
    yearly_sales = yearly_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    yearly_profit = calculate_profit(yearly_orders)

    # --- Charts Data ---
    # 1. Sales Trend (Last 30 Days)
    sales_trend = Order.objects.filter(
        created_at__gte=last_30_days
    ).exclude(
        status='CANCELLED'
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('total_amount')
    ).order_by('date')

    trend_dates = [entry['date'].strftime('%Y-%m-%d') for entry in sales_trend]
    trend_values = [float(entry['total']) for entry in sales_trend]

    # 2. Category Distribution
    category_sales = OrderItem.objects.exclude(
        order__status='CANCELLED'
    ).values(
        'product__category__name'
    ).annotate(
        total=Sum('total_price')
    ).order_by('-total')

    cat_labels = [entry['product__category__name'] or 'Uncategorized' for entry in category_sales]
    cat_values = [float(entry['total']) for entry in category_sales]

    # --- Product Rankings ---
    
    # 1. Top Selling (by Quantity)
    top_selling = OrderItem.objects.exclude(
        order__status='CANCELLED'
    ).values(
        'product__name'
    ).annotate(
        total_qty=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_qty')[:10]

    # 2. Lowest Selling
    lowest_selling = OrderItem.objects.exclude(
        order__status='CANCELLED'
    ).values(
        'product__name'
    ).annotate(
        total_qty=Sum('quantity')
    ).order_by('total_qty')[:10]

    # 3. Product Margins (Static based on current price)
    # Margin % = ((Retail - Cost) / Retail) * 100
    products_with_margin = Product.objects.annotate(
        margin=ExpressionWrapper(
            (F('retail_price') - F('cost_price')) * 100 / F('retail_price'),
            output_field=DecimalField(max_digits=5, decimal_places=2)
        ),
        profit_amount=ExpressionWrapper(
            F('retail_price') - F('cost_price'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).filter(is_active=True).order_by('-margin')

    highest_margin = products_with_margin[:10]
    lowest_margin = products_with_margin.reverse()[:10]

    # 4. Most Profitable (Estimated based on sales)
    # This is complex in pure SQL/ORM without storing historical cost. 
    # We will approximate by iterating top sellers.
    # For a robust solution, we'd need to store cost_price on OrderItem.
    # Here we use the calculated list from top_selling and enrich it.
    
    # Context
    context = {
        'daily_sales': daily_sales,
        'daily_profit': daily_profit,
        'monthly_sales': monthly_sales,
        'monthly_profit': monthly_profit,
        'yearly_sales': yearly_sales,
        'yearly_profit': yearly_profit,
        
        'trend_dates': json.dumps(trend_dates),
        'trend_values': json.dumps(trend_values),
        'cat_labels': json.dumps(cat_labels),
        'cat_values': json.dumps(cat_values),
        
        'top_selling': top_selling,
        'lowest_selling': lowest_selling,
        'highest_margin': highest_margin,
        'lowest_margin': lowest_margin,
    }
    return render(request, 'core/analytics.html', context)

from django.http import JsonResponse
from products.models import ProductNotification
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from django.contrib import messages

@require_POST
def notify_stock(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    email = request.POST.get('email')
    
    # If user is logged in, use their email if not provided (though logic usually demands form input)
    if request.user.is_authenticated and not email:
        email = request.user.email

    try:
        validate_email(email)
        
        # Check if already subscribed
        if not ProductNotification.objects.filter(product=product, email=email, is_notified=False).exists():
            ProductNotification.objects.create(
                product=product,
                email=email,
                user=request.user if request.user.is_authenticated else None
            )
            messages.success(request, f"We'll notify you at {email} when this product is back in stock!")
        else:
            messages.info(request, "You are already on the notification list for this product.")
            
    except ValidationError:
        messages.error(request, "Please provide a valid email address.")
    
    return redirect('product-detail', slug=product.slug)

