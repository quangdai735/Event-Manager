import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from bson import ObjectId
from config.constants import PROVINCES
from config.ui_config import *
from database.db import categories, events, tickets, db
from PIL import Image, ImageTk
from tkcalendar import DateEntry


class OrganizerEventsFrame(tk.Frame):

    def __init__(self, parent, username):
        super().__init__(parent, bg=BG_COLOR)

        self.username = username
        self.selected_id = None
        self.category_map = {}
        
        # Quản lý đường dẫn ảnh
        self.image_path = ""
        self.gallery_paths = []
        
        self.image_preview_ref = None
        self.album_thumbs_ref = []

        # ===== VARIABLES =====
        self.name_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.total_var = tk.StringVar()
        self.short_desc_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.org_name_var = tk.StringVar()
        self.time_var = tk.StringVar(value="19:00")

        # Lấy tên BTC thực tế từ Hồ sơ cá nhân trong MongoDB
        self.load_organizer_profile_name()

        # TITLE
        tk.Label(
            self, text="🎫 Sự kiện của tôi", 
            font=("Segoe UI", 15, "bold"), bg=BG_COLOR, fg="#1F2937"
        ).pack(pady=(6, 2))

        # ==============================================================================
        # 🟢 MAIN CONTENT (Sắp xếp lại layout Cân đối 2 Cột Trái / Phải)
        # ==============================================================================
        self.main_content = tk.Frame(self, bg=BG_COLOR)
        self.main_content.pack(fill="x", padx=15, pady=2)

        self.main_content.columnconfigure(0, weight=3) # Cột Form trái
        self.main_content.columnconfigure(1, weight=2) # Cột Ảnh phải

        # ------------------------------------------------------------------
        # ⬅️ CỘT TRÁI: Form nhập liệu
        # ------------------------------------------------------------------
        self.left_panel = tk.Frame(self.main_content, bg="white", bd=1, relief="solid", padx=12, pady=8)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        form = tk.Frame(self.left_panel, bg="white")
        form.pack(fill="both", expand=True)

        # Giúp các ô nhập liệu giãn đều hết chiều ngang
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=1)
        form.columnconfigure(3, weight=1)

        # ===== ROW 0, 1 =====
        labels_r0 = ["Tên sự kiện", "Ngày tổ chức", "Giờ bắt đầu", "Thể loại"]
        for i, t in enumerate(labels_r0):
            tk.Label(form, text=t, bg="white", font=("Segoe UI", 9, "bold")).grid(row=0, column=i, padx=4, pady=(0, 2), sticky="w")

        tk.Entry(form, textvariable=self.name_var, font=("Segoe UI", 9)).grid(row=1, column=0, padx=4, pady=(0, 4), sticky="ew")

        self.date_picker = DateEntry(form, date_pattern="dd-mm-yyyy", background='darkblue', foreground='white')
        self.date_picker.grid(row=1, column=1, padx=4, pady=(0, 4), sticky="ew")

        time_list = [f"{h:02d}:{m:02d}" for h in range(7, 23) for m in (0, 30)]
        self.combo_time = ttk.Combobox(form, values=time_list, textvariable=self.time_var, state="readonly", font=("Segoe UI", 9))
        self.combo_time.grid(row=1, column=2, padx=4, pady=(0, 4), sticky="ew")

        self.combo_category = ttk.Combobox(form, state="readonly", font=("Segoe UI", 9))
        self.combo_category.grid(row=1, column=3, padx=4, pady=(0, 4), sticky="ew")

        # ===== ROW 2, 3 =====
        labels_r2 = ["Địa điểm (Tỉnh/Thành)", "Giá vé (VNĐ)", "Số lượng vé", "Tên BTC (Tự động)"]
        for i, t in enumerate(labels_r2):
            tk.Label(form, text=t, bg="white", font=("Segoe UI", 9, "bold")).grid(row=2, column=i, padx=4, pady=(0, 2), sticky="w")

        self.combo_location = ttk.Combobox(form, values=PROVINCES[1:], state="readonly", font=("Segoe UI", 9))
        self.combo_location.grid(row=3, column=0, padx=4, pady=(0, 4), sticky="ew")

        tk.Entry(form, textvariable=self.price_var, font=("Segoe UI", 9)).grid(row=3, column=1, padx=4, pady=(0, 4), sticky="ew")
        tk.Entry(form, textvariable=self.total_var, font=("Segoe UI", 9)).grid(row=3, column=2, padx=4, pady=(0, 4), sticky="ew")
        
        # 🔥 KHÓA KHÔNG CHO KHÁCH BẤM SỬA TÊN BTC TRỰC TIẾP
        self.entry_org = tk.Entry(form, textvariable=self.org_name_var, state="readonly", bg="#F3F4F6", font=("Segoe UI", 9))
        self.entry_org.grid(row=3, column=3, padx=4, pady=(0, 4), sticky="ew")

        # ===== ROW 4, 5 =====
        tk.Label(form, text="Địa chỉ chi tiết (🏠 Tên địa điểm, số nhà...)", bg="white", font=("Segoe UI", 9, "bold")).grid(row=4, column=0, columnspan=2, padx=4, pady=(0, 2), sticky="w")
        tk.Label(form, text="Mô tả ngắn (1 câu giới thiệu nhanh)", bg="white", font=("Segoe UI", 9, "bold")).grid(row=4, column=2, columnspan=2, padx=4, pady=(0, 2), sticky="w")

        tk.Entry(form, textvariable=self.address_var, font=("Segoe UI", 9)).grid(row=5, column=0, columnspan=2, padx=4, pady=(0, 4), sticky="ew")
        tk.Entry(form, textvariable=self.short_desc_var, font=("Segoe UI", 9)).grid(row=5, column=2, columnspan=2, padx=4, pady=(0, 4), sticky="ew")

        # ===== ROW 6, 7, 8 =====
        ttk.Separator(form, orient="horizontal").grid(row=6, column=0, columnspan=4, sticky="ew", pady=(2, 4))
        tk.Label(form, text="📌 Giới thiệu & Mô tả chi tiết nội dung sự kiện", bg="white", font=("Segoe UI", 9, "bold"), fg=PRIMARY).grid(row=7, column=0, columnspan=4, padx=4, pady=(0, 2), sticky="w")
        
        self.full_desc_text = tk.Text(form, height=3, font=("Segoe UI", 9), wrap="word", bd=1, relief="solid")
        self.full_desc_text.grid(row=8, column=0, columnspan=4, padx=4, pady=(0, 4), sticky="ew")

        # ===== BUTTONS CRUD =====
        btn_action_frame = tk.Frame(self.left_panel, bg="white")
        btn_action_frame.pack(fill="x", pady=(4, 0))

        tk.Button(btn_action_frame, text="+ Tạo Sự kiện", bg=SUCCESS, fg="white", font=("Segoe UI", 9, "bold"), padx=8, pady=3, cursor="hand2", command=self.add_event).pack(side="left", padx=2)
        tk.Button(btn_action_frame, text="✏ Cập nhật", bg=PRIMARY, fg="white", font=("Segoe UI", 9, "bold"), padx=8, pady=3, cursor="hand2", command=self.update_event).pack(side="left", padx=2)
        tk.Button(btn_action_frame, text="🗑 Xóa", bg=DANGER, fg="white", font=("Segoe UI", 9, "bold"), padx=8, pady=3, cursor="hand2", command=self.delete_event).pack(side="left", padx=2)
        tk.Button(btn_action_frame, text="🧹 Nhập lại", bg="#6B7280", fg="white", font=("Segoe UI", 9, "bold"), padx=8, pady=3, cursor="hand2", command=self.clear_form).pack(side="left", padx=2)

        # ------------------------------------------------------------------
        # ➡️ CỘT PHẢI: Khu vực Quản lý Ảnh (Gọn gàng vừa khít)
        # ------------------------------------------------------------------
        self.right_panel = tk.Frame(self.main_content, bg="white", bd=1, relief="solid", padx=10, pady=8)
        self.right_panel.grid(row=0, column=1, sticky="nsew")

        tk.Label(self.right_panel, text="🖼️ Quản lý Hình Ảnh", font=("Segoe UI", 9, "bold"), bg="white", fg="#1F2937").pack(pady=(0, 2), anchor="w")

        self.banner_preview_frame = tk.Frame(self.right_panel, bg="#E5E7EB", height=115, bd=1, relief="solid")
        self.banner_preview_frame.pack(fill="x", pady=(0, 4))
        self.banner_preview_frame.pack_propagate(False)

        self.img_label = tk.Label(self.banner_preview_frame, text="🎪 BANNER PREVIEW", bg="#E5E7EB", fg="#9CA3AF", font=("Segoe UI", 9, "bold"))
        self.img_label.pack(fill="both", expand=True)

        img_btn_frame = tk.Frame(self.right_panel, bg="white")
        img_btn_frame.pack(fill="x", pady=(0, 4))
        
        tk.Button(img_btn_frame, text="📷 Chọn Ảnh bìa Banner", font=("Segoe UI", 8, "bold"), bg="#F3F4F6", cursor="hand2", command=self.choose_image).pack(fill="x")

        ttk.Separator(self.right_panel, orient="horizontal").pack(fill="x", pady=4)
        
        tk.Label(self.right_panel, text="Album Ảnh quảng cáo (Tối đa 4 ảnh)", font=("Segoe UI", 8, "bold"), bg="white").pack(anchor="w", pady=(0, 2))

        album_btn_frame = tk.Frame(self.right_panel, bg="white")
        album_btn_frame.pack(fill="x", pady=2)
        tk.Button(album_btn_frame, text="+ Thêm Album", font=("Segoe UI", 8), bg="#F3F4F6", cursor="hand2", command=self.choose_gallery_images).pack(side="left", padx=2, expand=True, fill="x")
        tk.Button(album_btn_frame, text="❌ Xóa Album", font=("Segoe UI", 8), bg="#F3F4F6", fg="red", cursor="hand2", command=self.clear_gallery).pack(side="left", padx=2, expand=True, fill="x")

        self.album_thumbs_frame = tk.Frame(self.right_panel, bg="white")
        self.album_thumbs_frame.pack(pady=2)

        self.lbl_gallery_info = tk.Label(self.right_panel, text="Album: 0/4 ảnh đã chọn", font=("Segoe UI", 8, "italic"), bg="white", fg="#6B7280")
        self.lbl_gallery_info.pack()

        # ==============================================================================
        # 📋 TABLE TREEVIEW
        # ==============================================================================
        table_container = tk.Frame(self, bg="white", bd=1, relief="solid")
        table_container.pack(fill="both", expand=True, padx=15, pady=(4, 6))

        tk.Label(table_container, text="📋 Danh sách Sự kiện tôi đã đăng ký", font=("Segoe UI", 9, "bold"), bg="#EFF6FF", fg=PRIMARY, padx=8, pady=3).pack(fill="x")

        tree_scroll_frame = tk.Frame(table_container, bg="white")
        tree_scroll_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_scroll_frame,
            columns=("name", "date_time", "location", "category", "status"),
            show="headings",
            height=5
        )

        tree_scrollbar = ttk.Scrollbar(tree_scroll_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        headings = [("name", "TÊN SỰ KIỆN", 200), ("date_time", "NGÀY & GIỜ", 130), ("location", "ĐỊA ĐIỂM", 110), ("category", "THỂ LOẠI", 100), ("status", "TRẠNG THÁI", 100)]
        for col, text, width in headings:
            self.tree.heading(col, text=text, anchor="w")
            self.tree.column(col, width=width, anchor="w")

        self.tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load_categories()
        self.load_events()

    # 🔥 HÀM TỰ ĐỘNG CẬP NHẬT TÊN BTC TỪ COLLECTION USERS
    def load_organizer_profile_name(self):
        user = db["users"].find_one({"username": self.username})
        if user and user.get("full_name"):
            self.org_name_var.set(user.get("full_name"))
        else:
            self.org_name_var.set(self.username)

    def show_preview(self, path):
        if path and os.path.exists(path):
            try:
                raw_img = Image.open(path)
                w = self.banner_preview_frame.winfo_width() or 240
                h = self.banner_preview_frame.winfo_height() or 115
                raw_img = raw_img.resize((w, h), Image.Resampling.LANCZOS)
                self.image_preview_ref = ImageTk.PhotoImage(raw_img)
                self.img_label.config(image=self.image_preview_ref, text="", bd=0)
            except Exception:
                self.show_default_img_label()
        else:
            self.show_default_img_label()

    def show_default_img_label(self):
        self.image_preview_ref = None
        self.img_label.config(image="", text="🎪 BANNER PREVIEW", bg="#E5E7EB", fg="#9CA3AF", bd=0)

    def choose_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")])
        if path:
            self.image_path = path
            self.show_preview(path)

    def choose_gallery_images(self):
        current_count = len(self.gallery_paths)
        if current_count >= 4:
            messagebox.showwarning("Thông báo", "Album đã đủ tối đa 4 ảnh!")
            return

        remain_slots = 4 - current_count
        files = filedialog.askopenfilenames(
            title=f"Chọn thêm tối đa {remain_slots} ảnh quảng cáo",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")]
        )
        if files:
            for f in list(files):
                if f not in self.gallery_paths and len(self.gallery_paths) < 4:
                    self.gallery_paths.append(f)
            self.update_album_thumbnails()

    def clear_gallery(self):
        self.gallery_paths = []
        self.update_album_thumbnails()

    def update_album_thumbnails(self):
        for widget in self.album_thumbs_frame.winfo_children():
            widget.destroy()
        
        self.album_thumbs_ref = []
        if not self.gallery_paths:
            self.lbl_gallery_info.config(text="Album: 0/4 ảnh đã chọn", fg="#6B7280")
            return

        count = 0
        valid_paths = []
        for img_p in self.gallery_paths[:4]:
            if os.path.exists(img_p):
                valid_paths.append(img_p)
                try:
                    g_img = Image.open(img_p).resize((45, 30), Image.Resampling.LANCZOS)
                    g_photo = ImageTk.PhotoImage(g_img)
                    self.album_thumbs_ref.append(g_photo)

                    lbl_g = tk.Label(self.album_thumbs_frame, image=g_photo, bg="white", bd=1, relief="solid")
                    lbl_g.pack(side="left", padx=2)
                    count += 1
                except Exception:
                    pass
        
        self.gallery_paths = valid_paths
        if count > 0:
            self.lbl_gallery_info.config(text=f"Album: Đã chọn {count}/4 ảnh thành công", fg="#16A34A")
        else:
            self.lbl_gallery_info.config(text="Album: 0/4 ảnh (File lỗi)", fg="#DC2626")

    def load_categories(self):
        self.category_map.clear()
        values = []
        for c in categories.find():
            self.category_map[c["name"]] = str(c["_id"])
            values.append(c["name"])
        self.combo_category["values"] = values

    def load_events(self):
        self.tree.delete(*self.tree.get_children())
        self.load_organizer_profile_name() # Luôn làm mới tên BTC khi load
        
        for e in events.find({"organizer": self.username}):
            cat = categories.find_one({"_id": ObjectId(e.get("category_id"))}) if e.get("category_id") else None
            cat_name = cat["name"] if cat else "N/A"
            date_time_str = f"{e.get('time', '19:00')} {e.get('date', 'N/A')}"

            self.tree.insert(
                "", "end", iid=str(e["_id"]),
                values=(e.get("name"), date_time_str, e.get("location"), cat_name, e.get("status"))
            )

    def validate_required_fields(self):
        required = [
            (self.name_var.get().strip(), "Tên sự kiện"),
            (self.date_picker.get().strip(), "Ngày tổ chức"),
            (self.time_var.get().strip(), "Giờ bắt đầu"),
            (self.combo_category.get().strip(), "Thể loại"),
            (self.combo_location.get().strip(), "Địa điểm (Tỉnh/Thành)"),
            (self.price_var.get().strip(), "Giá vé (VNĐ)"),
            (self.total_var.get().strip(), "Số lượng vé"),
            (self.address_var.get().strip(), "Địa chỉ chi tiết"),
            (self.short_desc_var.get().strip(), "Mô tả ngắn"),
            (self.full_desc_text.get("1.0", tk.END).strip(), "Giới thiệu & Mô tả chi tiết"),
            (self.image_path, "Ảnh bìa Banner"),
        ]

        for value, field_name in required:
            if not value:
                messagebox.showwarning("Lỗi", f"Vui lòng nhập đầy đủ thông tin!\nThiếu: {field_name}")
                return False

        try:
            if int(self.price_var.get()) == 0 or int(self.total_var.get()) <= 0:
                messagebox.showwarning("Lỗi", "Giá vé và Số lượng vé phải lớn hơn 0!")
                return False
        except ValueError:
            messagebox.showwarning("Lỗi", "Giá vé / Số lượng vé không hợp lệ!")
            return False

        return True

    def add_event(self):
        if not self.validate_required_fields():
            return

        self.load_organizer_profile_name()

        events.insert_one({
            "name": self.name_var.get(),
            "date": self.date_picker.get(),
            "time": self.time_var.get(),
            "location": self.combo_location.get(),
            "address": self.address_var.get(),
            "map_link": f"https://www.google.com/maps/search/{self.address_var.get()}",
            "category_id": self.category_map.get(self.combo_category.get()),
            "price": int(self.price_var.get() or 0),
            "total_tickets": int(self.total_var.get() or 0),
            "mo_ta_ngan": self.short_desc_var.get(),
            "description": self.full_desc_text.get("1.0", tk.END).strip(),
            "image": self.image_path,
            "danh_sach_anh": self.gallery_paths[:4],
            "organizer": self.username,
            "organizer_name": self.org_name_var.get(), # Lấy chính xác tên BTC
            "status": "pending",
        })

        messagebox.showinfo("Thành công", "Tạo sự kiện thành công! Sự kiện đang chờ Admin phê duyệt.")
        self.clear_form()
        self.load_events()

    def update_event(self):
        if not self.selected_id:
            messagebox.showwarning("Lỗi", "Hãy chọn một sự kiện trong bảng để sửa!")
            return

        self.load_organizer_profile_name()

        update_data = {
            "name": self.name_var.get(),
            "date": self.date_picker.get(),
            "time": self.time_var.get(),
            "location": self.combo_location.get(),
            "address": self.address_var.get(),
            "map_link": f"https://www.google.com/maps/search/{self.address_var.get()}",
            "category_id": self.category_map.get(self.combo_category.get()),
            "price": int(self.price_var.get() or 0),
            "total_tickets": int(self.total_var.get() or 0),
            "mo_ta_ngan": self.short_desc_var.get(),
            "description": self.full_desc_text.get("1.0", tk.END).strip(),
            "image": self.image_path,
            "danh_sach_anh": self.gallery_paths[:4],
            "organizer_name": self.org_name_var.get(), # Đồng bộ tên BTC mới nhất
        }

        events.update_one({"_id": ObjectId(self.selected_id)}, {"$set": update_data})
        messagebox.showinfo("Thành công", "Đã cập nhật sự kiện thành công!")
        self.clear_form()
        self.load_events()

    def delete_event(self):
        if not self.selected_id:
            messagebox.showwarning("Lỗi", "Hãy chọn một sự kiện để xóa!")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa sự kiện này?"):
            tickets.delete_many({"event_id": self.selected_id})
            events.delete_one({"_id": ObjectId(self.selected_id)})
            messagebox.showinfo("Thành công", "Đã xóa sự kiện!")
            self.clear_form()
            self.load_events()

    def on_select(self, e):
        sel = self.tree.selection()
        if not sel:
            return

        self.selected_id = sel[0]
        ev = events.find_one({"_id": ObjectId(self.selected_id)})
        if not ev:
            return

        self.name_var.set(ev.get("name", ""))
        self.time_var.set(ev.get("time", "19:00"))
        self.combo_location.set(ev.get("location", ""))
        self.address_var.set(ev.get("address", ""))
        
        # Luôn load tên BTC chuẩn nhất từ DB Hồ sơ
        self.load_organizer_profile_name()
        
        self.short_desc_var.set(ev.get("mo_ta_ngan", ""))

        self.full_desc_text.delete("1.0", tk.END)
        self.full_desc_text.insert("1.0", ev.get("description", ""))

        self.price_var.set(str(ev.get("price", 0)))
        self.total_var.set(str(ev.get("total_tickets", 0)))

        raw_date = ev.get("date")
        if raw_date:
            try:
                parsed_date = datetime.strptime(raw_date, "%d-%m-%Y").date()
                self.date_picker.set_date(parsed_date)
            except Exception:
                pass

        self.combo_category.set(next((k for k, v in self.category_map.items() if v == ev.get("category_id")), ""))

        # Banner preview
        self.image_path = ev.get("image", "")
        if self.image_path:
            self.show_preview(self.image_path)
        else:
            self.show_default_img_label()

        # Thumbnails Album
        self.gallery_paths = ev.get("danh_sach_anh", [])[:4]
        self.update_album_thumbnails()

    def clear_form(self):
        self.selected_id = None
        self.name_var.set("")
        self.price_var.set("")
        self.total_var.set("")
        self.short_desc_var.set("")
        self.time_var.set("19:00")
        self.full_desc_text.delete("1.0", tk.END)
        self.address_var.set("")
        
        self.load_organizer_profile_name()
        
        self.combo_location.set("")
        self.combo_category.set("")
        
        self.image_path = ""
        self.gallery_paths = []
        self.show_default_img_label()
        self.update_album_thumbnails()