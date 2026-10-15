from django.urls import path

from . import views

app_name = "listings"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("browse/", views.ProductListView.as_view(), name="browse"),
    path("category/<slug:slug>/", views.ProductListView.as_view(), name="category"),
    path("product/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]
