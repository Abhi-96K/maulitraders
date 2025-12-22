import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maulitraders.settings')
django.setup()

from users.models import CustomUser, ResellerProfile
from users.utils import send_html_email

def test_flow():
    print(">>> STARTING TEST FLOW")
    
    # 1. Create Test User
    email = f"test_reseller_{int(time.time())}@example.com"
    print(f"\n1. Creating Test User: {email}")
    user = CustomUser.objects.create_user(
        username=email,
        email=email,
        password='password123',
        first_name='Test',
        last_name='User',
        mobile=f"{int(time.time())}"[-10:] # Random mobile
    )
    print("   User created.")

    # 2. Simulate Upgrade (Create Profile)
    print("\n2. Simulating Reseller Upgrade...")
    profile = ResellerProfile.objects.create(
        user=user,
        shop_name="Test Shop",
        business_address="123 Test St"
    )
    user.role = CustomUser.Role.RESELLER
    user.is_verified = False
    user.save()
    print("   Profile created. Role set to RESELLER. is_verified=False.")
    
    # 3. Simulate Sending OTP Email (View Logic)
    print("\n3. Testing OTP Email Sending...")
    context = {
        'user': user,
        'shop_name': profile.shop_name,
        'otp_code': '123456'
    }
    send_html_email('Test OTP Email', 'emails/reseller_otp.html', context, [user.email])
    
    # 4. Simulate Admin Approval
    print("\n4. Simulating Admin Approval (Triggering Signals)...")
    profile.is_approved = True
    profile.save()
    print("   Profile saved with is_approved=True.")
    
    print("\n>>> TEST FLOW COMPLETE")

if __name__ == '__main__':
    test_flow()
