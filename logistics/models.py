from django.conf import settings
from django.db import models

from orders.models import Order

NIGERIAN_STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue",
    "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu",
    "FCT (Abuja)", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina",
    "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo",
    "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara",
]
STATE_CHOICES = [(s, s) for s in NIGERIAN_STATES]


class Rider(models.Model):
    """A delivery rider/driver the admin can manually dispatch to a request."""

    VEHICLE_CHOICES = [
        ("motorcycle", "Motorcycle"),
        ("car", "Car"),
        ("van", "Van"),
        ("truck", "Truck"),
    ]

    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=12, choices=VEHICLE_CHOICES)
    state = models.CharField(max_length=30, choices=STATE_CHOICES, help_text="Where this rider is based")
    is_active = models.BooleanField(default=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="rider_profile", help_text="Login account for this rider, if they have one"
    )

    def __str__(self):
        return f"{self.name} ({self.get_vehicle_type_display()}, {self.state})"


class DeliveryRequest(models.Model):
    """A buyer's chosen delivery route for an order. Admin reviews the
    pickup/dropoff details and manually assigns an appropriate rider —
    there's no live distance/routing calculation, this is a manual dispatch
    workflow by design.
    """

    VEHICLE_CHOICES = Rider.VEHICLE_CHOICES

    # Flat estimated rates per vehicle tier — matches the client's mockup
    # pricing (Img 5/8). Not distance-based since there's no maps API wired up.
    VEHICLE_RATES = {
        "motorcycle": 3000,
        "car": 5000,
        "van": 7000,
        "truck": 10000,
    }

    STATUS_CHOICES = [
        ("pending", "Pending Assignment"),
        ("assigned", "Rider Assigned"),
        ("picked_up", "Picked Up"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="delivery_request")
    pickup_address = models.CharField(max_length=255, help_text="Seller's pickup location")
    dropoff_address = models.CharField(max_length=255, help_text="Buyer's delivery address")
    state = models.CharField(max_length=30, choices=STATE_CHOICES)
    vehicle_type = models.CharField(max_length=12, choices=VEHICLE_CHOICES)
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Admin can override the estimate once the rider confirms the actual distance/cost"
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    assigned_rider = models.ForeignKey(
        Rider, on_delete=models.SET_NULL, null=True, blank=True, related_name="deliveries"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Delivery for Order #{self.order_id} — {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.estimated_price:
            self.estimated_price = self.VEHICLE_RATES.get(self.vehicle_type, 0)
        super().save(*args, **kwargs)