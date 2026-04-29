# -*- coding: utf-8 -*-
"""
Декораторы для views модуля store.

Содержит общие декораторы для проверки прав доступа,
чтобы избежать дублирования кода.
"""

from functools import wraps
from django.http import JsonResponse


def admin_required(view_func):
    """
    Декоратор для проверки прав администратора.

    Проверяет, что пользователь авторизован и имеет роль 'admin'.

    Пример использования:
        @admin_required
        def api_admin_orders(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Необходима авторизация'},
                status=401
            )
        if request.user.role != 'admin':
            return JsonResponse(
                {'error': 'Доступ запрещён'},
                status=403
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def require_post(view_func):
    """
    Декоратор, требующий метод POST для API endpoints.

    Возвращает ошибку 405, если метод не POST.

    Пример использования:
        @csrf_exempt
        @require_post
        def api_add_to_cart(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method != 'POST':
            return JsonResponse(
                {'error': 'Метод не поддерживается'},
                status=405
            )
        return view_func(request, *args, **kwargs)
    return wrapper
