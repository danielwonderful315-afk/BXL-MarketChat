from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from .forms import SignUpForm
from .models import OTP, User
from .otp import create_and_send_otp

class RoleAwareLoginView(LoginView):
    """Same login form everyone uses — riders just get sent to their
    dashboard instead of the homepage afterward."""

    template_name = "accounts/login.html"

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, "rider_profile"):
            return reverse_lazy("logistics:rider_dashboard")
        return super().get_success_url()

    
class SignUpView(generic.CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # locked out until they verify
        user.save()

        create_and_send_otp(user, channel="email")
        self.request.session["pending_verification_user_id"] = user.pk
        return redirect("accounts:verify_otp")


class VerifyOTPView(generic.View):
    """Enter the 6-digit code sent at signup (or via resend)."""

    template_name = "accounts/verify_otp.html"

    def _pending_user(self, request):
        user_id = request.session.get("pending_verification_user_id")
        if not user_id:
            return None
        return User.objects.filter(pk=user_id, is_active=False).first()

    def get(self, request):
        user = self._pending_user(request)
        if not user:
            return redirect("accounts:signup")
        return render(request, self.template_name, {"pending_user": user})

    def post(self, request):
        user = self._pending_user(request)
        if not user:
            return redirect("accounts:signup")

        code = request.POST.get("code", "").strip()
        otp = OTP.objects.filter(user=user, code=code, is_used=False).first()

        if otp and otp.is_valid():
            otp.is_used = True
            otp.save()

            user.is_active = True
            if otp.channel == "email":
                user.is_email_verified = True
            elif otp.channel == "phone":
                user.is_phone_verified = True
            user.save()

            del request.session["pending_verification_user_id"]
            messages.success(request, "You're verified — you can log in now.")
            return redirect("accounts:login")

        messages.error(request, "That code is incorrect or has expired.")
        return render(request, self.template_name, {"pending_user": user})


class ResendOTPView(generic.View):
    def post(self, request):
        user_id = request.session.get("pending_verification_user_id")
        if user_id:
            user = get_object_or_404(User, pk=user_id, is_active=False)
            create_and_send_otp(user, channel="email")
            messages.info(request, "A new code has been sent to your email.")
        return redirect("accounts:verify_otp")


class ProfileView(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = "accounts/profile.html"

    def get_object(self):
        return self.request.user


class SellerStorefrontView(generic.DetailView):
    """Public seller page — reviews, listings, response rate (see mockup Img 7)."""

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "accounts/storefront.html"
    context_object_name = "seller"
