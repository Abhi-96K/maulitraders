from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    customer_name = forms.CharField(required=True)
    customer_mobile = forms.CharField(required=True)
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    shipping_city = forms.CharField(required=True)
    shipping_pincode = forms.CharField(required=True)
    
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_mobile', 'customer_email', 'shipping_address', 'shipping_city', 'shipping_pincode']
