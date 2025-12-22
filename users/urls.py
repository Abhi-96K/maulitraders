from django.urls import path
from .views import RegisterView, ResellerRegisterView, VerifyOTPView, AdminResellerListView, AdminResellerActionView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api-register'),
    path('register/reseller/', ResellerRegisterView.as_view(), name='api-register-reseller'),
    path('verify-otp/', VerifyOTPView.as_view(), name='api-verify-otp'),
    path('admin/resellers/', AdminResellerListView.as_view(), name='admin-reseller-list'),
    path('admin/resellers/<int:pk>/action/', AdminResellerActionView.as_view(), name='admin-reseller-action'),
]
