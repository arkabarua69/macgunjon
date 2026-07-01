from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('products/', views.dashboard_products, name='products'),
    path('orders/', views.dashboard_orders, name='orders'),
    path('orders/<int:order_id>/', views.dashboard_order_detail, name='order_detail'),
    path('payments/', views.dashboard_payments, name='payments'),
    path('customers/', views.dashboard_customers, name='customers'),
    path('reports/', views.dashboard_reports, name='reports'),
    path('site-settings/', views.dashboard_site_settings, name='site_settings'),
    path('email-logs/', views.dashboard_email_logs, name='email_logs'),
    path('delivery-logs/', views.dashboard_delivery_logs, name='delivery_logs'),
    path('coupons/', views.dashboard_coupons, name='coupons'),
    path('newsletter/', views.dashboard_newsletter, name='newsletter'),
    path('blog/', views.dashboard_blog, name='blog'),
    path('contact-messages/', views.dashboard_contact_messages, name='contact_messages'),
]
