import logging
from django.utils import timezone
from datetime import timedelta
from .models import DeliveryToken, DownloadLog

logger = logging.getLogger(__name__)


def generate_delivery_tokens(order):
    items = order.items.select_related('product').all()
    tokens = []

    for item in items:
        product = item.product
        download_url = product.download_link or ''
        token = DeliveryToken.objects.create(
            order=order,
            order_item=item,
            download_url=download_url,
            max_downloads=3,
            expires_at=timezone.now() + timedelta(hours=48),
        )
        tokens.append(token)

    logger.info(f'Generated {len(tokens)} delivery token(s) for order {order.id}')
    return tokens


def get_download_response(token_str, request):
    from django.shortcuts import get_object_or_404
    from django.http import FileResponse, HttpResponseRedirect, Http404

    try:
        import uuid
        token_uuid = uuid.UUID(token_str)
    except ValueError:
        return None

    token = get_object_or_404(DeliveryToken, token=token_uuid)

    if not token.is_valid():
        return None

    token.record_download(
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )

    product = token.order_item.product if token.order_item else None

    if product and product.file:
        response = FileResponse(product.file.open(), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{product.file.name}"'
        return response

    if token.download_url:
        return HttpResponseRedirect(token.download_url)

    raise Http404('No download file available')


def expire_old_tokens():
    cutoff = timezone.now() - timedelta(hours=48)
    expired = DeliveryToken.objects.filter(
        is_active=True,
        expires_at__lt=timezone.now(),
    ).update(is_active=False)
    if expired:
        logger.info(f'Expired {expired} old delivery token(s)')
    return expired
