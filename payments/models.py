import uuid

from django.db import models

from orders.models import Order


class Payment(models.Model):
    """Escrow payment for an order — same flow as TrustDecent: buyer pays
    upfront, platform holds the funds, seller is only paid out once the
    buyer confirms the item was actually received.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]
    ESCROW_CHOICES = [
        ("held", "Held in Escrow"),
        ("released", "Released to Seller"),
        ("refunded", "Refunded to Buyer"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Product total")
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    tx_ref = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    flutterwave_transaction_id = models.CharField(max_length=100, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    escrow_status = models.CharField(max_length=10, choices=ESCROW_CHOICES, default="held")

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment for Order #{self.order_id} — {self.get_status_display()}"