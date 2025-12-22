from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomPasswordChangeView

app_name = 'myapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/', views.detail, name='detail'),
    
    # Auth URLs
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path("password-change/", CustomPasswordChangeView.as_view(), name="password_change"),
    
    # Email verification & Password reset
    path('activate/<str:token>/', views.activate_account, name='activate_account'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    
    # Admin site (riêng biệt)
    path('admin-site/', views.admin_login_view, name='admin_site'),
    path('admin-site/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-site/orders/', views.admin_orders, name='admin_orders'),
    path('admin-site/orders/<int:order_id>/view/', views.admin_order_view, name='admin_order_view'),
    path('admin-site/orders/<int:order_id>/update-status/', views.admin_order_update_status, name='admin_order_update_status'),
    path('admin-site/products/', views.admin_products, name='admin_products'),
    path('admin-site/products/create/', views.admin_product_create, name='admin_product_create'),
    path('admin-site/products/<int:product_id>/edit/', views.admin_product_edit, name='admin_product_edit'),
    path('admin-site/products/<int:product_id>/delete/', views.admin_product_delete, name='admin_product_delete'),
    path('admin-site/users/', views.admin_users, name='admin_users'),
    path('admin-site/users/<int:user_id>/view/', views.admin_user_view, name='admin_user_view'),
    path('admin-site/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin-site/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin-site/users/<int:user_id>/toggle-active/', views.admin_user_toggle_active, name='admin_user_toggle_active'),
    path('admin-site/categories/', views.admin_categories, name='admin_categories'),
    path('admin-site/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('admin-site/categories/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin-site/categories/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
]
