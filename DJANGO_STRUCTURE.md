# Cấu Trúc Thư Mục Django "Cổ Điển" (Templates)

## 📁 Cấu trúc thư mục hiện tại:

```
naitei14_python_nhom3/          ← Thư mục gốc (root)
│
├── manage.py                   ← Công cụ dòng lệnh quản lý dự án
│
├── ecommerce/                  ← Thư mục cấu hình project
│   ├── __init__.py
│   ├── settings.py             ← File cài đặt quan trọng nhất
│   ├── urls.py                 ← File điều hướng URL cấp cao nhất
│   ├── wsgi.py                 ← Dùng cho máy chủ WSGI (production)
│   └── asgi.py                 ← Dùng cho máy chủ ASGI (production)
│
├── myapp/                      ← Ứng dụng cụ thể
│   ├── __init__.py
│   ├── admin.py                ← Đăng ký models với Admin
│   ├── apps.py                 ← Cấu hình của app
│   ├── models.py               ← Định nghĩa cấu trúc database
│   ├── tests.py                ← Viết unit test
│   ├── views.py                ← Logic xử lý request/response
│   ├── urls.py                 ← Điều hướng URL của app
│   └── migrations/             ← Lịch sử thay đổi database
│
├── templates/                  ← ⭐️ THƯ MỤC TEMPLATES (CHUNG)
│   ├── base.html               ← Template cơ sở (layout chung)
│   └── myapp/                  ← Thư mục con trùng tên app (namespacing)
│       ├── index.html          ← Trang chủ của myapp
│       └── detail.html         ← Trang chi tiết
│
└── static/                     ← ⭐️ THƯ MỤC STATIC FILES (CHUNG)
    ├── css/
    │   └── style.css           ← File CSS
    ├── js/
    │   └── main.js             ← File JavaScript
    └── images/                 ← Thư mục chứa hình ảnh
```

## ⚙️ Cấu hình đã thực hiện trong `settings.py`:

1. **INSTALLED_APPS**: Đã thêm `'myapp'`
2. **TEMPLATES**: Đã cấu hình `'DIRS': [BASE_DIR / 'templates']`
3. **STATICFILES_DIRS**: Đã cấu hình `[BASE_DIR / 'static']`

## 🚀 Cách chạy dự án:

```bash
# 1. Chạy migration (tạo database)
python manage.py migrate

# 2. Tạo superuser (admin) - Tùy chọn
python manage.py createsuperuser

# 3. Chạy server
python manage.py runserver
```

## 🌐 Truy cập:

- Trang chủ: http://127.0.0.1:8000/
- Trang detail: http://127.0.0.1:8000/detail/
- Admin: http://127.0.0.1:8000/admin/

## 📝 Giải thích cách hoạt động:

1. **Request** đến URL `/` hoặc `/detail/`
2. Django kiểm tra `ecommerce/urls.py` → tìm thấy `include('myapp.urls')`
3. Django chuyển sang `myapp/urls.py` → tìm view tương ứng
4. View trong `myapp/views.py` xử lý logic và render template
5. Template từ `templates/myapp/*.html` được hiển thị
6. CSS/JS từ `static/` được load vào template

## 💡 Lưu ý quan trọng:

- **Namespacing templates**: Luôn tạo thư mục con `templates/myapp/` thay vì đặt trực tiếp `templates/index.html` để tránh xung đột tên file giữa các app.
- **Static files**: Trong template, sử dụng `{% load static %}` và `{% static 'css/style.css' %}`
- **Inheritance**: Sử dụng `{% extends "base.html" %}` để kế thừa layout chung.

## 📚 Tiếp theo bạn có thể:

- Tạo thêm app mới: `python manage.py startapp <tên_app>`
- Tạo models trong `myapp/models.py`
- Đăng ký models với admin trong `myapp/admin.py`
- Tạo thêm views và templates
