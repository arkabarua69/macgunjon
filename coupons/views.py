from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import CouponApplyForm


@require_POST
def apply_coupon(request):
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        request.session['coupon_code'] = code
        messages.success(request, f'Coupon "{code}" applied successfully!')
    else:
        messages.error(request, 'Invalid or expired coupon code.')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))


def remove_coupon(request):
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
        messages.success(request, 'Coupon removed.')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))
