import tkinter as tk
from config.ui_config import *
from user.user_events import UserEventFrame # Import khung tính năng sự kiện
from user.user_tickets import MyTicketsFrame # Frame danh sách vé
from user.user_profile import UserProfileFrame # Thêm import file Hồ sơ cá nhân


class UserDashboard(tk.Tk):
    def __init__(self, username, full_name, on_logout_callback):
        super().__init__()
        self.username = username
        self.full_name = full_name
        self.on_logout_callback = on_logout_callback
        
        self.title("Event Manager - Người Tham Gia")
        self.geometry("1200x700")
        self.state('zoomed')
        self.configure(bg=BG_COLOR)
        
        # ----- THANH MENU BÊN TRÁI -----
        sidebar = tk.Frame(self, bg=PRIMARY, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Hiển thị tên người dùng
        tk.Label(sidebar, text=f"Xin chào,\n{self.full_name}", font=("Arial", 14, "bold"), 
                 bg=PRIMARY, fg="white", justify="center").pack(pady=20)
        
        # Các nút chuyển trang
        tk.Button(sidebar, text=" Khám phá sự kiện", font=("Arial", 12), bg=PRIMARY, fg="white", 
                  relief="flat", anchor="w", padx=20, command=self.show_events_page).pack(fill="x", ipady=12)
        
        tk.Button(sidebar, text=" Vé của tôi", font=("Arial", 12), bg=PRIMARY, fg="white", 
                  relief="flat", anchor="w", padx=20, command=self.show_my_tickets_page).pack(fill="x", ipady=12)
        
        # --- BỔ SUNG NÚT HỒ SƠ TẠI ĐÂY ---
        tk.Button(sidebar, text=" Hồ sơ cá nhân", font=("Arial", 12), bg=PRIMARY, fg="white", 
                  relief="flat", anchor="w", padx=20, command=self.show_profile_page).pack(fill="x", ipady=12)
        
        # Nút đăng xuất
        tk.Button(sidebar, text=" Đăng xuất", font=("Arial", 12, "bold"), bg="#d32f2f", fg="white", 
                  relief="flat", command=self.logout).pack(side="bottom", fill="x", ipady=12)
                  
        # ----- KHUNG HIỂN THỊ NỘI DUNG CHÍNH (BÊN PHẢI) -----
        self.content_frame = tk.Frame(self, bg=BG_COLOR)
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Mặc định hiển thị trang Khám phá sự kiện trước
        self.show_events_page()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_events_page(self):
        self.clear_content()
        # Gọi Frame danh sách sự kiện và truyền username vào
        page = UserEventFrame(self.content_frame, self.username)
        page.pack(fill="both", expand=True)

    def show_my_tickets_page(self):
        self.clear_content()
        # Khởi chạy khung danh sách vé thực tế từ database
        page = MyTicketsFrame(self.content_frame, self.username)
        page.pack(fill="both", expand=True)

    def show_profile_page(self):
        self.clear_content()
        # Truyền self.user_info (hoặc thông tin user hiện tại)
        page = UserProfileFrame(self.content_frame, getattr(self, 'user_data', self.username))
        page.pack(fill="both", expand=True)

    def logout(self):
        self.on_logout_callback()