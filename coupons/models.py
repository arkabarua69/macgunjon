from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from decimal import Decimal


class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    min_purchase = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    max_uses = models.PositiveIntegerField(default=0, help_text='0 = unlimited uses')
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    applicable_products = models.ManyToManyField('products.Product', related_name='coupons', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.active:
            return False
        if now < self.valid_from or now > self.valid_to:
            return False
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False
        return True

    def get_discount_amount(self, subtotal):
        if self.discount_type == 'percentage':
            discount = subtotal * (self.discount_value / Decimal('100'))
            return min(discount, subtotal)
        else:
            return min(self.discount_value, subtotal)

    def apply(self):
        self.used_count += 1
        self.save()

    def deactivate(self):
        self.active = False
        self.save()


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, related_name='usages', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-used_at']
        verbose_name_plural = 'Coupon usages'

    def __str__(self):
        return f'{self.coupon.code} - {self.user or "Anonymous"}'
