from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('categories', CategoriesView.as_view(), name='categories'),
    path('products', ProductListView.as_view(), name='products'),
    path('product/<int:pk>', ProductView.as_view(), name='product'),
    path('cart', cart, name='cart'),
    path('about', about, name='about')
]
