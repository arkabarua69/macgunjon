from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Product, Category
from blog.models import BlogPost


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return ['pages:about', 'pages:contact', 'pages:faq', 'pages:privacy', 'pages:terms']

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Product.objects.filter(available=True)

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Category.objects.all()


class BlogSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return BlogPost.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.updated_at
