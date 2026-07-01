from django.db import models
from django.urls import reverse
from django.conf import settings


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True, help_text='Short summary for listings')
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    image_url = models.URLField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True, help_text='SEO meta description (max 160 chars)')
    tags = models.ManyToManyField(Tag, related_name='blog_posts', blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Blog posts'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', args=[self.slug])

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url
