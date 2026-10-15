import random

from django.conf import settings
from django.core.mail import send_mail

from .models import OTP


def generate_code():
    """6-digit numeric code, e.g. '042917'."""
    return f"{random.randint(0, 999999):06d}"


def create_and_send_otp(user, channel="email"):
    """Creates an OTP row and dispatches it over the requested channel.

    Any previous unused OTP for this user+channel is invalidated first, so a
    resend can't leave two valid codes floating around.
    """
    OTP.objects.filter(user=user, channel=channel, is_used=False).update(is_used=True)

    otp = OTP.objects.create(user=user, code=generate_code(), channel=channel)

    if channel == "email":
        _send_email_otp(user, otp.code)
    elif channel == "phone":
        _send_sms_otp(user, otp.code)
    else:
        raise ValueError(f"Unknown OTP channel: {channel}")

    return otp


def _send_email_otp(user, code):
    send_mail(
        subject="Your BXL Market Chat verification code",
        message=(
            f"Hi {user.username},\n\n"
            f"Your verification code is: {code}\n"
            f"This code expires in {settings.OTP_EXPIRY_MINUTES} minutes.\n\n"
            "If you didn't request this, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def _send_sms_otp(user, code):
    """Stub — wire this up to an SMS provider once one is chosen.

    Termii and Africa's Talking are the two most commonly used for Nigerian
    numbers; Twilio works too but is pricier for local delivery. Whichever
    is picked, the pattern is the same: POST the code + user.phone_number
    to their API using a key from settings (see TERMII_API_KEY in
    settings.py / .env.example as a placeholder).
    """
    if not settings.SMS_PROVIDER_API_KEY:
        # No provider configured yet — fail loud in dev instead of pretending it sent.
        print(f"[SMS OTP STUB] Would send code {code} to {user.phone_number}")
        return

    raise NotImplementedError(
        "SMS_PROVIDER_API_KEY is set but the actual provider request isn't wired up yet."
    )
