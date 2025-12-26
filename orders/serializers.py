from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from billing.models import Payment

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ('total_price',)

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    payments = PaymentSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(required=False, allow_blank=True)
    customer_mobile = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('total_amount', 'tax_amount', 'discount_amount', 'created_by', 'created_at', 'updated_at')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context.get('request')
        validated_data['created_by'] = request.user if request else None
        
        from django.db import transaction
        
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            
            total_amount = 0
            tax_amount = 0
            
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                unit_price = item_data['unit_price']
                tax_rate = item_data['tax_rate']
                
                if product.stock_quantity < quantity:
                    raise serializers.ValidationError(f"Insufficient stock for {product.name}. Available: {product.stock_quantity}")

                # Calculate line total
                line_total = quantity * unit_price
                
                OrderItem.objects.create(order=order, total_price=line_total, **item_data)
                
                total_amount += line_total
                # Simple tax calc (inclusive or exclusive? Assuming exclusive for now based on fields)
                # Actually, usually tax is included or calculated. 
                # Let's assume unit_price is base price.
                tax_amount += line_total * (tax_rate / 100)
                
                # Update stock
                product.stock_quantity -= quantity
                product.save()

            order.total_amount = total_amount + tax_amount
            order.tax_amount = tax_amount
            order.save()
        
        return order
