from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from products.models import Product, Category, Review, Wishlist, ProductVariant
from orders.models import Order, OrderItem
from users.models import User
from .serializers import (
    CategorySerializer, ProductSerializer, ReviewSerializer,
    OrderSerializer, WishlistSerializer, ProductVariantSerializer,
    UserSerializer,
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(available=True).select_related('category').prefetch_related('reviews')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category__slug', 'product_type', 'featured']
    search_fields = ['name', 'description']
    ordering_fields = ['price_usd', 'price_gbp', 'created_at', 'name']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        product = self.get_object()
        reviews = product.reviews.select_related('user').all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_review(self, request, pk=None):
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            Review.objects.create(
                product=product,
                user=request.user,
                rating=serializer.validated_data['rating'],
                comment=serializer.validated_data['comment'],
            )
            return Response({'message': 'Review added successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        product = self.get_object()
        variants = product.variants.all()
        from .serializers import ProductVariantSerializer
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'product').all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in ('pending', 'paid'):
            return Response(
                {'error': 'This order cannot be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = 'cancelled'
        order.save()
        return Response({'message': 'Order cancelled successfully'})

    @action(detail=True, methods=['get'])
    def invoice(self, request, pk=None):
        order = self.get_object()
        items = OrderItem.objects.filter(order=order).select_related('product')
        data = {
            'order_id': order.id,
            'customer': f'{order.first_name} {order.last_name}',
            'email': order.email,
            'address': order.address,
            'city': order.city,
            'country': order.country,
            'currency': order.currency,
            'total': str(order.total_amount),
            'status': order.status,
            'items': [
                {
                    'product': item.product.name,
                    'price': str(item.price),
                    'quantity': item.quantity,
                    'total': str(item.get_cost()),
                }
                for item in items
            ],
        }
        return Response(data)


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def destroy(self, request, *args, **kwargs):
        request.user.delete()
        return Response({'message': 'Account deleted'}, status=status.HTTP_204_NO_CONTENT)
