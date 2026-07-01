from django.contrib import admin
from django.core.cache import cache


_original_index = admin.site.index


def _custom_index(request, extra_context=None):
    from products.models import Product, Category, Review, Newsletter
    from orders.models import Order
    from users.models import User
    from blog.models import BlogPost
    from coupons.models import Coupon
    from chatbot.models import ChatMessage
    from pages.models import ContactMessage

    cache_key = 'admin_dashboard_counts'
    counts = cache.get(cache_key)
    if counts is None:
        counts = {
            'product_count': Product.objects.count(),
            'order_count': Order.objects.count(),
            'user_count': User.objects.filter(is_staff=False).count(),
            'subscriber_count': Newsletter.objects.count(),
            'category_count': Category.objects.count(),
            'review_count': Review.objects.count(),
            'blog_count': BlogPost.objects.count(),
            'coupon_count': Coupon.objects.count(),
            'chat_count': ChatMessage.objects.count(),
            'contact_count': ContactMessage.objects.count(),
        }
        cache.set(cache_key, counts, 300)

    extra_context = extra_context or {}
    extra_context.update(counts)
    return _original_index(request, extra_context=extra_context)


admin.site.index = _custom_index
admin.site.index_template = 'admin/index.html'
