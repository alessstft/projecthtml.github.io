from django.db import migrations


def create_products(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    products = [
        {
            'name': 'Худи Oversize Black',
            'price': 3490,
            'old_price': 4990,
            'image': '/static/images/худи.jpg',
            'sku': '4322231',
            'category': 'hoodies',
            'is_new': False,
            'is_popular': True,
            'description': 'Качественное худи оверсайз из плотного хлопка. Удобный крой, капюшон с верёвками. Идеально для повседневной носки.',
        },
        {
            'name': 'Худи Sport Grey',
            'price': 3990,
            'old_price': None,
            'image': '/static/images/худи2.jpg',
            'sku': '2452342',
            'category': 'hoodies',
            'is_new': True,
            'is_popular': True,
            'description': 'Спортивное худи из мягкого материала. Идеально для прогулок и тренировок.',
        },
        {
            'name': 'Худи Minimal White',
            'price': 4290,
            'old_price': None,
            'image': '/static/images/худи3.jpg',
            'sku': '235203',
            'category': 'hoodies',
            'is_new': False,
            'is_popular': True,
            'description': 'Минималистичное худи белого цвета. Лаконичный дизайн для повседневной носки.',
        },
        {
            'name': 'Худи Urban Navy',
            'price': 3670,
            'old_price': 4590,
            'image': '/static/images/худи4.jpg',
            'sku': '4235304',
            'category': 'hoodies',
            'is_new': False,
            'is_popular': True,
            'description': 'Городское худи тёмно-синего цвета. Стиль оверсайз.',
        },
        {
            'name': 'Футболка Basic Black',
            'price': 1290,
            'old_price': None,
            'image': '/static/images/тишка.jpg',
            'sku': '6324891',
            'category': 'tshirts',
            'is_new': False,
            'is_popular': True,
            'description': 'Классическая базовая футболка чёрного цвета. 100% хлопок.',
        },
        {
            'name': 'Футболка Graphic White',
            'price': 1590,
            'old_price': None,
            'image': '/static/images/тишка2.jpg',
            'sku': '34698232',
            'category': 'tshirts',
            'is_new': True,
            'is_popular': True,
            'description': 'Футболка с принтом. Хлопок премиум качества.',
        },
        {
            'name': 'Футболка Cotton Grey',
            'price': 1390,
            'old_price': None,
            'image': '/static/images/тишка3.jpg',
            'sku': '4382973',
            'category': 'tshirts',
            'is_new': False,
            'is_popular': True,
            'description': 'Мягкая хлопковая футболка серого цвета.',
        },
        {
            'name': 'Футболка Oversize Cream',
            'price': 1490,
            'old_price': None,
            'image': '/static/images/тишка4.jpg',
            'sku': '8491704',
            'category': 'tshirts',
            'is_new': False,
            'is_popular': True,
            'description': 'Оверсайз футболка бежевого оттенка.',
        },
        {
            'name': 'Рубашка Casual Blue',
            'price': 2790,
            'old_price': None,
            'image': '/static/images/рубашка.jpg',
            'sku': '71498781',
            'category': 'shirts',
            'is_new': False,
            'is_popular': True,
            'description': 'Кэжуал рубашка голубого цвета. Идеально для офиса и отдыха.',
        },
    ]
    for data in products:
        Product.objects.create(**data)


def delete_products(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    Product.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_products, delete_products),
    ]
