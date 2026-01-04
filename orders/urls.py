from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cart/', views.cart_detail, name='cart-detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart-add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart-update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart-remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('invoice/<int:order_id>/', views.invoice_view, name='invoice'),
    path('pay/<int:order_id>/', views.pay_order_view, name='pay_order'),
    path('terms/', views.terms, name='terms'),
]
