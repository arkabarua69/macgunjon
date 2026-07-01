from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import set_language
from django.contrib.sitemaps.views import sitemap
from . import views
from . import admin as admin_override  # noqa: F401 — apply custom admin index
from payments.webhooks import stripe_webhook as stripe_webhook_view
from .sitemaps import StaticViewSitemap, ProductSitemap, CategorySitemap, BlogSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'blog': BlogSitemap,
}

handler400 = 'macgunjon.views.bad_request'
handler403 = 'macgunjon.views.permission_denied'
handler404 = 'macgunjon.views.page_not_found'
handler500 = 'macgunjon.views.server_error'

admin.site.site_header = 'Mac GunJon - Is Bot | Admin'
admin.site.site_title = 'Mac GunJon Admin'
admin.site.index_title = 'Administration'
admin.site.password_change_template = 'admin/password_change_form.html'
admin.site.password_change_done_template = 'admin/password_change_done.html'

urlpatterns = [
    path('admin/', admin.site.urls),
    # Specific prefixed apps first — prevents products slug pattern swallowing them
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('coupons/', include('coupons.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('accounts/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    path('blog/', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('analytics/', include('analytics.urls')),
    path('set-currency/', views.set_currency, name='set_currency'),
    path('i18n/', set_language),
    path('health/', views.health_check, name='health_check'),
    path('payments/', include('payments.urls')),
    path('delivery/', include('delivery.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('notifications/', include('notifications.urls')),
    path('webhook/stripe/', stripe_webhook_view, name='stripe_webhook'),
    path('robots.txt', views.robots_txt),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('', include('products.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
