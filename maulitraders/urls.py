"""
URL configuration for maulitraders project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from users import views as users_views
from users.views import register_view, verify_otp_view, reseller_register_view, resend_otp_view, verify_email_entry_view, pending_approval_view
from orders import views as order_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', register_view, name='register'),
    path('register/reseller/', reseller_register_view, name='reseller-register'),
    path('verify-otp/', verify_otp_view, name='verify-otp'),
    path('resend-otp/', resend_otp_view, name='resend-otp'),
    path('verify-email/', verify_email_entry_view, name='verify-email-entry'),
    path('pending-approval/', pending_approval_view, name='pending-approval'),
    path('profile/update/', users_views.update_profile_view, name='update-profile'),
    
    # Order URLs
    path('cart/', order_views.cart_detail, name='cart-detail'),
    path('cart/add/<int:product_id>/', order_views.cart_add, name='cart-add'),
    path('cart/remove/<int:product_id>/', order_views.cart_remove, name='cart-remove'),
    path('checkout/', order_views.checkout, name='checkout'),

    path('api/users/', include('users.urls')),
    path('api/inventory/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/billing/', include('billing.urls')),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
