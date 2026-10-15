from django import forms

from accounts.forms import SignUpForm

from .models import DeliveryRequest, Rider
from accounts.forms import SignUpForm
from .models import STATE_CHOICES


class DeliveryRequestForm(forms.ModelForm):
    class Meta:
        model = DeliveryRequest
        fields = ["dropoff_address", "state", "vehicle_type"]
        widgets = {
            "dropoff_address": forms.TextInput(attrs={"placeholder": "Full delivery address"}),
        }


class RiderSignUpForm(SignUpForm):
    """Reuses the normal signup form's fields (username, email, phone,
    password) and adds rider-specific ones on top."""

    full_name = forms.CharField(max_length=100, label="Full Name")
    vehicle_type = forms.ChoiceField(choices=Rider.VEHICLE_CHOICES)
    state = forms.ChoiceField(choices=STATE_CHOICES)        