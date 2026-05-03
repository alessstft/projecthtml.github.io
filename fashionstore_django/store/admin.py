from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'old_price', 'is_new', 'is_popular')
    list_filter = ('category', 'is_new', 'is_popular')
    search_fields = ('name',)
