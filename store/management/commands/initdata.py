from django.core.management.base import BaseCommand
from store.models import Category, Product, User


class Command(BaseCommand):
    help = 'Заполнить базу данных начальными данными для магазина'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Худи', 'slug': 'hoodies'},
            {'name': 'Футболки', 'slug': 'tshirts'},
            {'name': 'Рубашки', 'slug': 'shirts'},
        ]
        for category_data in categories:
            Category.objects.update_or_create(slug=category_data['slug'], defaults=category_data)

        if not Product.objects.exists():
            products = [
                {
                    'name': 'Худи Oversize Black',
                    'price': 3490,
                    'old_price': 4990,
                    'image': 'images/худи.jpg',
                    'sku': '4322231',
                    'category_slug': 'hoodies',
                    'is_new': False,
                    'is_popular': True,
                    'rating': 4.8,
                    'reviews_count': 127,
                    'description': 'Качественное худи оверсайз из плотного хлопка. Удобный крой, капюшон с верёвками. Идеально для повседневной носки.',
                    'colors': '#1a1a1a,#6b7280,#1e3a5f',
                    'color_names': 'Чёрный,Серый,Тёмно-синий',
                    'sizes': 'S,M,L,XL,XXL',
                    'sizes_in_stock': 'S:5,M:12,L:8,XL:3,XXL:0',
                    'material': '80% хлопок, 20% полиэстер',
                    'care': 'Машинная стирка при 30°C',
                },
                {
                    'name': 'Худи Sport Grey',
                    'price': 3990,
                    'image': 'images/худи2.jpg',
                    'sku': '2452342',
                    'category_slug': 'hoodies',
                    'is_new': True,
                    'is_popular': True,
                    'rating': 4.9,
                    'reviews_count': 89,
                    'description': 'Спортивное худи из мягкого материала. Идеально для прогулок и тренировок.',
                    'colors': '#9ca3af,#374151',
                    'color_names': 'Серый,Тёмно-серый',
                    'sizes': 'S,M,L,XL',
                    'sizes_in_stock': 'S:8,M:15,L:10,XL:6',
                    'material': '85% хлопок, 15% вискоза',
                    'care': 'Деликатная стирка при 30°C',
                },
                {
                    'name': 'Футболка Grey',
                    'price': 1290,
                    'image': 'images/тишка.jpg',
                    'sku': '6324891',
                    'category_slug': 'tshirts',
                    'is_new': False,
                    'is_popular': True,
                    'rating': 4.5,
                    'reviews_count': 342,
                    'description': 'Футболка серого цвета. Хлопок премиум качества.',
                    'colors': '#9ca3af,#f5f5f5,#1a1a1a',
                    'color_names': 'Серый,Белый,Чёрный',
                    'sizes': 'XS,S,M,L,XL',
                    'sizes_in_stock': 'XS:15,S:25,M:30,L:20,XL:10',
                    'material': '100% хлопок',
                    'care': 'Машинная стирка при 40°C',
                },
            ]

            for product_data in products:
                category = Category.objects.get(slug=product_data.pop('category_slug'))
                Product.objects.create(category=category, **product_data)

        admin_email = 'admin@fashionstore.ru'
        admin_password = 'admin123'
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(email=admin_email, password=admin_password, name='Администратор', role='admin')

        self.stdout.write(self.style.SUCCESS('Initial data loaded successfully.'))
