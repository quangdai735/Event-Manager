import tkinter as tk
from tkinter import messagebox

from admin.admin_events import EventManagementFrame
from admin.admin_users import UserManagementFrame
from admin.admin_tickets import TicketManagementFrame
from admin.admin_stats import StatsFrame

from config.ui_config import *


class AdminDashboard(tk.Tk):
    def __init__(self, username, full_name, on_logout, role):
        super().__init__()

        self.username = username
        self.full_name = full_name
        self.on_logout = on_logout
        self.role = role

        self.title("Event Manager")
        self.geometry("1200x700")
        self.state("zoomed")
        self.configure(bg=BG_COLOR)

        # ===== SIDEBAR =====
        self.sidebar = tk.Frame(self, bg=PRIMARY, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="⚡ EVENT ADMIN",
            bg=PRIMARY,
            fg="white",
            font=("Arial", 16, "bold")
        ).pack(pady=(25, 10))

        tk.Label(
            self.sidebar,
            text=f"👤 {self.full_name}",
            bg=PRIMARY,
            fg="white",
            font=("Arial", 11)
        ).pack(pady=(0, 30))

        self.active_btn = None

        self.create_menu_btn("📅 Sự kiện", self.show_event)
        self.create_menu_btn("🎟️ Vé", self.show_ticket)

        if self.role == "admin":
            self.create_menu_btn("👥 Người dùng", self.show_user)
            self.create_menu_btn("📊 Thống kê", self.show_stats)

        tk.Button(
            self.sidebar,
            text="🚪 Đăng xuất",
            bg=DANGER,
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            command=self.logout
        ).pack(side="bottom", fill="x", padx=20, pady=20, ipady=10)

        # ===== MAIN =====
        self.main = tk.Frame(self, bg=BG_COLOR)
        self.main.pack(side="right", fill="both", expand=True)

        # ===== HEADER =====
        self.header = tk.Frame(self.main, bg="white", height=60)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.title_label = tk.Label(
            self.header,
            text="Dashboard",
            bg="white",
            font=("Arial", 16, "bold")
        )
        self.title_label.pack(anchor="w", padx=20)

        # ===== CONTENT =====
        self.content = tk.Frame(self.main, bg=BG_COLOR)
        self.content.pack(fill="both", expand=True)

        # ===== FRAMES =====
        self.event_view = EventManagementFrame(self.content, self.username)
        self.ticket_view = TicketManagementFrame(self.content)
        self.user_view = UserManagementFrame(self.content)
        self.stats_view = StatsFrame(self.content)

        self.show_event()

    # ================= MENU =================

    def create_menu_btn(self, text, command):
        btn = tk.Button(
            self.sidebar,
            text=text,
            bg=PRIMARY,
            fg="white",
            font=("Arial", 12),
            anchor="w",
            padx=20,
            relief="flat",
            cursor="hand2",
            command=lambda: self.switch_view(command, btn)
        )
        btn.pack(fill="x", pady=2, ipady=10)
        return btn

    def switch_view(self, command, btn):
        if self.active_btn:
            self.active_btn.config(bg=PRIMARY)

        btn.config(bg="#166fe5")
        self.active_btn = btn
        command()

    # ================= VIEW =================

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.pack_forget()

    def show_event(self):
        self.title_label.config(text="📅 Quản lý sự kiện")
        self.clear_content()
        self.event_view.pack(fill="both", expand=True)
        self.event_view.load_events_data()

    def show_ticket(self):
        self.title_label.config(text="🎟️ Quản lý vé")
        self.clear_content()
        self.ticket_view.pack(fill="both", expand=True)
        self.ticket_view.load_events()
        self.ticket_view.load_tickets()

    def show_user(self):
        self.title_label.config(text="👥 Quản lý người dùng")
        self.clear_content()
        self.user_view.pack(fill="both", expand=True)
        self.user_view.load_users_data()

    def show_stats(self):
        self.title_label.config(text="📊 Thống kê")
        self.clear_content()
        self.stats_view.pack(fill="both", expand=True)
        self.stats_view.refresh_stats()

    # ================= LOGOUT =================

    def logout(self):
        if messagebox.askyesno(
            "Đăng xuất",
            "Bạn chắc chắn muốn đăng xuất?"
        ):
            self.destroy()
            self.on_logout()