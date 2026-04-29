# Fashion Store — Django Application

Онлайн-магазин одежды, реализованный на Django.

## Структура проекта

```
projecthtml.github.io/
├── fashionstore/           # Django проект
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/                  # Django приложение магазина
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── management/
│   │   └── commands/
│   │       └── initdata.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── templates/              # Django шаблоны
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── admin/
│   │   └── index.html
│   ├── base.html
│   ├── cart.html
│   ├── catalog.html
│   ├── checkout.html
│   ├── contacts.html
│   ├── index.html
│   ├── order_success.html
│   ├── product.html
│   ├── profile.html
│   └── about.html
├── app/                    # Статические файлы и старые Flask-ресурсы
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
├── manage.py               # Точка входа Django
├── requirements.txt        # Зависимости
└── README.md               # Документация
```

## Установка и запуск

1. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Выполните миграции и загрузите начальные данные:
```bash
python manage.py migrate
python manage.py initdata
```

4. Запустите приложение:
```bash
python manage.py runserver
```

5. Откройте в браузере: http://localhost:8000

## Тестовые аккаунты

**Администратор:**
- Email: admin@fashionstore.ru
- Пароль: admin123

**Покупатель:** зарегистрируйтесь через форму регистрации

## Функционал

- Просмотр каталога товаров с фильтрацией
- Поиск товаров
- Добавление в корзину
- Выбор размера товара
- Оформление заказа в 3 шага
- Система авторизации (регистрация, вход)
- Личный кабинет с историей заказов
- Бонусная программа (3 уровня лояльности)
- Отзывы и рейтинги товаров
- Админ-панель для управления заказами

## Технологии

- Flask 3.0
- Flask-SQLAlchemy
- Flask-Login
- SQLite
