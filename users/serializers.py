from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ResellerProfile, OTPVerification
import random
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'mobile', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            mobile=validated_data['mobile'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=User.Role.CUSTOMER
        )
        self.generate_otp(user)
        return user

    def generate_otp(self, user):
        otp_code = str(random.randint(100000, 999999))
        OTPVerification.objects.create(
            user=user,
            otp=otp_code,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        # TODO: Send OTP via Email/SMS
        print(f"OTP for {user.email}: {otp_code}")

class ResellerProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_mobile = serializers.CharField(source='user.mobile', read_only=True)

    class Meta:
        model = ResellerProfile
        fields = ('id', 'user_email', 'user_mobile', 'shop_name', 'gst_number', 'business_address', 'is_approved', 'gst_certificate', 'kyc_document', 'shop_image')

class ResellerRegistrationSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()
    
    class Meta:
        model = ResellerProfile
        fields = ('user', 'shop_name', 'gst_number', 'business_address', 'gst_certificate', 'kyc_document', 'shop_image')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserRegistrationSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        user.role = User.Role.RESELLER
        user.save()
        
        reseller_profile = ResellerProfile.objects.create(user=user, **validated_data)
        return reseller_profile

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        otp_record = OTPVerification.objects.filter(
            user=user,
            otp=otp,
            is_verified=False,
            expires_at__gt=timezone.now()
        ).first()

        if not otp_record:
            raise serializers.ValidationError("Invalid or expired OTP")

        return data

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()
        
        otp_record = OTPVerification.objects.filter(
            user=user,
            otp=self.validated_data['otp']
        ).first()
        otp_record.is_verified = True
        otp_record.save()
        return user
