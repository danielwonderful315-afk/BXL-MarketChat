"""
ASGI config for bxl_marketchat project.
Routes HTTP to Django views and WebSocket connections to Channels consumers.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bxl_marketchat.settings")

django_asgi_app = get_asgi_application()

import chat.routing  # noqa: E402  (must import after django_asgi_app is set up)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
