from django import forms

from listings.models import Product, ProductImage


class ProductPostForm(forms.ModelForm):
    """Maps to the 'Post Your Item' flow: title, description, category, price, location (Img 2)."""

    class Meta:
        model = Product
        fields = [
            "title", "description", "category", "price",
            "negotiable", "condition", "location",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"maxlength": 1000, "rows": 5}),
        }


ProductImageFormSet = forms.inlineformset_factory(
    Product,
    ProductImage,
    fields=["image", "is_primary"],
    extra=10,
    max_num=10,
    can_delete=True,
)
