from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='Mac GunJon - Is Bot')
    tagline = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    contact_email = models.EmailField(blank=True, default='support@macgunjon.com')
    whatsapp_number = models.CharField(max_length=20, blank=True, default='+8809638089695')
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    discord_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    map_embed_url = models.TextField(blank=True, help_text='Google Maps embed URL')
    business_hours = models.JSONField(default=dict, blank=True, help_text='JSON object with day ranges as keys and hours as values')
    maintenance_mode = models.BooleanField(default=False)
    google_analytics_id = models.CharField(max_length=50, blank=True)
    facebook_pixel_id = models.CharField(max_length=50, blank=True)
    meta_title = models.CharField(max_length=200, blank=True, default='Mac GunJon - Is Bot')
    meta_description = models.TextField(blank=True)
    og_image = models.ImageField(upload_to='site/', blank=True, null=True)
    stripe_public_key_display = models.CharField(max_length=255, blank=True, help_text='Display only, actual key in .env')
    footer_text = models.TextField(blank=True)
    about_text = models.TextField(blank=True)
    about_story_title = models.CharField(max_length=200, blank=True, default='Built for the digital age')
    about_story_text = models.TextField(blank=True)
    about_mission_title = models.CharField(max_length=200, blank=True, default='Our Mission')
    about_mission_text = models.TextField(blank=True)
    about_mission_points = models.JSONField(default=list, blank=True, help_text='List of mission commitment strings')
    about_founded_year = models.PositiveIntegerField(default=2024)
    is_singleton = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        if self.is_singleton:
            self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1, defaults={'is_singleton': True})
        return obj


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=150, help_text='e.g., E-commerce Owner')
    quote = models.TextField()
    rating = models.PositiveIntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    avatar_image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    avatar_color = models.CharField(max_length=7, default='#3b82f6', help_text='Hex color for avatar fallback')
    is_featured = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordering', '-created_at']

    def __str__(self):
        return f'{self.name} - {self.role}'


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('orders', 'Orders'),
        ('payments', 'Payments'),
        ('delivery', 'Delivery'),
        ('products', 'Products'),
        ('account', 'Account'),
        ('general', 'General'),
    ]

    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    ordering = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordering', '-created_at']

    def __str__(self):
        return self.question[:80]


class CompanyStat(models.Model):
    value = models.CharField(max_length=20, help_text='e.g., 50+, 1K+, 99%, 24/7')
    label = models.CharField(max_length=100, help_text='e.g., Products, Happy Customers')
    icon = models.CharField(max_length=50, blank=True, help_text='Lucide icon name')
    ordering = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['ordering']

    def __str__(self):
        return f'{self.value} - {self.label}'


class TimelineEntry(models.Model):
    year = models.CharField(max_length=10, help_text='e.g., 2024')
    title = models.CharField(max_length=150)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, help_text='Lucide icon name')
    ordering = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['ordering']

    def __str__(self):
        return f'{self.year} - {self.title}'


class HomePageBanner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    chip_text = models.CharField(max_length=100, blank=True, default='100% Instant Digital Delivery')
    cta_text = models.CharField(max_length=100, blank=True, default='Browse Products')
    cta_url = models.CharField(max_length=200, blank=True, default='products:product_list')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Home page banners'

    def __str__(self):
        return self.title


class EcosystemCard(models.Model):
    PAGE_CHOICES = [
        ('home', 'Home Page'),
        ('about', 'About Page'),
    ]
    page = models.CharField(max_length=10, choices=PAGE_CHOICES, default='home')
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=300)
    icon = models.CharField(max_length=50, blank=True, default='layout', help_text='Lucide icon name')
    color = models.CharField(max_length=7, default='#3b82f6', help_text='Hex color')
    ordering = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordering']
        verbose_name_plural = 'Ecosystem cards'

    def __str__(self):
        return self.title


class HomePageSection(models.Model):
    SECTION_TYPES = [
        ('hero', 'Hero Banner'),
        ('ecosystem', 'Ecosystem Card'),
        ('how_it_works', 'How It Works Step'),
    ]

    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Lucide icon name')
    color = models.CharField(max_length=7, default='#3b82f6', help_text='Hex color')
    cta_text = models.CharField(max_length=100, blank=True)
    cta_url = models.CharField(max_length=200, blank=True)
    ordering = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordering']
        verbose_name_plural = 'Home page sections'

    def __str__(self):
        return f'{self.get_section_type_display()}: {self.title}'
