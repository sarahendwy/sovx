from django.urls import path
from .views import *

urlpatterns = [
    path('', DashboardView.as_view(), name='admin_dashboard'),
    
    path('orders/', OrdersView.as_view(), name='admin_orders'),
    path('orders/<order_id>/', OrderDetailsView.as_view(), name='order_details'),
    path('orders/<order_id>/status', change_order_status, name='change_order_status'),

    path('contact-requests/', ContactUsRequestsView.as_view(), name='admin_contact_requests'),
    path('sell-with-us-requests/', SellWithUsRequestsView.as_view(), name='admin_sell_with_us_requests'),

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

    path('hero-slides/', HeroSlidesView.as_view(), name='admin_hero_slides'),
    path('hero-slides/add', AddHeroSlideView.as_view(), name='add_hero_slide'),
    path('hero-slides/edit/<pk>', EditHeroSlideView.as_view(), name='edit_hero_slide'),
    path('hero-slides/delete/<pk>', DeleteHeroSlideView.as_view(), name='delete_hero_slide'),

    path('sell-with-us-cards/',SellWithUsCardsView.as_view(), name='admin_sell_with_us_cards'),
    path('sell-with-us-cards/add', AddSellWithUsCardView.as_view(), name='add_sell_with_us_card'),
    path('sell-with-us-cards/edit/<pk>', EditSellWithUsCardView.as_view(), name='edit_sell_with_us_card'),
    path('sell-with-us-cards/delete/<pk>', DeleteSellWithUsCardView.as_view(), name='delete_sell_with_us_card'),

    path('about-us-sections/', AboutUsSectionsView.as_view(), name='admin_about_us_sections'),
    path('about-us-sections/add', AddAboutUsSectionView.as_view(), name='add_about_us_section'),
    path('about-us-sections/edit/<pk>', EditAboutUsSectionView.as_view(), name='edit_about_us_section'),
    path('about-us-sections/delete/<pk>', DeleteAboutUsSectionView.as_view(), name='delete_about_us_section'),

    path('articles/', ArticlesView.as_view(), name='admin_articles'),
    path('articles/add', AddArticleView.as_view(), name='add_article'),
    path('articles/edit/<pk>', EditArticleView.as_view(), name='edit_article'),
    path('articles/delete/<pk>', DeleteArticleView.as_view(), name='delete_article'),

    path('reviews/', ReviewsView.as_view(), name='admin_reviews'),
    path('reviews/add', AddReviewView.as_view(), name='add_review'),
    path('reviews/edit/<pk>', EditReviewView.as_view(), name='edit_review'),
    path('reviews/delete/<pk>', DeleteReviewView.as_view(), name='delete_review'),

    path('shipping-fees/', ShippingFeesView.as_view(), name='admin_shipping_fees'),
    path('shipping-fees/add', AddShippingFeeView.as_view(), name='add_shipping_fee'),
    path('shipping-fees/edit/<pk>', EditShippingFeeView.as_view(), name='edit_shipping_fee'),
    path('shipping-fees/delete/<pk>', DeleteShippingFeeView.as_view(), name='delete_shipping_fee'),

    path('api/cities/', get_cities, name='api_cities'),
    path('api/shipping-fee/', get_shipping_fee, name='api_shipping_fee'),
]
