from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.db import connection


@require_POST
def set_currency(request):
    currency = request.POST.get('currency', 'USD')
    if currency in ['USD', 'GBP']:
        request.session['currency'] = currency
    return redirect(request.META.get('HTTP_REFERER', '/'))


def bad_request(request, exception=None):
    return render(request, 'errors/400.html', status=400)


def permission_denied(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def page_not_found(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def server_error(request, exception=None):
    return render(request, 'errors/500.html', status=500)


def health_check(request):
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False
    status = 200 if db_ok else 503
    return JsonResponse({'status': 'ok' if db_ok else 'db_error', 'database': 'connected' if db_ok else 'disconnected'}, status=status)


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /dashboard/',
        'Disallow: /api/',
        'Disallow: /payment/',
        'Disallow: /download/',
        'Disallow: /accounts/',
        'Disallow: /cart/',
        'Disallow: /chatbot/',
        f'Sitemap: {request.build_absolute_uri("/sitemap.xml")}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
