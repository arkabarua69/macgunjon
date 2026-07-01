import stripe
import logging
from django.conf import settings
from decimal import Decimal

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_intent(order):
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),
            currency=order.currency.lower(),
            metadata={'order_id': order.id},
            description=f'Order #{order.id} - Mac GunJon',
        )
        order.stripe_payment_intent_id = intent.id
        order.save(update_fields=['stripe_payment_intent_id'])
        logger.info(f'PaymentIntent created for order {order.id}: {intent.id}')
        return intent.client_secret
    except stripe.error.StripeError as e:
        logger.error(f'Stripe create_payment_intent failed for order {order.id}: {e}')
        raise


def verify_webhook_signature(payload, sig_header):
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    if not webhook_secret:
        logger.warning('STRIPE_WEBHOOK_SECRET not configured')
        return None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        return event
    except ValueError as e:
        logger.error(f'Invalid webhook payload: {e}')
        return None
    except stripe.error.SignatureVerificationError as e:
        logger.error(f'Invalid webhook signature: {e}')
        return None


def process_payment_success(payment_intent):
    from orders.models import Order
    from delivery.services import generate_delivery_tokens
    from notifications.tasks import send_payment_receipt_email, send_delivery_email
    from .models import Payment

    order_id = payment_intent.get('metadata', {}).get('order_id')
    if not order_id:
        logger.error('No order_id in payment_intent metadata')
        return None

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f'Order {order_id} not found for payment success')
        return None

    order.status = 'paid'
    order.stripe_payment_intent_id = payment_intent['id']
    order.save(update_fields=['status', 'stripe_payment_intent_id'])

    Payment.objects.create(
        order=order,
        gateway='stripe',
        transaction_id=payment_intent['id'],
        amount=Decimal(str(payment_intent['amount'] / 100)),
        currency=payment_intent['currency'].upper(),
        status='success',
        raw_response=payment_intent,
    )

    generate_delivery_tokens(order)

    send_payment_receipt_email.delay(order.id)
    send_delivery_email.delay(order.id)

    logger.info(f'Payment success processed for order {order.id}')
    return order


def process_payment_failed(payment_intent):
    from orders.models import Order
    from .models import Payment

    order_id = payment_intent.get('metadata', {}).get('order_id')
    if not order_id:
        logger.error('No order_id in payment_intent metadata')
        return None

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f'Order {order_id} not found for payment failure')
        return None

    Payment.objects.create(
        order=order,
        gateway='stripe',
        transaction_id=payment_intent['id'],
        amount=Decimal(str(payment_intent['amount'] / 100)),
        currency=payment_intent['currency'].upper(),
        status='failed',
        raw_response=payment_intent,
    )

    logger.warning(f'Payment failed for order {order.id}')
    return order


def create_refund(order, amount=None):
    import stripe
    from .models import Payment, Refund

    if not order.stripe_payment_intent_id:
        logger.error(f'No payment intent for order {order.id}')
        return None

    try:
        if amount:
            refund_amount = int(amount * 100)
            refund = stripe.Refund.create(
                payment_intent=order.stripe_payment_intent_id,
                amount=refund_amount,
            )
        else:
            refund = stripe.Refund.create(
                payment_intent=order.stripe_payment_intent_id,
            )

        payment = Payment.objects.filter(order=order, status='success').first()
        if payment:
            payment.status = 'refunded'
            payment.save(update_fields=['status'])
            Refund.objects.create(
                payment=payment,
                amount=amount or order.total_amount,
                reason='Refund requested',
                status='succeeded',
                stripe_refund_id=refund.id,
            )

        order.status = 'refunded'
        order.save(update_fields=['status'])

        logger.info(f'Refund processed for order {order.id}: {refund.id}')
        return refund

    except stripe.error.StripeError as e:
        logger.error(f'Refund failed for order {order.id}: {e}')
        raise
