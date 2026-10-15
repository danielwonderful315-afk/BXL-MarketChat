from django.urls import path

from . import views

app_name = "logistics"

urlpatterns = [
    path("create/<int:order_id>/", views.CreateDeliveryRequestView.as_view(), name="create_delivery"),
    path("track/<int:order_id>/", views.TrackDeliveryView.as_view(), name="track_delivery"),
    path("rider/", views.RiderDashboardView.as_view(), name="rider_dashboard"),
    path("rider/accept/<int:pk>/", views.AcceptJobView.as_view(), name="accept_job"),
    path("rider/update/<int:pk>/", views.UpdateJobStatusView.as_view(), name="update_job_status"),
    path("become-a-rider/", views.RiderSignUpView.as_view(), name="rider_signup"),
]