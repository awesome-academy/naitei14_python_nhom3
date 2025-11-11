# 📋 Git Workflow - Hướng dẫn làm việc với Git

## 🎯 Mục đích
Tài liệu này hướng dẫn quy trình làm việc với Git cho các thành viên trong team, đảm bảo code luôn được đồng bộ và lịch sử commit sạch sẽ.

**Lưu ý quan trọng:** Repository đã được fork sẵn và tất cả thành viên đã được thêm vào với quyền truy cập. Bạn sẽ làm việc trên repo fork này và tạo Pull Request sang repo gốc.

---

## 1️⃣ Thiết lập ban đầu (Clone Repository)

### Bước 1.1: Clone Repository về máy
**Repository fork của team:** `https://github.com/ttdN120734/naitei14_python_nhom3`

```bash
git clone https://github.com/ttdN120734/naitei14_python_nhom3.git
cd naitei14_python_nhom3
```

### Bước 1.2: Thêm Remote "sun" (Repository gốc)
```bash
git remote add sun https://github.com/awesome-academy/naitei14_python_nhom3.git
```

### Bước 1.3: Kiểm tra Remote
```bash
git remote -v
```
Kết quả sẽ hiển thị:
```
origin  https://github.com/ttdN120734/naitei14_python_nhom3.git (fetch)
origin  https://github.com/ttdN120734/naitei14_python_nhom3.git (push)
sun     https://github.com/awesome-academy/naitei14_python_nhom3.git (fetch)
sun     https://github.com/awesome-academy/naitei14_python_nhom3.git (push)
```

**Giải thích:**
- `origin`: Repository fork của team (nơi bạn push code)
- `sun`: Repository gốc của dự án (nơi bạn pull code mới nhất và tạo PR đến đây)

---

## 2️⃣ Quy trình làm việc hàng ngày

### Bước 2.1: Tạo nhánh mới cho tính năng/task
```bash
# Đảm bảo bạn đang ở nhánh master
git checkout master

# Tạo nhánh mới và chuyển sang nhánh đó
git checkout -b <ten_nhanh>
```

**Quy tắc đặt tên nhánh:**
- Feature: `feature/ten-tinh-nang` (ví dụ: `feature/login`, `feature/user-profile`)
- Bugfix: `bugfix/ten-loi` (ví dụ: `bugfix/fix-login-error`)
- Hotfix: `hotfix/ten-loi-gap` (ví dụ: `hotfix/security-patch`)

### Bước 2.2: Làm việc và Commit
```bash
# Sau khi code xong một phần
git add .

# Hoặc thêm từng file cụ thể
git add <ten_file>

# Commit với message rõ ràng
git commit -m "Message mô tả thay đổi"
```

**Quy tắc viết Commit Message:**
- Sử dụng tiếng Anh
- Bắt đầu bằng động từ: `Add`, `Update`, `Fix`, `Remove`, `Refactor`
- Ngắn gọn, rõ ràng (< 50 ký tự cho dòng đầu)
- Ví dụ:
  - ✅ `Add user login functionality`
  - ✅ `Fix validation error in signup form`
  - ❌ `update` (quá chung chung)

---

## 3️⃣ Đồng bộ hóa với Repository gốc (Rebase)

**⚠️ QUAN TRỌNG:** Trước khi push code, luôn đồng bộ với repository gốc (`sun`) để tránh conflict!

### Bước 3.1: Chuyển về nhánh master
```bash
git checkout master
```

### Bước 3.2: Pull code mới nhất từ repository gốc
```bash
git pull sun master
```
*Lưu ý: Pull từ `sun` (repo gốc), không phải `origin`*

### Bước 3.3: Cập nhật master lên origin (repository fork)
```bash
git push origin master
```
*Bước này đảm bảo repo fork của team cũng được cập nhật*

### Bước 3.4: Quay lại nhánh làm việc
```bash
git checkout <ten_nhanh>
```

### Bước 3.5: Rebase nhánh của bạn với master
```bash
git rebase master
```

**Giải thích:** Lệnh rebase sẽ lấy tất cả các commit của bạn và đặt chúng lên trên cùng của nhánh master mới nhất (đã được cập nhật từ `sun`). Điều này giúp lịch sử commit luôn thẳng hàng và dễ theo dõi.

---

## 4️⃣ Xử lý Conflict (Xung đột)

Nếu có conflict khi rebase, Git sẽ báo lỗi. Làm theo các bước sau:

### Bước 4.1: Xem các file bị conflict
```bash
git status
```

### Bước 4.2: Mở file và sửa conflict
Tìm các dấu hiệu:
```
<<<<<<< HEAD
Code hiện tại trên master
=======
Code của bạn
>>>>>>> your-branch
```

**Cách sửa:**
- Xóa các dấu `<<<<<<<`, `=======`, `>>>>>>>`
- Giữ lại code đúng (hoặc kết hợp cả hai)
- Lưu file

### Bước 4.3: Add file đã sửa
```bash
git add <file_da_sua>
```

### Bước 4.4: Tiếp tục rebase
```bash
git rebase --continue
```

### Bước 4.5: Nếu muốn hủy rebase
```bash
git rebase --abort
```

**Lưu ý:** Lặp lại bước 4.1 → 4.4 cho đến khi rebase hoàn tất.

---

## 5️⃣ Push code lên GitHub

