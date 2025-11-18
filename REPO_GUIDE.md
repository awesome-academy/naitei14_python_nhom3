# Hướng dẫn sử dụng repository

## 1. Clone repository về máy

```bash
git clone git@github.com:ttdN120734/naitei14_python_nhom3.git
cd naitei14_python_nhom3
```

## 2. Cài đặt môi trường Python (khuyến nghị dùng venv)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

## 3. Cài đặt các package cần thiết

```bash
pip install -r requirements.txt  # Nếu có file này
pip install django  # Nếu chưa có requirements.txt
```

## 4. Cấu hình remote để sync với repo gốc (upstream)

```bash
git remote add upstream git@github.com:awesome-academy/naitei14_python_nhom3.git
git remote -v
```

## 5. Cập nhật code mới nhất từ repo gốc

```bash
git fetch upstream
git merge upstream/master  # hoặc main nếu repo gốc dùng main
```

## 6. Tạo branch mới để phát triển tính năng

```bash
git checkout -b ten-branch-moi
```

## 7. Commit và push code lên repo fork của bạn

```bash
git add .
git commit -m "Mô tả thay đổi"
git push origin ten-branch-moi
```

## 8. Tạo Pull Request (PR)
- Lên GitHub, vào repo fork của bạn
- Chọn branch vừa push
- Nhấn "Compare & pull request"
- Chọn base là repo gốc (awesome-academy/naitei14_python_nhom3), branch là branch bạn muốn merge vào (thường là `master` hoặc `main`)
- Viết mô tả, gửi PR

## 9. Một số lệnh git hữu ích

- Kiểm tra remote:
  ```bash
  git remote -v
  ```
- Đổi remote origin sang SSH:
  ```bash
  git remote set-url origin git@github.com:ttdN120734/naitei14_python_nhom3.git
  ```
- Kiểm tra user/email commit:
  ```bash
  git config user.name
  git config user.email
  ```
- Kiểm tra SSH key đang dùng:
  ```bash
  ssh -T git@github.com
  ```

---

**Nếu gặp vấn đề về quyền push/pull, hãy kiểm tra lại SSH key và quyền truy cập repo.**

**Mọi thắc mắc vui lòng liên hệ mentor hoặc maintainer của dự án!**
