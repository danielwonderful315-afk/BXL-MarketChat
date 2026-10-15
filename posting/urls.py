from django.urls import path

from . import views

app_name = "posting"

urlpatterns = [
    path("", views.PostItemView.as_view(), name="post_item"),
]
