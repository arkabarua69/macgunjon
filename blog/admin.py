from django.contrib import admin
from .models import BlogPost, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_per_page = 12


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'published', 'featured', 'published_at', 'created_at']
    list_filter = ['status', 'published', 'featured', 'created_at']
    search_fields = ['title', 'content', 'author__email']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    raw_id_fields = ['author']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['tags']
    list_per_page = 12
    list_select_related = ['author']

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'image', 'image_url')
        }),
        ('Metadata', {
            'fields': ('author', 'status', 'published', 'featured', 'published_at', 'tags')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['publish_posts', 'unpublish_posts', 'feature_posts', 'unfeature_posts']

    @admin.action(description='Publish selected posts')
    def publish_posts(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(published=True, status='published', published_at=timezone.now())
        self.message_user(request, f'{count} post(s) published.')

    @admin.action(description='Unpublish selected posts')
    def unpublish_posts(self, request, queryset):
        count = queryset.update(published=False, status='draft')
        self.message_user(request, f'{count} post(s) unpublished.')

    @admin.action(description='Feature selected posts')
    def feature_posts(self, request, queryset):
        count = queryset.update(featured=True)
        self.message_user(request, f'{count} post(s) featured.')

    @admin.action(description='Remove featured from selected posts')
    def unfeature_posts(self, request, queryset):
        count = queryset.update(featured=False)
        self.message_user(request, f'{count} post(s) unfeatured.')
