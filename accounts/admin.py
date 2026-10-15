from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import OTP, SellerProfile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Marketplace info", {
            "fields": ("phone_number", "location", "avatar", "is_verified_seller", "wallet_balance"),
        }),
        ("Verification", {
            "fields": ("is_email_verified", "is_phone_verified"),
        }),
    )
    list_display = ("username", "email", "is_active", "is_email_verified", "location", "wallet_balance")
    search_fields = ["username", "email"]


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ("store_name", "user", "response_rate")


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("user", "channel", "code", "is_used", "created_at", "expires_at")
    list_filter = ("channel", "is_used")
