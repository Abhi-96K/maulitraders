from django.shortcuts import redirect
from django.urls import reverse
from .models import CustomUser, ResellerProfile

class ResellerApprovalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.role == CustomUser.Role.RESELLER:
            try:
                profile = request.user.reseller_profile
                if not profile.is_approved:
                    # List of allowed paths for unapproved resellers
                    allowed_paths = [
                        reverse('logout'),
                        reverse('pending-approval'),
                        reverse('verify-otp'),
                        reverse('resend-otp'),
                        reverse('verify-email-entry'),
                        '/static/',
                        '/media/',
                    ]
                    
                    # Check if current path starts with any allowed path
                    is_allowed = any(request.path.startswith(path) for path in allowed_paths)
                    
                    if not is_allowed:
                        return redirect('pending-approval')
                        
            except ResellerProfile.DoesNotExist:
                # Should not happen for role=RESELLER, but safe fallback
                pass

        response = self.get_response(request)
        return response
