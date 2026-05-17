# Smart Expense Management System

Hệ thống quản lý chi tiêu cá nhân được xây dựng bằng FastAPI kết hợp frontend HTML/CSS/JavaScript.

Dự án hỗ trợ:
- Quản lý chi tiêu
- Quản lý ngân sách
- Phân loại khoản chi
- Xác thực người dùng bằng JWT
- Dashboard thống kê tài chính
- RESTful API

---

# Chức năng chính

## Người dùng
- Đăng ký tài khoản
- Đăng nhập
- Xác thực JWT Token

## Quản lý chi tiêu
- Thêm khoản chi
- Sửa khoản chi
- Xóa khoản chi
- Xem lịch sử chi tiêu

## Danh mục
- Tạo danh mục chi tiêu
- Quản lý category

## Ngân sách
- Thiết lập ngân sách
- Theo dõi giới hạn chi tiêu

## Dashboard
- Giao diện quản lý tài chính
- Theo dõi tổng quan chi tiêu

---

# Công nghệ sử dụng

## Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JWT Authentication

## Frontend
- HTML
- CSS
- JavaScript

## Database
- SQLite
- Có thể nâng cấp PostgreSQL/MySQL

---

# Cấu trúc thư mục

```bash
smart_expense_api/
│
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   └── api.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── crud/
│   ├── models/
│   ├── schemas/
│   └── database.py
│
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── script.js
│   ├── dashboard.js
│   └── style.css
│
├── requirements.txt
├── main.py
└── init_data.py
```

# Cấu hình môi trường

Tạo file `.env`

```env
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./expense.db
```

---

# Tài liệu API

FastAPI tự động sinh tài liệu API.

# Hướng phát triển tiếp theo
- AI Financial Assistant
- Phân tích tài chính bằng AI
- OCR quét hóa đơn
- Dashboard biểu đồ nâng cao
- React Frontend
- Docker Deployment
- PostgreSQL Production
- CI/CD Pipeline
- Role-based Authentication
- AI Agent tích hợp quản lý tài chính
---
