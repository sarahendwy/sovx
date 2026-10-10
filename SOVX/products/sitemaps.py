from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from dashboard.models import Article
from .models import Product


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return ["index", "products", "articles", "about"]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return Product.objects.order_by("pk")

    def lastmod(self, obj):
        return obj.updated_at


class ArticleSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Article.objects.order_by("pk")

    def lastmod(self, obj):
        return obj.created_at
