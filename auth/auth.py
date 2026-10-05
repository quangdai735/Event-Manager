import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
import re
from database.db import db


users = db["users"]
    
    # Tự động tạo 1 tài khoản Admin mặc định nếu chưa có trên Cloud
if not users.find_one({"username": "admin"}):
    users.insert_one({
        "username": "admin",
        "email": "admin@event.com",
        "password": "123",
        "role": "admin",
        "full_name": "Quản trị viên"
    })

class AuthWindow(tk.Tk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success # Callback nhận kết quả khi đăng nhập thành công
        
        self.title("Event Manager - Nền tảng quản lý sự kiện")
        self.geometry("1100x650")
        self.resizable(True, True)
        self.state('zoomed')
        self.configure(bg="#f0f2f5")

        self.main_container = tk.Frame(self, bg="#f0f2f5")
        self.main_container.place(relx=0.5, rely=0.5, anchor="center", width=1050, height=600)

        # Phần bên trái (Branding)
        left_frame = tk.Frame(self.main_container, bg="#f0f2f5", width=520, height=600)
        left_frame.pack(side="left", fill="both", expand=True)
        left_frame.pack_propagate(False)

        tk.Label(left_frame, text="⚡ Event Manager", font=("Arial", 28, "bold"), bg="#f0f2f5", fg="#1877f2").pack(anchor="w", padx=40, pady=(60, 20))
        tk.Label(left_frame, text="Khám phá và\nquản lý những\nsự kiện bạn\nyêu thích.", font=("Arial", 38, "bold"), bg="#f0f2f5", fg="#1c1e21", justify="left").pack(anchor="w", padx=40, pady=(0, 20))
        tk.Label(left_frame, text="Nền tảng kết nối ban tổ chức và người tham gia\nnhanh chóng, thông minh và chuyên nghiệp.", font=("Arial", 14), bg="#f0f2f5", fg="#606770", justify="left").pack(anchor="w", padx=40)

        # Phần bên phải (Card Auth Form)
        right_frame = tk.Frame(self.main_container, bg="#f0f2f5", width=530, height=600)
        right_frame.pack(side="right", fill="both", expand=True)
        right_frame.pack_propagate(False)

        self.card = tk.Frame(right_frame, bg="#ffffff", width=440, height=580, highlightbackground="#dadde1", highlightthickness=1)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        self.create_login_ui()

    def bind_hover(self, button, bg_color, hover_color):
        button.bind("<Enter>", lambda e: button.config(bg=hover_color))
        button.bind("<Leave>", lambda e: button.config(bg=bg_color))

    def toggle_password(self, entry, btn_toggle):
        if entry.cget('show') == '':
            entry.config(show='*')
            btn_toggle.config(text='👁', fg="gray")
        else:
            entry.config(show='')
            btn_toggle.config(text='Ẩn', fg="#1877f2")

    def create_input_box(self, parent, label_text, is_password=False):
        tk.Label(parent, text=label_text, font=("Arial", 10, "bold"), bg="#ffffff", fg="#1c1e21").pack(anchor="w", padx=35, pady=(4, 2))
        frame = tk.Frame(parent, bg="#f5f6f7", highlightbackground="#dddfe2", highlightthickness=1)
        frame.pack(fill="x", padx=35, pady=(0, 10))

        entry = tk.Entry(frame, font=("Arial", 12), bg="#f5f6f7", fg="black", relief="flat")
        entry.pack(side="left", fill="x", expand=True, ipady=7, padx=10)

        if is_password:
            entry.config(show="*")
            btn_eye = tk.Label(frame, text="👁", font=("Arial", 11), bg="#f5f6f7", fg="gray", cursor="hand2")
            btn_eye.pack(side="right", padx=10)
            btn_eye.bind("<Button-1>", lambda e: self.toggle_password(entry, btn_eye))
        return entry

    def create_login_ui(self):
        for widget in self.card.winfo_children():
            widget.destroy()

        tk.Label(self.card, text="Đăng nhập hệ thống", font=("Arial", 22, "bold"), bg="#ffffff", fg="#1877f2").pack(pady=(35, 5))
        tk.Label(self.card, text="Chào mừng bạn quay trở lại", font=("Arial", 11), bg="#ffffff", fg="#606770").pack(pady=(0, 20))

        self.entry_user = self.create_input_box(self.card, "Tên đăng nhập:")
        self.entry_pass = self.create_input_box(self.card, "Mật khẩu:", is_password=True)

        self.entry_pass.bind("<Return>", lambda event: self.login_logic())
        self.entry_user.bind("<Return>", lambda event: self.login_logic())

        btn_login = tk.Button(self.card, text="Đăng nhập", font=("Arial", 13, "bold"), bg="#1877f2", fg="white", relief="flat", cursor="hand2", command=self.login_logic)
        btn_login.pack(fill="x", padx=35, pady=(10, 15), ipady=8)
        self.bind_hover(btn_login, "#1877f2", "#166fe5")

        tk.Frame(self.card, height=1, bg="#dadde1").pack(fill="x", padx=35, pady=10)

        btn_register = tk.Button(self.card, text="Tạo tài khoản mới", font=("Arial", 12, "bold"), bg="#42b72a", fg="white", relief="flat", cursor="hand2", command=self.create_register_ui)
        btn_register.pack(pady=10, ipady=8, ipadx=20)
        self.bind_hover(btn_register, "#42b72a", "#36a420")

    def create_register_ui(self):
        for widget in self.card.winfo_children():
            widget.destroy()

        tk.Label(self.card, text="Tạo tài khoản", font=("Arial", 22, "bold"), bg="#ffffff", fg="#1877f2").pack(pady=(20, 5))
        tk.Label(self.card, text="Nhanh chóng và dễ dàng.", font=("Arial", 11), bg="#ffffff", fg="#606770").pack(pady=(0, 15))

        self.reg_fullname = self.create_input_box(self.card,"Họ và tên:")
        self.reg_user = self.create_input_box(self.card, "Tên đăng nhập (4-20 ký tự):")
        self.reg_email = self.create_input_box(self.card, "Địa chỉ Email:")
        self.reg_pass = self.create_input_box(self.card, "Mật khẩu (Ít nhất 6 ký tự):", is_password=True)
        self.reg_confirm = self.create_input_box(self.card, "Xác nhận mật khẩu:", is_password=True)

        self.reg_confirm.bind("<Return>", lambda event: self.register_logic())

        btn_reg = tk.Button(self.card, text="Đăng ký", font=("Arial", 13, "bold"), bg="#1877f2", fg="white", relief="flat", cursor="hand2", command=self.register_logic)
        btn_reg.pack(fill="x", padx=35, pady=(5, 10), ipady=7)
        self.bind_hover(btn_reg, "#1877f2", "#166fe5")

        lbl_back = tk.Label(self.card, text="Đã có tài khoản? Đăng nhập", font=("Arial", 11), bg="#ffffff", fg="#1877f2", cursor="hand2")
        lbl_back.pack(pady=5)
        lbl_back.bind("<Button-1>", lambda e: self.create_login_ui())

    def login_logic(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đủ thông tin!")
            return

        # Tìm người dùng theo username
        user = users.find_one({"username": username})

        if not user or user["password"] != password:
            messagebox.showerror("Lỗi", "Tài khoản hoặc mật khẩu không chính xác!")
            return

        # Kiểm tra tài khoản bị khóa
        if user.get("status", "active") == "blocked":
            messagebox.showerror(
                "Tài khoản bị khóa",
                "Tài khoản của bạn đã bị khóa.\nVui lòng liên hệ quản trị viên."
            )
            return

        # ===== Đăng nhập thành công =====
        messagebox.showinfo(
            "Thành công",
            f"Chào mừng {user.get('full_name', username)} đăng nhập thành công!"
        )

        role = user.get("role", "user")
        full_name = user.get("full_name", username)

        self.withdraw()
        self.on_login_success(username, role, full_name)


    def register_logic(self):
        full_name = self.reg_fullname.get().strip()
        username = self.reg_user.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_pass.get().strip()
        confirm = self.reg_confirm.get().strip()

        if not all([full_name, username, email, password, confirm]):
            messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ tất cả các trường!")
            return

        if not (4 <= len(username) <= 20) or not username.isalnum():
            messagebox.showerror("Lỗi", "Tên đăng nhập phải từ 4-20 ký tự và chỉ chứa chữ/số!")
            return

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            messagebox.showerror("Lỗi", "Địa chỉ Email không hợp lệ!")
            return

        if len(password) < 6:
            messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 6 ký tự!")
            return
        if password != confirm:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
            return

        if users.find_one({"username": username}):
            messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại!")
            return
        if users.find_one({"email": email}):
            messagebox.showerror("Lỗi", "Email này đã được sử dụng!")
            return

        users.insert_one({
            "full_name": full_name,
            "username": username,
            "email": email,
            "password": password, 
            "role": "user"
        })
        
        messagebox.showinfo("Thành công", "Đăng ký thành công! Vui lòng đăng nhập.")
        self.create_login_ui()