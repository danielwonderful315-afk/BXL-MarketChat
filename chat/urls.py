from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.InboxView.as_view(), name="inbox"),
    path("start/<slug:product_slug>/", views.StartConversationView.as_view(), name="start"),
    path("<int:conversation_id>/", views.ConversationView.as_view(), name="conversation"),
]
