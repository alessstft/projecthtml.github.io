import os
from pathlib import Path


def load_env(path):
    path = Path(path)
    if path.exists():
        with path.open(encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if value and ((value[0] == value[-1]) and value[0] in "'\""):
                    value = value[1:-1]
                os.environ.setdefault(key, value)


BASE_DIR = Path(__file__).resolve().parent.parent
load_env(BASE_DIR / '.env')


def env(key, default=None):
    return os.environ.get(key, default)


SECRET_KEY = env('SECRET_KEY', 'django-insecure-fashionstore-dev-key-change-in-production-2024')

DEBUG = env('DEBUG', 'True').lower() in ('1', 'true', 'yes')

ALLOWED_HOSTS = [host.strip() for host in env('ALLOWED_HOSTS', '*,localhost,127.0.0.1,testserver').split(',') if host.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fashionstore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fashionstore.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(env('EMAIL_PORT', '587'))
EMAIL_USE_TLS = env('EMAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
EMAIL_HOST_USER = env('EMAIL_HOST_USER', 'marketolog.ichto@gmail.com')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', '')

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', 'marketolog.ichto@gmail.com')
