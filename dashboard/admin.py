from django.contrib import admin
from .models import SiteSettings, Testimonial, FAQ, CompanyStat, TimelineEntry, HomePageSection, HomePageBanner, EcosystemCard


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('site_name', 'tagline', 'logo', 'favicon')
        }),
        ('Contact', {
            'fields': ('contact_email', 'whatsapp_number', 'map_embed_url', 'business_hours')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'github_url', 'discord_url', 'youtube_url', 'instagram_url')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'og_image', 'google_analytics_id', 'facebook_pixel_id')
        }),
        ('Appearance', {
            'fields': ('footer_text', 'about_text')
        }),
        ('About Page', {
            'fields': ('about_story_title', 'about_story_text', 'about_mission_title', 'about_mission_text', 'about_mission_points', 'about_founded_year'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('maintenance_mode', 'stripe_public_key_display')
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def has_add_permission(self, request):
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'rating', 'is_featured', 'ordering', 'created_at']
    list_filter = ['is_featured', 'rating']
    search_fields = ['name', 'role', 'quote']
    list_editable = ['ordering', 'is_featured']
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ('name', 'role', 'quote', 'rating')
        }),
        ('Media', {
            'fields': ('avatar_image', 'avatar_color')
        }),
        ('Display', {
            'fields': ('is_featured', 'ordering')
        }),
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_active', 'ordering', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
    list_editable = ['ordering', 'is_active']
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ('question', 'answer', 'category')
        }),
        ('Display', {
            'fields': ('is_active', 'ordering')
        }),
    )


@admin.register(CompanyStat)
class CompanyStatAdmin(admin.ModelAdmin):
    list_display = ['value', 'label', 'icon', 'is_active', 'ordering']
    list_editable = ['ordering', 'is_active']
    list_per_page = 20


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    list_display = ['year', 'title', 'ordering', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    list_editable = ['ordering', 'is_active']
    list_per_page = 20


@admin.register(HomePageSection)
class HomePageSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'section_type', 'is_active', 'ordering']
    list_filter = ['section_type', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['ordering', 'is_active']
    list_per_page = 30

    fieldsets = (
        (None, {
            'fields': ('section_type', 'title', 'description')
        }),
        ('Display', {
            'fields': ('icon', 'color', 'cta_text', 'cta_url', 'ordering', 'is_active')
        }),
    )


@admin.register(HomePageBanner)
class HomePageBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'chip_text', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title', 'subtitle']
    list_editable = ['is_active']
    list_per_page = 10


@admin.register(EcosystemCard)
class EcosystemCardAdmin(admin.ModelAdmin):
    list_display = ['title', 'color', 'ordering', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    list_editable = ['ordering', 'is_active']
    list_per_page = 20
