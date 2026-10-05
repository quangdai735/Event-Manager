import tkinter as tk
from tkinter import messagebox

# ===== UI CONFIG =====
try:
    from config.ui_config import BG_COLOR, PRIMARY
except Exception:
    BG_COLOR = "#f4f6f9"
    PRIMARY = "#1e88e5"

# ===== DATABASE =====
try:
    from database.db import users
except Exception:
    users = None


class UserProfileFrame(tk.Frame):
    def __init__(self, parent, user_data):
        super().__init__(parent, bg=BG_COLOR)

        # ===== LOAD USER =====
        if isinstance(user_data, dict):
            self.username = user_data.get("username", "")
            self.user_info = user_data
        else:
            self.username = str(user_data)
            self.user_info = {"username": self.username}

        # 🔥 Load DB
        if users is not None and self.username:
            try:
                db_user = users.find_one({"username": self.username})
                if db_user:
                    self.user_info.update(db_user)
            except Exception as e:
                print("DB Error:", e)

        # ===== UI =====
        self.build_ui()

    # ================= UI =================
    def build_ui(self):
        # 1. TIÊU ĐỀ TRANG (CĂN GIỮA)
        tk.Label(
            self,
            text="👤 Hồ sơ cá nhân",
            font=("Segoe UI", 18, "bold"),
            bg=BG_COLOR,
            fg="#1F2937"
        ).pack(anchor="center", pady=(20, 15))

        # 2. KHUNG CHỨA TOÀN BỘ CARD (DÙNG ĐỂ CĂN GIỮA CHÍNH MÀN HÌNH)
        center_container = tk.Frame(self, bg=BG_COLOR)
        center_container.pack(expand=True, fill="both")

        # Khung Card màu trắng chứa thông tin
        card = tk.Frame(center_container, bg="white", bd=1, relief="solid", padx=30, pady=25)
        card.pack(anchor="center", pady=10)

        # ===== SECTON 1: THÔNG TIN TÀI KHOẢN =====
        tk.Label(
            card,
            text="👤 Thông tin tài khoản",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg=PRIMARY
        ).pack(anchor="w", pady=(0, 15))

        info = tk.Frame(card, bg="white")
        info.pack(fill="x", pady=5)

        # Username
        tk.Label(
            info, text="Username:", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#374151", width=14, anchor="w"
        ).grid(row=0, column=0, pady=8, sticky="w")
        
        tk.Label(
            info, text=f"@{self.username}", font=("Segoe UI", 11, "bold"),
            bg="#F3F4F6", fg="#2563EB", padx=8, pady=3, anchor="w"
        ).grid(row=0, column=1, sticky="w", pady=8)

        # Full name (EDITABLE)
        full_name = self.user_info.get("full_name", "")
        tk.Label(
            info, text="Họ tên:", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#374151", width=14, anchor="w"
        ).grid(row=1, column=0, pady=8, sticky="w")

        self.entry_name = tk.Entry(info, width=28, font=("Segoe UI", 11))
        self.entry_name.insert(0, full_name)
        self.entry_name.grid(row=1, column=1, sticky="w", pady=8, padx=(0, 10))

        tk.Button(
            info, text="Cập nhật",
            bg=PRIMARY, fg="white", font=("Segoe UI", 10, "bold"),
            padx=12, pady=3, cursor="hand2",
            command=self.update_name
        ).grid(row=1, column=2, padx=5, pady=8)

        # Email
        tk.Label(
            info, text="Email:", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#374151", width=14, anchor="w"
        ).grid(row=2, column=0, pady=8, sticky="w")

        self.entry_email = tk.Entry(info, width=28, font=("Segoe UI", 11))
        self.entry_email.insert(0, self.user_info.get("email", ""))
        self.entry_email.grid(row=2, column=1, sticky="w", pady=8, padx=(0, 10))

        tk.Button(
            info, text="Cập nhật",
            bg=PRIMARY, fg="white", font=("Segoe UI", 10, "bold"),
            padx=12, pady=3, cursor="hand2",
            command=self.update_email
        ).grid(row=2, column=2, padx=5, pady=8)

        # ===== DÒNG PHÂN CÁCH =====
        tk.Frame(card, height=1, bg="#E5E7EB").pack(fill="x", pady=20)

        # ===== SECTION 2: ĐỔI MẬT KHẨU =====
        tk.Label(
            card, text="🔒 Đổi mật khẩu",
            font=("Segoe UI", 13, "bold"),
            bg="white", fg=PRIMARY
        ).pack(anchor="w", pady=(0, 10))

        pwd = tk.Frame(card, bg="white")
        pwd.pack(fill="x", pady=5)

        tk.Label(
            pwd, text="Mật khẩu cũ:", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#374151", width=14, anchor="w"
        ).grid(row=0, column=0, pady=8, sticky="w")
        
        self.old_pwd = tk.Entry(pwd, show="*", width=28, font=("Segoe UI", 11))
        self.old_pwd.grid(row=0, column=1, pady=8, sticky="w")

        tk.Label(
            pwd, text="Mật khẩu mới:", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#374151", width=14, anchor="w"
        ).grid(row=1, column=0, pady=8, sticky="w")
        
        self.new_pwd = tk.Entry(pwd, show="*", width=28, font=("Segoe UI", 11))
        self.new_pwd.grid(row=1, column=1, pady=8, sticky="w")

        tk.Label(
            pwd, text="Xác nhận:", font=("Segoe UI", 11, "bold"),
            bg="white", fg="#374151", width=14, anchor="w"
        ).grid(row=2, column=0, pady=8, sticky="w")
        
        self.confirm_pwd = tk.Entry(pwd, show="*", width=28, font=("Segoe UI", 11))
        self.confirm_pwd.grid(row=2, column=1, pady=8, sticky="w")

        tk.Button(
            pwd, text="🔑 Đổi mật khẩu",
            bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"),
            padx=18, pady=6, cursor="hand2",
            command=self.change_password
        ).grid(row=3, column=1, pady=(15, 5), sticky="w")

    # ================= UPDATE NAME =================
    def update_name(self):
        new_name = self.entry_name.get().strip()

        if not new_name:
            messagebox.showwarning("Lỗi", "Tên không được trống")
            return

        if users is not None:
            users.update_one(
                {"username": self.username},
                {"$set": {"full_name": new_name}}
            )

        self.user_info["full_name"] = new_name
        messagebox.showinfo("OK", "Đã cập nhật tên thành công")

    # ================= UPDATE EMAIL =================
    def update_email(self):
        email = self.entry_email.get().strip()

        if "@" not in email:
            messagebox.showwarning("Lỗi", "Email không hợp lệ")
            return

        if users is not None:
            users.update_one(
                {"username": self.username},
                {"$set": {"email": email}}
            )

        messagebox.showinfo("OK", "Cập nhật email thành công")

    # ================= CHANGE PASSWORD =================
    def change_password(self):
        old = self.old_pwd.get()
        new = self.new_pwd.get()
        confirm = self.confirm_pwd.get()

        if not old or not new or not confirm:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        if new != confirm:
            messagebox.showerror("Lỗi", "Mật khẩu mới xác nhận không khớp")
            return

        if users is not None:
            user = users.find_one({"username": self.username})

            if user and user.get("password") != old:
                messagebox.showerror("Sai", "Mật khẩu cũ không chính xác")
                return

            users.update_one(
                {"username": self.username},
                {"$set": {"password": new}}
            )

        messagebox.showinfo("OK", "Đổi mật khẩu thành công")

        self.old_pwd.delete(0, tk.END)
        self.new_pwd.delete(0, tk.END)
        self.confirm_pwd.delete(0, tk.END)