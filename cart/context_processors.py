from .cart import Cart


def cart_context(request):
    context = {'cart': Cart(request)}
    if request.user.is_authenticated:
        from products.models import Wishlist
        context['wishlist_count'] = Wishlist.objects.filter(user=request.user).count()
    return context
