import logging
from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from .models import EmailLog

logger = logging.getLogger(__name__)


def _log_email(recipient, subject, template_name, order_id=None, status='pending', error_message=''):
    log = EmailLog.objects.create(
        recipient=recipient,
        subject=subject,
        template_name=template_name,
        status=status,
        error_message=error_message,
        order_id=order_id,
    )
    if status == 'sent':
        log.sent_at = timezone.now()
        log.save(update_fields=['sent_at'])
    return log


def _send_email(subject, template_name, context, recipient_list, order_id=None):
    from django.conf import settings as django_settings
    context.setdefault('SITE_URL', django_settings.SITE_URL)
    html_message = render_to_string(f'orders/email/{template_name}.html', context)
    try:
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        _log_email(
            recipient=recipient_list[0],
            subject=subject,
            template_name=template_name,
            order_id=order_id,
            status='sent',
        )
        return True
    except Exception as e:
        logger.error(f'Email send failed ({template_name}): {e}')
        _log_email(
            recipient=recipient_list[0],
            subject=subject,
            template_name=template_name,
            order_id=order_id,
            status='failed',
            error_message=str(e),
        )
        return False


@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email(self, order_id):
    from orders.models import Order
    try:
        order = Order.objects.get(id=order_id)
        _send_email(
            subject=f'Order #{order.id} Confirmation - Mac GunJon',
            template_name='order_confirmation',
            context={'order': order, 'items': order.items.select_related('product').all()},
            recipient_list=[order.email],
            order_id=order.id,
        )
        logger.info(f'Order confirmation email sent for order {order_id}')
    except Exception as exc:
        logger.error(f'Failed to send order confirmation email for order {order_id}: {exc}')
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_payment_receipt_email(self, order_id):
    from orders.models import Order
    try:
        order = Order.objects.get(id=order_id)
        _send_email(
            subject=f'Payment Receipt - Order #{order.id} - Mac GunJon',
            template_name='payment_receipt',
            context={'order': order, 'items': order.items.select_related('product').all()},
            recipient_list=[order.email],
            order_id=order.id,
        )
        logger.info(f'Payment receipt email sent for order {order_id}')
    except Exception as exc:
        logger.error(f'Failed to send payment receipt email for order {order_id}: {exc}')
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_delivery_email(self, order_id):
    from orders.models import Order
    try:
        order = Order.objects.get(id=order_id)
        delivery_tokens = order.delivery_tokens.all()
        _send_email(
            subject=f'Your Order #{order.id} is Ready for Download! - Mac GunJon',
            template_name='delivery',
            context={
                'order': order,
                'items': order.items.select_related('product').all(),
                'delivery_tokens': delivery_tokens,
            },
            recipient_list=[order.email],
            order_id=order.id,
        )
        logger.info(f'Delivery email sent for order {order_id}')
    except Exception as exc:
        logger.error(f'Failed to send delivery email for order {order_id}: {exc}')
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_id):
    from users.models import User
    try:
        user = User.objects.get(id=user_id)
        _send_email(
            subject='Welcome to Mac GunJon - Is Bot!',
            template_name='welcome',
            context={'user': user},
            recipient_list=[user.email],
        )
        logger.info(f'Welcome email sent to user {user_id}')
    except Exception as exc:
        logger.error(f'Failed to send welcome email for user {user_id}: {exc}')
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_id, token):
    from users.models import User
    try:
        user = User.objects.get(id=user_id)
        reset_url = f'{settings.SITE_URL}/accounts/password-reset/confirm/{token}/'
        _send_email(
            subject='Password Reset - Mac GunJon',
            template_name='password_reset',
            context={'user': user, 'reset_url': reset_url},
            recipient_list=[user.email],
        )
        logger.info(f'Password reset email sent to user {user_id}')
    except Exception as exc:
        logger.error(f'Failed to send password reset email for user {user_id}: {exc}')
        self.retry(exc=exc, countdown=60)


@shared_task
def send_newsletter_blast(subject, message, recipient_ids):
    from notifications.models import EmailLog
    from users.models import User

    users = User.objects.filter(id__in=recipient_ids, email_verified=True)
    for user in users:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            EmailLog.objects.create(
                recipient=user.email,
                subject=subject,
                template_name='newsletter_blast',
                status='sent',
            )
        except Exception as e:
            logger.error(f'Newsletter send failed to {user.email}: {e}')
            EmailLog.objects.create(
                recipient=user.email,
                subject=subject,
                template_name='newsletter_blast',
                status='failed',
                error_message=str(e),
            )


@shared_task
def send_low_stock_alert(product_id):
    from products.models import Product
    from django.core.mail import mail_admins
    try:
        product = Product.objects.get(id=product_id)
        mail_admins(
            subject=f'Low Stock Alert: {product.name}',
            message=f'Product "{product.name}" has only {product.stock} items left in stock.',
            fail_silently=True,
        )
        logger.warning(f'Low stock alert sent for product {product_id}: {product.stock} left')
    except Product.DoesNotExist:
        logger.error(f'Product {product_id} not found for low stock alert')
