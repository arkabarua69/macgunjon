from django.contrib import admin
from .models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'subject', 'status', 'order', 'sent_at', 'created_at']
    list_filter = ['status', 'sent_at', 'created_at']
    search_fields = ['recipient', 'subject', 'order__id']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_per_page = 12
    list_select_related = ['order']
