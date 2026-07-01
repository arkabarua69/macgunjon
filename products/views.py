from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from .models import Product, Category, Review, Wishlist, Newsletter
from cart.forms import CartAddProductForm
from .forms import ReviewForm, NewsletterForm


from django.core.paginator import Paginator


def home(request):
    cache_key = 'home_page_data'
    context = cache.get(cache_key)
    if context is None:
        categories = Category.objects.annotate(product_count=Count('products')).order_by('-product_count')[:4]
        products = Product.objects.filter(available=True).select_related('category').prefetch_related('reviews')

        popular_products = products.annotate(
            order_count=Count('order_items')
        ).order_by('-order_count', '-created_at')[:8]

        featured_products = products.filter(featured=True)[:4]

        new_arrivals = products.order_by('-created_at')[:4]

        from orders.models import Order
        from users.models import User
        from dashboard.models import Testimonial, CompanyStat, HomePageSection, HomePageBanner, EcosystemCard

        total_products = Product.objects.filter(available=True).count()
        total_orders = Order.objects.count()
        total_users = User.objects.count()
        avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
        total_reviews = Review.objects.count()

        testimonials = Testimonial.objects.filter(is_featured=True).order_by('ordering')
        company_stats = CompanyStat.objects.filter(is_active=True).order_by('ordering')
        ecosystem_cards = HomePageSection.objects.filter(section_type='ecosystem', is_active=True).order_by('ordering')
        hero_banners = HomePageBanner.objects.filter(is_active=True)
        ecosystem_cards_new = EcosystemCard.objects.filter(is_active=True, page='home').order_by('ordering')
        ecosystem_list = list(ecosystem_cards_new)
        half = len(ecosystem_list) // 2
        ecosystem_left = ecosystem_list[:half] if half else []
        ecosystem_right = ecosystem_list[half:] if half else []

        context = {
            'categories': categories,
            'popular_products': popular_products,
            'featured_products': featured_products,
            'new_arrivals': new_arrivals,
            'total_products': total_products,
            'total_orders': total_orders,
            'total_users': total_users,
            'avg_rating': round(float(avg_rating), 1),
            'total_reviews': total_reviews,
            'testimonials': testimonials,
            'company_stats': company_stats,
            'ecosystem_cards': ecosystem_cards,
            'hero_banners': hero_banners,
            'ecosystem_cards_new': ecosystem_cards_new,
            'ecosystem_left': ecosystem_left,
            'ecosystem_right': ecosystem_right,
        }
        cache.set(cache_key, context, 300)

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    context['wishlist_ids'] = wishlist_ids

    return render(request, 'products/home.html', context)


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True).select_related('category').prefetch_related('reviews')

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    else:
        category = None
        cat_slug = request.GET.get('category')
        if cat_slug:
            category = Category.objects.filter(slug=cat_slug).first()
            if category:
                products = products.filter(category=category)

    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price_usd')
    elif sort_by == 'price_high':
        products = products.order_by('-price_usd')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')

    product_type = request.GET.get('type')
    if product_type:
        products = products.filter(product_type=product_type)

    paginator = Paginator(products, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    featured_cache_key = 'featured_products_list'
    featured_products = cache.get(featured_cache_key)
    if featured_products is None:
        featured_products = list(Product.objects.filter(available=True, featured=True).select_related('category')[:3])
        cache.set(featured_cache_key, featured_products, 600)

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))

    total_products_cache_key = 'total_products_count'
    total_products = cache.get(total_products_cache_key)
    if total_products is None:
        total_products = Product.objects.filter(available=True).count()
        cache.set(total_products_cache_key, total_products, 600)

    context = {
        'category': category,
        'categories': categories,
        'products': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'featured_products': featured_products,
        'query': query,
        'sort_by': sort_by,
        'product_type': product_type,
        'wishlist_ids': wishlist_ids,
        'total_products': total_products,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('reviews'),
        id=id, slug=slug, available=True
    )
    cart_product_form = CartAddProductForm()
    review_form = ReviewForm()

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).select_related('category').exclude(id=product.id)[:3]

    reviews = product.reviews.select_related('user').all()

    reviews_avg = product.get_average_rating()
    reviews_count = reviews.count()

    features = product.features.all().order_by('ordering')
    whats_included = product.whats_included if product.whats_included else [
        {'title': product.get_product_type_display(), 'description': 'Full source files and assets'},
        {'title': 'Documentation', 'description': 'Step-by-step setup guide (PDF)'},
        {'title': 'Support Access', 'description': 'Ticket-based priority support'},
    ]

    if product.schema_markup:
        schema = product.schema_markup
    else:
        schema = {
            '@context': 'https://schema.org',
            '@type': 'Product',
            'name': product.name,
            'description': (product.meta_description or product.description)[:160],
            'brand': {'@type': 'Brand', 'name': 'Mac GunJon'},
            'offers': {
                '@type': 'Offer',
                'price': str(product.price_usd),
                'priceCurrency': 'USD',
                'availability': 'https://schema.org/InStock' if product.available else 'https://schema.org/OutOfStock',
            },
        }
        if reviews_avg:
            schema['aggregateRating'] = {
                '@type': 'AggregateRating',
                'ratingValue': str(round(reviews_avg, 1)),
                'reviewCount': reviews_count,
            }

    context = {
        'product': product,
        'cart_product_form': cart_product_form,
        'review_form': review_form,
        'related_products': related_products,
        'reviews': reviews,
        'in_wishlist': in_wishlist,
        'features': features,
        'whats_included': whats_included,
        'meta_title': product.meta_title or f'{product.name} | Mac GunJon',
        'meta_description': product.meta_description or product.description[:160],
        'og_image': product.display_image,
        'canonical_url': request.build_absolute_uri(),
        'schema_markup': schema,
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    if created:
        return redirect('products:wishlist')
    return redirect(product.get_absolute_url())


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect('products:wishlist')


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'products/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect(product.get_absolute_url())
    return redirect(product.get_absolute_url())


@csrf_protect
@require_POST
def newsletter_subscribe(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'active': True, 'consent_at': now(), 'consent_ip': request.META.get('REMOTE_ADDR')}
        )
        if created:
            messages.success(request, 'Thank you for subscribing to our newsletter!')
        else:
            if not newsletter.active:
                newsletter.active = True
                newsletter.consent_at = now()
                newsletter.consent_ip = request.META.get('REMOTE_ADDR')
                newsletter.save()
                messages.success(request, 'Welcome back! You have been re-subscribed.')
            else:
                messages.info(request, 'You are already subscribed to our newsletter.')
    return redirect(request.META.get('HTTP_REFERER', '/'))
