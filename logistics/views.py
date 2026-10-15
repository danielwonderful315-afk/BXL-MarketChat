from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic

from orders.models import Order

from .forms import DeliveryRequestForm
from .models import DeliveryRequest, Rider


class CreateDeliveryRequestView(LoginRequiredMixin, generic.View):
    """Buyer picks a delivery route/vehicle right after 'Buy Now' (Img 5/8:
    pickup/dropoff + vehicle tier selection)."""

    template_name = "logistics/create_delivery.html"

    def get_order(self, request, order_id):
        return get_object_or_404(Order, pk=order_id, buyer=request.user)

    def get(self, request, order_id):
        order = self.get_order(request, order_id)
        form = DeliveryRequestForm(initial={"dropoff_address": request.user.location})
        return render(request, self.template_name, {"order": order, "form": form})

    def post(self, request, order_id):
        order = self.get_order(request, order_id)
        form = DeliveryRequestForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.order = order
            delivery.pickup_address = order.product.location
            delivery.save()
            return redirect("payments:initiate", order_id=order.pk)
        return render(request, self.template_name, {"order": order, "form": form})


class TrackDeliveryView(LoginRequiredMixin, generic.DetailView):
    """Status view matching mockup Img 5/8's tracking screen — no live map,
    just the current manual-dispatch status."""

    model = DeliveryRequest
    template_name = "logistics/track_delivery.html"
    context_object_name = "delivery"
    pk_url_kwarg = "order_id"

    def get_object(self, queryset=None):
        order = get_object_or_404(Order, pk=self.kwargs["order_id"])
        if order.buyer != self.request.user and order.seller != self.request.user:
            from django.http import Http404
            raise Http404
        return get_object_or_404(DeliveryRequest, order=order)



from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic

from .models import DeliveryRequest


class RiderRequiredMixin:
    """Only lets in users who actually have a linked Rider profile."""

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, "rider_profile"):
            raise PermissionDenied("This account isn't set up as a rider.")
        return super().dispatch(request, *args, **kwargs)


class RiderDashboardView(LoginRequiredMixin, RiderRequiredMixin, generic.View):
    """Job board: available deliveries matching this rider's vehicle type
    and state, plus their currently assigned/in-progress jobs."""

    template_name = "logistics/rider_dashboard.html"

    def get(self, request):
        rider = request.user.rider_profile

        available_jobs = DeliveryRequest.objects.filter(
            status="pending",
            assigned_rider__isnull=True,
            vehicle_type=rider.vehicle_type,
            state=rider.state,
        ).select_related("order", "order__product")

        my_jobs = DeliveryRequest.objects.filter(
            assigned_rider=rider,
        ).exclude(status__in=["delivered", "cancelled"]).select_related("order", "order__product")

        return render(request, self.template_name, {
            "available_jobs": available_jobs,
            "my_jobs": my_jobs,
            "rider": rider,
        })


class AcceptJobView(LoginRequiredMixin, RiderRequiredMixin, generic.View):
    """The critical bit: a single conditional UPDATE so two riders can't
    both claim the same job. No select_for_update needed — this pattern
    is safe on SQLite and Postgres alike."""

    def post(self, request, pk):
        rider = request.user.rider_profile

        updated = DeliveryRequest.objects.filter(
            pk=pk, assigned_rider__isnull=True, status="pending",
            vehicle_type=rider.vehicle_type, state=rider.state,
        ).update(assigned_rider=rider, status="assigned")

        if updated:
            messages.success(request, "Job accepted — it's yours now.")
        else:
            messages.error(request, "Sorry, someone else already grabbed that one.")

        return redirect("logistics:rider_dashboard")


class UpdateJobStatusView(LoginRequiredMixin, RiderRequiredMixin, generic.View):
    """Rider moves their own job forward: assigned -> picked_up -> in_transit -> delivered."""

    ALLOWED_TRANSITIONS = {
        "assigned": "picked_up",
        "picked_up": "in_transit",
        "in_transit": "delivered",
    }

    def post(self, request, pk):
        rider = request.user.rider_profile
        job = get_object_or_404(DeliveryRequest, pk=pk, assigned_rider=rider)

        next_status = self.ALLOWED_TRANSITIONS.get(job.status)
        if not next_status:
            messages.error(request, "This job can't be moved forward from its current status.")
            return redirect("logistics:rider_dashboard")

        job.status = next_status
        job.save()
        messages.success(request, f"Marked as {job.get_status_display()}.")
        return redirect("logistics:rider_dashboard")

from django.shortcuts import render, redirect
from accounts.otp import create_and_send_otp

from .forms import RiderSignUpForm


class RiderSignUpView(generic.View):
    """Riders sign up here directly instead of admin creating them manually.
    Goes through the same email OTP verification as everyone else."""

    template_name = "logistics/rider_signup.html"

    def get(self, request):
        form = RiderSignUpForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = RiderSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # locked out until they verify, same as normal signup
            user.save()

            Rider.objects.create(
                user=user,
                name=form.cleaned_data["full_name"],
                phone_number=form.cleaned_data["phone_number"],
                vehicle_type=form.cleaned_data["vehicle_type"],
                state=form.cleaned_data["state"],
            )

            create_and_send_otp(user, channel="email")
            request.session["pending_verification_user_id"] = user.pk
            return redirect("accounts:verify_otp")

        return render(request, self.template_name, {"form": form})    
    