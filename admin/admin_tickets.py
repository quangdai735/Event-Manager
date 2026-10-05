import tkinter as tk
from tkinter import messagebox, ttk

from bson import ObjectId
from config.ui_config import *
from database.db import db, events, tickets, users


class TicketManagementFrame(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)

        self.event_map = {}
        self.selected_id = None

        # ===== TABLE =====
        table = tk.Frame(self, bg="white", bd=1)
        table.pack(fill="both", expand=True, padx=20, pady=(10, 5))

        style = ttk.Style()
        style.configure("Treeview", rowheight=32, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        self.tree = ttk.Treeview(
            table,
            columns=("event", "price", "total", "sold"),
            show="headings",
        )

        self.tree.heading("event", text="Sự kiện")
        self.tree.heading("price", text="Giá")
        self.tree.heading("total", text="Tổng vé")
        self.tree.heading("sold", text="Đã bán")

        self.tree.column("event", width=320)
        self.tree.column("price", width=120, anchor="center")
        self.tree.column("total", width=120, anchor="center")
        self.tree.column("sold", width=120, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ===== NÚT XÓA =====
        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Button(
            btn_frame,
            text="🗑 Xóa",
            bg=DANGER,
            fg="white",
            command=self.delete_ticket,
        ).pack(side="left")

        # Cache tên hiển thị của BTC theo username để tránh truy vấn lặp lại
        self._organizer_display_cache = {}

        # ===== LOAD DATA =====
        self.load_events()
        self.load_tickets()

    # ===== LẤY TÊN HIỂN THỊ CỦA BAN TỔ CHỨC =====
    def get_organizer_display(self, e):
        """Ưu tiên lấy tên BTC thực tế (organizer_name / full_name).
        Không gán cứng 'Quản trị viên' dù người tạo có là admin."""
        username = e.get("organizer", "")
        
        # 1. Kiểm tra trường organizer_name trong document sự kiện
        organizer_name = e.get("organizer_name")
        if organizer_name and organizer_name.strip():
            return organizer_name.strip()

        if not username:
            return "N/A"

        # 2. Sử dụng cache nếu đã truy vấn trước đó
        if username in self._organizer_display_cache:
            return self._organizer_display_cache[username]

        # 3. Tìm thông tin người dùng trong DB để lấy full_name
        user = users.find_one({"username": username})
        if user and user.get("full_name"):
            display_name = user.get("full_name").strip()
        else:
            display_name = username

        self._organizer_display_cache[username] = display_name
        return display_name

    # ===== LOAD EVENTS =====
    def load_events(self):
        self.event_map.clear()

        for e in events.find():
            display = f"{e['name']} (👤 {self.get_organizer_display(e)})"
            self.event_map[display] = str(e["_id"])  # Lưu string ID

    # ===== LOAD TICKETS =====
    def load_tickets(self):
        self.tree.delete(*self.tree.get_children())

        for t in tickets.find():
            event_name = "❌ Không có"
            event_id = t.get("event_id")

            try:
                if event_id:
                    event = events.find_one({"_id": ObjectId(event_id)})
                    if event:
                        event_name = f"{event['name']} (👤 {self.get_organizer_display(event)})"
            except Exception:
                pass

            # Đếm số vé đã bán thực tế từ collection user_tickets
            sold_count = 0
            if event_id:
                sold_count = db["user_tickets"].count_documents(
                    {
                        "$or": [
                            {"event_id": str(event_id)},
                            {"event_id": ObjectId(event_id)},
                        ]
                    }
                )

            self.tree.insert(
                "",
                "end",
                iid=str(t["_id"]),
                values=(
                    event_name,
                    f"{t.get('price', 0):,} đ",
                    t.get("total", 0),
                    sold_count,
                ),
            )

    # ===== SELECT =====
    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_id = selected[0]

    # ===== DELETE =====
    def delete_ticket(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Hãy chọn một vé để xóa")
            return

        if not messagebox.askyesno("Xác nhận", "Xóa vé này?"):
            return

        tickets.delete_one({"_id": ObjectId(self.selected_id)})

        self.clear_form()
        self.load_tickets()

    # ===== CLEAR =====
    def clear_form(self):
        self.selected_id = None