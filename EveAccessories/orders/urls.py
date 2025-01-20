from django.urls import path
from .views import *

urlpatterns = [
    path('cart', CartView.as_view(), name='cart'),
    path('cart/remove/<int:product_id>', remove_from_cart, name='remove_from_cart'),
    path('order/<pk>', OrderDetails.as_view(), name='order_details'),
    path('order/create', CreateOrder.as_view(), name='create_order'),
    path('order/success', OrderSuccess.as_view(), name='order_success'),
]
