from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('download/<uuid:token>/', views.download_file, name='download'),
    path('download/expired/', views.download_expired, name='download_expired'),
]
