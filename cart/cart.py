from decimal import Decimal
from django.conf import settings


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price_usd': str(product.price_usd),
                'price_gbp': str(product.price_gbp),
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        from products.models import Product
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids).select_related('category')
        for product in products:
            self.cart[str(product.id)]['product'] = product
        for item in self.cart.values():
            item['price_usd'] = Decimal(item['price_usd'])
            item['price_gbp'] = Decimal(item['price_gbp'])
            item['total_price_usd'] = item['price_usd'] * item['quantity']
            item['total_price_gbp'] = item['price_gbp'] * item['quantity']
            item['total_price'] = item['total_price_usd']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self, currency='USD'):
        if currency == 'USD':
            return sum(Decimal(item['price_usd']) * item['quantity'] for item in self.cart.values())
        else:
            return sum(Decimal(item['price_gbp']) * item['quantity'] for item in self.cart.values())

    def get_discount(self, currency='USD'):
        coupon_code = self.session.get('coupon_code')
        if not coupon_code:
            return Decimal('0')
        try:
            from coupons.models import Coupon
            coupon = Coupon.objects.get(code=coupon_code)
            subtotal = self.get_total_price(currency)
            return coupon.get_discount_amount(subtotal)
        except Coupon.DoesNotExist:
            return Decimal('0')

    def get_total_after_discount(self, currency='USD'):
        return self.get_total_price(currency) - self.get_discount(currency)

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()
