from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ResellerProfile

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'role', 'mobile', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'mobile', 'is_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'mobile', 'is_verified')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ResellerProfile)
