from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.conf import settings
from django.core.mail import send_mail


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, default='customer')
    bonus_balance = models.IntegerField(default=0)
    BONUS_LEVELS = [
        ('bronze', 'Бронзовый'),
        ('silver', 'Серебряный'),
        ('gold', 'Золотой'),
    ]
    bonus_level = models.CharField(max_length=20, default='bronze', choices=BONUS_LEVELS)
    bonus_level_updated_at = models.DateTimeField(null=True, blank=True)
    total_spent_cached = models.IntegerField(default=0)
    payment_method = models.CharField(max_length=50, default='card')
    card_number = models.CharField(max_length=19, blank=True)
    card_holder = models.CharField(max_length=100, blank=True)
    card_expiry = models.CharField(max_length=5, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.name or self.email

    def get_bonus_level_display(self):
        return dict(self.BONUS_LEVELS).get(self.bonus_level, self.bonus_level)

    def update_bonus_level(self):
        """Автоматическое обновление уровня на основе total_spent"""
        from django.utils import timezone
        total = self.total_spent_cached or 0
        old_level = self.bonus_level
        if total >= 15000:
            new_level = 'gold'
        elif total >= 5000:
            new_level = 'silver'
        else:
            new_level = 'bronze'
        if old_level != new_level:
            self.bonus_level = new_level
            self.bonus_level_updated_at = timezone.now()
            self.save(update_fields=['bonus_level', 'bonus_level_updated_at'])
        return old_level != new_level

    def recalc_total_spent(self):
        """Пересчёт total_spent на основе доставленных заказов"""
        total = sum(
            o.total for o in Order.objects.filter(user=self, status='delivered')
        )
        self.total_spent_cached = int(total)
        self.save(update_fields=['total_spent_cached'])
        return self.total_spent_cached

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'bonus_balance': self.bonus_balance,
            'bonus_level': self.bonus_level,
            'bonus_level_display': self.get_bonus_level_display(),
            'total_spent': self.total_spent_cached,
            'role': self.role,
        }


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'slug': self.slug}


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    old_price = models.IntegerField(null=True, blank=True)
    image = models.CharField(max_length=255, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    is_new = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    material = models.CharField(max_length=100, blank=True)
    care = models.CharField(max_length=100, blank=True)
    colors = models.CharField(max_length=255, blank=True)
    color_names = models.CharField(max_length=255, blank=True)
    sizes = models.CharField(max_length=255, blank=True)
    sizes_in_stock = models.CharField(max_length=255, blank=True)
    rating = models.FloatField(default=0)
    reviews_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def sizes_list(self):
        return [size.strip() for size in self.sizes.split(',')] if self.sizes else []

    @property
    def colors_list(self):
        return [color.strip() for color in self.colors.split(',')] if self.colors else []

    @property
    def color_names_list(self):
        return [name.strip() for name in self.color_names.split(',')] if self.color_names else []

    @property
    def sizes_in_stock_dict(self):
        result = {}
        if not self.sizes_in_stock:
            return result
        for pair in self.sizes_in_stock.split(','):
            if ':' in pair:
                k, v = pair.split(':')
                result[k.strip()] = int(v.strip())
        return result

    @property
    def stock_total(self):
        return sum(self.sizes_in_stock_dict.values())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'old_price': self.old_price,
            'image': self.image,
            'sku': self.sku,
            'category': self.category.slug if self.category else None,
            'category_name': self.category.name if self.category else None,
            'is_new': self.is_new,
            'is_popular': self.is_popular,
            'description': self.description,
            'colors': self.colors_list,
            'color_names': self.color_names_list,
            'sizes': self.sizes_list,
            'sizes_in_stock': self.sizes_in_stock_dict,
            'rating': self.rating,
            'reviews_count': self.reviews_count,
            'material': self.material,
            'care': self.care,
        }


