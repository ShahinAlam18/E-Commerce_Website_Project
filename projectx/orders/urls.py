from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/start/', views.checkout_start, name='checkout_start'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),
]


