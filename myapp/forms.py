from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "full_name", "phone_number", "address"]

        labels = {
            "username": "Tên đăng nhập",
            "email": "Email",
            "full_name": "Họ và tên",
            "phone_number": "Số điện thoại",
            "address": "Địa chỉ",
        }

        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
        }


class VNPasswordChangeForm(PasswordChangeForm):
    error_messages = {
        "password_incorrect": "Mật khẩu hiện tại không chính xác.",
        "password_mismatch": "Hai mật khẩu bạn nhập không trùng khớp.",
    }

    old_password = forms.CharField(
        label="Mật khẩu hiện tại",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Nhập mật khẩu hiện tại"
        })
    )
    new_password1 = forms.CharField(
        label="Mật khẩu mới",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Nhập mật khẩu mới"
        })
    )
    new_password2 = forms.CharField(
        label="Nhập lại mật khẩu mới",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Nhập lại mật khẩu mới"
        })
    )

    # Việt hóa lỗi validator mật khẩu
    def clean_new_password1(self):
        password1 = self.cleaned_data.get("new_password1")
        try:
            validate_password(password1, self.user)
        except ValidationError as e:
            raise ValidationError(  
                [self._translate_password_error(msg) for msg in e.messages]
            )
        return password1

    def _translate_password_error(self, msg):
        translations = {
            "This password is too short. It must contain at least 8 characters.":
                "Mật khẩu quá ngắn, phải có ít nhất 8 ký tự.",
            "This password is too common.":
                "Mật khẩu quá phổ biến, vui lòng chọn mật khẩu mạnh hơn.",
            "This password is entirely numeric.":
                "Mật khẩu không được chỉ chứa số.",
            "The password is too similar to the username.":
                "Mật khẩu quá giống tên đăng nhập.",
            "The password is too similar to the email address.":
                "Mật khẩu quá giống email.",
        }

        return translations.get(msg, msg)

