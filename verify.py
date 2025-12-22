import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maulitraders.settings')
os.environ['SQL_ENGINE'] = 'django.db.backends.sqlite3'
os.environ['SQL_DATABASE'] = 'db.sqlite3'

django.setup()

from products.models import Category, Brand, Product
from users.models import CustomUser
from orders.models import Order, OrderItem

def verify():
    print("Verifying system...")
    
    # Create Admin
    admin, created = CustomUser.objects.get_or_create(
        email='admin@example.com',
        defaults={
            'username': 'admin',
            'mobile': '9999999999',
            'is_staff': True,
            'is_superuser': True,
            'role': 'ADMIN'
        }
    )
    if created:
        admin.set_password('password')
        admin.save()
        print("Admin created.")
    else:
        print("Admin already exists.")

    # Create Category
    cat, _ = Category.objects.get_or_create(name='Plumbing', slug='plumbing')
    print(f"Category: {cat.name}")

    # Create Brand
    brand, _ = Brand.objects.get_or_create(name='Supreme', slug='supreme')
    print(f"Brand: {brand.name}")

    # Create Product
    product, _ = Product.objects.get_or_create(
        sku='PVC001',
        defaults={
            'name': 'PVC Pipe 4 inch',
            'slug': 'pvc-pipe-4-inch',
            'brand': brand,
            'category': cat,
            'retail_price': 500,
            'wholesale_price': 450,
            'cost_price': 400,
            'stock_quantity': 100,
            'unit': 'pcs'
        }
    )
    print(f"Product: {product.name}, Stock: {product.stock_quantity}")

    print("Verification complete.")

if __name__ == '__main__':
    verify()
