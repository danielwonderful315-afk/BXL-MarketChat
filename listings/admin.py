from django.contrib import admin

from .models import Category, Favorite, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "seller", "category", "price", "status", "created_at")
    list_filter = ("status", "category", "condition")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductImageInline]


admin.site.register(Category)
admin.site.register(Favorite)
