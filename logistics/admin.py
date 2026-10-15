from django.contrib import admin

from .models import DeliveryRequest, Rider


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number", "vehicle_type", "state", "is_active")
    list_filter = ("vehicle_type", "state", "is_active")
    search_fields = ("name", "phone_number")
    autocomplete_fields = ["user"]


@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(admin.ModelAdmin):
    """This is the dispatch board: admin sees every request, sorted newest
    first, and picks an appropriate active rider for the state/vehicle type
    directly from the dropdown — no automation, deliberately manual.
    """

    list_display = (
        "id", "order", "state", "dropoff_address", "vehicle_type",
        "status", "assigned_rider", "estimated_price", "final_price", "created_at",
    )
    list_filter = ("status", "state", "vehicle_type")
    search_fields = ("dropoff_address", "pickup_address", "order__product__title")
    list_editable = ("status", "assigned_rider", "final_price")
    autocomplete_fields = ["assigned_rider"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("order", "order__product", "assigned_rider")

    