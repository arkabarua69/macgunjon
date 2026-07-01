from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from orders.models import Order
from products.models import Product
from users.models import User
from payments.models import Payment
from notifications.models import EmailLog
from delivery.models import DeliveryToken, DownloadLog
from coupons.models import Coupon, CouponUsage
from products.models import Newsletter
from blog.models import BlogPost
from pages.models import ContactMessage
from .models import SiteSettings


@staff_member_required
def overview(request):
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)

    total_orders = Order.objects.count()
    total_revenue_usd = Order.objects.filter(currency='USD').aggregate(total=Sum('total_amount'))['total'] or 0
    total_revenue_gbp = Order.objects.filter(currency='GBP').aggregate(total=Sum('total_amount'))['total'] or 0
    total_users = User.objects.count()
    total_products = Product.objects.filter(available=True).count()

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    context = {
        'total_orders': total_orders,
        'total_revenue_usd': total_revenue_usd,
        'total_revenue_gbp': total_revenue_gbp,
        'total_users': total_users,
        'total_products': total_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/overview.html', context)


@staff_member_required
def dashboard_products(request):
    products = Product.objects.select_related('category').prefetch_related('reviews').all()
    return render(request, 'dashboard/product_list.html', {'products': products})


@staff_member_required
def dashboard_orders(request):
    orders = Order.objects.select_related('user').prefetch_related('items__product').all()

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '')
    currency = request.GET.get('currency', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if search:
        orders = orders.filter(
            Q(id__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    if status:
        orders = orders.filter(status=status)
    if currency:
        orders = orders.filter(currency=currency)
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)

    context = {
        'orders': orders,
        'search': search,
        'filter_status': status,
        'filter_currency': currency,
        'filter_date_from': date_from,
        'filter_date_to': date_to,
    }
    return render(request, 'dashboard/order_list.html', context)


@staff_member_required
def dashboard_order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product', 'status_history', 'delivery_tokens'),
        id=order_id
    )
    return render(request, 'dashboard/order_detail.html', {'order': order})


@staff_member_required
def dashboard_payments(request):
    payments = Payment.objects.select_related('order').all()
    return render(request, 'dashboard/payment_list.html', {'payments': payments})


@staff_member_required
def dashboard_customers(request):
    customers = User.objects.prefetch_related('addresses').annotate(
        order_count=Count('orders')
    ).all()

    search = request.GET.get('search', '').strip()
    role = request.GET.get('role', '')
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if search:
        customers = customers.filter(
            Q(email__icontains=search) |
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    if role == 'staff':
        customers = customers.filter(is_staff=True)
    elif role == 'superuser':
        customers = customers.filter(is_superuser=True)
    elif role == 'regular':
        customers = customers.filter(is_staff=False, is_superuser=False)
    if status == 'active':
        customers = customers.filter(is_active=True)
    elif status == 'inactive':
        customers = customers.filter(is_active=False)
    if date_from:
        customers = customers.filter(date_joined__date__gte=date_from)
    if date_to:
        customers = customers.filter(date_joined__date__lte=date_to)

    context = {
        'customers': customers,
        'search': search,
        'filter_role': role,
        'filter_status': status,
        'filter_date_from': date_from,
        'filter_date_to': date_to,
    }
    return render(request, 'dashboard/customer_list.html', context)


@staff_member_required
def dashboard_reports(request):
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)

    orders_30d = Order.objects.filter(created_at__date__gte=last_30_days)
    revenue_usd = orders_30d.filter(currency='USD').aggregate(total=Sum('total_amount'))['total'] or 0
    revenue_gbp = orders_30d.filter(currency='GBP').aggregate(total=Sum('total_amount'))['total'] or 0

    from django.db.models.functions import TruncDate
    revenue_by_day = orders_30d.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        revenue=Sum('total_amount'),
        count=Count('id')
    ).order_by('date')

    context = {
        'revenue_usd': revenue_usd,
        'revenue_gbp': revenue_gbp,
        'orders_count': orders_30d.count(),
        'revenue_by_day': list(revenue_by_day),
    }
    return render(request, 'dashboard/reports.html', context)


@staff_member_required
def dashboard_site_settings(request):
    settings = SiteSettings.get_settings()
    if request.method == 'POST':
        form = request.POST
        settings.site_name = form.get('site_name', settings.site_name)
        settings.tagline = form.get('tagline', settings.tagline)
        settings.contact_email = form.get('contact_email', settings.contact_email)
        settings.whatsapp_number = form.get('whatsapp_number', settings.whatsapp_number)
        settings.facebook_url = form.get('facebook_url', settings.facebook_url)
        settings.twitter_url = form.get('twitter_url', settings.twitter_url)
        settings.linkedin_url = form.get('linkedin_url', settings.linkedin_url)
        settings.github_url = form.get('github_url', settings.github_url)
        settings.discord_url = form.get('discord_url', settings.discord_url)
        settings.meta_title = form.get('meta_title', settings.meta_title)
        settings.meta_description = form.get('meta_description', settings.meta_description)
        settings.google_analytics_id = form.get('google_analytics_id', settings.google_analytics_id)
        settings.facebook_pixel_id = form.get('facebook_pixel_id', settings.facebook_pixel_id)
        settings.footer_text = form.get('footer_text', settings.footer_text)
        settings.about_text = form.get('about_text', settings.about_text)
        settings.maintenance_mode = form.get('maintenance_mode') == 'on'
        settings.save()
        messages.success(request, 'Site settings updated successfully.')
        return redirect('dashboard:site_settings')
    return render(request, 'dashboard/site_settings.html', {'settings': settings})


@staff_member_required
def dashboard_email_logs(request):
    logs = EmailLog.objects.all()
    return render(request, 'dashboard/email_logs.html', {'logs': logs})


@staff_member_required
def dashboard_delivery_logs(request):
    logs = DownloadLog.objects.select_related('token__order').all()
    return render(request, 'dashboard/delivery_logs.html', {'logs': logs})


@staff_member_required
def dashboard_coupons(request):
    coupons = Coupon.objects.all()
    return render(request, 'dashboard/coupon_list.html', {'coupons': coupons})


@staff_member_required
def dashboard_newsletter(request):
    subscribers = Newsletter.objects.all()
    return render(request, 'dashboard/newsletter_list.html', {'subscribers': subscribers})


@staff_member_required
def dashboard_blog(request):
    posts = BlogPost.objects.all()
    return render(request, 'dashboard/blog_list.html', {'posts': posts})


@staff_member_required
def dashboard_contact_messages(request):
    contact_messages = ContactMessage.objects.all()

    search = request.GET.get('search', '').strip()
    read_status = request.GET.get('read', '')

    if search:
        contact_messages = contact_messages.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(subject__icontains=search)
        )
    if read_status == 'read':
        contact_messages = contact_messages.filter(read=True)
    elif read_status == 'unread':
        contact_messages = contact_messages.filter(read=False)

    context = {
        'contact_messages': contact_messages,
        'search': search,
        'filter_read': read_status,
    }
    return render(request, 'dashboard/contact_messages.html', context)
