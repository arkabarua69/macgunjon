from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib import messages
from django.template.loader import render_to_string
import stripe
import json
import logging
from .models import Order, OrderItem
from products.models import Product
from .forms import OrderCreateForm
from notifications.tasks import send_order_confirmation_email, send_payment_receipt_email
from cart.cart import Cart

logger = logging.getLogger(__name__)

def _verify_order_ownership(order, request):
    if request.user.is_authenticated:
        if order.user is None or order.user != request.user:
            return False
    else:
        session_order_id = request.session.get('order_id')
        if session_order_id != order.id:
            return False
    return True


@login_required
@require_POST
@transaction.atomic
def order_create(request):
    cart = Cart(request)
    form = OrderCreateForm(request.POST)

    if form.is_valid():
        order = form.save(commit=False)
        order.currency = request.session.get('currency', 'USD')
        order.total_amount = cart.get_total_price(order.currency)
        order.user = request.user
        order.save()

        for item in cart:
            product = item['product']
            updated = Product.objects.filter(
                id=product.id, stock__gte=item['quantity']
            ).update(stock=F('stock') - item['quantity'])
            if not updated:
                messages.error(request, f'Sorry, "{product.name}" has only {product.stock} left in stock.')
                return redirect('cart:cart_detail')
            OrderItem.objects.create(
                order=order,
                product=product,
                price=item['price_usd'] if order.currency == 'USD' else item['price_gbp'],
                quantity=item['quantity']
            )

        cart.clear()
        request.session['order_id'] = order.id

        send_order_confirmation_email.delay(order.id)

        return redirect('orders:payment', order_id=order.id)

    return render(request, 'orders/order_create.html', {
        'cart': cart,
        'form': form,
        'cart_total_usd': cart.get_total_price('USD'),
        'cart_total_gbp': cart.get_total_price('GBP'),
    })


@login_required
def order_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if not _verify_order_ownership(order, request):
        messages.error(request, 'You do not have access to this order.')
        return redirect('users:dashboard')

    try:
        if order.stripe_payment_intent_id:
            intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent_id)
        else:
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),
                currency=order.currency.lower(),
                metadata={'order_id': order.id}
            )
            order.stripe_payment_intent_id = intent.id
            order.save(update_fields=['stripe_payment_intent_id'])
        client_secret = intent.client_secret
    except stripe.error.StripeError as e:
        logger.error(f'Stripe error for order {order_id}: {e}')
        return render(request, 'orders/payment_error.html', {'error': str(e)})

    return render(request, 'orders/payment.html', {
        'order': order,
        'client_secret': client_secret,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


@login_required
def order_success(request):
    order_id = request.session.get('order_id')
    if not order_id:
        messages.warning(request, 'No recent order found.')
        return redirect('products:product_list')

    order = get_object_or_404(Order, id=order_id)

    if not _verify_order_ownership(order, request):
        messages.error(request, 'You do not have access to this order.')
        return redirect('users:dashboard')

    if 'order_id' in request.session:
        del request.session['order_id']

    return render(request, 'orders/success.html', {'order': order})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product'),
        id=order_id
    )

    if not _verify_order_ownership(order, request):
        messages.error(request, 'You do not have access to this order.')
        return redirect('users:dashboard')

    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
@require_POST
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status not in ('pending', 'paid'):
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('orders:order_detail', order_id=order.id)

    if order.status == 'paid' and order.stripe_payment_intent_id:
        try:
            stripe.Refund.create(payment_intent=order.stripe_payment_intent_id)
        except stripe.error.StripeError as e:
            logger.error(f'Refund failed for order {order_id}: {e}')
            messages.error(request, 'Refund failed. Please contact support.')
            return redirect('orders:order_detail', order_id=order.id)

    order.status = 'cancelled'
    order.save()
    messages.success(request, f'Order #{order.id} has been cancelled.')
    return redirect('orders:order_detail', order_id=order.id)


@login_required
@require_POST
@user_passes_test(lambda u: u.is_staff)
def order_refund(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'paid':
        messages.error(request, 'Only paid orders can be refunded.')
        return redirect('orders:order_detail', order_id=order.id)

    if order.stripe_payment_intent_id:
        try:
            stripe.Refund.create(payment_intent=order.stripe_payment_intent_id)
            order.status = 'refunded'
            order.save()
            messages.success(request, f'Refund for Order #{order.id} has been initiated.')
        except stripe.error.StripeError as e:
            logger.error(f'Refund failed for order {order_id}: {e}')
            messages.error(request, 'Refund failed. Please contact support.')
    else:
        messages.error(request, 'No payment information found for this order.')

    return redirect('orders:order_detail', order_id=order.id)


@login_required
def order_invoice(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product'),
        id=order_id
    )

    if not _verify_order_ownership(order, request):
        messages.error(request, 'You do not have access to this order.')
        return redirect('users:dashboard')

    html_string = render_to_string('orders/invoice.html', {
        'order': order,
        'items': order.items.select_related('product').all(),
    })

    try:
        from weasyprint import HTML
        pdf = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice-{order.id}.pdf"'
        return response
    except ImportError:
        messages.warning(request, 'PDF generation is not available. Please install WeasyPrint.')
        return render(request, 'orders/invoice.html', {'order': order, 'items': order.items.all()})


@csrf_protect
@require_POST
def stripe_webhook(request):
    from payments.webhooks import stripe_webhook as payments_webhook
    return payments_webhook(request)
