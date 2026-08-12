from django.contrib import admin
from .models import Order, OrderEntry, OrderLog

admin.site.register(Order)
admin.site.register(OrderEntry)
admin.site.register(OrderLog)