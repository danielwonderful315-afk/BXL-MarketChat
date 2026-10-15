from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("bxl-admin-portal/", admin.site.urls),  # was "admin/"
    path("accounts/", include("accounts.urls")),
    path("sell/", include("posting.urls")),
    path("chat/", include("chat.urls")),
    path("orders/", include("orders.urls")),
    path("delivery/", include("logistics.urls")),
    path("payments/", include("payments.urls")),
    path("", include("listings.urls")),
    path("terms/", TemplateView.as_view(template_name="legal/terms.html"), name="terms"),
    path("privacy/", TemplateView.as_view(template_name="legal/privacy.html"), name="privacy"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()


