from django.contrib import admin
from .models import DeliveryToken, DownloadLog


class DownloadLogInline(admin.TabularInline):
    model = DownloadLog
    extra = 0
    readonly_fields = ['ip_address', 'user_agent', 'downloaded_at']
    can_delete = False


@admin.register(DeliveryToken)
class DeliveryTokenAdmin(admin.ModelAdmin):
    list_display = ['token', 'order', 'order_item', 'download_count', 'max_downloads', 'is_active', 'expires_at', 'created_at']
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['token', 'order__id']
    readonly_fields = ['token', 'download_count', 'created_at']
    inlines = [DownloadLogInline]
    date_hierarchy = 'created_at'
    list_per_page = 12
    list_select_related = ['order', 'order_item']


@admin.register(DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ['token', 'ip_address', 'downloaded_at']
    list_filter = ['downloaded_at']
    search_fields = ['token__token', 'ip_address']
    readonly_fields = ['downloaded_at']
    list_per_page = 12
