import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from .forms import LoginForm, RegisterForm
from .models import Category, Product, Order, OrderItem, CartItem, Review, User


def get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def get_cart_items(request):
    session_key = get_session_key(request)
    user = request.user if request.user.is_authenticated else None
    items = CartItem.objects.filter(session_key=session_key)
    if user:
        user_items = CartItem.objects.filter(user=user)
        items = items | user_items
    return items.distinct()


def index(request):
    categories = Category.objects.all()
    popular_products = Product.objects.filter(is_popular=True)[:6]
    return render(request, 'index.html', {'categories': categories, 'popular_products': popular_products})


def catalog(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    category_slug = request.GET.get('cat')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', 'popular')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    colors = request.GET.getlist('color')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search:
        products = products.filter(name__icontains=search)
    if price_min and price_min.isdigit():
        products = products.filter(price__gte=int(price_min))
    if price_max and price_max.isdigit():
        products = products.filter(price__lte=int(price_max))

    if colors:
        filtered = []
        for product in products:
            product_colors = [c.strip() for c in product.colors.split(',')] if product.colors else []
            if any(color in product_colors for color in colors):
                filtered.append(product)
        products = filtered

    if sort == 'price-asc':
        products = sorted(products, key=lambda p: p.price)
    elif sort == 'price-desc':
        products = sorted(products, key=lambda p: p.price, reverse=True)
    elif sort == 'new':
        products = [p for p in products if p.is_new]
    elif sort == 'rating':
        products = sorted(products, key=lambda p: p.rating or 0, reverse=True)
    else:
        products = sorted(products, key=lambda p: not p.is_popular)

    return render(request, 'catalog.html', {
        'categories': categories,
        'products': products,
        'active_category': category_slug,
        'active_sort': sort,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = product.reviews.order_by('-created_at')[:10]
    return render(request, 'product.html', {'product': product, 'reviews': reviews})


def cart_page(request):
    cart_items = get_cart_items(request)
    cart_total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'cart_total': cart_total})


def checkout_page(request):
    cart_items = get_cart_items(request)
    cart_total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'checkout.html', {'cart_items': cart_items, 'cart_total': cart_total})


def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'order_success.html', {'order': order})


@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    total_spent = sum(o.total for o in orders if o.status not in ['cancelled', 'refunded'])
    return render(request, 'profile.html', {'orders': orders, 'total_spent': total_spent})


def about(request):
    return render(request, 'about.html')


