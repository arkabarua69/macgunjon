from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('payment/<int:order_id>/', views.order_payment, name='payment'),
    path('success/', views.order_success, name='success'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('<int:order_id>/cancel/', views.order_cancel, name='order_cancel'),
    path('<int:order_id>/refund/', views.order_refund, name='order_refund'),
    path('<int:order_id>/invoice/', views.order_invoice, name='order_invoice'),
]
