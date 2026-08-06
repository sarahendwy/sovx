from django.urls import path
from .views import *

urlpatterns = [
    path('cart', CartView.as_view(), name='cart'),
    path('cart/remove/<int:product_id>', remove_from_cart, name='remove_from_cart'),
    path('create', CreateOrder.as_view(), name='create_order'),
    path('success/<int:order_id>', order_success, name='order_success'),
    path('details/<int:pk>', OrderDetails.as_view(), name='order_details'),
    path('sell', SellWithUs.as_view(), name='sell_with_us'),
]
