from rest_framework import viewsets, permissions, filters
from .models import Category, Brand, Product, StockAdjustmentLog
from .serializers import (
    CategorySerializer, BrandSerializer, ProductSerializer, 
    ProductCreateUpdateSerializer, StockAdjustmentLogSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sku', 'brand__name', 'category__name']
    ordering_fields = ['price', 'created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def adjust_stock(self, request, pk=None):
        product = self.get_object()
        quantity_change = int(request.data.get('quantity_change', 0))
        reason = request.data.get('reason', 'OTHER')
        note = request.data.get('note', '')

        if quantity_change == 0:
            return Response({"error": "Quantity change cannot be zero"}, status=400)

        product.stock_quantity += quantity_change
        if product.stock_quantity < 0:
            return Response({"error": "Insufficient stock"}, status=400)
        
        product.save()

        StockAdjustmentLog.objects.create(
            product=product,
            quantity_change=quantity_change,
            reason=reason,
            note=note,
            created_by=request.user
        )

        return Response({"status": "Stock updated", "new_quantity": product.stock_quantity})

class StockAdjustmentLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockAdjustmentLog.objects.all().order_by('-created_at')
    serializer_class = StockAdjustmentLogSerializer
    permission_classes = [permissions.IsAdminUser]
