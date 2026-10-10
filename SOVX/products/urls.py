from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('articles',ArticleView.as_view(), name='articles'),
    path('articles/<int:pk>', ArticleDetailView.as_view(), name='article'),
    path('about', AboutView.as_view(), name='about'),
    path('products', ProductListView.as_view(), name='products'),
    path('product/<int:pk>', ProductView.as_view(), name='product'),
]   
    