from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, default='folder', help_text='Lucide icon name')
    parent = models.ForeignKey('self', related_name='children', on_delete=models.SET_NULL, null=True, blank=True)
    ordering = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordering', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_TYPES = [
        ('digital', 'Digital Product'),
        ('website', 'Website Template'),
        ('bot', 'Bot/Automation'),
        ('course', 'Course'),
    ]

    CURRENCIES = [
        ('USD', 'US Dollar'),
        ('GBP', 'British Pound'),
    ]

    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    price_gbp = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='digital')
    image = models.ImageField(upload_to='products/images/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text='URL to product image')
    file = models.FileField(upload_to='products/files/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['zip', 'pdf', 'rar', 'jpg', 'png', 'mp4', 'mov', 'csv', 'json', 'py', 'js', 'css', 'html', 'txt', 'docx', 'xlsx'])])
    download_link = models.URLField(blank=True, help_text='External download link if no file upload')
    stock = models.PositiveIntegerField(default=999999, help_text='Digital products have unlimited stock')
    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    has_variants = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True, help_text='SEO meta description (max 160 chars)')
    schema_markup = models.JSONField(null=True, blank=True, help_text='JSON-LD structured data')
    whats_included = models.JSONField(default=list, blank=True, help_text='List of What Included items as JSON array of dicts with title and description keys')
    related_products = models.ManyToManyField('self', blank=True, symmetrical=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_price(self, currency='USD'):
        return self.price_usd if currency == 'USD' else self.price_gbp

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:product_detail', args=[self.id, self.slug])

    def get_average_rating(self):
        from django.db.models import Avg
        avg = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return avg if avg else 0

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text='e.g., Basic, Pro, Enterprise')
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    price_gbp = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    stock = models.PositiveIntegerField(default=999999)
    sku = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price_usd']

    def __str__(self):
        return f'{self.product.name} - {self.name}'


class ProductFAQ(models.Model):
    product = models.ForeignKey(Product, related_name='faqs', on_delete=models.CASCADE)
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Product FAQs'

    def __str__(self):
        return f'{self.product.name}: {self.question[:50]}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images/')
    alt_text = models.CharField(max_length=200, blank=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordering']

    def __str__(self):
        return f'{self.product.name} - {self.alt_text or "Image"}'


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'


class Wishlist(models.Model):
    user = models.ForeignKey('users.User', related_name='wishlist', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlisted_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    consent_at = models.DateTimeField(null=True, blank=True)
    consent_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class ProductFeature(models.Model):
    product = models.ForeignKey(Product, related_name='features', on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Lucide icon name')
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordering']

    def __str__(self):
        return f'{self.product.name}: {self.title}'
