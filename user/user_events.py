import os
import random
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from bson import ObjectId
import qrcode
from PIL import Image, ImageTk

# Import cấu hình & kết nối Database
from config.ui_config import *
from database.db import db, events, categories


# ==========================================
# 🎪 POPUP XEM CHI TIẾT SỰ KIỆN (BANNER & SLIDE TỈ LỆ CÂN ĐỐI CHUẨN)
# ==========================================
class EventDetailWindow(tk.Toplevel):
    def __init__(self, parent, event_data):
        super().__init__(parent)
        self.event_data = event_data

        self.title(f"Chi tiết sự kiện - {event_data.get('ten_su_kien', 'Sự kiện')}")
        self.geometry("850x750")
        self.minsize(780, 680)
        self.configure(bg="#F4F6F9")

        self.center_window()
        self.transient(parent)
        self.grab_set()

        self.gallery_images = []
        self.current_img_index = 0
        self.current_photo = None
        self.banner_photo = None

        self.init_gallery_data()
        self.create_widgets()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        cx = int((self.winfo_screenwidth() - w) / 2)
        cy = int((self.winfo_screenheight() - h) / 2)
        self.geometry(f"{w}x{h}+{cx}+{cy}")

    def init_gallery_data(self):
        """Lấy danh sách tối đa 4 ảnh cho Album/Slider"""
        raw_list = self.event_data.get("danh_sach_anh", [])
        valid_imgs = [path for path in raw_list if path and os.path.exists(path)]
        self.gallery_images = valid_imgs[:4]

    def create_widgets(self):
        canvas = tk.Canvas(self, bg="#F4F6F9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#F4F6F9")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # 1. BANNER BÌA CHÍNH
        banner_container = tk.Frame(scrollable_frame, bg="white", padx=20, pady=15)
        banner_container.pack(fill="x")

        img_path = self.event_data.get("hinh_anh", "")
        if img_path and os.path.exists(img_path):
            try:
                raw_img = Image.open(img_path)
                raw_img = raw_img.resize((810, 580), Image.Resampling.LANCZOS)
                self.banner_photo = ImageTk.PhotoImage(raw_img)
                
                lbl_banner = tk.Label(banner_container, image=self.banner_photo, bg="white")
                lbl_banner.pack(fill="both", expand=True)
            except Exception:
                self.show_default_banner(banner_container)
        else:
            self.show_default_banner(banner_container)

        # 2. KHỐI THÔNG TIN SỰ KIỆN
        container = tk.Frame(scrollable_frame, bg="#F4F6F9", padx=20, pady=15)
        container.pack(fill="both", expand=True)

        header_card = tk.Frame(container, bg="white", bd=1, relief="solid", padx=20, pady=15)
        header_card.pack(fill="x", pady=(0, 15))

        cat_name = self.event_data.get("category_name", "Sự kiện")
        tk.Label(
            header_card, text=f"  {cat_name.upper()}  ",
            font=("Segoe UI", 9, "bold"), bg="#E0E7FF", fg="#2563EB", pady=2
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            header_card, text=self.event_data.get("ten_su_kien", "Chưa có tên"),
            font=("Segoe UI", 15, "bold"), fg="#1F2937", bg="white", wraplength=730, justify="left"
        ).pack(anchor="w", pady=(0, 10))

        info_grid = tk.Frame(header_card, bg="white")
        info_grid.pack(fill="x", pady=5)

        time_str = self.event_data.get("gio_to_chuc", "19:00")
        date_str = self.event_data.get("ngay_to_chuc", "N/A")
        full_time = f"⏰ {time_str} - {date_str}"

        tk.Label(info_grid, text=f"Thời gian: {full_time}", font=("Segoe UI", 10, "bold"), fg="#2563EB", bg="white").grid(row=0, column=0, sticky="w", pady=3, padx=(0, 30))
        tk.Label(info_grid, text=f"🏢 BTC: {self.event_data.get('ban_to_chuc', 'N/A')}", font=("Segoe UI", 10), fg="#1F2937", bg="white").grid(row=0, column=1, sticky="w", pady=3)

        tk.Label(info_grid, text=f"📍 Địa điểm: {self.event_data.get('dia_diem', 'N/A')}", font=("Segoe UI", 10), fg="#1F2937", bg="white").grid(row=1, column=0, sticky="w", pady=3, padx=(0, 30))

        price = self.event_data.get('gia_ve', 0)
        price_str = f"{price:,.0f} VNĐ" if price > 0 else "MIỄN PHÍ"
        tk.Label(info_grid, text=f"🎟️ Giá vé: {price_str}", font=("Segoe UI", 11, "bold"), fg="#10B981", bg="white").grid(row=1, column=1, sticky="w", pady=3)

        # 3. SLIDER ALBUM 4 ÁNH QUẢNG CÁO
        if self.gallery_images:
            slider_card = tk.Frame(container, bg="white", bd=1, relief="solid", padx=20, pady=15)
            slider_card.pack(fill="x", pady=(0, 15))

            tk.Label(
                slider_card, text=f"🖼️ Hình Ảnh Quảng Cáo ({len(self.gallery_images)} ảnh)",
                font=("Segoe UI", 12, "bold"), fg="#1F2937", bg="white"
            ).pack(anchor="w", pady=(0, 10))

            carousel_frame = tk.Frame(slider_card, bg="#F3F4F6", padx=5, pady=5)
            carousel_frame.pack(fill="x", expand=True)

            self.btn_prev = tk.Button(
                carousel_frame, text="◀", font=("Arial", 13, "bold"),
                bg="#E5E7EB", fg="#1F2937", activebackground="#D1D5DB",
                bd=1, relief="solid", cursor="hand2", padx=8, pady=15, command=self.prev_image
            )
            self.btn_prev.pack(side="left", padx=(0, 5))

            self.slider_img_label = tk.Label(carousel_frame, bg="#F3F4F6")
            self.slider_img_label.pack(side="left", fill="both", expand=True)

            self.btn_next = tk.Button(
                carousel_frame, text="▶", font=("Arial", 13, "bold"),
                bg="#E5E7EB", fg="#1F2937", activebackground="#D1D5DB",
                bd=1, relief="solid", cursor="hand2", padx=8, pady=15, command=self.next_image
            )
            self.btn_next.pack(side="right", padx=(5, 0))

            self.lbl_counter = tk.Label(slider_card, text="", font=("Segoe UI", 9, "bold"), fg="#6B7280", bg="white")
            self.lbl_counter.pack(anchor="center", pady=(8, 0))

            self.update_slider_image()

        # 4. MÔ TẢ CHI TIẾT SỰ KIỆN
        desc_card = tk.Frame(container, bg="white", bd=1, relief="solid", padx=20, pady=15)
        desc_card.pack(fill="both", expand=True, pady=(0, 15))

        tk.Label(
            desc_card, text="📌 Giới thiệu & Mô tả chi tiết nội dung sự kiện",
            font=("Segoe UI", 12, "bold"), fg="#1F2937", bg="white"
        ).pack(anchor="w", pady=(0, 8))

        ttk.Separator(desc_card, orient="horizontal").pack(fill="x", pady=(0, 10))

        full_desc = self.event_data.get("mo_ta", "Chưa có bài giới thiệu chi tiết.")
        desc_text = tk.Text(
            desc_card, font=("Segoe UI", 10), fg="#1F2937", bg="white",
            wrap="word", relief="flat", highlightthickness=0, height=8
        )
        desc_text.insert("1.0", full_desc)
        desc_text.configure(state="disabled")
        desc_text.pack(fill="both", expand=True)

    def show_default_banner(self, parent):
        lbl = tk.Label(
            parent, text="🎪 BANNER SỰ KIỆN",
            font=("Segoe UI", 16, "bold"), fg="#9CA3AF", bg="#374151", height=7
        )
        lbl.pack(fill="both", expand=True)

    def update_slider_image(self):
        if not self.gallery_images:
            return

        img_path = self.gallery_images[self.current_img_index]
        try:
            raw_img = Image.open(img_path)
            raw_img = raw_img.resize((680, 480), Image.Resampling.LANCZOS)
            self.current_photo = ImageTk.PhotoImage(raw_img)

            self.slider_img_label.config(image=self.current_photo)
            self.lbl_counter.config(text=f"Ảnh {self.current_img_index + 1} / {len(self.gallery_images)}")
        except Exception:
            self.slider_img_label.config(text="⚠️ Lỗi hiển thị ảnh", fg="red")

    def prev_image(self):
        if self.gallery_images:
            self.current_img_index = (self.current_img_index - 1) % len(self.gallery_images)
            self.update_slider_image()

    def next_image(self):
        if self.gallery_images:
            self.current_img_index = (self.current_img_index + 1) % len(self.gallery_images)
            self.update_slider_image()


