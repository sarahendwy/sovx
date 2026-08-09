from django.urls import path
from .views import *

urlpatterns = [
    path('create', CreateOrder.as_view(), name='create_order'),
    path('success/<int:order_id>', order_success, name='order_success'),
    path('details/<int:pk>', OrderDetails.as_view(), name='order_details'),
    path('sell', SellWithUs.as_view(), name='sell_with_us'),
    path('contact', ContactUs.as_view(), name='contact'),
]
