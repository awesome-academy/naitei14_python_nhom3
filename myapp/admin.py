from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Category, Product, ProductImage,
    CartItem, Order, OrderItem
)


# Custom User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'full_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'full_name', 'phone_number']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'full_name', 'address', 'phone_number',
                      'activation_token', 'reset_token')
        }),
    )


# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['name']


# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'stock_quantity', 'category', 'is_featured', 'created_at']
    list_filter = ['category', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_featured']
    ordering = ['-created_at']


# ProductImage Admin
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'image_url', 'is_primary']
    list_filter = ['is_primary', 'product']
    search_fields = ['product__name']


# CartItem Admin
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'product__name']


# OrderItem Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price_at_purchase']


# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_date', 'total_amount', 'status', 'updated_at']
    list_filter = ['status', 'order_date']
    search_fields = ['user__username', 'shipping_address']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['order_date', 'total_amount']
    
    fieldsets = [
        ('Order Information', {
            'fields': ['user', 'order_date', 'total_amount', 'status']
        }),
        ('Shipping & Payment', {
            'fields': ['shipping_address', 'payment_method']
        }),
        ('Admin Actions', {
            'fields': ['rejection_reason', 'updated_at']
        }),
    ]


# OrderItem Admin
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price_at_purchase']
    list_filter = ['order__order_date']
    search_fields = ['order__id', 'product__name']


# Customize admin site
admin.site.site_header = "Admin Ecommerce PythonTraining"
admin.site.site_title = "Ecommerce Admin"
admin.site.index_title = "Quản lý hệ thống"