# ==========================================
# 💳 POPUP THANH TOÁN
# ==========================================
class PaymentWindow(tk.Toplevel):
    def __init__(self, parent, event_name, amount, qty, on_success_callback):
        super().__init__(parent)
        self.title("Chọn phương thức thanh toán")
        self.configure(bg="white")
        self.resizable(False, False)

        self.amount = amount
        self.qty = qty
        self.event_name = event_name
        self.on_success_callback = on_success_callback
        self.payment_method = tk.StringVar(value="QR")

        w, h = 450, 580
        cx = int((self.winfo_screenwidth() - w) / 2)
        cy = int((self.winfo_screenheight() - h) / 2)
        self.geometry(f"{w}x{h}+{cx}+{cy}")

        self.transient(parent)
        self.grab_set()

        tk.Label(self, text="💳 XÁC NHẬN THANH TOÁN VÉ", font=("Arial", 13, "bold"), bg="white", fg="#1e88e5").pack(pady=(15, 5))
        tk.Label(self, text=f"Sự kiện: {event_name}", font=("Arial", 10, "bold"), bg="white", fg="#2c3e50").pack()
        tk.Label(self, text=f"Số lượng: {qty} vé | Tổng tiền: {amount:,.0f} VNĐ", font=("Arial", 11, "bold"), bg="white", fg="#e67e22").pack(pady=5)

        method_frame = tk.LabelFrame(self, text=" Chọn hình thức thanh toán ", bg="white", font=("Arial", 10, "bold"), fg="#34495e")
        method_frame.pack(fill="x", padx=20, pady=10)

        tk.Radiobutton(method_frame, text="📲 Chuyển khoản QR Code (Online)", variable=self.payment_method, value="QR", bg="white", font=("Arial", 10), command=self.toggle_method).pack(anchor="w", padx=10, pady=3)
        tk.Radiobutton(method_frame, text="💵 Thanh toán trực tiếp / Tiền mặt (Tại quầy)", variable=self.payment_method, value="CASH", bg="white", font=("Arial", 10), command=self.toggle_method).pack(anchor="w", padx=10, pady=3)

        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=5)

        btn_confirm = tk.Button(self, text="✔️ Xác nhận đặt vé", bg=SUCCESS, fg="white", font=("Arial", 11, "bold"), padx=15, pady=8, cursor="hand2", command=self.confirm_payment)
        btn_confirm.pack(pady=15)

        self.toggle_method()

    def toggle_method(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        method = self.payment_method.get()
        if method == "QR":
            payment_info = f"STK: 0999999999 | MBBank\nNoi dung: TT {self.qty} VE {self.event_name}\nSo tien: {int(self.amount)} VND"
            qr_img = qrcode.make(payment_info).resize((190, 190))
            self.qr_photo = ImageTk.PhotoImage(qr_img, master=self)

            lbl_qr = tk.Label(self.content_frame, image=self.qr_photo, bg="white", bd=1, relief="solid")
            lbl_qr.pack(pady=5)
            tk.Label(self.content_frame, text="Dùng App Ngân hàng hoặc MoMo quét mã để thanh toán", font=("Arial", 9, "italic"), bg="white", fg="gray").pack()
        else:
            box = tk.Frame(self.content_frame, bg="#f8f9fa", bd=1, relief="solid", padx=15, pady=15)
            box.pack(fill="both", expand=True, pady=10)

            tk.Label(box, text="📌 HƯỚNG DẪN THANH TOÁN TRỰC TIẾP", font=("Arial", 10, "bold"), bg="#f8f9fa", fg="#c0392b").pack(anchor="w", pady=(0, 5))
            guide_text = f"1. Mã vé của bạn sẽ được khởi tạo ngay sau khi bấm Xác nhận.\n\n2. Bạn vui lòng di chuyển đến Quầy vé (Box Office) tại địa điểm diễn ra sự kiện.\n\n3. Cung cấp Mã vé/Mã QR cho nhân viên và thanh toán số tiền {self.amount:,.0f} VNĐ bằng tiền mặt để nhận vé vào cổng."
            tk.Label(box, text=guide_text, font=("Arial", 9), bg="#f8f9fa", justify="left", wraplength=350).pack(anchor="w")

    def confirm_payment(self):
        method_selected = self.payment_method.get()
        self.destroy()
        if self.on_success_callback:
            self.on_success_callback(method_selected)


# ==========================================
# 🎉 GIAO DIỆN KHÁM PHÁ SỰ KIỆN DÀNH CHO USER (CÓ THANH TÌM KIẾM & LỌC)
# ==========================================
class UserEventFrame(tk.Frame):
    def __init__(self, parent, username=None):
        super().__init__(parent, bg=BG_COLOR)

        self.username = username
        self.selected_id = None
        self.img_ref = None
        self.category_map = {}  # Lưu dictionary {tên_danh_mục: id_danh_mục}

        tk.Label(self, text="🎉 Khám phá sự kiện", font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg="#1F2937").pack(pady=(10, 5))

        # 🔍 1. KHUNG TÌM KIẾM VÀ LỌC SỰ KIỆN
        search_frame = tk.Frame(self, bg="white", bd=1, relief="solid", padx=15, pady=10)
        search_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Tìm theo từ khóa
        tk.Label(search_frame, text="🔍 Tìm kiếm:", font=("Segoe UI", 10, "bold"), bg="white", fg="#374151").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25, font=("Segoe UI", 10))
        self.search_entry.pack(side="left", padx=(0, 15))
        # Bấm Enter để tìm kiếm luôn
        self.search_entry.bind("<Return>", lambda e: self.load_events())

        # Lọc theo thể loại
        tk.Label(search_frame, text="🏷️ Thể loại:", font=("Segoe UI", 10, "bold"), bg="white", fg="#374151").pack(side="left", padx=(0, 5))
        self.cat_filter_var = tk.StringVar(value="Tất cả")
        self.cat_combobox = ttk.Combobox(search_frame, textvariable=self.cat_filter_var, state="readonly", width=18, font=("Segoe UI", 10))
        self.cat_combobox.pack(side="left", padx=(0, 15))
        self.cat_combobox.bind("<<ComboboxSelected>>", lambda e: self.load_events())

        # Nút bấm Tìm kiếm & Làm mới
        tk.Button(search_frame, text="🔎 Tìm", bg=PRIMARY, fg="white", font=("Segoe UI", 9, "bold"), padx=12, pady=3, cursor="hand2", command=self.load_events).pack(side="left", padx=3)
        tk.Button(search_frame, text="🔄 Làm mới", bg="#6B7280", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=3, cursor="hand2", command=self.reset_filter).pack(side="left", padx=3)

        # ------------------------------------------
        main = tk.Frame(self, bg=BG_COLOR)
        main.pack(fill="both", expand=True, padx=20, pady=5)

        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=2)
        main.grid_rowconfigure(0, weight=1)

        # TABLE BÊN TRÁI
        table_frame = tk.Frame(main, bg="white", bd=1, relief="solid")
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.tree = ttk.Treeview(table_frame, columns=("name", "date_time", "category", "organizer"), show="headings")
        self.tree.heading("name", text="TÊN SỰ KIỆN", anchor="w")
        self.tree.heading("date_time", text="THỜI GIAN", anchor="w")
        self.tree.heading("category", text="THỂ LOẠI", anchor="w")
        self.tree.heading("organizer", text="BTC", anchor="w")

        self.tree.column("name", width=180, anchor="w")
        self.tree.column("date_time", width=120, anchor="w")
        self.tree.column("category", width=90, anchor="w")
        self.tree.column("organizer", width=90, anchor="w")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.open_detail)

        # KHUNG PREVIEW BÊN PHẢI
        right = tk.Frame(main, bg="white", bd=1, relief="solid", padx=15, pady=15)
        right.grid(row=0, column=1, sticky="nsew")

        self.img_frame = tk.Frame(right, bg="white", height=170)
        self.img_frame.pack(fill="x", pady=(0, 10))
        self.img_frame.pack_propagate(False)

        self.img_label = tk.Label(self.img_frame, bg="white")
        self.img_label.pack(fill="both", expand=True)

        btn_frame = tk.Frame(right, bg="white")
        btn_frame.pack(side="bottom", fill="x", pady=(10, 0))

        tk.Button(btn_frame, text="🎟 Mua vé ngay", bg=SUCCESS, fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=5, command=self.buy_ticket).pack(side="left", padx=2, expand=True, fill="x")
        tk.Button(btn_frame, text="📍 Bản đồ", bg=PRIMARY, fg="white", font=("Segoe UI", 10, "bold"), padx=8, pady=5, command=self.open_map).pack(side="left", padx=2)
        tk.Button(btn_frame, text="🔎 Chi tiết", bg="#374151", fg="white", font=("Segoe UI", 10, "bold"), padx=8, pady=5, command=self.open_detail).pack(side="left", padx=2)

        self.detail_box = tk.Text(right, bg="white", wrap="word", font=("Segoe UI", 10), relief="flat", highlightthickness=0, height=8)
        self.detail_box.pack(fill="both", expand=True, pady=5)

        # Khởi tạo dữ liệu danh mục & nạp bảng sự kiện
        self.load_categories()
        self.load_events()

    def load_categories(self):
        """Tải danh sách danh mục vào Combobox lọc"""
        self.category_map = {"Tất cả": None}
        cat_list = ["Tất cả"]
        for cat in categories.find():
            c_name = cat.get("name", "")
            if c_name:
                cat_list.append(c_name)
                self.category_map[c_name] = str(cat["_id"])
        self.cat_combobox["values"] = cat_list

    def reset_filter(self):
        """Đặt lại điều kiện tìm kiếm ban đầu"""
        self.search_var.set("")
        self.cat_filter_var.set("Tất cả")
        self.load_events()

    def get_organizer_name(self, ev):
        name = ev.get("organizer_name")
        if name and name != ev.get("organizer"):
            return name
        user = db["users"].find_one({"username": ev.get("organizer")})
        if user:
            return user.get("full_name", ev.get("organizer"))
        return ev.get("organizer")

    def get_remaining(self, event_id):
        ev = events.find_one({"_id": ObjectId(event_id)})
        if not ev:
            return 0
        total = ev.get("total_tickets", 0)
        sold = db["user_tickets"].count_documents({"event_id": str(event_id)})
        return max(total - sold, 0)

    def load_events(self):
        """Nạp danh sách sự kiện kết hợp Tìm kiếm tên & Lọc danh mục"""
        self.tree.delete(*self.tree.get_children())
        self.detail_box.delete("1.0", tk.END)
        self.img_label.config(image="", text="")
        self.selected_id = None

        # Build truy vấn MongoDB
        query = {"status": "approved"}

        # 1. Lọc theo từ khóa (Không phân biệt hoa thường)
        keyword = self.search_var.get().strip()
        if keyword:
            query["name"] = {"$regex": keyword, "$options": "i"}

        # 2. Lọc theo danh mục
        selected_cat = self.cat_filter_var.get()
        if selected_cat != "Tất cả" and selected_cat in self.category_map:
            cat_id = self.category_map[selected_cat]
            if cat_id:
                query["category_id"] = cat_id

        # Truy vấn dữ liệu
        for e in events.find(query):
            cat_name = "N/A"
            if e.get("category_id"):
                cat = categories.find_one({"_id": ObjectId(e["category_id"])})
                if cat:
                    cat_name = cat["name"]

            date_time_str = f"{e.get('time', '19:00')} {e.get('date', 'N/A')}"
            self.tree.insert("", "end", iid=str(e["_id"]), values=(e.get("name"), date_time_str, cat_name, self.get_organizer_name(e)))

    def on_select(self, e):
        sel = self.tree.selection()
        if not sel:
            return

        self.selected_id = sel[0]
        ev = events.find_one({"_id": ObjectId(self.selected_id)})

        organizer_name = self.get_organizer_name(ev)
        remain = self.get_remaining(self.selected_id)

        short_desc = ev.get("mo_ta_ngan", "")
        if not short_desc:
            full = ev.get("description", "")
            short_desc = full[:110] + "..." if len(full) > 110 else full

        date_time_str = f"{ev.get('time', '19:00')} - {ev.get('date', 'N/A')}"

        detail = f"""🎫 {ev.get('name')}

⏰ {date_time_str}
📍 {ev.get('location')} ({ev.get('address', '')})
👤 BTC: {organizer_name}

💵 Giá vé: {ev.get('price',0):,} VNĐ
🎟 Vé còn lại: {remain}

💡 Tóm tắt ngắn:
{short_desc}
"""
        self.detail_box.delete("1.0", tk.END)
        self.detail_box.insert(tk.END, detail)

        try:
            if ev.get("image") and os.path.exists(ev["image"]):
                img = Image.open(ev["image"]).resize((300, 170), Image.Resampling.LANCZOS)
                self.img_ref = ImageTk.PhotoImage(img)
                self.img_label.config(image=self.img_ref, text="")
            else:
                self.img_label.config(image="", text="")
        except Exception:
            self.img_label.config(image="", text="")

    def open_detail(self, event=None):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Thông báo", "Vui lòng chọn sự kiện để xem chi tiết!")
            return

        ev = events.find_one({"_id": ObjectId(sel[0])})
        if not ev:
            return

        cat_name = "N/A"
        if ev.get("category_id"):
            cat = categories.find_one({"_id": ObjectId(ev["category_id"])})
            if cat:
                cat_name = cat.get("name", "N/A")

        detail_data = {
            "ten_su_kien": ev.get("name", "N/A"),
            "category_name": cat_name,
            "ngay_to_chuc": ev.get("date", "N/A"),
            "gio_to_chuc": ev.get("time", "19:00"),
            "dia_diem": ev.get("location", "N/A"),
            "ban_to_chuc": self.get_organizer_name(ev),
            "gia_ve": ev.get("price", 0),
            "hinh_anh": ev.get("image", ""),
            "danh_sach_anh": ev.get("danh_sach_anh", []),
            "mo_ta": ev.get("description", "Chưa có bài giới thiệu chi tiết.")
        }

        EventDetailWindow(self, detail_data)

    def buy_ticket(self):
        if not self.selected_id:
            messagebox.showwarning("Lỗi", "Hãy chọn sự kiện muốn mua vé!")
            return

        ev = events.find_one({"_id": ObjectId(self.selected_id)})
        price = ev.get("price", 0)
        remain = self.get_remaining(self.selected_id)

        if remain <= 0:
            messagebox.showerror("Hết vé", "Sự kiện này đã hết vé!")
            return

        qty = simpledialog.askinteger(
            "Mua vé",
            f"💵 Giá: {price:,} đ\n🎟 Vé còn: {remain}\n\nNhập số lượng vé muốn mua:",
            minvalue=1, maxvalue=remain
        )

        if not qty:
            return

        total = price * qty

        def execute_ticket_creation(payment_method):
            payment_status = "Đã thanh toán" if payment_method == "QR" else "Chờ thanh toán tại quầy"

            for _ in range(qty):
                code = f"TK{random.randint(100000, 999999)}"
                db["user_tickets"].insert_one({
                    "username": self.username,
                    "event_id": str(ev["_id"]),
                    "event_name": ev.get("name"),
                    "date": ev.get("date"),
                    "time": ev.get("time", "19:00"),
                    "location": ev.get("location"),
                    "price": price,
                    "ticket_code": code,
                    "payment_method": "Chuyển khoản QR" if payment_method == "QR" else "Tiền mặt tại quầy",
                    "payment_status": payment_status,
                    "purchase_date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                })

            msg = f"🎉 Bạn đã mua thành công {qty} vé!" if payment_method == "QR" else f"🎟 Đã đặt thành công {qty} vé!\nVui lòng thanh toán tại quầy khi nhận vé."
            messagebox.showinfo("Thành công", msg)
            self.on_select(None)

        PaymentWindow(
            parent=self,
            event_name=ev.get("name", "Sự kiện"),
            amount=total,
            qty=qty,
            on_success_callback=execute_ticket_creation
        )

    def open_map(self):
        if not self.selected_id:
            messagebox.showwarning("Thông báo", "Vui lòng chọn sự kiện!")
            return

        ev = events.find_one({"_id": ObjectId(self.selected_id)})
        if ev and ev.get("map_link"):
            webbrowser.open(ev["map_link"])
        else:
            messagebox.showinfo("Thông báo", "Sự kiện này chưa cập nhật liên kết bản đồ.")