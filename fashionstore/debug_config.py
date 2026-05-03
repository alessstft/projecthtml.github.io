
import os

# ========================================
# ОСНОВНЫЕ ФЛАГИ ОТЛАДКИ
# ========================================

# Режим отладки Django (включает детальную информацию об ошибках)
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

# Режим отладки JavaScript
JS_DEBUG_MODE = os.environ.get('JS_DEBUG', 'True').lower() == 'true'

# Уровень логирования
DEBUG_LEVEL = os.environ.get('DEBUG_LEVEL', 'normal')  # 'verbose', 'normal', 'minimal'

# ========================================
# ИНСТРУМЕНТЫ ОТЛАДКИ
# ========================================

# Django Debug Toolbar
ENABLE_DEBUG_TOOLBAR = DEBUG and os.environ.get('ENABLE_DEBUG_TOOLBAR', 'True').lower() == 'true'

# Логирование SQL запросов
ENABLE_SQL_LOGGING = DEBUG and os.environ.get('ENABLE_SQL_LOGGING', 'False').lower() == 'true'

# Логирование производительности
ENABLE_PERFORMANCE_LOGGING = DEBUG and os.environ.get('ENABLE_PERFORMANCE_LOGGING', 'False').lower() == 'true'

# ========================================
# ЛОГИРОВАНИЕ
# ========================================

if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '[{asctime}] {levelname} {name} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose' if DEBUG_LEVEL == 'verbose' else 'simple',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'debug.log',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'DEBUG' if DEBUG_LEVEL == 'verbose' else 'INFO',
            },
            'django.db.backends': {
                'handlers': ['console'] if ENABLE_SQL_LOGGING else [],
                'level': 'DEBUG',
                'propagate': False,
            },
            'store': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
            },
        },
    }

# ========================================
# DEBUG TOOLBAR
# ========================================

if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'store',
        'debug_toolbar',
    ]
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', 'localhost']

# ========================================
# УСЛОВНАЯ КОМПИЛЯЦИЯ
# ========================================

# В DEBUG-режиме: дополнительные проверки и валидация
if DEBUG:
    # Дополнительные проверки данных
    ENABLE_EXTRA_VALIDATION = True
    # Логирование всех API запросов
    ENABLE_API_LOGGING = True
    # Проверка CSRF для всех эндпоинтов
    STRICT_CSRF = False
else:
    ENABLE_EXTRA_VALIDATION = False
    ENABLE_API_LOGGING = False
    STRICT_CSRF = True