def contacts(request):
    return render(request, 'contacts.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, 'Добро пожаловать!')
            return redirect(request.GET.get('next') or 'index')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация успешна! Войдите в аккаунт.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта')
    return redirect('index')


def admin_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        raise Http404()
    products = Product.objects.all()
    orders = Order.objects.order_by('-created_at')
    users = User.objects.filter(role='customer')
    categories = Category.objects.all()
    total_revenue = sum(o.total for o in orders if o.status != 'cancelled')
    return render(request, 'admin/index.html', {
        'products': products,
        'orders': orders,
        'users': users,
        'categories': categories,
        'total_revenue': total_revenue,
    })


def json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return {}


def api_products(request):
    products = Product.objects.all()
    return JsonResponse([product.to_dict() for product in products], safe=False)


def api_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return JsonResponse(product.to_dict())


def api_popular_products(request):
    products = Product.objects.filter(is_popular=True)[:6]
    return JsonResponse([product.to_dict() for product in products], safe=False)


def api_categories(request):
    categories = Category.objects.all()
    return JsonResponse([category.to_dict() for category in categories], safe=False)


def api_get_cart(request):
    items = get_cart_items(request)
    return JsonResponse([item.to_dict() for item in items], safe=False)


@csrf_exempt
def api_add_to_cart(request):
    data = json_body(request)
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    size = data.get('size', 'M')
    product = get_object_or_404(Product, pk=product_id)
    session_key = get_session_key(request)
    user = request.user if request.user.is_authenticated else None
    cart_item, created = CartItem.objects.get_or_create(
        session_key=session_key, product=product, size=size,
        defaults={'user': user, 'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        if user and not cart_item.user:
            cart_item.user = user
        cart_item.save()
    count = sum(item.quantity for item in get_cart_items(request))
    return JsonResponse({'success': True, 'cart_count': count})


@csrf_exempt
def api_update_cart_item(request, item_id):
    data = json_body(request)
    quantity = int(data.get('quantity', 1))
    item = get_object_or_404(CartItem, pk=item_id)
    if quantity <= 0:
        item.delete()
    else:
        item.quantity = quantity
        item.save()
    return JsonResponse({'success': True})


@csrf_exempt
def api_remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id)
    item.delete()
    return JsonResponse({'success': True})


@csrf_exempt
def api_clear_cart(request):
    items = get_cart_items(request)
    items.delete()
    return JsonResponse({'success': True})


@csrf_exempt
def api_create_order(request):
    data = json_body(request)
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    delivery_type = data.get('delivery_type', 'courier')
    address = data.get('address', '')
    comment = data.get('comment', '')
    bonus_used = int(data.get('bonus_used', 0) or 0)

    items = get_cart_items(request)
    if not items.exists():
        return JsonResponse({'error': 'Корзина пуста'}, status=400)

    subtotal = sum(item.product.price * item.quantity for item in items)
    delivery_cost = 0 if subtotal >= 3000 else (550 if delivery_type == 'express' else 350)
    if delivery_type == 'pickup':
        delivery_cost = 0
    total = subtotal + delivery_cost - bonus_used
    user = request.user if request.user.is_authenticated else None

    if user and bonus_used > 0:
        if user.bonus_balance >= bonus_used:
            user.bonus_balance -= bonus_used
            user.save()
        else:
            bonus_used = 0

    order = Order.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        delivery_type=delivery_type,
        address=address,
        comment=comment,
        bonus_used=bonus_used,
        subtotal=subtotal,
        delivery_cost=delivery_cost,
        total=total,
        status='new',
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            product_image=item.product.image,
            price=item.product.price,
            quantity=item.quantity,
            size=item.size,
        )

    if user and total > 0:
        cashback_percent = {'bronze': 3, 'silver': 5, 'gold': 10}.get(user.bonus_level, 3)
        cashback = int(total * cashback_percent / 100)
        user.bonus_balance += cashback
        user.save()

    items.delete()
    return JsonResponse({'success': True, 'order_id': order.id})


@login_required
def api_get_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return JsonResponse([order.to_dict() for order in orders], safe=False)


@login_required
@csrf_exempt
def api_add_review(request):
    data = json_body(request)
    product_id = data.get('product_id')
    rating = int(data.get('rating', 0))
    text = data.get('text', '')
    if not all([product_id, rating, text]):
        return JsonResponse({'error': 'Missing data'}, status=400)
    product = get_object_or_404(Product, pk=product_id)
    review = Review.objects.create(user=request.user, product=product, rating=rating, text=text)
    all_reviews = Review.objects.filter(product=product)
    total_rating = sum(r.rating for r in all_reviews)
    product.rating = round(total_rating / all_reviews.count(), 1)
    product.reviews_count = all_reviews.count()
    product.save()
    return JsonResponse({'success': True})


def api_get_reviews(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = product.reviews.order_by('-created_at')
    return JsonResponse([review.to_dict() for review in reviews], safe=False)


@login_required
def api_admin_orders(request):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    orders = Order.objects.order_by('-created_at')
    return JsonResponse([order.to_dict() for order in orders], safe=False)


@login_required
@csrf_exempt
def api_admin_update_order_status(request, order_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    data = json_body(request)
    order = get_object_or_404(Order, pk=order_id)
    order.status = data.get('status', order.status)
    order.save()
    return JsonResponse({'success': True})


@login_required
@csrf_exempt
def api_update_profile(request):
    data = json_body(request)
    request.user.name = data.get('name', request.user.name)
    request.user.phone = data.get('phone', request.user.phone)
    request.user.payment_method = data.get('payment_method', request.user.payment_method)
    if 'card_number' in data:
        card_number = data.get('card_number', '')
        request.user.card_number = card_number.replace(' ', '')[-4:]
    request.user.card_holder = data.get('card_holder', request.user.card_holder).upper()
    request.user.card_expiry = data.get('card_expiry', request.user.card_expiry)
    request.user.save()
    return JsonResponse({'success': True})


@login_required
@csrf_exempt
def api_change_password(request):
    data = json_body(request)
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    if not request.user.check_password(old_password):
        return JsonResponse({'success': False, 'error': 'Неверный текущий пароль'})
    request.user.set_password(new_password)
    request.user.save()
    return JsonResponse({'success': True})


def api_current_user(request):
    if request.user.is_authenticated:
        return JsonResponse(request.user.to_dict())
    return JsonResponse(None, safe=False)


@login_required
@csrf_exempt
def api_admin_create_product(request):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    data = json_body(request)
    category = None
    if data.get('category_id'):
        category = Category.objects.filter(pk=data['category_id']).first()
    product = Product.objects.create(
        name=data.get('name', ''),
        sku=data.get('sku', ''),
        price=data.get('price', 0),
        old_price=data.get('old_price') or None,
        description=data.get('description', ''),
        image=data.get('image', 'images/placeholder.jpg'),
        category=category,
        is_new=bool(data.get('is_new', False)),
        is_popular=bool(data.get('is_popular', False)),
        sizes_in_stock=data.get('sizes_in_stock', 'S:10,M:15,L:10,XL:5'),
        colors=data.get('colors', ''),
    )
    return JsonResponse({'success': True, 'id': product.id})


@login_required
@csrf_exempt
def api_admin_update_product(request, product_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    data = json_body(request)
    product = get_object_or_404(Product, pk=product_id)
    if data.get('category_id'):
        product.category = Category.objects.filter(pk=data['category_id']).first()
    product.name = data.get('name', product.name)
    product.sku = data.get('sku', product.sku)
    product.price = data.get('price', product.price)
    product.old_price = data.get('old_price', product.old_price)
    product.description = data.get('description', product.description)
    product.image = data.get('image', product.image)
    product.is_new = bool(data.get('is_new', product.is_new))
    product.is_popular = bool(data.get('is_popular', product.is_popular))
    if 'sizes_in_stock' in data:
        product.sizes_in_stock = data['sizes_in_stock']
    if 'colors' in data:
        product.colors = data['colors']
    product.save()
    return JsonResponse({'success': True})


@login_required
@csrf_exempt
def api_admin_delete_product(request, product_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    return JsonResponse({'success': True})
