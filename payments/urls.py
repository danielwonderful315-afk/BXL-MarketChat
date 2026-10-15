from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("pay/<int:order_id>/", views.InitiatePaymentView.as_view(), name="initiate"),
    path("callback/", views.PaymentCallbackView.as_view(), name="callback"),
    path("confirm-received/<int:order_id>/", views.ConfirmReceivedView.as_view(), name="confirm_received"),
]