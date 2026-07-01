from django.contrib import admin
from .models import PageView, SalesReport


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['url', 'user', 'ip_address', 'referrer', 'created_at']
    list_filter = ['created_at']
    search_fields = ['url', 'ip_address', 'user__email']
    raw_id_fields = ['user']
    readonly_fields = ['url', 'user', 'ip_address', 'user_agent', 'referrer', 'created_at']
    date_hierarchy = 'created_at'
    list_per_page = 12


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_orders', 'total_revenue_usd', 'total_revenue_gbp', 'new_users']
    list_filter = ['date']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    list_per_page = 12
