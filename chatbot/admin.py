from django.contrib import admin
from .models import ChatMessage, ChatSession


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['session_id', 'user__email']
    date_hierarchy = 'created_at'
    list_per_page = 12
    list_select_related = ['user']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'role', 'user', 'legacy_session_id', 'truncated_message', 'truncated_response', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['message', 'response', 'user__email', 'legacy_session_id']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'session']
    date_hierarchy = 'created_at'
    list_per_page = 12
    list_select_related = ['user', 'session']

    def truncated_message(self, obj):
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    truncated_message.short_description = 'Message'

    def truncated_response(self, obj):
        return obj.response[:80] + '...' if len(obj.response) > 80 else obj.response
    truncated_response.short_description = 'Response'
