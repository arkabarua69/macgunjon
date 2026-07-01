from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')
router.register(r'users', views.UserViewSet, basename='user')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
