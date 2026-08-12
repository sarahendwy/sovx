from django.contrib import admin
from .models import Product, ProductBuyingOption


# Register your models here.
class ProductBuyingOptionInline(admin.StackedInline):
    model = ProductBuyingOption
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductBuyingOptionInline,
    ]


admin.site.register(Product, ProductAdmin)
