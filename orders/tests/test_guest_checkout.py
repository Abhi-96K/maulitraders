from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product, Category, Brand
from orders.models import Order, OrderItem
from orders.forms import OrderCreateForm

class GuestCheckoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.brand = Brand.objects.create(name='Test Brand', slug='test-brand')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            brand=self.brand,
            cost_price=100,
            wholesale_price=150,
            retail_price=200,
            stock_quantity=10,
            unit='kg',
            is_active=True
        )
        self.checkout_url = reverse('checkout')
        self.cart_add_url = reverse('cart-add', args=[self.product.id])

    def test_guest_checkout_flow(self):
        # 1. Add product to cart
        self.client.post(self.cart_add_url, {'quantity': 1})
        
        # 2. Submit checkout form as guest
        data = {
            'customer_name': 'Guest User',
            'customer_mobile': '9876543210',
            'customer_email': 'guest@example.com',
            'shipping_address': '123 Guest St',
            'shipping_city': 'Mumbai',
            'shipping_pincode': '400001',
            'payment_method': 'COD'
        }
        
        response = self.client.post(self.checkout_url, data)
        
        # 3. Verify order created
        self.assertEqual(response.status_code, 200) # Should render success page or redirect
        # Check if created.html is used (based on view logic)
        self.assertTemplateUsed(response, 'orders/created.html')
        
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertIsNone(order.user)
        self.assertEqual(order.customer_name, 'Guest User')
        self.assertEqual(order.customer_email, 'guest@example.com')
        self.assertEqual(order.shipping_city, 'Mumbai')
        # Check payment status default
        self.assertEqual(order.payment_status, 'PENDING')
        
        # Verify items
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.product, self.product)

    def test_form_validation(self):
        form_data = {
            'customer_name': '', # Required
            'customer_mobile': '123'
        }
        form = OrderCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
