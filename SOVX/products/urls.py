from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('articles', index, name='articles'),
    path('about', index, name='about'),
    path('products', ProductListView.as_view(), name='products'),
    path('product/<int:pk>', ProductView.as_view(), name='product'),
]
    