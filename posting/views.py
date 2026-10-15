from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils.text import slugify
from django.views import View

from .forms import ProductImageFormSet, ProductPostForm


class PostItemView(LoginRequiredMixin, View):
    """Multi-step 'Post Your Item' form: details, category, price, photos, location (Img 2)."""

    template_name = "posting/post_item.html"

    def get(self, request):
        form = ProductPostForm()
        formset = ProductImageFormSet()
        return render(request, self.template_name, {"form": form, "formset": formset})

    def post(self, request):
        form = ProductPostForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.slug = slugify(f"{product.title}-{request.user.username}")
            product.save()

            formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
            if formset.is_valid():
                formset.save()
                return redirect(product.get_absolute_url())
        else:
            formset = ProductImageFormSet(request.POST, request.FILES)

        return render(request, self.template_name, {"form": form, "formset": formset})
