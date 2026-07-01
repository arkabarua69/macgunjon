from django.db import models
from django.conf import settings


class PageView(models.Model):
    url = models.CharField(max_length=500)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.url} - {self.created_at}'


class SalesReport(models.Model):
    date = models.DateField(unique=True)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenue_gbp = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_users = models.PositiveIntegerField(default=0)
    top_product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'Report {self.date}'
