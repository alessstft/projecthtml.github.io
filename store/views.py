import json
import os
import uuid
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .forms import LoginForm, RegisterForm
from .models import Category, Product, Order, OrderItem, CartItem, Review, User, UserMeasurement, BonusTransaction


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
    amount_for_free_delivery = max(0, 3000 - cart_total)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'amount_for_free_delivery': amount_for_free_delivery,
    })


def checkout_page(request):
    cart_items = get_cart_items(request)
    cart_total = sum(item.product.price * item.quantity for item in cart_items)
    delivery_courier = 350 if cart_total < 3000 else 0
    delivery_express = 550
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'delivery_courier': delivery_courier,
        'delivery_express': delivery_express,
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'order_success.html', {'order': order})


@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    user = request.user

    # Пересчёт суммы и уровня
    user.recalc_total_spent()
    user.update_bonus_level()

    total_spent = user.total_spent_cached or 0

    # Calculate bonus progress
    bonus_transactions = BonusTransaction.objects.filter(user=user)[:20]
    if total_spent < 5000:
        bonus_progress = (total_spent / 5000) * 100
        remaining_for_silver = 5000 - total_spent
        remaining_for_gold = 15000 - total_spent
    elif total_spent < 15000:
        bonus_progress = ((total_spent - 5000) / 10000) * 100
        remaining_for_silver = 0
        remaining_for_gold = 15000 - total_spent
    else:
        bonus_progress = 100
        remaining_for_silver = 0
        remaining_for_gold = 0

    return render(request, 'profile.html', {
        'orders': orders,
        'total_spent': total_spent,
        'bonus_progress': bonus_progress,
        'remaining_for_silver': remaining_for_silver,
        'remaining_for_gold': remaining_for_gold,
        'bonus_transactions': bonus_transactions,
    })


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
    # Проверка: товар должен принадлежать текущей сессии или пользователю
    session_key = get_session_key(request)
    user = request.user if request.user.is_authenticated else None
    if user:
        if item.user_id and item.user_id != user.id:
            return JsonResponse({'error': 'Access denied'}, status=403)
    else:
        if item.session_key != session_key:
            return JsonResponse({'error': 'Access denied'}, status=403)
    if quantity <= 0:
        item.delete()
    else:
        item.quantity = quantity
        item.save()
    return JsonResponse({'success': True})


@csrf_exempt
def api_remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id)
    session_key = get_session_key(request)
    user = request.user if request.user.is_authenticated else None
    if user:
        if item.user_id and item.user_id != user.id:
            return JsonResponse({'error': 'Access denied'}, status=403)
    else:
        if item.session_key != session_key:
            return JsonResponse({'error': 'Access denied'}, status=403)
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
    
    # Если пользователь авторизован — берем данные из профиля
    if request.user.is_authenticated:
        first_name = request.user.name or ''
        last_name = request.user.last_name or ''
        email = request.user.email or ''
        phone = request.user.phone or ''
    else:
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
    total = max(0, subtotal + delivery_cost - bonus_used)
    user = request.user if request.user.is_authenticated else None

    order = Order.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        delivery_type=delivery_type,
        payment_method=data.get('payment_method', 'card'),
        address=address,
        comment=comment,
        bonus_used=bonus_used,
        subtotal=subtotal,
        delivery_cost=delivery_cost,
        total=total,
        status='new',
    )

    # Списание бонусов после создания заказа
    if user and bonus_used > 0:
        if user.bonus_balance >= bonus_used:
            user.bonus_balance -= bonus_used
            user.save(update_fields=['bonus_balance'])
            BonusTransaction.objects.create(
                user=user,
                amount=-bonus_used,
                transaction_type='spend',
                order=order,
                balance_after=user.bonus_balance,
                description=f'Списание бонусов за заказ #{order.id}'
            )
        else:
            bonus_used = 0
            order.bonus_used = 0
            order.save(update_fields=['bonus_used'])

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
    # Отправляем уведомление о новом заказе
    order.send_notification()
    return JsonResponse({'success': True, 'order_id': order.id})


