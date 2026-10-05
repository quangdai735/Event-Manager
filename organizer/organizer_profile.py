import tkinter as tk
from tkinter import messagebox

try:
    from config.ui_config import BG_COLOR, PRIMARY
except Exception:
    BG_COLOR = "#f4f6f9"
    PRIMARY = "#1e88e5"

try:
    from database.db import users
except Exception:
    users = None


class OrganizerProfileFrame(tk.Frame):
    def __init__(self, parent, username, *args, **kwargs):
        super().__init__(parent, bg=BG_COLOR)
        self.username = username

        # Tiêu đề
        tk.Label(
            self, 
            text="Hồ sơ Đơn vị Tổ chức", 
            font=("Arial", 16, "bold"), 
            bg=BG_COLOR, 
            fg="#2c3e50"
        ).pack(anchor="w", padx=25, pady=(15, 5))

        # Card container
        self.card = tk.Frame(self, bg="white", bd=1, relief="solid", padx=25, pady=20)
        self.card.pack(fill="both", expand=True, padx=25, pady=10)

        self.render_ui()
        self.load_profile_data()

    def render_ui(self):
        info_frame = tk.Frame(self.card, bg="white")
        info_frame.pack(fill="x", pady=10)

        # Đã đổi 9.5 -> 10 để tránh lỗi integer
        tk.Label(info_frame, text="Tên đơn vị/Thương hiệu:", font=("Arial", 10, "bold"), bg="white", width=22, anchor="w").grid(row=0, column=0, pady=8, sticky="w")
        self.entry_fullname = tk.Entry(info_frame, font=("Arial", 10), bd=1, relief="solid", width=35)
        self.entry_fullname.grid(row=0, column=1, pady=8, sticky="w")

        tk.Label(info_frame, text="Tên đăng nhập:", font=("Arial", 10, "bold"), bg="white", width=22, anchor="w").grid(row=1, column=0, pady=8, sticky="w")
        self.lbl_username = tk.Label(info_frame, text=self.username, font=("Arial", 10, "italic"), bg="white", fg="#7f8c8d")
        self.lbl_username.grid(row=1, column=1, pady=8, sticky="w")

        tk.Label(info_frame, text="Email liên hệ:", font=("Arial", 10, "bold"), bg="white", width=22, anchor="w").grid(row=2, column=0, pady=8, sticky="w")
        self.entry_email = tk.Entry(info_frame, font=("Arial", 10), bd=1, relief="solid", width=35)
        self.entry_email.grid(row=2, column=1, pady=8, sticky="w")

        tk.Label(info_frame, text="Số điện thoại hotline:", font=("Arial", 10, "bold"), bg="white", width=22, anchor="w").grid(row=3, column=0, pady=8, sticky="w")
        self.entry_phone = tk.Entry(info_frame, font=("Arial", 10), bd=1, relief="solid", width=35)
        self.entry_phone.grid(row=3, column=1, pady=8, sticky="w")

        tk.Label(info_frame, text="Giới thiệu đơn vị:", font=("Arial", 10, "bold"), bg="white", width=22, anchor="nw").grid(row=4, column=0, pady=8, sticky="w")
        self.txt_bio = tk.Text(info_frame, font=("Arial", 10), height=4, width=35, bd=1, relief="solid")
        self.txt_bio.grid(row=4, column=1, pady=8, sticky="w")

        btn_save = tk.Button(
            self.card, 
            text="💾 Lưu thông tin", 
            font=("Arial", 10, "bold"), 
            bg=PRIMARY, 
            fg="white", 
            relief="flat", 
            cursor="hand2",
            padx=15,
            pady=6,
            command=self.save_profile
        )
        btn_save.pack(anchor="w", pady=(15, 0))

    def load_profile_data(self):
        if users is not None:
            u = users.find_one({"username": self.username})
            if u:
                self.entry_fullname.insert(0, u.get("full_name", ""))
                self.entry_email.insert(0, u.get("email", ""))
                self.entry_phone.insert(0, u.get("phone", ""))
                self.txt_bio.insert("1.0", u.get("bio", ""))

    def save_profile(self):
        full_name = self.entry_fullname.get().strip()
        email = self.entry_email.get().strip()
        phone = self.entry_phone.get().strip()
        bio = self.txt_bio.get("1.0", tk.END).strip()

        if users is not None:
            users.update_one(
                {"username": self.username},
                {"$set": {
                    "full_name": full_name,
                    "email": email,
                    "phone": phone,
                    "bio": bio
                }}
            )
            messagebox.showinfo("Thành công", "Cập nhật thông tin hồ sơ thành công!")