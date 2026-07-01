from django.db import models
from django.conf import settings


class EmailLog(models.Model):
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    template_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default='pending')
    error_message = models.TextField(blank=True)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient} - {self.subject[:50]}'
