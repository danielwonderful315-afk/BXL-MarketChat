from django.conf import settings
from django.db import models

from listings.models import Product


class Order(models.Model):
    """A buyer's request to purchase a product.

    NOTE: no payment gateway is wired up yet (Paystack/Flutterwave keys are
    still just stubs in settings). This records intent to buy and kicks off
    the delivery flow, but doesn't move real money. Wire up payment
    confirmation before treating 'confirmed' as anything financial.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders_as_buyer")
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders_as_seller")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orders")
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} — {self.product.title}"

    @property
    def total_price(self):
        return self.product.price * self.quantity
