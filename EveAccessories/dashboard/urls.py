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

    path('settings/', SettingsView.as_view(), name='admin_settings'),

    path('product-lists/', ProductListsView.as_view(), name='admin_product_lists'),
    path('product-lists/add', AddProductListView.as_view(), name='add_product_list'),
    path('product-lists/edit/<pk>', EditProductListView.as_view(), name='edit_product_list'),
    path('product-lists/delete/<pk>', DeleteProductListView.as_view(), name='delete_product_list'),

    path('sections/', SectionsView.as_view(), name='admin_sections'),
    path('sections/add', AddSectionView.as_view(), name='add_section'),
    path('sections/edit/<pk>', EditSectionView.as_view(), name='edit_section'),
    path('sections/delete/<pk>', DeleteSectionView.as_view(), name='delete_section'),
]
