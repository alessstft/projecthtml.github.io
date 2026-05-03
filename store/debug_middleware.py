"""
Мiddleware для отладки и логирования Fashion Store
Версия: 1.2

Назначение:
- Логирование всех запросов и ответов
- Замер времени выполнения запросов
- Проверка валидности данных
- Отслеживание ошибок
"""

import time
import logging
from django.conf import settings

logger = logging.getLogger('store')


class DebugLoggingMiddleware:
    """Middleware для логирования запросов в DEBUG-режиме."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Только в DEBUG режиме
        if not getattr(settings, 'DEBUG', False):
            return self.get_response(request)

        # Замер времени начала
        start_time = time.time()

        # Логирование запроса
        logger.info(
            f"REQUEST: {request.method} {request.path} "
            f"IP: {request.META.get('REMOTE_ADDR', 'unknown')}"
        )

        # Логирование данных POST запросов
        if request.method == 'POST' and hasattr(settings, 'ENABLE_API_LOGGING') and settings.ENABLE_API_LOGGING:
            try:
                body = request.body.decode('utf-8')
                if body and len(body) < 1000:
                    logger.debug(f"BODY: {body}")
            except Exception:
                pass

        # Выполнение запроса
        response = self.get_response(request)

        # Замер времени выполнения
        duration = time.time() - start_time

        # Логирование ответа
        logger.info(
            f"RESPONSE: {response.status_code} "
            f"Duration: {duration:.3f}s"
        )

        # Предупреждение для медленных запросов
        if duration > 1.0:
            logger.warning(
                f"SLOW REQUEST: {request.method} {request.path} "
                f"took {duration:.3f}s"
            )

        # Добавление заголовка с временем выполнения
        response['X-Request-Duration'] = f'{duration:.3f}s'

        return response


class ValidationMiddleware:
    """Middleware для дополнительной валидации в DEBUG-режиме."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, 'DEBUG', False):
            return self.get_response(request)

        # Проверка Content-Type для POST запросов
        if request.method == 'POST':
            content_type = request.META.get('CONTENT_TYPE', '')
            if 'application/json' in content_type and not request.body:
                logger.warning(
                    f"Empty JSON body for POST {request.path}"
                )

        response = self.get_response(request)
        return response
