from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.RoleAwareLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("verify/", views.VerifyOTPView.as_view(), name="verify_otp"),
    path("verify/resend/", views.ResendOTPView.as_view(), name="resend_otp"),
    path("me/", views.ProfileView.as_view(), name="profile"),
    path("seller/<str:username>/", views.SellerStorefrontView.as_view(), name="storefront"),
]
