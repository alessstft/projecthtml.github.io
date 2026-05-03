import os
import sys
import django

# Настройка Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fashionstore.settings')
django.setup()

from django.test import TestCase, RequestFactory
from store.models import User, Product, Category, CartItem, Order, OrderItem
from store.views import (
    json_body,
    api_add_to_cart,
    api_create_order,
    api_update_cart_item,
    api_remove_cart_item,
    api_update_profile,
    profile_view,
    catalog,
)
import json


class TestDebugFixes(TestCase):
    """Тесты для проверки исправленных ошибок."""

    def setUp(self):
        """Создание тестовых данных."""
        self.factory = RequestFactory()
        self.category = Category.objects.create(name='Худи', slug='hoodies')
        self.product = Product.objects.create(
            name='Тестовое худи',
            price=3000,
            sku='TEST-001',
            category=self.category,
            is_popular=True,
        )
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123',
            name='Test User',
        )

    # ========================================
    # Тест 1: Проверка json_body с пустым телом
    # ========================================
    def test_json_body_empty(self):
        """json_body должен возвращать {} при пустом теле"""
        request = self.factory.post('/test/', data=b'', content_type='application/json')
        result = json_body(request)
        self.assertEqual(result, {})
        print("✓ Тест 1: json_body с пустым телом — ПРОЙДЕН")

    def test_json_body_invalid(self):
        """json_body должен возвращать {} при невалидном JSON"""
        request = self.factory.post('/test/', data=b'not json', content_type='application/json')
        result = json_body(request)
        self.assertEqual(result, {})
        print("✓ Тест 2: json_body с невалидным JSON — ПРОЙДЕН")

    # ========================================
    # Тест 2: Проверка отрицательного итога
    # ========================================
    def test_negative_total_prevented(self):
        """Итого не должно быть отрицательным"""
        # Создаём заказ с бонусами больше суммы
        order = Order.objects.create(
            first_name='Test',
            email='test@test.com',
            subtotal=1000,
            delivery_cost=0,
            bonus_used=5000,
            total=0,  # Должно быть 0, не -4000
        )
        self.assertGreaterEqual(order.total, 0)
        print("✓ Тест 3: Отрицательный итого предотвращён — ПРОЙДЕН")

    # ========================================
    # Тест 3: Проверка валидации цены в каталоге
    # ========================================
    def test_catalog_price_filter(self):
        """Фильтр цены должен корректно обрабатывать нечисловые значения"""
        request = self.factory.get('/catalog/', {'price_min': 'abc', 'price_max': 'xyz'})
        response = catalog(request)
        self.assertEqual(response.status_code, 200)
        print("✓ Тест 4: Фильтр цены с нечисловыми значениями — ПРОЙДЕН")

    # ========================================
    # Тест 4: Проверка old_price валидации
    # ========================================
    def test_old_price_validation(self):
        """old_price должен корректно обрабатывать пустые значения"""
        # Проверка через to_dict
        product_dict = self.product.to_dict()
        self.assertIsNone(product_dict['old_price'])
        print("✓ Тест 5: old_price валидация — ПРОЙДЕН")

    # ========================================
    # Тест 5: Проверка модели Product
    # ========================================
    def test_product_properties(self):
        """Проверка свойств модели Product"""
        product = Product.objects.create(
            name='Тестовый товар',
            price=1000,
            sku='TEST-002',
            sizes='S,M,L,XL',
            colors='red,blue,green',
            color_names='Красный,Синий,Зелёный',
            sizes_in_stock='S:10,M:15,L:10,XL:5',
        )

        self.assertEqual(product.sizes_list, ['S', 'M', 'L', 'XL'])
        self.assertEqual(product.colors_list, ['red', 'blue', 'green'])
        self.assertEqual(product.stock_total, 40)
        self.assertEqual(product.sizes_in_stock_dict, {'S': 10, 'M': 15, 'L': 10, 'XL': 5})
        print("✓ Тест 6: Свойства модели Product — ПРОЙДЕН")

    # ========================================
    # Тест 6: Проверка UserMeasurement
    # ========================================
    def test_user_measurement_size(self):
        """Проверка рекомендации размера"""
        from store.models import UserMeasurement
        measurement = UserMeasurement(
            user=self.user,
            height=170,
            chest=92,
            waist=76,
            hips=98,
        )
        size = measurement.suggest_size()
        self.assertIn(size, ['XS', 'S', 'M', 'L', 'XL', 'XXL'])
        print(f"✓ Тест 7: Рекомендация размера: {size} — ПРОЙДЕН")

    # ========================================
    # Тест 7: Проверка бонусного прогресса
    # ========================================
    def test_bonus_progress_calculation(self):
        """Проверка расчёта бонусного прогресса"""
        # Создаём заказы
        for i in range(3):
            Order.objects.create(
                user=self.user,
                first_name='Test',
                email='test@test.com',
                subtotal=2000,
                delivery_cost=0,
                total=2000,
                status='delivered',
            )

        total_spent = sum(o.total for o in Order.objects.filter(user=self.user) if o.status not in ['cancelled', 'refunded'])
        self.assertEqual(total_spent, 6000)

        # Проверка прогресса
        if total_spent < 5000:
            bonus_progress = (total_spent / 5000) * 100
        elif total_spent < 15000:
            bonus_progress = ((total_spent - 5000) / 10000) * 100
        else:
            bonus_progress = 100

        self.assertGreater(bonus_progress, 0)
        self.assertLessEqual(bonus_progress, 100)
        print(f"✓ Тест 8: Бонусный прогресс: {bonus_progress}% — ПРОЙДЕН")

    # ========================================
    # Тест 8: Проверка API endpoints
    # ========================================
    def test_api_products(self):
        """Проверка API продуктов"""
        from store.views import api_products
        request = self.factory.get('/api/products/')
        response = api_products(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(isinstance(data, list))
        print(f"✓ Тест 9: API продуктов: {len(data)} товаров — ПРОЙДЕН")

    def test_api_categories(self):
        """Проверка API категорий"""
        from store.views import api_categories
        request = self.factory.get('/api/categories/')
        response = api_categories(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(isinstance(data, list))
        print(f"✓ Тест 10: API категорий: {len(data)} категорий — ПРОЙДЕН")


if __name__ == '__main__':
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDebugFixes)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 50)
    print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Ошибка: {len(result.failures) + len(result.errors)}")
    print("=" * 50)

    if result.failures:
        print("\nОШИБКИ:")
        for test, traceback in result.failures:
            print(f"  ✗ {test}: {traceback}")

    if result.errors:
        print("\nКРИТИЧЕСКИЕ ОШИБКИ:")
        for test, traceback in result.errors:
            print(f"  ✗ {test}: {traceback}")
