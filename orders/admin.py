from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ['product', 'price', 'quantity']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'changed_by', 'note', 'created_at']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'email', 'status', 'currency', 'total_amount', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'id']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 12
    raw_id_fields = ['user']
    list_select_related = ['user']

    fieldsets = (
        ('Customer', {
            'fields': ('user', 'first_name', 'last_name', 'email')
        }),
        ('Shipping', {
            'fields': ('address', 'postal_code', 'city', 'country')
        }),
        ('Payment', {
            'fields': ('currency', 'subtotal', 'discount_amount', 'total_amount', 'tax_amount', 'stripe_payment_intent_id', 'status')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'internal_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_paid', 'mark_processing', 'mark_completed', 'mark_cancelled', 'mark_refunded']

    @admin.action(description='Mark selected orders as Paid')
    def mark_paid(self, request, queryset):
        count = queryset.filter(status='pending').update(status='paid')
        self.message_user(request, f'{count} order(s) marked as paid.')

    @admin.action(description='Mark selected orders as Processing')
    def mark_processing(self, request, queryset):
        count = queryset.filter(status='paid').update(status='processing')
        self.message_user(request, f'{count} order(s) marked as processing.')

    @admin.action(description='Mark selected orders as Completed')
    def mark_completed(self, request, queryset):
        count = queryset.filter(status='processing').update(status='completed')
        self.message_user(request, f'{count} order(s) marked as completed.')

    @admin.action(description='Cancel selected orders')
    def mark_cancelled(self, request, queryset):
        count = queryset.filter(status__in=['pending', 'paid', 'processing']).update(status='cancelled')
        self.message_user(request, f'{count} order(s) cancelled.')

    @admin.action(description='Refund selected orders')
    def mark_refunded(self, request, queryset):
        count = queryset.filter(status='paid').update(status='refunded')
        self.message_user(request, f'{count} order(s) marked as refunded.')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'price', 'quantity', 'get_cost']
    list_filter = ['order__status']
    search_fields = ['order__id', 'product__name']
    raw_id_fields = ['order', 'product']
    readonly_fields = ['get_cost']
    list_per_page = 12

    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Cost'


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'old_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['new_status', 'created_at']
    search_fields = ['order__id', 'note']
    raw_id_fields = ['order', 'changed_by']
    readonly_fields = ['created_at']
    list_per_page = 12