class Order(models.Model):
    user = models.ForeignKey('store.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    delivery_type = models.CharField(max_length=50, blank=True, default='courier')
    payment_method = models.CharField(max_length=50, blank=True, default='card', choices=[('card', 'Карта онлайн'), ('receiving', 'При получении')])
    address = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    bonus_used = models.IntegerField(default=0)
    subtotal = models.IntegerField()
    delivery_cost = models.IntegerField(default=0)
    total = models.IntegerField()
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
        ('refunded', 'Возврат'),
    ]
    status = models.CharField(max_length=50, default='new', choices=STATUS_CHOICES)
    status_updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text="Причина отмены/возврата и т.д.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Заказ #{self.id} - {self.first_name}'

    def save(self, *args, **kwargs):
        old_status = None
        if self.pk:
            old_status = Order.objects.filter(pk=self.pk).values_list('status', flat=True).first()
        super().save(*args, **kwargs)
        # При смене статуса на "доставлен" — начисляем кэшбэк и обновляем уровень
        if old_status and old_status != 'delivered' and self.status == 'delivered':
            if self.user:
                self.user.recalc_total_spent()
                self.user.update_bonus_level()
                # Кэшбэк
                cashback_percent = {'bronze': 3, 'silver': 5, 'gold': 10}.get(self.user.bonus_level, 3)
                cashback = int(self.total * cashback_percent / 100)
                if cashback > 0:
                    self.user.bonus_balance += cashback
                    self.user.save(update_fields=['bonus_balance'])
                    BonusTransaction.objects.create(
                        user=self.user,
                        amount=cashback,
                        transaction_type='cashback',
                        order=self,
                        balance_after=self.user.bonus_balance,
                        description=f'Кэшбэк за заказ #{self.id}'
                    )
        # При отмене/возврате — возврат списанных бонусов
        if old_status and old_status != self.status and self.status in ['cancelled', 'refunded']:
            if self.user and self.bonus_used > 0:
                self.user.bonus_balance += self.bonus_used
                self.user.save(update_fields=['bonus_balance'])
                BonusTransaction.objects.create(
                    user=self.user,
                    amount=self.bonus_used,
                    transaction_type='refund',
                    order=self,
                    balance_after=self.user.bonus_balance,
                    description=f'Возврат бонусов за отменённый заказ #{self.id}'
                )
        
        # Отправка уведомления при изменении статуса
        if old_status and old_status != self.status:
            self.send_notification()

    def send_notification(self):
        """Отправка уведомления о заказе клиенту и менеджеру"""
        manager_email = 'Marketolog.icht@gmail.com'
        
        items_text = '\n'.join([
            f'- {item.product_name} x{item.quantity} = {item.price * item.quantity}₽'
            for item in self.items.all()
        ])
        
        # Письмо менеджеру (всегда)
        subject_manager = f'Новый заказ #{self.id} — {self.get_status_display()}'
        payment_display = self.get_payment_method_display() if hasattr(self, 'get_payment_method_display') else self.payment_method
        delivery_display = self.get_delivery_type_display() if hasattr(self, 'get_delivery_type_display') else self.delivery_type
        message_manager = f"""
Поступил новый заказ #{self.id}!

Клиент: {self.first_name} {self.last_name}
Email: {self.email or 'Не указан'}
Телефон: {self.phone or 'Не указан'}
Статус: {self.get_status_display()}

Товары:
{items_text}

Подытог: {self.subtotal}₽
Доставка: {self.delivery_cost}₽ ({delivery_display})
Способ оплаты: {payment_display}
Итого: {self.total}₽

Комментарий: {self.comment or 'Нет'}

Fashion Store
"""
        try:
            send_mail(
                subject_manager,
                message_manager,
                settings.DEFAULT_FROM_EMAIL,
                [manager_email],
                fail_silently=True,
            )
        except Exception:
            pass
        
        # Письмо клиенту (только если есть email)
        if self.email:
            subject_client = f'Ваш заказ #{self.id} — {self.get_status_display()}'
            message_client = f"""
Здравствуйте, {self.first_name}!

Ваш заказ #{self.id} успешно оформлен.
Статус: {self.get_status_display()}

Товары:
{items_text}

Подытог: {self.subtotal}₽
Доставка: {self.delivery_cost}₽
Бонусов списано: {self.bonus_used}
Итого: {self.total}₽

Спасибо за покупку!
Fashion Store
"""
            try:
                send_mail(
                    subject_client,
                    message_client,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.email],
                    fail_silently=True,
                )
                return True
            except Exception:
                return False
        return True
        
        # Email для менеджера
        manager_email = 'Marketolog.icht@gmail.com'
        
        items_text = '\n'.join([
            f'- {item.product_name} x{item.quantity} = {item.price * item.quantity}₽'
            for item in self.items.all()
        ])
        
        # Письмо клиенту
        subject_client = f'Ваш заказ #{self.id} — {self.get_status_display()}'
        message_client = f"""
Здравствуйте, {self.first_name}!

Ваш заказ #{self.id} обновлён.
Статус: {self.get_status_display()}

Товары:
{items_text}

Подытог: {self.subtotal}₽
Доставка: {self.delivery_cost}₽
Бонусов списано: {self.bonus_used}
Итого: {self.total}₽

Спасибо за покупку!
Fashion Store
"""
        # Письмо менеджеру
        subject_manager = f'Новый заказ #{self.id} — {self.get_status_display()}'
        payment_display = self.get_payment_method_display() if hasattr(self, 'get_payment_method_display') else self.payment_method
        message_manager = f"""
Поступил новый заказ #{self.id}!

Клиент: {self.first_name} {self.last_name}
Email: {self.email}
Телефон: {self.phone}
Статус: {self.get_status_display()}

Товары:
{items_text}

Подытог: {self.subtotal}₽
Доставка: {self.delivery_cost}₽ ({self.get_delivery_type_display() if hasattr(self, 'get_delivery_type_display') else self.delivery_type})
Способ оплаты: {payment_display}
Итого: {self.total}₽

Комментарий: {self.comment or 'Нет'}

Fashion Store
"""
        try:
            # Письмо клиенту
            send_mail(
                subject_client,
                message_client,
                settings.DEFAULT_FROM_EMAIL,
                [self.email],
                fail_silently=True,
            )
            # Письмо менеджеру
            send_mail(
                subject_manager,
                message_manager,
                settings.DEFAULT_FROM_EMAIL,
                [manager_email],
                fail_silently=True,
            )
            return True
        except Exception:
            return False
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'status': self.status,
            'status_display': self.get_status_display(),
            'subtotal': self.subtotal,
            'delivery_cost': self.delivery_cost,
            'bonus_used': self.bonus_used,
            'total': self.total,
            'delivery_type': self.delivery_type,
            'address': self.address,
            'comment': self.comment,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'status_updated_at': self.status_updated_at.isoformat() if self.status_updated_at else None,
            'order_items': [item.to_dict() for item in self.items.all()],
        }


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    product_image = models.CharField(max_length=255, blank=True)
    price = models.IntegerField()
    quantity = models.IntegerField()
    size = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.product_name

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product.id if self.product else None,
            'product_name': self.product_name,
            'product_image': self.product_image,
            'price': self.price,
            'quantity': self.quantity,
            'size': self.size,
        }


