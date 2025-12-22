from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'invoices', views.InvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('pos/', views.pos_view, name='pos'),
]
