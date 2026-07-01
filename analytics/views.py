from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from products.models import Product
from users.models import User


@staff_member_required
def analytics_dashboard(request):
    from django.db.models.functions import TruncDate

    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)

    orders_30d = Order.objects.filter(created_at__date__gte=last_30_days)
    orders_7d = Order.objects.filter(created_at__date__gte=last_7_days)

    total_revenue_usd = orders_30d.filter(currency='USD').aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    total_revenue_gbp = orders_30d.filter(currency='GBP').aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    revenue_by_day = orders_30d.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        revenue=Sum('total_amount'),
        count=Count('id')
    ).order_by('date')

    top_products = Product.objects.annotate(
        order_count=Count('order_items')
    ).order_by('-order_count')[:10]

    new_users_30d = User.objects.filter(date_joined__date__gte=last_30_days).count()
    new_users_7d = User.objects.filter(date_joined__date__gte=last_7_days).count()

    context = {
        'total_orders_30d': orders_30d.count(),
        'total_orders_7d': orders_7d.count(),
        'total_revenue_usd': total_revenue_usd,
        'total_revenue_gbp': total_revenue_gbp,
        'revenue_by_day': list(revenue_by_day),
        'top_products': top_products,
        'new_users_30d': new_users_30d,
        'new_users_7d': new_users_7d,
        'total_products': Product.objects.count(),
        'total_users': User.objects.count(),
    }
    return render(request, 'analytics/dashboard.html', context)
