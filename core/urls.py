from django.urls import path
from .views import home, product_list, product_detail, dashboard, contact, support, suggestions, analytics_view, terms, about, notify_stock

urlpatterns = [
    path('', home, name='home'),
    path('products/', product_list, name='product-list'),
    path('products/<slug:slug>/', product_detail, name='product-detail'),
    path('dashboard/', dashboard, name='dashboard'),
    path('contact/', contact, name='contact'),
    path('support/', support, name='support'),
    path('support/', support, name='support'),
    path('suggestions/', suggestions, name='suggestions'),
    path('about/', about, name='about'),
    path('notify/<int:product_id>/', notify_stock, name='notify-stock'),
    path('terms/', terms, name='terms'),
    path('analytics/', analytics_view, name='analytics'),
]
