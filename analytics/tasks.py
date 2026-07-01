import logging
from celery import shared_task
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta
from .models import SalesReport
from orders.models import Order
from users.models import User
from products.models import Product

logger = logging.getLogger(__name__)


@shared_task
def generate_daily_report():
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    orders = Order.objects.filter(created_at__date=yesterday)
    total_orders = orders.count()
    revenue_usd = orders.filter(currency='USD').aggregate(total=Sum('total_amount'))['total'] or 0
    revenue_gbp = orders.filter(currency='GBP').aggregate(total=Sum('total_amount'))['total'] or 0
    new_users = User.objects.filter(date_joined__date=yesterday).count()

    top_product = Product.objects.annotate(
        order_count=Count('order_items', filter=Q(order_items__order__created_at__date=yesterday))
    ).order_by('-order_count').first()

    report, created = SalesReport.objects.update_or_create(
        date=yesterday,
        defaults={
            'total_orders': total_orders,
            'total_revenue_usd': revenue_usd,
            'total_revenue_gbp': revenue_gbp,
            'new_users': new_users,
            'top_product': top_product,
        }
    )

    logger.info(f'Daily report {"created" if created else "updated"} for {yesterday}: {total_orders} orders, ${revenue_usd}/{revenue_gbp}')
    return report.id


