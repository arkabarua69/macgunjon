from django.contrib import admin
from .models import Payment, Refund


class RefundInline(admin.TabularInline):
    model = Refund
    extra = 0
    readonly_fields = ['amount', 'reason', 'status', 'stripe_refund_id', 'created_at']
    can_delete = False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'gateway', 'transaction_id', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'gateway', 'currency', 'created_at']
    search_fields = ['transaction_id', 'order__id']
    readonly_fields = ['raw_response', 'created_at', 'updated_at']
    inlines = [RefundInline]
    date_hierarchy = 'created_at'
    list_per_page = 12
    list_select_related = ['order']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'amount', 'status', 'stripe_refund_id', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['stripe_refund_id', 'payment__transaction_id']
    readonly_fields = ['created_at']
    list_per_page = 12
