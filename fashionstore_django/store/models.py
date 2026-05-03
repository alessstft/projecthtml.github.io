from django.conf import settings
from django.db import models


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('hoodies', 'Худи'),
        ('tshirts', 'Футболки'),
        ('shirts', 'Рубашки'),
    ]

    name = models.CharField(max_length=200)
    price = models.IntegerField()
    old_price = models.IntegerField(null=True, blank=True)
    image = models.CharField(max_length=200)
    sku = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_new = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    description = models.TextField()

    def __str__(self):
        return self.name


class CustomerProfile(models.Model):
    LEVEL_BRONZE = 'bronze'
    LEVEL_SILVER = 'silver'
    LEVEL_GOLD = 'gold'
    LEVEL_PLATINUM = 'platinum'

    LEVEL_CHOICES = [
        (LEVEL_BRONZE, 'Бронзовый'),
        (LEVEL_SILVER, 'Серебряный'),
        (LEVEL_GOLD, 'Золотой'),
        (LEVEL_PLATINUM, 'Платиновый'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bonus_points = models.IntegerField(default=0)
    total_spent = models.IntegerField(default=0)
    address = models.CharField(max_length=300, blank=True, default='')

    @property
    def level(self):
        if self.total_spent >= 20000:
            return self.LEVEL_PLATINUM
        if self.total_spent >= 10000:
            return self.LEVEL_GOLD
        if self.total_spent >= 5000:
            return self.LEVEL_SILVER
        return self.LEVEL_BRONZE

    @property
    def level_label(self):
        return dict(self.LEVEL_CHOICES).get(self.level, 'Бронзовый')

    def __str__(self):
        return f'{self.user.username} profile'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id} — {self.user.username} — {self.total}₽'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()

    def __str__(self):
        return f'{self.product} x{self.quantity} ({self.price}₽)'

    @property
    def subtotal(self):
        return self.price * self.quantity


class BonusTransaction(models.Model):
    profile = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='bonustransaction_set')
    amount = models.IntegerField()
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.profile.user.username} — {self.amount} ({self.description})'
