from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, ResellerRegistrationSerializer, OTPVerifySerializer, ResellerProfileSerializer
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import ResellerProfile

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class ResellerRegisterView(generics.CreateAPIView):
    serializer_class = ResellerRegistrationSerializer
    permission_classes = [AllowAny]

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminResellerListView(generics.ListAPIView):
    queryset = ResellerProfile.objects.filter(is_approved=False)
    serializer_class = ResellerProfileSerializer
    permission_classes = [IsAdminUser]

class AdminResellerActionView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            profile = ResellerProfile.objects.get(pk=pk)
        except ResellerProfile.DoesNotExist:
            return Response({"error": "Reseller not found"}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'approve':
            profile.is_approved = True
            profile.save()
            
            # Notifications are handled by signals, but if we want to be explicit here:
            # The signal will catch the save() and send notifications.
            
            return Response({"message": "Reseller approved"}, status=status.HTTP_200_OK)
        elif action == 'reject':
            profile.delete() # Or just mark as rejected
            # TODO: Send rejection email
            return Response({"message": "Reseller rejected"}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

# Frontend Views
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import OTPVerification, CustomUser
from django.utils import timezone
import random
import datetime

from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm, ResellerRegistrationForm

def generate_otp():
    return str(random.randint(100000, 999999))

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # Deactivate until verified
            user.is_verified = False
            user.save()
            
            # Generate OTP
            otp_code = generate_otp()
            expires_at = timezone.now() + datetime.timedelta(minutes=10)
            OTPVerification.objects.create(user=user, otp=otp_code, expires_at=expires_at)
            
            # Send OTP via Email
            subject = 'Verify your email - Mauli Traders'
            message = f'Your OTP for verification is: {otp_code}. It expires in 10 minutes.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            
            print(f"DEBUG: Attempting to send OTP to {user.email}")
            print(f"DEBUG: OTP Code: {otp_code}")
            
            try:
                send_mail(subject, message, from_email, recipient_list)
                print(f"DEBUG: Email sent successfully to {user.email}")
                messages.success(request, f"OTP sent to {user.email}. Please verify.")
            except Exception as e:
                print(f"DEBUG: Error sending email: {e}")
                messages.warning(request, f"OTP generated but email failed. Check console for OTP (Dev Mode).")
                print(f"OTP for {user.email}: {otp_code}")

            # Store user_id in session for verification
            request.session['verification_user_id'] = user.id
            return redirect('verify-otp')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

from .forms import UserRegistrationForm, ResellerRegistrationForm, ResellerProfileForm
from .utils import send_html_email, send_whatsapp_message

def reseller_register_view(request):
    if request.user.is_authenticated:
        # Upgrade Flow
        if request.method == 'POST':
            form = ResellerProfileForm(request.POST, request.FILES)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                
                # Temporarily set role to RESELLER but not verified
                request.user.role = CustomUser.Role.RESELLER
                request.user.is_verified = False # Force re-verification
                request.user.save()
                
                # Generate OTP
                otp_code = generate_otp()
                expires_at = timezone.now() + datetime.timedelta(minutes=10)
                OTPVerification.objects.create(user=request.user, otp=otp_code, expires_at=expires_at)
                
                # Send HTML OTP Email
                subject = 'Verify your Shop - Mauli Traders'
                context = {
                    'user': request.user,
                    'shop_name': profile.shop_name,
                    'otp_code': otp_code
                }
                send_html_email(subject, 'emails/reseller_otp.html', context, [request.user.email])
                
                request.session['verification_user_id'] = request.user.id
                messages.success(request, "Application submitted! Please verify your email again.")
                return redirect('verify-otp')
        else:
            form = ResellerProfileForm()
        return render(request, 'users/reseller_register.html', {'form': form, 'is_upgrade': True})
        
    else:
        # New Registration Flow
        if request.method == 'POST':
            form = ResellerRegistrationForm(request.POST, request.FILES)
            if form.is_valid():
                user = form.save(commit=False)
                user.role = CustomUser.Role.RESELLER
                user.is_active = False
                user.is_verified = False
                user.save()
                
                # Create Reseller Profile
                profile = ResellerProfile.objects.create(
                    user=user,
                    shop_name=form.cleaned_data['shop_name'],
                    gst_number=form.cleaned_data.get('gst_number'),
                    business_address=form.cleaned_data['business_address'],
                    gst_certificate=form.cleaned_data.get('gst_certificate'),
                    kyc_document=form.cleaned_data.get('kyc_document'),
                    shop_image=form.cleaned_data.get('shop_image')
                )
                
                # Generate OTP
                otp_code = generate_otp()
                expires_at = timezone.now() + datetime.timedelta(minutes=10)
                OTPVerification.objects.create(user=user, otp=otp_code, expires_at=expires_at)
                
                # Send HTML OTP Email
                subject = 'Verify your Shop - Mauli Traders'
                context = {
                    'user': user,
                    'shop_name': profile.shop_name,
                    'otp_code': otp_code
                }
                send_html_email(subject, 'emails/reseller_otp.html', context, [user.email])
                
                request.session['verification_user_id'] = user.id
                messages.success(request, f"OTP sent to {user.email}. Please verify.")
                return redirect('verify-otp')
        else:
            form = ResellerRegistrationForm()
        return render(request, 'users/reseller_register.html', {'form': form, 'is_upgrade': False})

def verify_otp_view(request):
    user_id = request.session.get('verification_user_id')
    if not user_id:
        return redirect('login')
        
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        try:
            user = CustomUser.objects.get(id=user_id)
            otp_record = OTPVerification.objects.filter(
                user=user, 
                otp=otp_input, 
                is_verified=False,
                expires_at__gt=timezone.now()
            ).first()
            
            if otp_record:
                otp_record.is_verified = True
                otp_record.save()
                
                user.is_verified = True
                user.is_active = True
                user.save()
                
                # Cleanup session
                del request.session['verification_user_id']
                
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                if user.role == CustomUser.Role.RESELLER:
                     messages.success(request, "Email verified! Your reseller account is pending approval.")
                     return redirect('pending-approval')
                
                messages.success(request, "Email verified successfully!")
                return redirect('home')
            else:
                messages.error(request, "Invalid or expired OTP.")
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('register')
            
    return render(request, 'users/verify_otp.html')

def resend_otp_view(request):
    user_id = request.session.get('verification_user_id')
    if not user_id:
        messages.error(request, "Session expired. Please enter your email to verify.")
        return redirect('verify-email-entry')
        
    try:
        user = CustomUser.objects.get(id=user_id)
        if user.is_verified:
            messages.info(request, "User already verified. Please login.")
            return redirect('login')
            
        # Generate new OTP
        otp_code = generate_otp()
        expires_at = timezone.now() + datetime.timedelta(minutes=10)
        
        # Update or create OTP record
        OTPVerification.objects.update_or_create(
            user=user,
            defaults={'otp': otp_code, 'expires_at': expires_at, 'is_verified': False}
        )
        
        # Send OTP via Email
        subject = 'Resend: Verify your email - Mauli Traders'
        message = f'Your new OTP for verification is: {otp_code}. It expires in 10 minutes.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        
        print(f"DEBUG: Resending OTP to {user.email}")
        print(f"DEBUG: OTP Code: {otp_code}")
        
        try:
            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, f"New OTP sent to {user.email}.")
        except Exception as e:
            print(f"DEBUG: Error sending email: {e}")
            messages.warning(request, "Failed to send email. Check console.")
            
        return redirect('verify-otp')
        
    except CustomUser.DoesNotExist:
        del request.session['verification_user_id']
        return redirect('register')

def verify_email_entry_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_verified:
                messages.info(request, "This email is already verified. Please login.")
                return redirect('login')
            
            # Generate OTP
            otp_code = generate_otp()
            expires_at = timezone.now() + datetime.timedelta(minutes=10)
            
            OTPVerification.objects.update_or_create(
                user=user,
                defaults={'otp': otp_code, 'expires_at': expires_at, 'is_verified': False}
            )
            
            # Send OTP via Email
            subject = 'Verify your email - Mauli Traders'
            message = f'Your OTP for verification is: {otp_code}. It expires in 10 minutes.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            
            print(f"DEBUG: Recovery OTP to {user.email}")
            print(f"DEBUG: OTP Code: {otp_code}")
            
            try:
                send_mail(subject, message, from_email, recipient_list)
                messages.success(request, f"OTP sent to {user.email}.")
            except Exception as e:
                print(f"DEBUG: Error sending email: {e}")
                messages.warning(request, "Failed to send email. Check console.")
            
            request.session['verification_user_id'] = user.id
            return redirect('verify-otp')
            
        except CustomUser.DoesNotExist:
            messages.error(request, "Email not found. Please register.")
            return redirect('register')
            
    return render(request, 'users/verify_email_entry.html')

def pending_approval_view(request):
    return render(request, 'users/pending_approval.html')

from .forms import UserUpdateForm, ResellerProfileUpdateForm

def update_profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        reseller_form = None
        
        if request.user.role == CustomUser.Role.RESELLER:
            reseller_form = ResellerProfileUpdateForm(request.POST, request.FILES, instance=request.user.reseller_profile)
            
        if user_form.is_valid() and (reseller_form is None or reseller_form.is_valid()):
            user_form.save()
            if reseller_form:
                reseller_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    
    return redirect('dashboard')
