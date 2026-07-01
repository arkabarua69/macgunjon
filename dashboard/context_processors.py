from .models import SiteSettings
from products.models import Category


def site_settings(request):
    try:
        settings = SiteSettings.get_settings()
        return {'site_settings': settings}
    except Exception:
        return {'site_settings': None}


from django.core.cache import cache


def nav_categories(request):
    categories = cache.get('nav_categories')
    if categories is None:
        categories = list(Category.objects.all())
        cache.set('nav_categories', categories, 3600)
    return {'nav_categories': categories}


def notification_context(request):
    notification_count = 0
    wishlist_count = 0
    if request.user.is_authenticated:
        cache_key = f'notification_count_{request.user.id}'
        counts = cache.get(cache_key)
        if counts is None:
            from notifications.models import EmailLog
            from products.models import Wishlist
            notification_count = EmailLog.objects.filter(recipient=request.user.email).count()
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
            cache.set(cache_key, (notification_count, wishlist_count), 300)
        else:
            notification_count, wishlist_count = counts
    return {'notification_count': notification_count, 'wishlist_count': wishlist_count}
