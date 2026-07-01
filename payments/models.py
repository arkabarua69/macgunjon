from django.db import models
from django.conf import settings
from decimal import Decimal


class Payment(models.Model):
    GATEWAYS = [
        ('stripe', 'Stripe'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    order = models.ForeignKey('orders.Order', related_name='payments', on_delete=models.CASCADE)
    gateway = models.CharField(max_length=20, choices=GATEWAYS, default='stripe')
    transaction_id = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    raw_response = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment #{self.id} - Order #{self.order.id} - {self.amount} {self.currency} ({self.status})'


class Refund(models.Model):
    payment = models.ForeignKey(Payment, related_name='refunds', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='pending')
    stripe_refund_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Refund #{self.id} - Order #{self.payment.order.id} - {self.amount} ({self.status})'
