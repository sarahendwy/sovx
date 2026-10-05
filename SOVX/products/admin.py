from django.contrib import admin
from .models import Product, ProductBuyingOption, NutritionalValue


# Register your models here.
class ProductBuyingOptionInline(admin.StackedInline):
    model = ProductBuyingOption
    extra = 1

class NutritionalValueInline(admin.StackedInline):
    model = NutritionalValue
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductBuyingOptionInline,
        NutritionalValueInline
    ]


admin.site.register(Product, ProductAdmin)
