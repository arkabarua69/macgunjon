from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import mail_admins
import logging
from .models import Product

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Product)
def check_low_stock(sender, instance, **kwargs):
    if instance.stock < 10 and instance.stock > 0 and instance.available:
        try:
            mail_admins(
                subject=f'Low Stock Alert: {instance.name}',
                message=f'Product "{instance.name}" has only {instance.stock} items left in stock.',
                fail_silently=True,
            )
            logger.warning(f'Low stock alert for {instance.name}: {instance.stock} left')
        except Exception as e:
            logger.error(f'Failed to send low stock alert: {e}')
