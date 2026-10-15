from django.views import generic


class ComingSoonView(generic.TemplateView):
    """One reusable page for any feature that isn't built yet — takes the
    feature name from the URL so it can serve BXL Deals, Stores, Services,
    BXL Global, Track Order, Help & Support, etc. without a separate view each."""

    template_name = "pages/coming_soon.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["feature_name"] = kwargs.get("feature_name", "This feature")
        return ctx


class TermsOfServiceView(generic.TemplateView):
    template_name = "pages/terms.html"


class PrivacyPolicyView(generic.TemplateView):
    template_name = "pages/privacy.html"