from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'read', 'created_at']
    list_filter = ['read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    date_hierarchy = 'created_at'
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']
    list_per_page = 12

    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('read', 'created_at')
        }),
    )

    actions = ['mark_read', 'mark_unread']

    @admin.action(description='Mark selected messages as read')
    def mark_read(self, request, queryset):
        count = queryset.update(read=True)
        self.message_user(request, f'{count} message(s) marked as read.')

    @admin.action(description='Mark selected messages as unread')
    def mark_unread(self, request, queryset):
        count = queryset.update(read=False)
        self.message_user(request, f'{count} message(s) marked as unread.')
