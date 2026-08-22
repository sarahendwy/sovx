from django.urls import path
from .views import *

urlpatterns = [
    path('create', CreateOrder.as_view(), name='create_order'),
    path('sell', SellWithUs.as_view(), name='sell_with_us'),
    path('contact', ContactUs.as_view(), name='contact_us'),
    path('thank-you', ThankYou.as_view(), name='thank_you'),
]
