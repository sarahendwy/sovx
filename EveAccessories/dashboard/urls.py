from django.urls import path
from .views import *

urlpatterns = [
    path('', DashboardView.as_view(), name='admin_dashboard'),
    
    path('orders/', OrdersView.as_view(), name='admin_orders'),
    path('orders/<order_id>/confirm', confirm_order, name='confirm_order'),
    path('orders/<order_id>/reject', reject_order, name='cancel_order'),
    path('orders/<order_id>/deliver', deliver_order, name='deliver_order'),
    path('orders/<order_id>/complete', complete_order, name='complete_order'),

    path('products/', ProductsView.as_view(), name='admin_products'),
    path('products/add', AddProductView.as_view(), name='add_products'),
    path('products/edit/<pk>', EditProductView.as_view(), name='edit_product'),
    path('products/delete/<pk>', DeleteProductView.as_view(), name='delete_product'),

    path('categories/', CategoriesView.as_view(), name='admin_categories'),
    path('categories/add', AddCategoryView.as_view(), name='add_categories'),
    path('categories/delete/<pk>', DeleteCategoryView.as_view(), name='delete_category'),

    path('settings/', SettingsView.as_view(), name='admin_settings'),
]
