from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from products.sitemaps import StaticViewSitemap, ProductSitemap, ArticleSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'articles': ArticleSitemap,
}

urlpatterns = ([
                   path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
                   path('admin/', admin.site.urls),
                   path('dashboard/', include('dashboard.urls')),
                   path('', include('products.urls')),
                   path('orders/', include('orders.urls')),
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
               + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
