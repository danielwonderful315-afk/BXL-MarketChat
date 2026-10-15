from datetime import timedelta

from django.conf import settings as django_settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom user so we can attach marketplace-specific fields from day one."""

    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=120, blank=True, help_text="e.g. Awka, Anambra")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    is_verified_seller = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    # OTP-based verification — is_active stays False until one of these is confirmed.
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class SellerProfile(models.Model):
    """Extra public-facing profile info shown on a seller's storefront page."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    store_name = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    response_rate = models.PositiveSmallIntegerField(default=0, help_text="Percent, 0-100")

    def __str__(self):
        return self.store_name or self.user.username


class OTP(models.Model):
    """One-time code for verifying a user's email or phone at signup (or on resend)."""

    CHANNEL_CHOICES = [
        ("email", "Email"),
        ("phone", "Phone"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default="email")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.channel} OTP for {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            minutes = getattr(django_settings, "OTP_EXPIRY_MINUTES", 10)
            self.expires_at = timezone.now() + timedelta(minutes=minutes)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
