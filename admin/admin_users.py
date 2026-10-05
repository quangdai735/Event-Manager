import tkinter as tk
from tkinter import ttk, messagebox
from database.db import users
from bson import ObjectId
from config.ui_config import *
import re


class UserManagementFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)

        self.selected_id = None

        # ===== TITLE & SEARCH =====
        header_frame = tk.Frame(self, bg=BG_COLOR)
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(
            header_frame,
            text="👥 Quản lý người dùng",
            font=("Segoe UI", 18, "bold"),
            bg=BG_COLOR
        ).pack(side="left")

        # Thanh tìm kiếm nhanh
        search_frame = tk.Frame(header_frame, bg=BG_COLOR)
        search_frame.pack(side="right")

        tk.Label(search_frame, text="🔍 Tìm:", bg=BG_COLOR, font=("Segoe UI", 10)).pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_users())
        tk.Entry(search_frame, textvariable=self.search_var, width=20, font=("Segoe UI", 10)).pack(side="left")

        # ===== FORM TẠO TÀI KHOẢN =====
        form = tk.Frame(self, bg="white", bd=1, relief="solid")
        form.pack(fill="x", padx=20, pady=10)

        self.fullname_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()

        tk.Label(form, text="Họ tên", bg="white", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=10, pady=(8, 2))
        tk.Label(form, text="Username", bg="white", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, padx=10, pady=(8, 2))
        tk.Label(form, text="Email", bg="white", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, padx=10, pady=(8, 2))
        tk.Label(form, text="Password", bg="white", font=("Segoe UI", 9, "bold")).grid(row=0, column=3, padx=10, pady=(8, 2))
        tk.Label(form, text="Role", bg="white", font=("Segoe UI", 9, "bold")).grid(row=0, column=4, padx=10, pady=(8, 2))

        tk.Entry(form, textvariable=self.fullname_var, width=20).grid(row=1, column=0, padx=10, pady=(0, 8))
        tk.Entry(form, textvariable=self.username_var, width=16).grid(row=1, column=1, padx=10, pady=(0, 8))
        tk.Entry(form, textvariable=self.email_var, width=25).grid(row=1, column=2, padx=10, pady=(0, 8))
        tk.Entry(form, textvariable=self.password_var, width=16, show="*").grid(row=1, column=3, padx=10, pady=(0, 8))

        self.combo_role = ttk.Combobox(
            form,
            values=["user", "organizer"],
            state="readonly",
            width=12
        )
        self.combo_role.set("user")
        self.combo_role.grid(row=1, column=4, padx=10, pady=(0, 8))

        tk.Button(
            form,
            text="+ Tạo tài khoản",
            bg=SUCCESS,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            relief="flat",
            command=self.create_user
        ).grid(row=1, column=5, padx=10, pady=(0, 8), ipady=2)

        # ===== TABLE =====
        table = tk.Frame(self, bg="white", bd=1, relief="solid")
        table.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(
            table,
            columns=("fullname", "username", "email", "role", "status"),
            show="headings"
        )

        self.tree.heading("fullname", text="Họ và tên")
        self.tree.heading("username", text="Tên đăng nhập")
        self.tree.heading("email", text="Email")
        self.tree.heading("role", text="Vai trò")
        self.tree.heading("status", text="Trạng thái")

        self.tree.column("fullname", width=200)
        self.tree.column("username", width=140)
        self.tree.column("email", width=240)
        self.tree.column("role", width=120, anchor="center")
        self.tree.column("status", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ===== ACTION BUTTONS =====
        action = tk.Frame(self, bg=BG_COLOR)
        action.pack(pady=10)


        tk.Button(
            action,
            text="🔒 Khóa tài khoản",
            bg=DANGER,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            relief="flat",
            command=self.block_user
        ).pack(side="left", padx=5, ipady=3)

        tk.Button(
            action,
            text="🔓 Mở khóa",
            bg=SUCCESS,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            relief="flat",
            command=self.unblock_user
        ).pack(side="left", padx=5, ipady=3)

        tk.Button(
            action,
            text="🗑 Xóa tài khoản",
            bg="#d9534f",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            relief="flat",
            command=self.delete_user
        ).pack(side="left", padx=5, ipady=3)

        self.load_users()

    # ===== CREATE USER =====
    def create_user(self):
        full_name = self.fullname_var.get().strip()
        username = self.username_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        role = self.combo_role.get()

        if not all([full_name, username, email, password]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        if users.find_one({"username": username}):
            messagebox.showerror("Lỗi", "Username đã tồn tại!")
            return

        if users.find_one({"email": email}):
            messagebox.showerror("Lỗi", "Email đã được sử dụng!")
            return

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, email):
            messagebox.showerror("Lỗi", "Email không hợp lệ!")
            return

        users.insert_one({
            "full_name": full_name,
            "username": username,
            "email": email,
            "password": password,
            "role": role,
            "status": "active"
        })

        messagebox.showinfo("Thành công", f"Đã tạo tài khoản [{role.upper()}] thành công!")

        self.fullname_var.set("")
        self.username_var.set("")
        self.email_var.set("")
        self.password_var.set("")
        self.combo_role.set("user")

        self.load_users()

    # ===== LOAD USER LIST =====
    def load_users(self):
        self.tree.delete(*self.tree.get_children())
        self.selected_id = None  # Reset lại dòng chọn sau khi load lại

        query = {}
        search_kw = self.search_var.get().strip()
        if search_kw:
            # Tìm theo tên, username hoặc email
            query = {
                "$or": [
                    {"full_name": {"$regex": search_kw, "$options": "i"}},
                    {"username": {"$regex": search_kw, "$options": "i"}},
                    {"email": {"$regex": search_kw, "$options": "i"}}
                ]
            }

        for u in users.find(query):
            role = u.get("role", "user")
            status = u.get("status", "active")

            if role == "admin":
                role_text = "👑 admin"
            elif role == "organizer":
                role_text = "🎫 organizer"
            else:
                role_text = "👤 user"

            status_text = "🔴 blocked" if status == "blocked" else "🟢 active"

            self.tree.insert(
                "",
                "end",
                iid=str(u["_id"]),
                values=(
                    u.get("full_name", ""),
                    u.get("username", ""),
                    u.get("email", ""),
                    role_text,
                    status_text
                )
            )

    # ===== SELECT =====
    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_id = selected[0]

    # ===== CHECK ADMIN =====
    def is_admin(self):
        if not self.selected_id:
            return False
        user = users.find_one({"_id": ObjectId(self.selected_id)})
        return user and user.get("role") == "admin"

    # ===== TOGGLE ROLE =====
    

    # ===== BLOCK =====
    def block_user(self):
        if not self.selected_id:
            messagebox.showwarning("Thông báo", "Vui lòng chọn tài khoản.")
            return

        if self.is_admin():
            messagebox.showwarning("Thông báo", "Không thể khóa tài khoản Admin.")
            return

        users.update_one(
            {"_id": ObjectId(self.selected_id)},
            {"$set": {"status": "blocked"}}
        )

        messagebox.showinfo("Thành công", "Đã khóa tài khoản.")
        self.load_users()

    # ===== UNBLOCK =====
    def unblock_user(self):
        if not self.selected_id:
            messagebox.showwarning("Thông báo", "Vui lòng chọn tài khoản.")
            return

        users.update_one(
            {"_id": ObjectId(self.selected_id)},
            {"$set": {"status": "active"}}
        )

        messagebox.showinfo("Thành công", "Đã mở khóa tài khoản.")
        self.load_users()

    # ===== DELETE USER =====
    def delete_user(self):
        if not self.selected_id:
            messagebox.showwarning("Thông báo", "Vui lòng chọn tài khoản cần xóa.")
            return

        if self.is_admin():
            messagebox.showwarning("Thông báo", "Không thể xóa tài khoản Admin.")
            return

        user = users.find_one({"_id": ObjectId(self.selected_id)})
        if not user:
            messagebox.showerror("Lỗi", "Không tìm thấy tài khoản.")
            return

        confirm = messagebox.askyesno(
            "Xác nhận",
            f"Bạn có chắc muốn xóa tài khoản:\n\nUsername: {user.get('username')}\nEmail: {user.get('email')} ?"
        )

        if not confirm:
            return

        users.delete_one({"_id": ObjectId(self.selected_id)})

        messagebox.showinfo("Thành công", "Đã xóa tài khoản khỏi hệ thống.")
        self.load_users()