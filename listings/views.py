from django.db.models import F
from django.views import generic

from .models import Category, Product


class HomeView(generic.TemplateView):
    """Landing page: hero, categories, featured listings (see mockup Img 1)."""

    template_name = "listings/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["featured_products"] = Product.objects.filter(status="active")[:8]
        return ctx


class ProductListView(generic.ListView):
    """Browse products, optionally filtered by category (see mockup Img 3/10)."""

    model = Product
    template_name = "listings/product_list.html"
    context_object_name = "products"
    paginate_by = 24

    def get_queryset(self):
        qs = Product.objects.filter(status="active")
        category_slug = self.kwargs.get("slug")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(title__icontains=query)
        return qs


class ProductDetailView(generic.DetailView):
    """Single listing page: specs, seller card, chat CTA (see mockup Img 7)."""

    model = Product
    template_name = "listings/product_detail.html"
    context_object_name = "product"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Product.objects.filter(pk=obj.pk).update(views=F("views") + 1)
        return obj
