import tkinter as tk
from tkinter import messagebox

try:
    from config.ui_config import BG_COLOR, PRIMARY
except Exception:
    BG_COLOR = "#f4f6f9"
    PRIMARY = "#1e88e5"

from organizer.organizer_attendees import OrganizerAttendeesFrame
from organizer.organizer_events import OrganizerEventsFrame
from organizer.organizer_profile import OrganizerProfileFrame
from organizer.organizer_reports import OrganizerReportsFrame


class OrganizerDashboard(tk.Tk):

    def __init__(
        self,
        username="organizer_test",
        full_name="",
        logout_handler=None,
        *args,
        **kwargs,
    ):
        super().__init__()
        self.username = username
        self.full_name = full_name or username
        self.logout_handler = logout_handler

        self.title("Hệ Thống Quản Lý Sự Kiện - Ban Tổ Chức")

        # Kích thước dự phòng tối thiểu khi thu nhỏ
        self.geometry("1280x720")
        self.minsize(1024, 600)

        # 🟢 Tự động bật Toàn màn hình (Maximize/Zoomed) ngay khi chạy
        try:
            self.state("zoomed")  # Hoạt động chuẩn trên Windows
        except Exception:
            self.attributes(
                "-fullscreen", True
            )  # Fallback hỗ trợ Linux / macOS

        self.configure(bg=BG_COLOR)

        # Header
        self.header_frame = tk.Frame(self, bg=PRIMARY, height=50)
        self.header_frame.pack(side="top", fill="x")
        self.header_frame.pack_propagate(False)

        tk.Label(
            self.header_frame,
            text="ORGANIZER PANEL",
            font=("Arial", 12, "bold"),
            fg="white",
            bg=PRIMARY,
        ).pack(side="left", padx=20)

        tk.Label(
            self.header_frame,
            text=f"Xin chào, {self.full_name}",
            font=("Arial", 10, "bold"),
            fg="white",
            bg=PRIMARY,
        ).pack(side="right", padx=20)

        # Sidebar
        self.sidebar_frame = tk.Frame(self, bg="#2c3e50", width=220)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # Content Area
        self.content_frame = tk.Frame(self, bg=BG_COLOR)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.create_sidebar_buttons()
        self.show_profile_page()

    def create_sidebar_buttons(self):
        buttons = [
            ("👤 Hồ sơ BTC", self.show_profile_page),
            ("📅 Quản lý Sự kiện", self.show_events_page),
            ("👥 Danh sách Khách", self.show_attendees_page),
            ("📊 Thống kê Doanh thu", self.show_reports_page),
            ("🚪 Đăng xuất", self.logout),
        ]

        for text, command in buttons:
            btn = tk.Button(
                self.sidebar_frame,
                text=text,
                font=("Arial", 10, "bold"),
                fg="white",
                bg="#2c3e50",
                activebackground="#34495e",
                activeforeground="white",
                relief="flat",
                anchor="w",
                padx=20,
                pady=12,
                cursor="hand2",
                command=command,
            )
            btn.pack(fill="x")

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_profile_page(self):
        self.clear_content()
        page = OrganizerProfileFrame(self.content_frame, self.username)
        page.pack(fill="both", expand=True)

    def show_events_page(self):
        self.clear_content()
        page = OrganizerEventsFrame(self.content_frame, self.username)
        page.pack(fill="both", expand=True)

    def show_attendees_page(self):
        self.clear_content()
        page = OrganizerAttendeesFrame(self.content_frame, self.username)
        page.pack(fill="both", expand=True)

    def show_reports_page(self):
        self.clear_content()
        page = OrganizerReportsFrame(self.content_frame, self.username)
        page.pack(fill="both", expand=True)

    def logout(self):
        if messagebox.askyesno(
            "Đăng xuất", "Bạn có chắc chắn muốn đăng xuất không?"
        ):
            if self.logout_handler:
                self.logout_handler()
            else:
                self.destroy()