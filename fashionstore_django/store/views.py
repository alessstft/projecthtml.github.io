import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import CustomerProfile, Order, OrderItem, Product


def get_products_json():
    products = Product.objects.all()
    result = []
    for p in products:
        result.append({
            'id': str(p.id),
            'name': p.name,
            'price': p.price,
            'oldPrice': p.old_price,
            'image': p.image,
            'sku': p.sku,
            'category': p.category,
            'isNew': p.is_new,
            'isPopular': p.is_popular,
            'description': p.description,
        })
    return json.dumps(result)


def get_customer_profile(user):
    profile, _ = CustomerProfile.objects.get_or_create(user=user)
    return profile


def build_level_data(profile):
    thresholds = {
        CustomerProfile.LEVEL_BRONZE: 0,
        CustomerProfile.LEVEL_SILVER: 5000,
        CustomerProfile.LEVEL_GOLD: 10000,
        CustomerProfile.LEVEL_PLATINUM: 20000,
    }
    current_level = profile.level
    next_level = None
    progress_percent = 100
    current_threshold = thresholds[current_level]
    next_threshold = None

    if current_level == CustomerProfile.LEVEL_BRONZE:
        next_level = CustomerProfile.LEVEL_SILVER
    elif current_level == CustomerProfile.LEVEL_SILVER:
        next_level = CustomerProfile.LEVEL_GOLD
    elif current_level == CustomerProfile.LEVEL_GOLD:
        next_level = CustomerProfile.LEVEL_PLATINUM

    if next_level:
        next_threshold = thresholds[next_level]
        progress_percent = min(100, max(0, int((profile.total_spent - current_threshold) / (next_threshold - current_threshold) * 100)))
        points_to_next = next_threshold - profile.total_spent
    else:
        next_threshold = thresholds[CustomerProfile.LEVEL_PLATINUM]
        points_to_next = 0

    return {
        'current_level': current_level,
        'current_level_name': profile.level_label,
        'next_level': next_level,
        'next_level_name': dict(CustomerProfile.LEVEL_CHOICES).get(next_level, 'Платиновый'),
        'progress_percent': progress_percent,
        'current_threshold': current_threshold,
        'next_threshold': next_threshold,
        'points_to_next': max(0, points_to_next),
    }


def index(request):
    return render(request, 'index.html', {
        'products_json': get_products_json(),
        'page': 'home',
    })


def catalog(request):
    return render(request, 'catalog.html', {
        'products_json': get_products_json(),
        'page': 'catalog',
    })


def product_detail(request, product_id):
    return render(request, 'product.html', {
        'products_json': get_products_json(),
        'page': 'catalog',
        'product_id': product_id,
    })


def about(request):
    return render(request, 'about.html', {
        'page': 'about',
    })


def contacts(request):
    return render(request, 'contacts.html', {
        'page': 'contacts',
    })


def login_view(request):
    next_url = request.GET.get('next', '/')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(request.POST.get('next') or '/')
    else:
        form = AuthenticationForm(request)
    return render(request, 'login.html', {
        'form': form,
        'next': next_url,
        'page': 'login',
    })


def register_view(request):
    next_url = request.GET.get('next', '/')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            get_customer_profile(user)
            login(request, user)
            return redirect(request.POST.get('next') or '/')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {
        'form': form,
        'next': next_url,
        'page': 'register',
    })


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required(login_url='login')
def profile_view(request):
    profile = get_customer_profile(request.user)
    orders = request.user.orders.prefetch_related('items__product').order_by('-created_at')
    level_data = build_level_data(profile)

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.save()

        profile.address = request.POST.get('address', '').strip()
        profile.save()

        from django.contrib import messages
        messages.success(request, 'Профиль успешно обновлён')
        return redirect('profile')

    return render(request, 'profile.html', {
        'page': 'profile',
        'profile': profile,
        'orders': orders,
        'level_data': level_data,
    })


@login_required(login_url='login')
def bonus_view(request):
    profile = get_customer_profile(request.user)
    level_data = build_level_data(profile)
    return render(request, 'bonus.html', {
        'page': 'bonuses',
        'profile': profile,
        'level_data': level_data,
    })


@login_required(login_url='login')
@require_POST
def checkout(request):
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)

    items = payload.get('items', [])
    if not items:
        return JsonResponse({'success': False, 'message': 'Корзина пуста'}, status=400)

    total = 0
    order = Order.objects.create(user=request.user, total=0)

    for item in items:
        product_id = str(item.get('id', ''))
        quantity = int(item.get('quantity', 1))
        product = Product.objects.filter(id=product_id).first()
        if not product or quantity <= 0:
            continue
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price,
        )
        total += product.price * quantity

    if not order.items.exists():
        order.delete()
        return JsonResponse({'success': False, 'message': 'Нет доступных товаров в заказе'}, status=400)

    order.total = total
    order.save()

    profile = get_customer_profile(request.user)
    profile.total_spent += total
    profile.bonus_points += total // 20
    profile.save()

    # Send email notification
    subject = f'Новый заказ #{order.id}'
    message = f'Пользователь: {request.user.username} ({request.user.email})\n\n'
    message += 'Товары:\n'
    for item in order.items.all():
        message += f'- {item.product.name} x{item.quantity} = {item.subtotal}₽\n'
    message += f'\nИтого: {order.total}₽\n'
    message += f'Дата: {order.created_at.strftime("%d.%m.%Y %H:%M")}'

    try:
        send_mail(
            subject,
            message,
            'marketolog.ichto@gmail.com',
            ['marketolog.ichto@gmail.com'],
            fail_silently=False,
        )
    except Exception as e:
        # Log error but don't fail the checkout
        print(f'Email send error: {e}')

    return JsonResponse({'success': True, 'message': 'Заказ оформлен', 'order_id': order.id})


def cart(request):
    return render(request, 'cart.html', {
        'products_json': get_products_json(),
        'page': 'cart',
    })
