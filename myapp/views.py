from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.urls import reverse, reverse_lazy
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.core.cache import cache
from django.utils import timezone
from django.db import transaction
from django.views.decorators.http import require_POST
from django.contrib.auth.views import PasswordChangeView
from datetime import timedelta

from .constants import ACTIVATION_TOKEN_LENGTH, RESET_TOKEN_LENGTH, RESET_TOKEN_EXPIRY_HOURS, ACTIVATION_TOKEN_EXPIRY_HOURS
from .models import Category, Product, Order

User = get_user_model()
from .forms import UserUpdateForm, VNPasswordChangeForm

# Create your views here.

def index(request):
    """
    View hiển thị trang index của myapp
    """
    context = {
        'user_name': 'Django Developer',  # Dữ liệu truyền vào template
    }
    return render(request, 'myapp/index.html', context)


def detail(request):
    """
    View hiển thị trang detail của myapp
    """
    return render(request, 'myapp/detail.html')


def register_user(request):
    """
    Đăng ký tài khoản mới
    """
    if request.user.is_authenticated:
        return redirect('myapp:index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        
        # Rate limiting: max 3 registration attempts per IP per hour
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        cache_key = f'register_attempts_{ip_address}'
        attempts = cache.get(cache_key, 0)
        
        if attempts >= 3:
            messages.error(request, 'Quá nhiều lần đăng ký. Vui lòng thử lại sau 1 giờ.')
            return render(request, 'myapp/register.html')
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()

        # Validate
        if password != password_confirm:
            messages.error(request, 'Mật khẩu xác nhận không khớp')
            return render(request, 'myapp/register.html')

        # Validate email format
        email_validator = EmailValidator()
        try:
            email_validator(email)
        except ValidationError:
            messages.error(request, 'Định dạng email không hợp lệ')
            return render(request, 'myapp/register.html')

        # Validate password strength
        try:
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'myapp/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username đã tồn tại')
            return render(request, 'myapp/register.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email đã được sử dụng')
            return render(request, 'myapp/register.html')

        # Use transaction to ensure user creation and email sending are atomic
        try:
            with transaction.atomic():
                # Tạo user mới (chưa kích hoạt)
                activation_token = get_random_string(length=ACTIVATION_TOKEN_LENGTH)
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    full_name=full_name,
                    phone_number=phone_number,
                    address=address,
                    is_active=False,  # Chưa kích hoạt
                    activation_token=activation_token,
                    activation_token_created_at=timezone.now()
                )

                # Gửi email kích hoạt
                activation_link = request.build_absolute_uri(
                    reverse('myapp:activate_account', args=[activation_token])
                )
                send_mail(
                    subject='Kích hoạt tài khoản',
                    message=f'Chào {username},\n\nVui lòng click vào link sau để kích hoạt tài khoản:\n{activation_link}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
            
            messages.success(request, 'Đăng ký thành công! Vui lòng kiểm tra email để kích hoạt tài khoản.')
            return redirect('myapp:login')
        except Exception as e:
            # Transaction will auto-rollback if email fails
            # Increment rate limit counter
            cache.set(cache_key, attempts + 1, 3600)  # 1 hour TTL
            messages.error(request, 'Gửi email thất bại. Vui lòng thử lại sau.')
            return render(request, 'myapp/register.html')

    return render(request, 'myapp/register.html')


def login_user(request):
    """
    Đăng nhập
    """
    if request.user.is_authenticated:
        return redirect('myapp:index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Rate limiting: max 5 login attempts per username per 15 minutes
        cache_key = f'login_attempts_{username}'
        attempts = cache.get(cache_key, 0)
        
        if attempts >= 5:
            messages.error(request, 'Quá nhiều lần đăng nhập thất bại. Vui lòng thử lại sau 15 phút.')
            return render(request, 'myapp/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                # Clear login attempts on successful login
                cache.delete(cache_key)
                login(request, user)
                messages.success(request, f'Chào mừng {user.username}!')
                next_url = request.GET.get('next', 'myapp:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Tài khoản chưa được kích hoạt hoặc đã bị khóa. Vui lòng kiểm tra email để kích hoạt tài khoản.')
        else:
            # Increment failed login attempts
            cache.set(cache_key, attempts + 1, 900)  # 15 minutes TTL
            messages.error(request, 'Username hoặc mật khẩu không đúng')

    return render(request, 'myapp/login.html')


@require_POST
def logout_user(request):
    """
    Đăng xuất
    """
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công')
    return redirect('myapp:login')



@login_required
def update_profile(request):
    """
    Cập nhật thông tin cá nhân
    """
    if request.method == 'POST':
        user = request.user
        
        # Sanitize and trim input
        full_name = request.POST.get('full_name', user.full_name)
        phone_number = request.POST.get('phone_number', user.phone_number)
        address = request.POST.get('address', user.address)
        
        user.full_name = full_name.strip() if isinstance(full_name, str) else full_name
        user.phone_number = phone_number.strip() if isinstance(phone_number, str) else phone_number
        user.address = address.strip() if isinstance(address, str) else address
        user.save()

        messages.success(request, 'Cập nhật thông tin thành công')
        return redirect('myapp:profile')

    return redirect('myapp:profile')


@login_required(login_url="myapp:login")
def profile(request):
    user = request.user

    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật hồ sơ thành công!")
            return redirect("myapp:profile")
    else:
        form = UserUpdateForm(instance=user)

    return render(request, "myapp/profile.html", {"form": form})


class CustomPasswordChangeView(PasswordChangeView):
    form_class = VNPasswordChangeForm
    template_name = "myapp/password_change.html"
    success_url = reverse_lazy("myapp:profile")

    def form_valid(self, form):
        messages.success(self.request, "Bạn đã đổi mật khẩu thành công!")
        return super().form_valid(form)

    def form_invalid(self, form):
        old_errors = form.errors.get("old_password", [])
        if old_errors:
            for err in old_errors:
                messages.error(self.request, f"Mật khẩu hiện tại: {err}")
            return super().form_invalid(form)

        new1_errors = form.errors.get("new_password1", [])
        for err in new1_errors:
            messages.error(self.request, f"Mật khẩu mới: {err}")

        new2_errors = form.errors.get("new_password2", [])
        for err in new2_errors:
            if "match" in err.lower():
                messages.error(self.request, "Xác nhận mật khẩu: Hai mật khẩu không trùng khớp.")

        for err in form.non_field_errors():
            messages.error(self.request, err)

        return super().form_invalid(form)
    
    
def activate_account(request, token):
    """
    Kích hoạt tài khoản qua email
    """
    try:
        user = User.objects.get(activation_token=token, is_active=False)
        
        # Validate token expiration
        if user.activation_token_created_at:
            expiry_time = user.activation_token_created_at + timedelta(hours=ACTIVATION_TOKEN_EXPIRY_HOURS)
            if timezone.now() > expiry_time:
                messages.error(request, 'Link kích hoạt đã hết hạn. Vui lòng đăng ký lại.')
                return redirect('myapp:register')
        
        user.is_active = True
        user.activation_token = ''  # Xóa token sau khi kích hoạt
        user.activation_token_created_at = None
        user.save()
        messages.success(request, 'Kích hoạt tài khoản thành công! Vui lòng đăng nhập.')
        return redirect('myapp:login')
    except User.DoesNotExist:
        messages.error(request, 'Link kích hoạt không hợp lệ hoặc đã hết hạn.')
        return redirect('myapp:register')


def forgot_password(request):
    """
    Quên mật khẩu - gửi link reset qua email
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        # Rate limiting: max 3 requests per email per hour
        cache_key = f'password_reset_{email}'
        request_count = cache.get(cache_key, 0)
        
        if request_count >= 3:
            messages.error(request, 'Bạn đã yêu cầu quá nhiều lần. Vui lòng thử lại sau 1 giờ.')
            return render(request, 'myapp/forgot_password.html')
        
        try:
            user = User.objects.get(email__iexact=email)
            
            # Tạo reset token
            reset_token = get_random_string(length=RESET_TOKEN_LENGTH)
            user.reset_token = reset_token
            user.reset_token_created_at = timezone.now()
            user.save()
            
            # Gửi email reset
            reset_link = request.build_absolute_uri(
                reverse('myapp:reset_password', args=[reset_token])
            )
            try:
                send_mail(
                    subject='Đặt lại mật khẩu',
                    message=f'Chào {user.username},\n\nClick vào link sau để đặt lại mật khẩu:\n{reset_link}\n\nLink này chỉ sử dụng được 1 lần.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                # Increment rate limit counter
                cache.set(cache_key, request_count + 1, 3600)  # 1 hour TTL
                
                messages.success(request, 'Đã gửi link đặt lại mật khẩu vào email của bạn.')
            except Exception as e:
                messages.error(request, 'Có lỗi khi gửi email. Vui lòng thử lại sau.')
            
            return redirect('myapp:login')
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security)
            # Still increment counter to prevent enumeration attacks
            cache.set(cache_key, request_count + 1, 3600)
            messages.success(request, 'Nếu email tồn tại trong hệ thống, bạn sẽ nhận được link đặt lại mật khẩu.')
            return redirect('myapp:login')
    
    return render(request, 'myapp/forgot_password.html')


def reset_password(request, token):
    """
    Đặt lại mật khẩu với token
    """
    try:
        user = User.objects.get(reset_token=token)
        
        # Check if token is empty (already used)
        if not user.reset_token:
            messages.error(request, 'Link đặt lại mật khẩu đã được sử dụng.')
            return redirect('myapp:forgot_password')
        
        # Validate token expiration
        if user.reset_token_created_at:
            expiry_time = user.reset_token_created_at + timedelta(hours=RESET_TOKEN_EXPIRY_HOURS)
            if timezone.now() > expiry_time:
                messages.error(request, 'Link đặt lại mật khẩu đã hết hạn. Vui lòng yêu cầu link mới.')
                return redirect('myapp:forgot_password')
        
    except User.DoesNotExist:
        messages.error(request, 'Link đặt lại mật khẩu không hợp lệ.')
        return redirect('myapp:forgot_password')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Mật khẩu xác nhận không khớp')
            return render(request, 'myapp/reset_password.html', {'token': token})
        
        # Validate password strength
        try:
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'myapp/reset_password.html', {'token': token})
        
        # Cập nhật mật khẩu mới
        user.set_password(password)
        user.reset_token = ''  # Xóa token sau khi sử dụng
        user.reset_token_created_at = None
        user.save()
        
        messages.success(request, 'Đặt lại mật khẩu thành công! Vui lòng đăng nhập.')
        return redirect('myapp:login')
    
    return render(request, 'myapp/reset_password.html', {'token': token})


# Admin views (chỉ cho admin/staff)
def admin_login_view(request):
    """Trang login riêng cho admin"""
    if request.user.is_authenticated:
        # Nếu đã login và là admin, redirect to dashboard
        if request.user.role == 'admin' or request.user.is_staff:
            return redirect('myapp:admin_dashboard')
        else:
            # Không phải admin, logout và báo lỗi
            logout(request)
            messages.error(request, 'Bạn không có quyền truy cập trang quản trị')
            return redirect('myapp:admin_site')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is admin
            if user.role == 'admin' or user.is_staff:
                login(request, user)
                messages.success(request, f'Chào mừng Admin {user.username}!')
                return redirect('myapp:admin_dashboard')
            else:
                messages.error(request, 'Bạn không có quyền truy cập. Chỉ dành cho quản trị viên.')
        else:
            messages.error(request, 'Username hoặc mật khẩu không đúng')
    
    return render(request, 'myapp/admin_login.html')


def admin_required(view_func):
    """Decorator để check user là admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Vui lòng đăng nhập')
            return redirect('myapp:admin_site')
        if request.user.role != 'admin' and not request.user.is_staff:
            messages.error(request, 'Bạn không có quyền truy cập')
            return redirect('myapp:admin_site')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    """Trang dashboard cho admin"""
    context = {
        'total_orders': Order.objects.count(),
        'total_products': Product.objects.count(),
        'total_users': User.objects.filter(role='user').count(),
        'total_categories': Category.objects.count(),
        'recent_orders': Order.objects.select_related('user').order_by('-order_date')[:10],
        'low_stock_products': Product.objects.filter(stock_quantity__lt=10).select_related('category').order_by('stock_quantity'),
    }
    return render(request, 'myapp/admin_dashboard.html', context)


@admin_required
def admin_orders(request):
    """Quản lý đơn hàng"""
    orders = Order.objects.select_related('user').order_by('-order_date')
    return render(request, 'myapp/admin_orders.html', {'orders': orders})


@admin_required
def admin_order_view(request, order_id):
    """Xem chi tiết đơn hàng"""
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.select_related('product').all()
    return render(request, 'myapp/admin_order_view.html', {
        'order': order,
        'order_items': order_items
    })


@admin_required
@require_POST
def admin_order_update_status(request, order_id):
    """Cập nhật trạng thái đơn hàng"""
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    rejection_reason = request.POST.get('rejection_reason', '').strip()
    
    # Validate status
    valid_statuses = ['pending', 'confirmed', 'shipped', 'completed', 'rejected']
    if new_status not in valid_statuses:
        messages.error(request, 'Trạng thái không hợp lệ')
        return redirect('myapp:admin_order_view', order_id=order_id)
    
    # Nếu từ chối thì phải có lý do
    if new_status == 'rejected' and not rejection_reason:
        messages.error(request, 'Vui lòng nhập lý do từ chối đơn hàng')
        return redirect('myapp:admin_order_view', order_id=order_id)
    
    old_status = order.status
    order.status = new_status
    
    if new_status == 'rejected':
        order.rejection_reason = rejection_reason
    
    order.save()
    
    status_text = dict([
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('shipped', 'Đang giao'),
        ('completed', 'Đã giao thành công'),
        ('rejected', 'Bị từ chối')
    ]).get(new_status, new_status)
    
    messages.success(request, f'Đã cập nhật trạng thái đơn hàng #{order.id} từ "{old_status}" sang "{status_text}"')
    return redirect('myapp:admin_order_view', order_id=order_id)


@admin_required
def admin_products(request):
    """Quản lý sản phẩm"""
    products = Product.objects.select_related('category').all()
    return render(request, 'myapp/admin_products.html', {'products': products})


@admin_required
def admin_product_create(request):
    """Tạo sản phẩm mới"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '').strip()
        stock_quantity = request.POST.get('stock_quantity', '0').strip()
        category_id = request.POST.get('category')
        is_featured = request.POST.get('is_featured') == 'on'
        
        # Validation
        if not name:
            messages.error(request, 'Tên sản phẩm không được để trống')
        elif not price:
            messages.error(request, 'Giá sản phẩm không được để trống')
        elif not category_id:
            messages.error(request, 'Danh mục là bắt buộc')
        else:
            try:
                category = Category.objects.get(id=category_id)
                product = Product.objects.create(
                    name=name,
                    description=description,
                    price=price,
                    stock_quantity=stock_quantity,
                    category=category,
                    is_featured=is_featured
                )
                messages.success(request, f'Đã tạo sản phẩm {product.name}')
                return redirect('myapp:admin_products')
            except Category.DoesNotExist:
                messages.error(request, 'Danh mục không tồn tại')
            except Exception as e:
                messages.error(request, f'Lỗi khi tạo sản phẩm: {str(e)}')
    
    categories = Category.objects.all()
    return render(request, 'myapp/admin_product_create.html', {'categories': categories})


@admin_required
def admin_product_edit(request, product_id):
    """Chỉnh sửa sản phẩm"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '').strip()
        stock_quantity = request.POST.get('stock_quantity', '0').strip()
        category_id = request.POST.get('category')
        is_featured = request.POST.get('is_featured') == 'on'
        
        if not name:
            messages.error(request, 'Tên sản phẩm không được để trống')
        elif not price:
            messages.error(request, 'Giá sản phẩm không được để trống')
        elif not category_id:
            messages.error(request, 'Danh mục là bắt buộc')
        else:
            try:
                category = Category.objects.get(id=category_id)
                product.name = name
                product.description = description
                product.price = price
                product.stock_quantity = stock_quantity
                product.category = category
                product.is_featured = is_featured
                product.save()
                messages.success(request, f'Đã cập nhật sản phẩm {product.name}')
                return redirect('myapp:admin_products')
            except Category.DoesNotExist:
                messages.error(request, 'Danh mục không tồn tại')
            except Exception as e:
                messages.error(request, f'Lỗi khi cập nhật: {str(e)}')
    
    categories = Category.objects.all()
    return render(request, 'myapp/admin_product_edit.html', {
        'product': product,
        'categories': categories
    })


@admin_required
@require_POST
def admin_product_delete(request, product_id):
    """Xóa sản phẩm"""
    product = get_object_or_404(Product, id=product_id)
    name = product.name
    product.delete()
    messages.success(request, f'Đã xóa sản phẩm {name}')
    return redirect('myapp:admin_products')


@admin_required
def admin_users(request):
    """Quản lý người dùng"""
    users = User.objects.exclude(role='admin').order_by('-created_at')
    return render(request, 'myapp/admin_users.html', {'users': users})


@admin_required
def admin_categories(request):
    """Quản lý danh mục"""
    categories = Category.objects.all()
    return render(request, 'myapp/admin_categories.html', {'categories': categories})


@admin_required
def admin_category_create(request):
    """Tạo danh mục mới"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, 'Tên danh mục không được để trống')
        else:
            try:
                category = Category.objects.create(
                    name=name,
                    description=description
                )
                messages.success(request, f'Đã tạo danh mục {category.name}')
                return redirect('myapp:admin_categories')
            except Exception as e:
                messages.error(request, f'Lỗi khi tạo danh mục: {str(e)}')
    
    return render(request, 'myapp/admin_category_create.html')


@admin_required
def admin_category_edit(request, category_id):
    """Chỉnh sửa danh mục"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, 'Tên danh mục không được để trống')
        else:
            try:
                category.name = name
                category.description = description
                category.save()
                messages.success(request, f'Đã cập nhật danh mục {category.name}')
                return redirect('myapp:admin_categories')
            except Exception as e:
                messages.error(request, f'Lỗi khi cập nhật: {str(e)}')
    
    return render(request, 'myapp/admin_category_edit.html', {'category': category})


@admin_required
@require_POST
def admin_category_delete(request, category_id):
    """Xóa danh mục"""
    category = get_object_or_404(Category, id=category_id)
    
    # Kiểm tra xem danh mục có sản phẩm không
    if category.products.count() > 0:
        messages.error(request, f'Không thể xóa danh mục {category.name} vì còn {category.products.count()} sản phẩm')
        return redirect('myapp:admin_categories')
    
    name = category.name
    category.delete()
    messages.success(request, f'Đã xóa danh mục {name}')
    return redirect('myapp:admin_categories')


@admin_required
def admin_user_view(request, user_id):
    """Xem chi tiết người dùng"""
    user = get_object_or_404(User, id=user_id)
    return render(request, 'myapp/admin_user_view.html', {'view_user': user})


@admin_required
def admin_user_edit(request, user_id):
    """Chỉnh sửa thông tin người dùng"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.username = request.POST.get('username', user.username).strip()
        user.email = request.POST.get('email', user.email).strip()
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.role = request.POST.get('role', user.role)
        
        try:
            user.save()
            messages.success(request, f'Đã cập nhật thông tin người dùng {user.username}')
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật: {str(e)}')
        
        return redirect('myapp:admin_users')
    
    return render(request, 'myapp/admin_user_edit.html', {'edit_user': user})


@admin_required
@require_POST
def admin_user_delete(request, user_id):
    """Xóa người dùng"""
    user = get_object_or_404(User, id=user_id)
    
    # Không cho phép xóa admin
    if user.role == 'admin':
        messages.error(request, 'Không thể xóa tài khoản admin!')
        return redirect('myapp:admin_users')
    
    # Không cho phép tự xóa chính mình
    if user.id == request.user.id:
        messages.error(request, 'Không thể xóa chính tài khoản của bạn!')
        return redirect('myapp:admin_users')
    
    username = user.username
    user.delete()
    messages.success(request, f'Đã xóa người dùng {username}')
    return redirect('myapp:admin_users')


@admin_required
@require_POST
def admin_user_toggle_active(request, user_id):
    """Khóa/Mở khóa tài khoản người dùng"""
    user = get_object_or_404(User, id=user_id)
    
    # Không cho phép khóa admin
    if user.role == 'admin':
        messages.error(request, 'Không thể khóa tài khoản admin!')
        return redirect('myapp:admin_users')
    
    # Không cho phép tự khóa chính mình
    if user.id == request.user.id:
        messages.error(request, 'Không thể khóa chính tài khoản của bạn!')
        return redirect('myapp:admin_users')
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'mở khóa' if user.is_active else 'khóa'
    messages.success(request, f'Đã {status} tài khoản {user.username}')
    return redirect('myapp:admin_users')
    return render(request, 'myapp/reset_password.html', {'token': token})