@login_required
@csrf_exempt
def api_pay_order(request, order_id):
    """Имитация оплаты заказа"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if order.status not in ['new', 'processing']:
        return JsonResponse({'error': 'Заказ уже оплачен или отменён'}, status=400)
    
    # Имитируем оплату (в реальности здесь был бы вызов платёжного шлюза)
    old_status = order.status
    order.status = 'processing'
    order.save(update_fields=['status'])
    
    # Отправляем уведомление
    order.send_notification()
    
    return JsonResponse({'success': True, 'message': 'Оплата прошла успешно'})


@login_required
def purchase_history(request):
    """История покупок с фильтрами и пагинацией"""
    from django.core.paginator import Paginator

    orders = Order.objects.filter(user=request.user)

    # Фильтры
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '')

    if status_filter:
        orders = orders.filter(status=status_filter)
    if date_from:
        from datetime import datetime
        try:
            df = datetime.strptime(date_from, '%Y-%m-%d')
            orders = orders.filter(created_at__gte=df)
        except ValueError:
            pass
    if date_to:
        from datetime import datetime
        try:
            dt = datetime.strptime(date_to, '%Y-%m-%d')
            orders = orders.filter(created_at__lte=dt)
        except ValueError:
            pass
    if search:
        orders = orders.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(pk__icontains=search)
        )

    orders = orders.order_by('-created_at')

    # Пагинация
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Статистика
    all_orders = Order.objects.filter(user=request.user)
    stats = {
        'total_orders': all_orders.count(),
        'total_spent': sum(o.total for o in all_orders if o.status != 'cancelled'),
        'avg_order': 0,
        'delivered_count': all_orders.filter(status='delivered').count(),
    }
    if stats['total_orders'] > 0:
        stats['avg_order'] = int(stats['total_spent'] / stats['total_orders'])

    return render(request, 'purchase_history.html', {
        'page_obj': page_obj,
        'orders': page_obj.object_list,
        'stats': stats,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
        'status_choices': Order.STATUS_CHOICES,
    })


@login_required
def purchase_detail(request, order_id):
    """Детальная страница заказа"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'purchase_detail.html', {'order': order})


