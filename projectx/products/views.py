from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.text import slugify
from .models import Category, Product, Tag
from orders.models import Cart


def is_admin(user):
    return user.is_authenticated and user.profile.is_admin


def home(request):
    children = Product.objects.filter(category__slug='children')[:4]
    men = Product.objects.filter(category__slug='men')[:4]
    women = Product.objects.filter(category__slug='women')[:4]
    return render(request, 'home.html', {
        'children_products': children,
        'men_products': men,
        'women_products': women,
    })


@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_slug = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        try:
            # Get or create category
            category = Category.objects.get(slug=category_slug)
            
            # Create product
            product = Product.objects.create(
                name=name,
                slug=slugify(name),
                category=category,
                price=price,
                description=description,
                image=image
            )
            
            messages.success(request, f'Product "{name}" has been added successfully!')
            return redirect('products:product_detail', slug=product.slug)
            
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
            
    return render(request, 'products/add_product.html')


def category_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = category.products.select_related('category').prefetch_related('tags').all()
    return render(request, 'products/category_list.html', {
        'category': category,
        'products': products,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'products/product_detail.html', {
        'product': product,
    })


def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.user.is_authenticated:
        user_cart = Cart.get_for_user(request.user)
        user_cart.add_product(product, 1)
    else:
        cart = request.session.get('cart', {})
        cart[str(product.id)] = cart.get(str(product.id), 0) + 1
        request.session['cart'] = cart
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f'{product.name} added to cart'})
    
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or 'products:home'
    return redirect(next_url)


def cart_view(request):
    items = []
    total = 0.0
    if request.user.is_authenticated:
        user_cart = Cart.get_for_user(request.user)
        cart_items = user_cart.items.select_related('product')
        for ci in cart_items:
            lt = float(ci.unit_price) * ci.quantity
            total += lt
            items.append({'product': ci.product, 'quantity': ci.quantity, 'line_total': lt})
    else:
        cart = request.session.get('cart', {})
        if cart:
            products = Product.objects.filter(id__in=cart.keys())
            for product in products:
                quantity = cart.get(str(product.id), 0)
                line_total = quantity * float(product.price)
                total += line_total
                items.append({'product': product, 'quantity': quantity, 'line_total': line_total})
    return render(request, 'orders/cart.html', {'items': items, 'total': total})


def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.user.is_authenticated:
        user_cart = Cart.get_for_user(request.user)
        user_cart.remove_product(product)
    else:
        cart = request.session.get('cart', {})
        if str(product.id) in cart:
            cart.pop(str(product.id))
            request.session['cart'] = cart
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or 'products:cart_view'
    return redirect(next_url)


def decrease_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.user.is_authenticated:
        user_cart = Cart.get_for_user(request.user)
        # emulate decrement: set quantity - 1
        try:
            ci = user_cart.items.get(product=product)
            if ci.quantity > 1:
                ci.quantity -= 1
                ci.save()
            else:
                ci.delete()
        except Exception:
            pass
    else:
        cart = request.session.get('cart', {})
        pid = str(product.id)
        if pid in cart:
            if cart[pid] > 1:
                cart[pid] -= 1
            else:
                cart.pop(pid)
            request.session['cart'] = cart
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or 'products:cart_view'
    return redirect(next_url)


def search(request):
    query = request.GET.get('q', '').strip()
    products = []
    if query:
        products = Product.objects.select_related('category').prefetch_related('tags').filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(tags__name__icontains=query)
        ).distinct()
    return render(request, 'products/search_results.html', {'query': query, 'products': products})


@login_required
def add_product(request):
    # Check if user is admin
    try:
        is_admin = request.user.profile.is_admin
    except:
        # If UserProfile doesn't exist, check if user is superuser as fallback
        is_admin = request.user.is_superuser
    
    if not is_admin:
        messages.error(request, 'Access denied. Only admin users can add products.')
        return redirect('products:home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')
        
        try:
            category = Category.objects.get(id=category_id)
            product = Product.objects.create(
                name=name,
                slug=slug,
                description=description,
                price=price,
                category=category,
                image=image
            )
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('products:product_detail', slug=product.slug)
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')
    
    categories = Category.objects.all()
    return render(request, 'products/add_product.html', {'categories': categories})


