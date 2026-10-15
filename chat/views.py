from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views import generic

from listings.models import Product

from .models import Conversation


class InboxView(LoginRequiredMixin, generic.ListView):
    """Chat list panel, left side of Img 4."""

    template_name = "chat/inbox.html"
    context_object_name = "conversations"

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(Q(buyer=user) | Q(seller=user)).select_related("product")


class ConversationView(LoginRequiredMixin, generic.DetailView):
    """Open thread view, right side of Img 4."""

    model = Conversation
    template_name = "chat/conversation.html"
    context_object_name = "conversation"
    pk_url_kwarg = "conversation_id"

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(Q(buyer=user) | Q(seller=user))


class StartConversationView(LoginRequiredMixin, generic.View):
    """Hit from a product page's 'Chat Seller' button (Img 7) — finds or creates the thread."""

    def post(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug)
        conversation, _ = Conversation.objects.get_or_create(
            product=product, buyer=request.user, seller=product.seller,
        )
        from django.shortcuts import redirect
        return redirect("chat:conversation", conversation_id=conversation.pk)
