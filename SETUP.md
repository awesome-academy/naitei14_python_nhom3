# Django Project Setup Guide

## 📋 Yêu cầu hệ thống
- Python 3.8 trở lên
- pip (Python package manager)

## 🚀 Hướng dẫn cài đặt

### 1. Tạo môi trường ảo (Virtual Environment)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Tạo file .env
```bash
copy .env.example .env
```
Sau đó chỉnh sửa file `.env` với thông tin cấu hình của bạn.

### 4. Chạy migrations
```bash
python manage.py migrate
```

### 5. Tạo superuser (admin)
```bash
python manage.py createsuperuser
```

### 6. Chạy development server
```bash
python manage.py runserver
```

Truy cập: http://127.0.0.1:8000/

## 📁 Cấu trúc thư mục

```
naitei14_python_nhom3/
│
├── config/                 # Django configuration
│   ├── __init__.py
│   ├── settings.py        # Settings chính
│   ├── urls.py            # URL routing chính
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                  # Django applications
│   └── __init__.py
│   # Tạo app mới: python manage.py startapp app_name
│
├── templates/             # HTML templates
│   ├── base.html         # Template gốc
│   └── index.html        # Trang chủ
│
├── static/               # Static files (CSS, JS, Images)
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│
├── media/                # User uploaded files
│
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## 🔧 Các lệnh Django thường dùng

### Tạo app mới
```bash
python manage.py startapp app_name
```
Sau đó thêm app vào `INSTALLED_APPS` trong `config/settings.py`

### Tạo migrations
```bash
python manage.py makemigrations
```

### Chạy migrations
```bash
python manage.py migrate
```

### Tạo superuser
```bash
python manage.py createsuperuser
```

### Chạy server
```bash
python manage.py runserver
```

### Chạy shell
```bash
python manage.py shell
```

### Thu thập static files
```bash
python manage.py collectstatic
```

## 📝 Quy trình phát triển

1. **Tạo nhánh mới** cho tính năng/bugfix
   ```bash
   git checkout -b feature/ten-tinh-nang
   ```

2. **Phát triển tính năng**
   - Tạo models trong `apps/your_app/models.py`
   - Tạo views trong `apps/your_app/views.py`
   - Tạo templates trong `templates/your_app/`
   - Tạo URLs trong `apps/your_app/urls.py`

3. **Test code** của bạn

4. **Commit & Push** (xem `GIT_WORKFLOW.md`)

5. **Tạo Pull Request** sang repo gốc

## 🗂️ Tạo App mới

```bash
# Tạo app trong thư mục apps
python manage.py startapp your_app apps/your_app

# Cấu trúc app:
apps/your_app/
├── __init__.py
├── admin.py          # Đăng ký models với admin
├── apps.py
├── models.py         # Database models
├── views.py          # Views/Controllers
├── urls.py           # URL routing (tạo mới)
├── forms.py          # Forms (tạo mới nếu cần)
├── tests.py          # Unit tests
└── migrations/
    └── __init__.py
```

Sau đó:
1. Thêm `'apps.your_app'` vào `INSTALLED_APPS` trong `config/settings.py`
2. Include URLs trong `config/urls.py`:
   ```python
   path('your-app/', include('apps.your_app.urls')),
   ```

## 🌐 Môi trường Production

Khi deploy lên production:

1. **Đổi DEBUG = False** trong `.env`
2. **Đặt SECRET_KEY mới** (bảo mật)
3. **Cấu hình ALLOWED_HOSTS** đúng
4. **Sử dụng database thực** (PostgreSQL, MySQL)
5. **Thu thập static files**: `python manage.py collectstatic`
6. **Sử dụng WSGI server** như Gunicorn

## 📖 Tài liệu tham khảo

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Tutorial](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
- [Git Workflow](GIT_WORKFLOW.md)

## 👥 Team Members

_(Thêm danh sách thành viên ở đây)_

## 📄 License

_(Thêm thông tin license nếu cần)_
