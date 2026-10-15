from django.conf import settings
from django.db import models

from listings.models import Product


class Conversation(models.Model):
    """One thread per (product, buyer) pair — mirrors the chat list in Img 4."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="conversations")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations_as_buyer")
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations_as_seller")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "buyer")

    def __str__(self):
        return f"{self.buyer} <-> {self.seller} on {self.product}"

    @property
    def room_group_name(self):
        return f"chat_{self.pk}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
