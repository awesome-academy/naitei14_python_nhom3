from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.core.cache import cache
from django.utils import timezone
from django.db import transaction
from django.views.decorators.http import require_POST
from datetime import timedelta
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import PasswordChangeView

from myapp.forms import UserUpdateForm, VNPasswordChangeForm
from myapp.models import Product
from .constants import ACTIVATION_TOKEN_LENGTH, RESET_TOKEN_LENGTH, RESET_TOKEN_EXPIRY_HOURS, ACTIVATION_TOKEN_EXPIRY_HOURS

User = get_user_model()

# Create your views here.

def index(request):
    """
    View hiển thị trang index của myapp
    """
    featured_products = Product.objects.filter(is_featured=True).order_by('-id')[:8]
    
    context = {
        'featured_products': featured_products
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
            messages.error(request, _('Quá nhiều lần đăng ký. Vui lòng thử lại sau 1 giờ.'))
            return render(request, 'myapp/register.html')
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()

        # Validate
        if password != password_confirm:
            messages.error(request, _('Mật khẩu xác nhận không khớp'))
            return render(request, 'myapp/register.html')

        # Validate email format
        email_validator = EmailValidator()
        try:
            email_validator(email)
        except ValidationError:
            messages.error(request, _('Định dạng email không hợp lệ'))
            return render(request, 'myapp/register.html')

        # Validate password strength
        try:
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'myapp/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, _('Username đã tồn tại'))
            return render(request, 'myapp/register.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, _('Email đã được sử dụng'))
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
                    subject=_('Kích hoạt tài khoản'),
                    message=_('Chào %(username)s,\n\nVui lòng click vào link sau để kích hoạt tài khoản:\n%(activation_link)s') % {
                        'username': username,
                        'activation_link': activation_link,
                    },
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
            
            messages.success(request, _('Đăng ký thành công! Vui lòng kiểm tra email để kích hoạt tài khoản.'))
            return redirect('myapp:login')
        except Exception as e:
            # Transaction will auto-rollback if email fails
            # Increment rate limit counter
            cache.set(cache_key, attempts + 1, 3600)  # 1 hour TTL
            messages.error(request, _('Gửi email thất bại. Vui lòng thử lại sau.'))
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
            messages.error(request, _('Quá nhiều lần đăng nhập thất bại. Vui lòng thử lại sau 15 phút.'))
            return render(request, 'myapp/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                # Clear login attempts on successful login
                cache.delete(cache_key)
                login(request, user)
                messages.success(request, _('Chào mừng %(username)s!') % {'username': user.username})
                next_url = request.GET.get('next', 'myapp:index')
                return redirect(next_url)
            else:
                messages.error(request, _('Tài khoản chưa được kích hoạt'))
        else:
            # Increment failed login attempts
            cache.set(cache_key, attempts + 1, 900)  # 15 minutes TTL
            messages.error(request, _('Username hoặc mật khẩu không đúng'))

    return render(request, 'myapp/login.html')


@require_POST
def logout_user(request):
    """
    Đăng xuất
    """
    logout(request)
    messages.success(request, _('Đã đăng xuất thành công'))
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

        messages.success(request, _('Cập nhật thông tin thành công'))
        return redirect('myapp:profile')

    return redirect('myapp:profile')

@login_required(login_url="myapp:login")
def profile(request):
    user = request.user

    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Cập nhật hồ sơ thành công!"))
            return redirect("myapp:profile")
    else:
        form = UserUpdateForm(instance=user)

    return render(request, "myapp/profile.html", {"form": form})


class CustomPasswordChangeView(PasswordChangeView):
    form_class = VNPasswordChangeForm
    template_name = "myapp/password_change.html"
    success_url = reverse_lazy("myapp:profile")

    def form_valid(self, form):
            messages.success(self.request, _("Bạn đã đổi mật khẩu thành công!"))
            return super().form_valid(form)

    def form_invalid(self, form):
        old_errors = form.errors.get("old_password", [])
        if old_errors:
            for err in old_errors:
                    messages.error(self.request, _("Mật khẩu hiện tại: %(error)s") % {"error": err})
            return super().form_invalid(form)

        new1_errors = form.errors.get("new_password1", [])
        for err in new1_errors:
                messages.error(self.request, _("Mật khẩu mới: %(error)s") % {"error": err})

        new2_errors = form.errors.get("new_password2", [])
        for err in new2_errors:
            if "match" in err.lower():
                    messages.error(self.request, _("Xác nhận mật khẩu: Hai mật khẩu không trùng khớp."))

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
                    messages.error(request, _('Link kích hoạt đã hết hạn. Vui lòng đăng ký lại.'))
            return redirect('myapp:register')
        
        user.is_active = True
        user.activation_token = ''  # Xóa token sau khi kích hoạt
        user.activation_token_created_at = None
        user.save()
        messages.success(request, _('Kích hoạt tài khoản thành công! Vui lòng đăng nhập.'))
        return redirect('myapp:login')
    except User.DoesNotExist:
            messages.error(request, _('Link kích hoạt không hợp lệ hoặc đã hết hạn.'))
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
                messages.error(request, _('Bạn đã yêu cầu quá nhiều lần. Vui lòng thử lại sau 1 giờ.'))
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
                        message=_('Chào %(username)s,\n\nClick vào link sau để đặt lại mật khẩu:\n%(reset_link)s\n\nLink này chỉ sử dụng được 1 lần.') % {
                            'username': user.username,
                            'reset_link': reset_link,
                        },
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                # Increment rate limit counter
                cache.set(cache_key, request_count + 1, 3600)  # 1 hour TTL
                
                messages.success(request, _('Đã gửi link đặt lại mật khẩu vào email của bạn.'))
            except Exception as e:
                    messages.error(request, _('Có lỗi khi gửi email. Vui lòng thử lại sau.'))
            
            return redirect('myapp:login')
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security)
            # Still increment counter to prevent enumeration attacks
            cache.set(cache_key, request_count + 1, 3600)
            messages.success(request, _('Nếu email tồn tại trong hệ thống, bạn sẽ nhận được link đặt lại mật khẩu.'))
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
            messages.error(request, _('Link đặt lại mật khẩu đã được sử dụng.'))
            return redirect('myapp:forgot_password')
        
        # Validate token expiration
        if user.reset_token_created_at:
            expiry_time = user.reset_token_created_at + timedelta(hours=RESET_TOKEN_EXPIRY_HOURS)
            if timezone.now() > expiry_time:
                messages.error(request, _('Link đặt lại mật khẩu đã hết hạn. Vui lòng yêu cầu link mới.'))
                return redirect('myapp:forgot_password')
        
    except User.DoesNotExist:
        messages.error(request, _('Link đặt lại mật khẩu không hợp lệ.'))
        return redirect('myapp:forgot_password')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, _('Mật khẩu xác nhận không khớp'))
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
        
        messages.success(request, _('Đặt lại mật khẩu thành công! Vui lòng đăng nhập.'))
        return redirect('myapp:login')
    
    return render(request, 'myapp/reset_password.html', {'token': token})
