import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_newsletter_email(self, subject, message, recipient_list):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        logger.info(f'Newsletter email sent to {len(recipient_list)} subscribers')
    except Exception as exc:
        logger.error(f'Failed to send newsletter email: {exc}')
        self.retry(exc=exc, countdown=60)


@shared_task
def check_low_stock():
    from products.models import Product
    from django.core.mail import mail_admins

    low_stock_products = list(Product.objects.filter(
        stock__lt=10,
        available=True
    ).values_list('name', 'stock'))

    if low_stock_products:
        product_list = '\n'.join([f'- {name}: {stock} left' for name, stock in low_stock_products])
        mail_admins(
            subject='Low Stock Alert - Mac GunJon',
            message=f'The following products are running low on stock:\n\n{product_list}',
            fail_silently=False,
        )
        logger.warning(f'Low stock alert: {len(low_stock_products)} products')


@shared_task
def cleanup_old_carts():
    from orders.models import Order
    from django.utils import timezone
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(days=30)
    stale_orders = Order.objects.filter(status='pending', created_at__lt=cutoff)
    count = stale_orders.count()
    if count:
        stale_orders.update(status='cancelled')
        logger.info(f'Cleaned up {count} stale pending orders older than 30 days')
    else:
        logger.info('Cart cleanup task executed - no stale orders found')
