from django.urls import path
from .views import *

urlpatterns = [
    path('', DashboardView.as_view(), name='admin_dashboard'),
    path('orders/', OrdersView.as_view(), name='admin_orders'),
    path('products/', ProductsView.as_view(), name='admin_products'),
    path('categories/', CategoriesView.as_view(), name='admin_categories'),
    path('settings/', SettingsView.as_view(), name='admin_settings'),
]
