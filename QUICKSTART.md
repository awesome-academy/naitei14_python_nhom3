# 🚀 Quick Start - Chạy nhanh project

## Cài đặt và chạy trong 5 phút

### 1️⃣ Clone project
```bash
git clone https://github.com/ttdN120734/naitei14_python_nhom3.git
cd naitei14_python_nhom3
```

### 2️⃣ Tạo virtual environment
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

### 3️⃣ Cài đặt packages
```bash
pip install -r requirements.txt
```

### 4️⃣ Setup environment
```bash
copy .env.example .env
```
*(Mac/Linux: `cp .env.example .env`)*

### 5️⃣ Chạy migrations
```bash
python manage.py migrate
```

### 6️⃣ Tạo superuser
```bash
python manage.py createsuperuser
```

### 7️⃣ Chạy server
```bash
python manage.py runserver
```

### 8️⃣ Truy cập
- **Trang chủ:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/

---

## ✅ Done!

Bây giờ bạn có thể:
1. Tạo nhánh mới: `git checkout -b feature/your-feature`
2. Bắt đầu code
3. Xem [GIT_WORKFLOW.md](GIT_WORKFLOW.md) để biết quy trình làm việc

---

## 📖 Tài liệu đầy đủ

- [SETUP.md](SETUP.md) - Hướng dẫn chi tiết
- [GIT_WORKFLOW.md](GIT_WORKFLOW.md) - Quy trình Git
