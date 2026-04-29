from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


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
    payment_method = models.CharField(max_length=50, default='card')
    card_number = models.CharField(max_length=19, blank=True)
    card_holder = models.CharField(max_length=100, blank=True)
    card_expiry = models.CharField(max_length=5, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.name or self.email

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'bonus_balance': self.bonus_balance,
            'bonus_level': self.bonus_level,
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
    delivery_type = models.CharField(max_length=50, blank=True)
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
    ]
    status = models.CharField(max_length=50, default='new', choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Заказ #{self.id} - {self.first_name}'

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'status': self.status,
            'subtotal': self.subtotal,
            'delivery_cost': self.delivery_cost,
            'total': self.total,
            'created_at': self.created_at.isoformat(),
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
