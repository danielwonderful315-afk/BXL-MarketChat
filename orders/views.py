from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from listings.models import Product

from .models import Order


class MyOrdersView(LoginRequiredMixin, generic.ListView):
    """Wires up the long-dead 'My Orders' nav link."""

    template_name = "orders/my_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).select_related("product")


class BuyNowView(LoginRequiredMixin, generic.View):
    """Hit from the 'Buy Now' button on a product page. Creates the order,
    then sends the buyer straight into the delivery request flow.

    No payment is actually processed here — see the note on the Order model.
    """

    def post(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug, status="active")
        order = Order.objects.create(
            buyer=request.user,
            seller=product.seller,
            product=product,
        )
        return redirect("logistics:create_delivery", order_id=order.pk)


class OrderDetailView(LoginRequiredMixin, generic.DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(Q(buyer=user) | Q(seller=user))