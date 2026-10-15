from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from orders.models import Order

from .paystack import PaystackError, initiate_payment, verify_transaction
from .models import Payment


class InitiatePaymentView(LoginRequiredMixin, generic.View):
    """Called right after the buyer picks a delivery option. Creates the
    Payment record (product price + delivery fee) and sends them to
    Paystack's hosted checkout."""

    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, buyer=request.user)

        delivery_fee = Decimal("0")
        if hasattr(order, "delivery_request"):
            dr = order.delivery_request
            delivery_fee = dr.final_price or dr.estimated_price

        payment, _ = Payment.objects.get_or_create(
            order=order,
            defaults={
                "amount": order.total_price,
                "delivery_fee": delivery_fee,
                "total_amount": order.total_price + delivery_fee,
            },
        )

        if payment.status == "paid":
            return redirect("logistics:track_delivery", order_id=order.pk)

        callback_url = request.build_absolute_uri(reverse("payments:callback"))

        try:
            checkout_url = initiate_payment(payment, request.user, callback_url)
        except (PaystackError, Exception) as e:
            messages.error(request, f"Couldn't start payment right now: {e}")
            return render(request, "payments/payment_error.html", {"order": order})

        return redirect(checkout_url)


class PaymentCallbackView(generic.View):
    """Paystack redirects here after checkout with just ?reference=xxx.
    We NEVER trust that alone — always re-verify with Paystack's API
    server-to-server before marking anything paid."""

    def get(self, request):
        reference = request.GET.get("reference") or request.GET.get("trxref")

        if not reference:
            messages.error(request, "Payment reference missing.")
            return redirect("orders:my_orders")

        payment = get_object_or_404(Payment, tx_ref=reference)
        order = payment.order

        try:
            result = verify_transaction(reference)
        except Exception:
            messages.error(request, "Couldn't confirm payment — contact support if you were charged.")
            return redirect("orders:order_detail", pk=order.pk)

        data = result.get("data", {})
        # Paystack amounts are in kobo — convert back to naira before comparing
        amount_paid_naira = Decimal(str(data.get("amount", 0))) / 100

        verified_ok = (
            result.get("status") is True
            and data.get("status") == "success"
            and amount_paid_naira >= payment.total_amount
            and data.get("currency") == "NGN"
        )

        if verified_ok:
            payment.status = "paid"
            payment.flutterwave_transaction_id = str(reference)  # reused field, holds Paystack reference too
            payment.paid_at = timezone.now()
            payment.save()
            order.status = "confirmed"
            order.save()
            messages.success(request, "Payment received — held safely until you confirm delivery.")
            return redirect("logistics:track_delivery", order_id=order.pk)

        payment.status = "failed"
        payment.save()
        messages.error(request, "Payment verification failed.")
        return redirect("orders:order_detail", pk=order.pk)


class ConfirmReceivedView(LoginRequiredMixin, generic.View):
    """Buyer confirms they got the item — this is what releases escrow to
    the seller. Only the buyer can do this, and only once delivery shows
    'delivered'."""

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, buyer=request.user)
        payment = get_object_or_404(Payment, order=order, status="paid")

        delivery_status = getattr(getattr(order, "delivery_request", None), "status", None)
        if delivery_status != "delivered":
            messages.error(request, "You can only confirm receipt after the item shows as delivered.")
            return redirect("logistics:track_delivery", order_id=order.pk)

        payment.escrow_status = "released"
        payment.released_at = timezone.now()
        payment.save()
        order.status = "completed"
        order.save()
        messages.success(request, "Thanks — payment has been released to the seller.")
        return redirect("logistics:track_delivery", order_id=order.pk)
