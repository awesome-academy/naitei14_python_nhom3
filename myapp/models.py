from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal
from .enums import ORDER_STATUS_CHOICES
from .constants import MAX_DIGITS, DECIMAL_PLACES
from myapp.enums import ORDER_STATUS_COMPLETED


# 1. User model (kế thừa AbstractUser)
class User(AbstractUser):
    USER_ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=USER_ROLE_CHOICES,
        default='user'
    )
    full_name = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=False)
    activation_token = models.CharField(
        max_length=255,
        blank=True,
        help_text='Token kích hoạt tài khoản 1 lần'
    )
    reset_token = models.CharField(
        max_length=255,
        blank=True,
        help_text='Token reset mật khẩu 1 lần'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


# 2. Category model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


# 3. Product model
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    is_featured = models.BooleanField(
        default=False,
        help_text='Sản phẩm nổi bật'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


# 4. ProductImage model
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_url = models.CharField(max_length=255)
    is_primary = models.BooleanField(
        default=False,
        help_text='Ảnh đại diện'
    )
    
    class Meta:
        db_table = 'product_images'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
    
    def __str__(self):
        return f"Image for {self.product.name}"


# 5. CartItem model
class CartItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = [['user', 'product']]
        indexes = [
            models.Index(fields=['user', 'product'], name='idx_user_product_unique'),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} x {self.quantity}"


# 6. Order model
class Order(models.Model):
    
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )
    shipping_address = models.TextField(
        help_text='Lưu địa chỉ tại thời điểm đặt hàng'
    )
    payment_method = models.CharField(max_length=50, blank=True)
    rejection_reason = models.TextField(
        blank=True,
        help_text='Lý do admin từ chối đơn'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Cập nhật trạng thái lần cuối'
    )
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


# 7. OrderItem model
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price_at_purchase = models.DecimalField(
        max_digits=MAX_DIGITS,
        decimal_places=DECIMAL_PLACES,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Giá tại thời điểm mua'
    )
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        
    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity
    
    @property
    def can_review(self):
        if self.order.status !=  ORDER_STATUS_COMPLETED:
            return False
        return timezone.now() - self.order.updated_at <= timedelta(days=7)   
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