class CartItem(models.Model):
    session_key = models.CharField(max_length=100)
    user = models.ForeignKey('store.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    size = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session_key', 'product', 'size')

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product.id,
            'product': self.product.to_dict(),
            'quantity': self.quantity,
            'size': self.size,
        }


class Review(models.Model):
    user = models.ForeignKey('store.User', on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Отзыв {self.user.email} - {self.product.name}'

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user.name or self.user.email,
            'rating': self.rating,
            'text': self.text,
            'created_at': self.created_at.isoformat(),
        }


class UserMeasurement(models.Model):
    """Модель для хранения измерений пользователя (рост, обхваты и т.д.)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='measurements')
    height = models.IntegerField(default=170, help_text="Рост в см")
    chest = models.IntegerField(default=92, help_text="Обхват груди в см")
    waist = models.IntegerField(default=76, help_text="Обхват талии в см")
    hips = models.IntegerField(default=98, help_text="Обхват бёдер в см")
    shoulders = models.IntegerField(default=116, help_text="Ширина плеч в см")
    arm_length = models.IntegerField(default=58, help_text="Длина руки в см")
    leg_length = models.IntegerField(default=80, help_text="Длина ноги в см")
    shoe_size = models.IntegerField(default=40, help_text="Размер обуви")
    weight = models.IntegerField(default=70, help_text="Вес в кг")
    gender = models.CharField(max_length=10, default='neutral', choices=[
        ('male', 'Мужской'),
        ('female', 'Женский'),
        ('neutral', 'Универсальный'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Измерения {self.user}'

    def to_dict(self):
        return {
            'id': self.id,
            'height': self.height,
            'chest': self.chest,
            'waist': self.waist,
            'hips': self.hips,
            'shoulders': self.shoulders,
            'arm_length': self.arm_length,
            'leg_length': self.leg_length,
            'shoe_size': self.shoe_size,
            'weight': self.weight,
            'gender': self.gender,
        }

    def suggest_size(self):
        """Рекомендация размера на основе измерений"""
        avg_measure = (self.chest + self.waist + self.hips) / 3
        if self.height < 160:
            if avg_measure < 85: return 'XS'
            elif avg_measure < 95: return 'S'
            elif avg_measure < 105: return 'M'
            else: return 'L'
        elif self.height < 175:
            if avg_measure < 90: return 'S'
            elif avg_measure < 100: return 'M'
            elif avg_measure < 110: return 'L'
            else: return 'XL'
        else:
            if avg_measure < 95: return 'M'
            elif avg_measure < 105: return 'L'
            elif avg_measure < 115: return 'XL'
            else: return 'XXL'
            

class BonusTransaction(models.Model):
    """Модель для учёта всех операций с бонусами"""
    TRANSACTION_TYPES = [
        ('earn', 'Начисление'),
        ('spend', 'Списание'),
        ('cashback', 'Кэшбэк'),
        ('refund', 'Возврат'),
        ('adjust', 'Корректировка'),
        ('expire', 'Списание по сроку'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bonus_transactions')
    amount = models.IntegerField(help_text="Положительная — начисление, отрицательная — списание")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    order = models.ForeignKey('Order', null=True, blank=True, on_delete=models.SET_NULL, related_name='bonus_transactions')
    balance_after = models.IntegerField(null=True, blank=True, help_text="Баланс после операции")
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.amount > 0 else ''
        return f'{self.user.email}: {sign}{self.amount} ({self.get_transaction_type_display()})'

    def save(self, *args, **kwargs):
        if self.balance_after is None and self.user:
            self.balance_after = self.user.bonus_balance
        super().save(*args, **kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'transaction_type_display': self.get_transaction_type_display(),
            'order_id': self.order.id if self.order else None,
            'balance_after': self.balance_after,
            'created_at': self.created_at.isoformat(),
            'description': self.description,
        }
