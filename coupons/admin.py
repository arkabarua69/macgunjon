from django.contrib import admin
from .models import Coupon, CouponUsage


class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    readonly_fields = ['user', 'order', 'used_at']
    can_delete = False


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'used_at']
    list_filter = ['used_at']
    search_fields = ['coupon__code', 'user__email']
    readonly_fields = ['used_at']
    list_per_page = 12


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'min_purchase', 'used_count', 'max_uses', 'active', 'valid_from', 'valid_to']
    list_filter = ['active', 'discount_type', 'valid_from', 'valid_to']
    search_fields = ['code']
    list_editable = ['active']
    date_hierarchy = 'created_at'
    readonly_fields = ['used_count', 'created_at']
    filter_horizontal = ['applicable_products']
    inlines = [CouponUsageInline]
    list_per_page = 12

    fieldsets = (
        ('Coupon Details', {
            'fields': ('code', 'discount_type', 'discount_value')
        }),
        ('Limits', {
            'fields': ('min_purchase', 'max_uses', 'used_count')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to', 'active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_coupons', 'deactivate_coupons']

    @admin.action(description='Activate selected coupons')
    def activate_coupons(self, request, queryset):
        count = queryset.update(active=True)
        self.message_user(request, f'{count} coupon(s) activated.')

    @admin.action(description='Deactivate selected coupons')
    def deactivate_coupons(self, request, queryset):
        count = queryset.update(active=False)
        self.message_user(request, f'{count} coupon(s) deactivated.')
