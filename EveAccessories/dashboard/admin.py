from django.contrib import admin
from .models import Setting, Governorate, City, ShippingFee
# Register your models here.
admin.site.register(Setting)
admin.site.register(Governorate)
admin.site.register(City)
admin.site.register(ShippingFee)