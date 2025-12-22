from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    mobile = forms.CharField(required=True, max_length=15)
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'mobile']

class ResellerRegistrationForm(UserRegistrationForm):
    shop_name = forms.CharField(max_length=255, required=True)
    gst_number = forms.CharField(max_length=20, required=False)
    business_address = forms.CharField(widget=forms.Textarea, required=True)
    gst_certificate = forms.FileField(required=False)
    kyc_document = forms.FileField(required=False)
    shop_image = forms.ImageField(required=False)

    class Meta(UserRegistrationForm.Meta):
        fields = UserRegistrationForm.Meta.fields + ['shop_name', 'gst_number', 'business_address', 'gst_certificate', 'kyc_document', 'shop_image']

from .models import ResellerProfile
class ResellerProfileForm(forms.ModelForm):
    class Meta:
        model = ResellerProfile
        fields = ['shop_name', 'gst_number', 'business_address', 'gst_certificate', 'kyc_document', 'shop_image']
        widgets = {
            'business_address': forms.Textarea(attrs={'rows': 3}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'mobile']

class ResellerProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = ResellerProfile
        fields = ['shop_name', 'gst_number', 'business_address', 'gst_certificate', 'kyc_document', 'shop_image']
        widgets = {
            'business_address': forms.Textarea(attrs={'rows': 3}),
        }
