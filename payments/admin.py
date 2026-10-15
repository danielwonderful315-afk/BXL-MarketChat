from django.contrib import admin
from django.utils import timezone

from .models import Payment


@admin.action(description="Release payment to seller (manual escrow release)")
def release_to_seller(modeladmin, request, queryset):
    updated = queryset.filter(status="paid", escrow_status="held").update(
        escrow_status="released", released_at=timezone.now()
    )
    modeladmin.message_user(request, f"{updated} payment(s) released to seller.")


@admin.action(description="Refund to buyer")
def refund_to_buyer(modeladmin, request, queryset):
    updated = queryset.filter(status="paid", escrow_status="held").update(escrow_status="refunded")
    modeladmin.message_user(
        request,
        f"{updated} payment(s) marked refunded. NOTE: this only updates the record — "
        f"the actual refund still has to be issued manually via your Flutterwave dashboard.",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order", "total_amount", "status", "escrow_status",
        "created_at", "paid_at", "released_at",
    )
    list_filter = ("status", "escrow_status")
    search_fields = ("order__product__title", "tx_ref", "flutterwave_transaction_id")
    actions = [release_to_seller, refund_to_buyer]