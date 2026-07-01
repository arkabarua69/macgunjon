from rest_framework import serializers
from products.models import Product, Category, Review, Wishlist, ProductVariant
from orders.models import Order, OrderItem
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'product_count']

    def get_product_count(self, obj):
        return obj.products.filter(available=True).count()


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    display_image = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price_usd', 'price_gbp',
            'product_type', 'display_image', 'image_url', 'stock', 'available',
            'featured', 'category', 'average_rating', 'review_count',
            'created_at', 'updated_at',
        ]

    def get_average_rating(self, obj):
        return obj.get_average_rating()

    def get_review_count(self, obj):
        return obj.reviews.count()


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    get_cost = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity', 'get_cost']

    def get_get_cost(self, obj):
        return obj.get_cost()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'first_name', 'last_name', 'email', 'address',
            'postal_code', 'city', 'country', 'currency', 'total_amount',
            'status', 'created_at', 'updated_at', 'items',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'country', 'date_joined']
        read_only_fields = ['email', 'date_joined']


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'created_at']
        read_only_fields = ['created_at']


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'price_usd', 'price_gbp', 'stock', 'sku']
