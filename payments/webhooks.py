import json
import logging
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .services import verify_webhook_signature, process_payment_success, process_payment_failed

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    event = verify_webhook_signature(payload, sig_header)
    if event is None:
        logger.error('Stripe webhook signature verification failed')
        return HttpResponseBadRequest('Invalid signature')

    event_type = event['type']
    event_data = event['data']['object']

    logger.info(f'Stripe webhook received: {event_type}')

    if event_type == 'payment_intent.succeeded':
        process_payment_success(event_data)

    elif event_type == 'payment_intent.payment_failed':
        process_payment_failed(event_data)

    elif event_type == 'charge.refunded':
        from orders.models import Order
        from .models import Payment, Refund

        charge = event_data
        payment_intent_id = charge.get('payment_intent')
        if payment_intent_id:
            payment = Payment.objects.filter(transaction_id=payment_intent_id).first()
            if payment and payment.status != 'refunded':
                payment.status = 'refunded'
                payment.save(update_fields=['status'])
                Refund.objects.create(
                    payment=payment,
                    amount=payment.amount,
                    reason='Stripe charge refunded',
                    status='succeeded',
                    stripe_refund_id=charge.get('id', ''),
                )
                order = payment.order
                if order and order.status != 'refunded':
                    order.status = 'refunded'
                    order.save(update_fields=['status'])
                logger.info(f'Charge refunded for payment {payment_intent_id}')

    return HttpResponse(status=200)
