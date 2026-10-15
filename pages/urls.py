from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("coming-soon/<slug:feature_name>/", views.ComingSoonView.as_view(), name="coming_soon"),
    path("terms/", views.TermsOfServiceView.as_view(), name="terms"),
    path("privacy/", views.PrivacyPolicyView.as_view(), name="privacy"),
]