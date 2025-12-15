from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<slug:category_slug>/', views.category_list, name='category_list'),
    path('search/', views.search, name='search'),
    path('add-product/', views.add_product, name='add_product'),  # Make sure this URL is correct
    path('<slug:slug>/add/', views.add_to_cart, name='add_to_cart'),
    path('<slug:slug>/dec/', views.decrease_from_cart, name='decrease_from_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/remove/<slug:slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]


