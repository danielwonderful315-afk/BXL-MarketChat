from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.MyOrdersView.as_view(), name="my_orders"),
    path("buy/<slug:product_slug>/", views.BuyNowView.as_view(), name="buy_now"),
    path("<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
]