### Bước 5.1: Push lần đầu lên repository fork
```bash
git push origin <ten_nhanh>
```
*Push lên `origin` (repo fork của team), không phải `sun`*

### Bước 5.2: Push sau khi rebase (Force Push)
⚠️ **CHÚ Ý:** Chỉ force push lên nhánh của bạn, KHÔNG BAO GIỜ force push lên master!

```bash
git push -f origin <ten_nhanh>
```

---

## 6️⃣ Tạo Pull Request (PR)

### Bước 6.1: Lên GitHub và tạo PR
1. Truy cập **repository gốc**: `https://github.com/awesome-academy/naitei14_python_nhom3`
2. Nhấn nút **"New pull request"**
3. Nhấn **"compare across forks"**
4. Chọn:
   - **Base repository:** `awesome-academy/naitei14_python_nhom3` **base:** `master` (repo gốc)
   - **Head repository:** `ttdN120734/naitei14_python_nhom3` **compare:** `<ten_nhanh>` (repo fork của bạn)
5. Nhấn **"Create pull request"**

### Bước 6.2: Điền thông tin PR
- **Title:** Mô tả ngắn gọn (ví dụ: `Add user authentication`)
- **Description:** 
  - Mô tả chi tiết những gì đã làm
  - Link đến issue (nếu có)
  - Screenshot (nếu có thay đổi giao diện)
  - Checklist các công việc đã hoàn thành

### Bước 6.3: Chọn Reviewers
- Chọn những người cần review code của bạn
- Gán Labels nếu cần (bug, enhancement, documentation...)

### Bước 6.4: Tạo PR
- Nhấn **"Create pull request"**
- Chờ review và phản hồi

### Bước 6.5: Xử lý Review Comments
Nếu reviewer yêu cầu sửa:
```bash
# Sửa code theo yêu cầu
git add .
git commit -m "Address review comments"
git push origin <ten_nhanh>
```
PR sẽ tự động cập nhật!

---

## 7️⃣ Sau khi PR được Merge

### Bước 7.1: Cập nhật nhánh master local từ repository gốc
```bash
git checkout master
git pull sun master
```

### Bước 7.2: Cập nhật master lên repository fork
```bash
git push origin master
```

### Bước 7.3: Xóa nhánh đã merge (tùy chọn)
```bash
# Xóa nhánh local
git branch -d <ten_nhanh>

# Xóa nhánh trên repository fork
git push origin --delete <ten_nhanh>
```

**Lưu ý:** Việc xóa nhánh sau khi merge giúp repository luôn gọn gàng và dễ quản lý.

---

## 📚 Các lệnh Git thường dùng

### Kiểm tra trạng thái
```bash
git status                    # Xem trạng thái hiện tại
git log                       # Xem lịch sử commit
git log --oneline             # Xem lịch sử commit dạng ngắn gọn
git branch                    # Xem danh sách nhánh
git branch -a                 # Xem tất cả nhánh (kể cả remote)
```

### Hoàn tác thay đổi
```bash
git checkout -- <file>        # Hủy thay đổi file chưa add
git reset HEAD <file>         # Bỏ file ra khỏi staging area
git reset --soft HEAD~1       # Hủy commit cuối, giữ lại thay đổi
git reset --hard HEAD~1       # Hủy commit cuối và xóa thay đổi
```

### Stash (Tạm cất thay đổi)
```bash
git stash                     # Cất thay đổi tạm thời
git stash list                # Xem danh sách stash
git stash pop                 # Lấy lại thay đổi gần nhất
git stash drop                # Xóa stash gần nhất
```

---

## ⚠️ Những điều KHÔNG NÊN làm

1. ❌ **KHÔNG** commit trực tiếp lên nhánh `master`
2. ❌ **KHÔNG** force push lên nhánh `master`
3. ❌ **KHÔNG** commit file không cần thiết:
   - File cấu hình cá nhân (`.idea/`, `.vscode/`)
   - File môi trường (`.env`)
   - File build (`dist/`, `build/`, `__pycache__/`)
   - Dependencies (`node_modules/`, `venv/`)
4. ❌ **KHÔNG** commit code chưa test
5. ❌ **KHÔNG** tạo PR quá lớn (nên chia nhỏ task)

---

## ✅ Best Practices

1. ✅ Thường xuyên pull code từ `sun master` để cập nhật với repo gốc
2. ✅ Commit nhỏ, thường xuyên với message rõ ràng
3. ✅ Test kỹ trước khi tạo PR
4. ✅ Review code của người khác
5. ✅ Sử dụng `.gitignore` đúng cách
6. ✅ Rebase thay vì merge để giữ lịch sử sạch
7. ✅ Đặt tên nhánh theo quy tắc
8. ✅ Luôn tạo PR từ repo fork → repo gốc (`sun`)

---

## 🆘 Trợ giúp

### Khi gặp vấn đề:
1. Đọc kỹ error message
2. Google error message
3. Hỏi team members
4. Tham khảo: [Git Documentation](https://git-scm.com/doc)

### Liên hệ:
- Team Leader: [Tên người lead]
- GitHub Issues: [Link đến issues của repo]

---

## 📖 Tài liệu tham khảo
- [Git Official Documentation](https://git-scm.com/doc)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [How to Write Good Commit Messages](https://chris.beams.io/posts/git-commit/)

---

**Cập nhật lần cuối:** 11/11/2025

**Version:** 1.0.0
