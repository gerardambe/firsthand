from django.urls import path
from . import views
from .webhooks import webhook


app_name = 'orders'

urlpatterns = [
    path('create', views.create_checkout, name='create_checkout'),
    path('cache_checkout_data/', views.cache_checkout_data, name='cache_checkout_data'),
    path('wh/', webhook, name='webhook'),
]
