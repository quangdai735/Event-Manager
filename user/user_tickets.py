import tkinter as tk
from tkinter import ttk
from bson import ObjectId
from database.db import db
from config.ui_config import *
import qrcode
from PIL import ImageTk, Image

class MyTicketsFrame(tk.Frame):
    def __init__(self, parent, username):
        super().__init__(parent, bg=BG_COLOR)
        self.username = username
        self.qr_photo = None

        tk.Label(self, text="🎫 Vé của tôi",
                 font=("Arial", 20, "bold"),
                 bg=BG_COLOR).pack(pady=10)

        # TABLE: Bổ sung thêm cột "Thanh toán"
        self.tree = ttk.Treeview(self,
                                 columns=("code", "name", "date", "price", "status"),
                                 show="headings")

        self.tree.heading("code", text="MÃ VÉ")
        self.tree.heading("name", text="TÊN SỰ KIỆN")
        self.tree.heading("date", text="NGÀY")
        self.tree.heading("price", text="GIÁ VÉ")
        self.tree.heading("status", text="TRẠNG THÁI THANH TOÁN")

        self.tree.column("code", width=100, anchor="center")
        self.tree.column("name", width=220)
        self.tree.column("date", width=110, anchor="center")
        self.tree.column("price", width=100, anchor="e")
        self.tree.column("status", width=180, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=15, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.detail = tk.Frame(self, bg="white", bd=1, relief="solid")
        self.detail.pack(fill="x", padx=15, pady=10)

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())

        tickets = db["user_tickets"].find({
            "username": self.username
        })

        for t in tickets:
            # Lấy trạng thái thanh toán (Mặc định là "Đã thanh toán" nếu vé cũ chưa có trường này)
            pay_status = t.get("payment_status", "Đã thanh toán")
            
            self.tree.insert("", "end", iid=str(t["_id"]),
                             values=(
                                 t.get("ticket_code"),
                                 t.get("event_name"),
                                 t.get("date"),
                                 f"{t.get('price', 0):,} đ",
                                 pay_status  # 🔥 Hiển thị trạng thái rõ ràng
                             ))

    def on_select(self, e):
        sel = self.tree.selection()
        if not sel:
            return

        t = db["user_tickets"].find_one({
            "_id": ObjectId(sel[0])
        })

        for w in self.detail.winfo_children():
            w.destroy()

        pay_status = t.get("payment_status", "Đã thanh toán")
        pay_method = t.get("payment_method", "Trực tuyến")

        # Xác định màu sắc hiển thị trạng thái
        status_color = "#2ecc71" if pay_status == "Đã thanh toán" else "#e74c3c"

        # KHUNG THÔNG TIN VÉ
        info_frame = tk.Frame(self.detail, bg="white")
        info_frame.pack(side="left", padx=20, pady=10)

        tk.Label(info_frame, text=f"🎪 {t.get('event_name')}", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
        tk.Label(info_frame, text=f"📅 Ngày diễn: {t.get('date')}", font=("Arial", 10), bg="white").pack(anchor="w")
        tk.Label(info_frame, text=f"💳 Hình thức: {pay_method}", font=("Arial", 10), bg="white").pack(anchor="w")
        
        # Nhãn hiển thị Trạng thái Thanh toán (Có màu sắc phân biệt)
        lbl_st = tk.Label(info_frame, text=f"TRẠNG THÁI: {pay_status.upper()}", 
                          font=("Arial", 11, "bold"), bg="white", fg=status_color)
        lbl_st.pack(anchor="w", pady=(5, 0))

        # TẠO MÃ QR VÉ (Mã QR chứa cả Mã vé + Trạng thái)
        qr_data = f"TICKET:{t.get('ticket_code')}|STATUS:{pay_status}"
        qr = qrcode.make(qr_data)
        qr = qr.resize((120, 120))

        self.qr_photo = ImageTk.PhotoImage(qr)
        tk.Label(self.detail, image=self.qr_photo, bg="white").pack(side="right", padx=20, pady=10)