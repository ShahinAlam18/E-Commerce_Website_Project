from decimal import Decimal
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Order, OrderItem, Cart


def checkout_start(request):
    # Build order items from session cart first (backwards compatible)
    session_cart = request.session.get('cart', {})
    items = []
    total = Decimal('0.00')

    if session_cart:
        products = Product.objects.filter(id__in=session_cart.keys())
        for product in products:
            qty = int(session_cart.get(str(product.id), 0))
            if qty > 0:
                items.append((product, qty, product.price))
                total += Decimal(qty) * product.price
    elif request.user.is_authenticated:
        # If no session cart, try database Cart for logged-in user
        user_cart = Cart.get_for_user(request.user)
        cart_items = list(user_cart.items.select_related('product'))
        for ci in cart_items:
            items.append((ci.product, ci.quantity, ci.unit_price))
            total += ci.unit_price * ci.quantity

    if not items:
        return redirect('products:cart_view')

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total_amount=total,
        status='pending',
    )
    for product, qty, price in items:
        OrderItem.objects.create(order=order, product=product, quantity=qty, price=price)

    # Stripe disabled: immediately mark as paid and redirect to success
    order.status = 'paid'
    order.save()
    request.session['cart'] = {}
    if request.user.is_authenticated:
        try:
            Cart.get_for_user(request.user).clear()
        except Exception:
            pass
    return redirect('orders:checkout_success')


def checkout_success(request):
    request.session['cart'] = {}
    if request.user.is_authenticated:
        try:
            Cart.get_for_user(request.user).clear()
        except Exception:
            pass
    return render(request, 'orders/checkout_success.html')


def checkout_cancel(request):
    return render(request, 'orders/checkout_cancel.html')


from django.http import HttpResponse


