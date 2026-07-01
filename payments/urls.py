from django.urls import path
from . import webhooks

app_name = 'payments'

urlpatterns = [
    path('webhook/stripe/', webhooks.stripe_webhook, name='stripe_webhook'),
]