@login_required
@csrf_exempt
def api_reorder(request, order_id):
    """Повторить заказ — добавить товары в корзину"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    added = 0
    for item in order.items.all():
        if item.product:
            session_key = get_session_key(request)
            cart_item, created = CartItem.objects.get_or_create(
                session_key=session_key,
                product=item.product,
                size=item.size or 'M',
                defaults={'user': request.user, 'quantity': item.quantity}
            )
            if not created:
                cart_item.quantity += item.quantity
                cart_item.save()
            added += 1
    return JsonResponse({'success': True, 'added': added})


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
        card_number = data.get('card_number', '').replace(' ', '')
        # Сохраняем только последние 4 цифры для отображения
        request.user.card_number = card_number[-4:] if len(card_number) >= 4 else card_number
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


def save_uploaded_image(file):
    """Save uploaded image and return the static path."""
    if not file:
        return 'images/placeholder.jpg'

    # Get file extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        ext = '.jpg'

    # Generate unique filename
    filename = f"{uuid.uuid4().hex}{ext}"
    static_images_dir = os.path.join(settings.BASE_DIR, 'app', 'static', 'images')

    # Create directory if not exists
    os.makedirs(static_images_dir, exist_ok=True)

    # Save file
    filepath = os.path.join(static_images_dir, filename)
    with open(filepath, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return f'images/{filename}'


def parse_request_data(request):
    """Parse JSON or FormData from request."""
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Handle FormData
        data = {
            'name': request.POST.get('name', ''),
            'sku': request.POST.get('sku', ''),
            'price': request.POST.get('price', 0),
            'old_price': request.POST.get('old_price') or None,
            'category_id': request.POST.get('category_id') or None,
            'description': request.POST.get('description', ''),
            'sizes_in_stock': request.POST.get('sizes_in_stock', 'S:10,M:15,L:10,XL:5'),
            'is_new': request.POST.get('is_new') in ['true', 'on', 'True'],
            'is_popular': request.POST.get('is_popular') in ['true', 'on', 'True'],
        }
        return data, request.FILES.get('image')
    else:
        # Handle JSON
        data = json_body(request)
        return data, None


@login_required
@csrf_exempt
def api_admin_create_product(request):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)

    data, image_file = parse_request_data(request)

    # Handle image upload
    if image_file:
        image_path = save_uploaded_image(image_file)
    else:
        image_path = data.get('image', 'images/placeholder.jpg')

    category = None
    if data.get('category_id'):
        category = Category.objects.filter(pk=data['category_id']).first()

    product = Product.objects.create(
        name=data.get('name', ''),
        sku=data.get('sku', '') or f'SKU-{uuid.uuid4().hex[:8]}',
        price=int(data.get('price', 0) or 0),
        old_price=int(data.get('old_price')) if data.get('old_price') else None,
        description=data.get('description', ''),
        image=image_path,
        category=category,
        is_new=data.get('is_new', False),
        is_popular=data.get('is_popular', False),
        sizes_in_stock=data.get('sizes_in_stock', 'S:10,M:15,L:10,XL:5'),
        colors=data.get('colors', ''),
    )
    return JsonResponse({'success': True, 'id': product.id})


@login_required
@csrf_exempt
def api_admin_update_product(request, product_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)

    data, image_file = parse_request_data(request)
    product = get_object_or_404(Product, pk=product_id)

    # Handle image upload
    if image_file:
        product.image = save_uploaded_image(image_file)

    if data.get('category_id'):
        product.category = Category.objects.filter(pk=data['category_id']).first()
    else:
        product.category = None

    product.name = data.get('name', product.name)
    product.sku = data.get('sku', product.sku)
    product.price = int(data.get('price', product.price))
    product.old_price = int(data['old_price']) if data.get('old_price') and str(data.get('old_price', '')).isdigit() else None
    product.description = data.get('description', product.description)
    product.is_new = data.get('is_new', product.is_new)
    product.is_popular = data.get('is_popular', product.is_popular)
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


# Category API
@login_required
@csrf_exempt
def api_admin_create_category(request):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)

    data = json_body(request)
    name = data.get('name', '').strip()
    slug = data.get('slug', '').strip()

    if not name or not slug:
        return JsonResponse({'success': False, 'error': 'Название и slug обязательны'}, status=400)

    # Auto-generate slug if empty
    if not slug:
        from django.utils.text import slugify
        slug = slugify(name)

    if Category.objects.filter(slug=slug).exists():
        return JsonResponse({'success': False, 'error': 'Категория с таким slug уже существует'}, status=400)

    category = Category.objects.create(name=name, slug=slug)
    return JsonResponse({'success': True, 'id': category.id})


@login_required
@csrf_exempt
def api_admin_update_category(request, category_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)

    data = json_body(request)
    category = get_object_or_404(Category, pk=category_id)

    name = data.get('name', '').strip()
    slug = data.get('slug', '').strip()

    if not name or not slug:
        return JsonResponse({'success': False, 'error': 'Название и slug обязательны'}, status=400)

    # Check for duplicate slug
    existing = Category.objects.filter(slug=slug).exclude(pk=category_id).first()
    if existing:
        return JsonResponse({'success': False, 'error': 'Категория с таким slug уже существует'}, status=400)

    category.name = name
    category.slug = slug
    category.save()
    return JsonResponse({'success': True})


@login_required
@csrf_exempt
def api_admin_delete_product(request, product_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    return JsonResponse({'success': True})


@login_required
@csrf_exempt
def api_admin_delete_product(request, product_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    return JsonResponse({'success': True})


@login_required
@csrf_exempt
def api_admin_delete_category(request, category_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Access denied'}, status=403)
    category = get_object_or_404(Category, pk=category_id)
    category.delete()
    return JsonResponse({'success': True})


# === User Measurements API ===

def api_get_user_measurements(request):
    """Получение измерений текущего пользователя"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Необходима авторизация'}, status=401)
    try:
        measurements = request.user.measurements
        return JsonResponse(measurements.to_dict())
    except UserMeasurement.DoesNotExist:
        return JsonResponse({
            'height': 170, 'chest': 92, 'waist': 76, 'hips': 98,
            'shoulders': 116, 'arm_length': 58, 'leg_length': 80,
            'shoe_size': 40, 'weight': 70, 'gender': 'neutral',
        })


@login_required
@csrf_exempt
def api_update_user_measurements(request):
    """Обновление измерений пользователя"""
    data = json_body(request)
    defaults = {
        'height': int(data.get('height', 170)),
        'chest': int(data.get('chest', 92)),
        'waist': int(data.get('waist', 76)),
        'hips': int(data.get('hips', 98)),
        'shoulders': int(data.get('shoulders', 116)),
        'arm_length': int(data.get('arm_length', 58)),
        'leg_length': int(data.get('leg_length', 80)),
        'shoe_size': int(data.get('shoe_size', 40)),
        'weight': int(data.get('weight', 70)),
        'gender': data.get('gender', 'neutral'),
    }
    measurements, created = UserMeasurement.objects.get_or_create(
        user=request.user, defaults=defaults
    )
    if not created:
        for field, value in defaults.items():
            setattr(measurements, field, value)
        measurements.save()
    return JsonResponse({'success': True, 'measurements': measurements.to_dict()})
