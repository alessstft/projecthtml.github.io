from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_page, name='cart'),
    path('checkout/', views.checkout_page, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('profile/', views.profile_view, name='profile'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),

    # Products API
    path('api/products/', views.api_products, name='api_products'),
    path('api/products/popular/', views.api_popular_products, name='api_popular_products'),
    path('api/products/<int:product_id>/', views.api_product, name='api_product'),

    # Cart API
    path('api/categories/', views.api_categories, name='api_categories'),
    path('api/cart/', views.api_get_cart, name='api_get_cart'),
    path('api/cart/add/', views.api_add_to_cart, name='api_add_to_cart'),
    path('api/cart/update/<int:item_id>/', views.api_update_cart_item, name='api_update_cart_item'),
    path('api/cart/remove/<int:item_id>/', views.api_remove_cart_item, name='api_remove_cart_item'),
    path('api/cart/clear/', views.api_clear_cart, name='api_clear_cart'),

    # Orders API
    path('api/orders/', views.api_get_orders, name='api_get_orders'),
    path('api/reviews/', views.api_add_review, name='api_add_review'),
    path('api/reviews/<int:product_id>/', views.api_get_reviews, name='api_get_reviews'),
    path('api/checkout/create/', views.api_create_order, name='api_create_order'),

    # Profile API
    path('api/profile/update/', views.api_update_profile, name='api_update_profile'),
    path('api/profile/password/', views.api_change_password, name='api_change_password'),
    path('api/user/', views.api_current_user, name='api_current_user'),

    # Admin API - Products
    path('api/admin/products/', views.api_admin_create_product, name='api_admin_create_product'),
    path('api/admin/products/<int:product_id>/', views.api_admin_update_product, name='api_admin_update_product'),
    path('api/admin/products/<int:product_id>/delete/', views.api_admin_delete_product, name='api_admin_delete_product'),
    path('api/admin/orders/', views.api_admin_orders, name='api_admin_orders'),
    path('api/admin/orders/<int:order_id>/status/', views.api_admin_update_order_status, name='api_admin_update_order_status'),

    # Admin API - Categories
    path('api/admin/categories/', views.api_admin_create_category, name='api_admin_create_category'),
    path('api/admin/categories/<int:category_id>/', views.api_admin_update_category, name='api_admin_update_category'),
    path('api/admin/categories/<int:category_id>/delete/', views.api_admin_delete_category, name='api_admin_delete_category'),
]
