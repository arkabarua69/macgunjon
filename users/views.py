from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.http import require_POST, require_safe
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .forms import UserRegistrationForm, UserProfileForm, AddressForm
from .models import User, Address, UserSession
from orders.models import Order
from products.models import Wishlist, Review


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verify_url = request.build_absolute_uri(
                f'/accounts/verify-email/{uid}/{token}/'
            )
            send_mail(
                subject='Verify Your Email - Mac GunJon',
                message=f'Click this link to verify your email: {verify_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )

            messages.success(request, f'Welcome {user.username}! A verification email has been sent.')
            return redirect('products:product_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user).select_related('user').prefetch_related('items__product')
    total_orders = orders.count()
    completed_orders = orders.filter(status='completed').count()
    pending_orders = orders.filter(status='pending').count()
    cancelled_orders = orders.filter(status='cancelled').count()
    total_downloads = orders.filter(
        status='completed',
        items__product__file__isnull=False
    ).distinct().count()
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')[:4]
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    address_count = Address.objects.filter(user=request.user).count()
    session_count = UserSession.objects.filter(user=request.user).count()
    review_count = Review.objects.filter(user=request.user).count()

    total_spent = orders.filter(status='completed').aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    recent_orders = orders[:5]

    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_orders_count = orders.filter(created_at__gte=thirty_days_ago).count()

    completed_percentage = 0
    if total_orders > 0:
        completed_percentage = round((completed_orders / total_orders) * 100)

    newsletter_subscribed = False
    try:
        from products.models import Newsletter
        newsletter_subscribed = Newsletter.objects.filter(email=request.user.email, active=True).exists()
    except Exception:
        pass

    social_accounts = []
    try:
        social_accounts = list(request.user.socialaccount_set.values_list('provider', flat=True))
    except Exception:
        pass

    return render(request, 'users/dashboard.html', {
        'orders': orders,
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'cancelled_orders': cancelled_orders,
        'total_downloads': total_downloads,
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_count,
        'address_count': address_count,
        'session_count': session_count,
        'review_count': review_count,
        'total_spent': total_spent,
        'recent_orders_count': recent_orders_count,
        'completed_percentage': completed_percentage,
        'newsletter_subscribed': newsletter_subscribed,
        'social_accounts': social_accounts,
    })


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('users:profile_edit')
    else:
        form = UserProfileForm(instance=request.user)

    password_form = PasswordChangeForm(user=request.user)
    address_count = Address.objects.filter(user=request.user).count()
    session_count = UserSession.objects.filter(user=request.user).count()

    social_accounts = []
    try:
        social_accounts = list(request.user.socialaccount_set.values_list('provider', flat=True))
    except Exception:
        pass

    return render(request, 'users/profile_edit.html', {
        'form': form,
        'password_form': password_form,
        'address_count': address_count,
        'session_count': session_count,
        'social_accounts': social_accounts,
    })


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.email_verified = True
        user.save()
        messages.success(request, 'Your email has been verified!')
        return redirect('users:login')
    else:
        messages.error(request, 'Invalid verification link.')
        return redirect('products:product_list')


@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'users/address_list.html', {'addresses': addresses})


@login_required
def address_create(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully.')
            return redirect('users:address_list')
    else:
        form = AddressForm()
    return render(request, 'users/address_form.html', {'form': form, 'action': 'Create'})


@login_required
def address_edit(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('users:address_list')
    else:
        form = AddressForm(instance=address)
    return render(request, 'users/address_form.html', {'form': form, 'action': 'Edit'})


@login_required
@require_POST
def address_delete(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted.')
    return redirect('users:address_list')


@login_required
def session_list(request):
    sessions = UserSession.objects.filter(user=request.user)
    return render(request, 'users/session_list.html', {'sessions': sessions})


@login_required
@require_POST
def session_revoke(request, session_id):
    session = get_object_or_404(UserSession, id=session_id, user=request.user)
    session.delete()
    messages.success(request, 'Session revoked.')
    return redirect('users:session_list')


@login_required
@require_POST
def change_password(request):
    password_form = PasswordChangeForm(user=request.user, data=request.POST)
    if password_form.is_valid():
        password_form.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, 'Your password has been changed successfully.')
    else:
        for field, errors in password_form.errors.items():
            for error in errors:
                messages.error(request, f'{error}')
    return redirect('users:profile_edit')


@login_required
@require_POST
def delete_account(request):
    user = request.user
    user.delete()
    messages.success(request, 'Your account has been deleted.')
    return redirect('products:home')
