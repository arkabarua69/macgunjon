import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class DeliveryToken(models.Model):
    order = models.ForeignKey('orders.Order', related_name='delivery_tokens', on_delete=models.CASCADE)
    order_item = models.ForeignKey('orders.OrderItem', related_name='delivery_tokens', on_delete=models.CASCADE, null=True, blank=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    download_url = models.URLField(blank=True, help_text='External download URL if applicable')
    max_downloads = models.PositiveIntegerField(default=3)
    download_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.order.id} - Token {str(self.token)[:8]}...'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=48)
        super().save(*args, **kwargs)

    def is_valid(self):
        if not self.is_active:
            return False
        if timezone.now() > self.expires_at:
            return False
        if self.download_count >= self.max_downloads:
            return False
        return True

    def record_download(self, ip_address, user_agent):
        self.download_count += 1
        if self.download_count >= self.max_downloads:
            self.is_active = False
        self.save(update_fields=['download_count', 'is_active'])
        DownloadLog.objects.create(
            token=self,
            ip_address=ip_address,
            user_agent=user_agent,
        )


class DownloadLog(models.Model):
    token = models.ForeignKey(DeliveryToken, related_name='download_logs', on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-downloaded_at']

    def __str__(self):
        return f'Download for Order #{self.token.order.id} from {self.ip_address or "unknown"}'
