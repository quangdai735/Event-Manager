# EventManager7

## 📌 Giới thiệu

**EventManager7** là ứng dụng quản lý sự kiện được xây dựng bằng **Python** và giao diện **Tkinter**.

Hệ thống hỗ trợ các nhóm người dùng chính:

* **Admin**: quản lý người dùng, sự kiện, vé và theo dõi thống kê.
* **Organizer**: tạo và quản lý sự kiện, theo dõi người tham dự và báo cáo.
* **User**: xem sự kiện, quản lý thông tin cá nhân và vé đã đăng ký.

Dữ liệu của hệ thống được lưu trữ trên **MongoDB Atlas**.

---

## 🛠️ Công nghệ sử dụng

* **Python**
* **Tkinter** – xây dựng giao diện người dùng
* **MongoDB Atlas** – lưu trữ dữ liệu
* **PyMongo** – kết nối Python với MongoDB
* **bcrypt** – mã hóa mật khẩu
* **python-dotenv** – quản lý biến môi trường
* **Pillow** – xử lý hình ảnh
* **qrcode** – tạo mã QR
* **tkcalendar** – hỗ trợ lựa chọn ngày tháng

---

## 📂 Cấu trúc project

```text
EventManager7/
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── main.py
├── main.spec
│
├── admin/
│   ├── admin_dashboard.py
│   ├── admin_events.py
│   ├── admin_stats.py
│   ├── admin_tickets.py
│   └── admin_users.py
│
├── auth/
│   └── auth.py
│
├── config/
│   ├── constants.py
│   └── ui_config.py
│
├── database/
│   └── db.py
│
├── organizer/
│   ├── organizer_attendees.py
│   ├── organizer_dashboard.py
│   ├── organizer_events.py
│   ├── organizer_profile.py
│   └── organizer_reports.py
│
├── user/
│   ├── user_dashboard.py
│   ├── user_events.py
│   ├── user_profile.py
│   └── user_tickets.py
│
└── images/
    └── ...
```

---

## ⚙️ Yêu cầu môi trường

* Python **3.10 trở lên**
* MongoDB Atlas
* Windows/Linux/macOS có hỗ trợ Tkinter

Kiểm tra phiên bản Python:

```bash
python --version
```

---

## 📦 Cài đặt

### 1. Clone project

```bash
git clone <URL_REPOSITORY>
cd EventManager7
```

### 2. Tạo môi trường ảo

```bash
python -m venv venv
```

Kích hoạt trên Windows:

```bash
venv\Scripts\activate
```

### 3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

---

## 🔐 Cấu hình MongoDB Atlas

Project sử dụng MongoDB Atlas để lưu trữ dữ liệu.

Tạo file `.env` tại **thư mục gốc của project**, cùng cấp với `main.py`:

```env
MONGO_URI=mongodb+srv://username:password@cluster.xxxxx.mongodb.net/
```

Trong code, URI được đọc thông qua biến môi trường:

```python
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
```

> ⚠️ **Không commit file `.env` lên GitHub** vì file này chứa thông tin xác thực MongoDB Atlas.

File `.gitignore` cần chứa:

```gitignore
.env
__pycache__/
*.pyc
build/
dist/
.vscode/
```

---

## ▶️ Chạy chương trình

Sau khi cài đặt đầy đủ thư viện và cấu hình MongoDB Atlas:

```bash
python main.py
```

Ứng dụng sẽ khởi động giao diện quản lý sự kiện bằng Tkinter.

---

## 👥 Các chức năng chính

### Admin

* Đăng nhập
* Quản lý người dùng
* Quản lý sự kiện
* Quản lý vé
* Xem thống kê
* Quản lý hệ thống

### Organizer

* Đăng nhập
* Quản lý thông tin cá nhân
* Tạo sự kiện
* Chỉnh sửa sự kiện
* Quản lý người tham dự
* Xem báo cáo

### User

* Đăng nhập/đăng ký
* Xem danh sách sự kiện
* Xem chi tiết sự kiện
* Đăng ký sự kiện
* Quản lý vé
* Quản lý thông tin cá nhân

---

## 📋 Requirements

Các thư viện chính được sử dụng:

```text
bcrypt==5.0.0
pymongo==4.17.0
python-dotenv==1.2.2
Pillow==12.0.0
qrcode==8.2
tkcalendar==1.6.1
```

**Tkinter** không cần cài bằng `pip` vì đây là thư viện GUI đi kèm Python trên các bản cài đặt Python thông thường.

---

## 🔒 Bảo mật

Không đưa các thông tin nhạy cảm lên GitHub, bao gồm:

* MongoDB username
* MongoDB password
* MongoDB connection string
* API key
* Secret key
* Các thông tin xác thực khác

Các thông tin này nên được lưu trong `.env` và thêm `.env` vào `.gitignore`.

---

## 📄 License

Project được thực hiện cho mục đích **học tập và nghiên cứu**.
