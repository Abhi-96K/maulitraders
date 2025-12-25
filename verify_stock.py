import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maulitraders.settings')
django.setup()

from django.test import RequestFactory
from django.urls import reverse
from core.views import product_detail
from products.models import Product, Category

def verify_stock_logic():
    # Setup
    category, _ = Category.objects.get_or_create(name='Test Category', slug='test-cat')
    product, created = Product.objects.get_or_create(
        name='Test Product', 
        slug='test-product',
        defaults={
            'sku': 'TEST001',
            'retail_price': 100,
            'wholesale_price': 80,
            'cost_price': 50,
            'category': category
        }
    )
    
    # Test 1: In Stock
    product.stock_quantity = 10
    product.save()
    factory = RequestFactory()
    request = factory.get(f'/products/{product.slug}/')
    request.user = type('User', (object,), {'is_authenticated': False, 'role': 'CUSTOMER'})()
    response = product_detail(request, slug=product.slug)
    
    content = response.content.decode('utf-8')
    if 'Add to Cart' in content and 'notify-form' not in content:
        print("PASS: In-stock product shows 'Add to Cart'")
    else:
        print("FAIL: In-stock logic incorrect")

    # Test 2: Out of Stock
    product.stock_quantity = 0
    product.save()
    response = product_detail(request, slug=product.slug)
    content = response.content.decode('utf-8')
    
    if 'notify-form' in content and 'Add to Cart' not in content:
        print("PASS: Out-of-stock product shows 'Notify Me' form")
    else:
        print("FAIL: Out-of-stock logic incorrect")
        
    print("Verification Complete")

if __name__ == '__main__':
    verify_stock_logic()
