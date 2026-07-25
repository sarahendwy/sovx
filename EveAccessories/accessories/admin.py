from django.contrib import admin
from .models import Product, ProductImage


# Register your models here.
class ImageInline(admin.StackedInline):
    model = ProductImage
    extra = 0
    fields = ("image", "image_url")


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ImageInline,
    ]


admin.site.register(Product, ProductAdmin)
