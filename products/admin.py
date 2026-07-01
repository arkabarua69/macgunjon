from django.contrib import admin
from django.db.models import Count, Avg
from django.utils.html import format_html
from .models import Category, Product, ProductVariant, ProductFAQ, ProductImage, ProductFeature, Review, Wishlist, Newsletter


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'product_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_per_page = 12
    list_editable = ['icon']

    def product_count(self, obj):
        return obj.products.filter(available=True).count()
    product_count.short_description = 'Products'


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ['name', 'price_usd', 'price_gbp', 'stock', 'sku']


class ProductFAQInline(admin.TabularInline):
    model = ProductFAQ
    extra = 0
    fields = ['question', 'answer', 'order']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ['image', 'alt_text', 'ordering']


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 0
    fields = ['title', 'description', 'icon', 'ordering']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'product_type_badge', 'stock', 'price_usd', 'order_count', 'rating_display', 'available', 'featured_badge', 'created_at']
    list_display_links = ['name']
    list_filter = ['product_type', 'category', 'available', 'featured', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    inlines = [ProductVariantInline, ProductFAQInline, ProductImageInline, ProductFeatureInline]
    filter_horizontal = ['related_products']
    list_per_page = 12
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['category']

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'category', 'description', 'product_type')
        }),
        ('Pricing', {
            'fields': ('price_usd', 'price_gbp')
        }),
        ('Media', {
            'fields': ('image', 'image_url')
        }),
        ('Inventory', {
            'fields': ('stock', 'available', 'featured')
        }),
        ('Digital Product', {
            'fields': ('file', 'download_link'),
            'classes': ('collapse',)
        }),
        ('Content', {
            'fields': ('whats_included',),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'schema_markup'),
            'classes': ('collapse',)
        }),
        ('Relations', {
            'fields': ('related_products',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['make_available', 'make_unavailable', 'make_featured', 'remove_featured']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            order_count_ann=Count('order_items'),
            avg_rating_ann=Avg('reviews__rating')
        )

    def order_count(self, obj):
        return getattr(obj, 'order_count_ann', 0)
    order_count.short_description = 'Orders'
    order_count.admin_order_field = 'order_count_ann'

    def rating_display(self, obj):
        avg = getattr(obj, 'avg_rating_ann', None)
        return round(float(avg), 1) if avg else 0
    rating_display.short_description = 'Rating'
    rating_display.admin_order_field = 'avg_rating_ann'

    def product_type_badge(self, obj):
        colors = {
            'digital': ('#50a5f1', 'fa-cube', 'Digital'),
            'website': ('#51d28c', 'fa-globe', 'Website'),
            'bot': '#f1b44c',
            'course': '#f46a6a',
        }
        cfg = colors.get(obj.product_type, ('#98a6ad', 'fa-box', obj.product_type.title()))
        if isinstance(cfg, str):
            cfg = (cfg, 'fa-box', obj.product_type.title())
        color, icon, label = cfg
        return format_html(
            '<span class="type-badge" style="background:{}15;color:{};border:1px solid {}30;">'
            '<i class="fas {}" style="font-size:10px;"></i> {}</span>',
            color, color, color, icon, label
        )
    product_type_badge.short_description = 'Type'
    product_type_badge.allow_tags = True
    product_type_badge.admin_order_field = 'product_type'

    def featured_badge(self, obj):
        if obj.featured:
            return format_html(
                '<span class="featured-star active" title="Featured"><i class="fas fa-star"></i></span>'
            )
        return format_html(
            '<span class="featured-star" title="Not featured"><i class="far fa-star"></i></span>'
        )
    featured_badge.short_description = '★'
    featured_badge.allow_tags = True
    featured_badge.admin_order_field = 'featured'

    @admin.action(description='Mark selected products as available')
    def make_available(self, request, queryset):
        count = queryset.update(available=True)
        self.message_user(request, f'{count} product(s) marked as available.')

    @admin.action(description='Mark selected products as unavailable')
    def make_unavailable(self, request, queryset):
        count = queryset.update(available=False)
        self.message_user(request, f'{count} product(s) marked as unavailable.')

    @admin.action(description='Mark selected products as featured')
    def make_featured(self, request, queryset):
        count = queryset.update(featured=True)
        self.message_user(request, f'{count} product(s) marked as featured.')

    @admin.action(description='Remove featured status from selected products')
    def remove_featured(self, request, queryset):
        count = queryset.update(featured=False)
        self.message_user(request, f'{count} product(s) unfeatured.')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['comment', 'user__email', 'product__name']
    raw_id_fields = ['user', 'product']
    readonly_fields = ['created_at']
    list_per_page = 12
    actions = ['approve_reviews', 'disapprove_reviews']

    @admin.action(description='Approve selected reviews')
    def approve_reviews(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f'{count} review(s) approved.')

    @admin.action(description='Disapprove selected reviews')
    def disapprove_reviews(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f'{count} review(s) disapproved.')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'product__name']
    raw_id_fields = ['user', 'product']
    readonly_fields = ['created_at']
    list_per_page = 12


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'active', 'subscribed_at']
    list_filter = ['active', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at']
    list_per_page = 12

    actions = ['activate_subscriptions', 'deactivate_subscriptions']

    @admin.action(description='Activate selected subscriptions')
    def activate_subscriptions(self, request, queryset):
        count = queryset.update(active=True)
        self.message_user(request, f'{count} subscription(s) activated.')

    @admin.action(description='Deactivate selected subscriptions')
    def deactivate_subscriptions(self, request, queryset):
        count = queryset.update(active=False)
        self.message_user(request, f'{count} subscription(s) deactivated.')
