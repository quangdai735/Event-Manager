import tkinter as tk
from tkinter import ttk
from bson import ObjectId

# Nhúng Matplotlib vào Tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

try:
    from config.ui_config import BG_COLOR, PRIMARY, SUCCESS, DANGER
except Exception:
    BG_COLOR = "#f4f6f9"
    PRIMARY = "#1e88e5"
    SUCCESS = "#2ecc71"
    DANGER = "#e74c3c"

from database.db import db, events, tickets, users


class StatsFrame(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)

        # --- 1. TIÊU ĐỀ & THANH LỌC BAN TỔ CHỨC ---
        header_frame = tk.Frame(self, bg=BG_COLOR)
        header_frame.pack(fill="x", padx=20, pady=(12, 8))

        tk.Label(
            header_frame,
            text="📊 Báo cáo & So sánh Doanh thu Ban tổ chức",
            font=("Segoe UI", 16, "bold"),
            bg=BG_COLOR,
            fg="#1F2937",
        ).pack(side="left")

        # Bộ lọc chọn BTC
        filter_frame = tk.Frame(header_frame, bg=BG_COLOR)
        filter_frame.pack(side="right")

        tk.Label(
            filter_frame,
            text="🏢 Chọn BTC:",
            font=("Segoe UI", 10, "bold"),
            bg=BG_COLOR,
            fg="#374151",
        ).pack(side="left", padx=(0, 5))

        self.org_var = tk.StringVar(value="Tất cả Ban tổ chức")
        self.org_combobox = ttk.Combobox(
            filter_frame,
            textvariable=self.org_var,
            state="readonly",
            width=22,
            font=("Segoe UI", 10),
        )
        self.org_combobox.pack(side="left", padx=(0, 5))
        self.org_combobox.bind("<<ComboboxSelected>>", lambda e: self.refresh_stats())

        tk.Button(
            filter_frame,
            text="🔄 Tất cả",
            bg=PRIMARY,
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.reset_filter,
        ).pack(side="left")

        # --- 2. CÁC THẺ KPI TỔNG QUAN ---
        kpi_frame = tk.Frame(self, bg=BG_COLOR)
        kpi_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.card_events = self.create_kpi_card(kpi_frame, "Số Sự Kiện (Đã duyệt)", "0", "#3b82f6")
        self.card_tickets = self.create_kpi_card(kpi_frame, "Vé Đã Bán / Đăng ký", "0", "#10b981")
        self.card_revenue = self.create_kpi_card(kpi_frame, "Tổng Doanh Thu", "0 VNĐ", "#f59e0b")
        self.card_best_event = self.create_kpi_card(kpi_frame, "Sự Kiện Hot Nhất", "Chưa có", "#8b5cf6")

        # --- 3. KHUNG CHÍNH CHỨA BẢNG SO SÁNH & BIỂU ĐỒ ---
        main_body = tk.Frame(self, bg=BG_COLOR)
        main_body.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        main_body.grid_columnconfigure(0, weight=3) # Bảng chiếm 60%
        main_body.grid_columnconfigure(1, weight=2) # Biểu đồ chiếm 40%
        main_body.grid_rowconfigure(0, weight=1)

        # ---------------- BẢNG SO SÁNH ----------------
        table_card = tk.Frame(main_body, bg="white", bd=1, relief="solid", padx=10, pady=10)
        table_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.lbl_table_title = tk.Label(
            table_card,
            text="📋 Bảng so sánh doanh thu chi tiết các sự kiện",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#1F2937",
        )
        self.lbl_table_title.pack(anchor="w", pady=(0, 8))

        style = ttk.Style()
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.tree = ttk.Treeview(
            table_card,
            columns=("name", "price", "sold_total", "rate", "revenue", "rank"),
            show="headings",
        )
        self.tree.heading("name", text="Tên Sự Kiện")
        self.tree.heading("price", text="Giá Vé")
        self.tree.heading("sold_total", text="Đã Bán/Tổng")
        self.tree.heading("rate", text="Tỷ Lệ Tỉ Lệ")
        self.tree.heading("revenue", text="Doanh Thu (VNĐ)")
        self.tree.heading("rank", text="Xếp Hạng")

        self.tree.column("name", width=160)
        self.tree.column("price", width=80, anchor="e")
        self.tree.column("sold_total", width=90, anchor="center")
        self.tree.column("rate", width=70, anchor="center")
        self.tree.column("revenue", width=120, anchor="e")
        self.tree.column("rank", width=80, anchor="center")

        self.tree.pack(fill="both", expand=True)

        # ---------------- BIỂU ĐỒ SO SÁNH (MATPLOTLIB) ----------------
        chart_card = tk.Frame(main_body, bg="white", bd=1, relief="solid", padx=10, pady=10)
        chart_card.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            chart_card,
            text="📊 Biểu đồ so sánh Doanh thu (Sự kiện có phí)",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#1F2937",
        ).pack(anchor="w", pady=(0, 5))

        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.fig.patch.set_facecolor("white")
        self.ax = self.fig.add_subplot(111)

        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=chart_card)
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Khởi tạo dữ liệu
        self.load_organizers()
        self.refresh_stats()

    def create_kpi_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg="white", bd=1, relief="solid", padx=12, pady=10)
        card.pack(side="left", fill="both", expand=True, padx=4)

        top_bar = tk.Frame(card, bg=color, height=3)
        top_bar.pack(fill="x", side="top", pady=(0, 6))

        lbl_title = tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), bg="white", fg="#6B7280")
        lbl_title.pack(anchor="w")

        lbl_val = tk.Label(card, text=value, font=("Segoe UI", 12, "bold"), bg="white", fg=color)
        lbl_val.pack(anchor="w", pady=(2, 0))

        return lbl_val

    def load_organizers(self):
        """Chỉ lấy danh sách Ban tổ chức của các sự kiện ĐÃ ĐƯỢC DUYỆT"""
        org_list = ["Tất cả Ban tổ chức"]
        for e in events.find({"status": "approved"}):
            org_display = e.get("organizer_name") or e.get("organizer")
            if org_display and org_display not in org_list:
                org_list.append(org_display)

        self.org_combobox["values"] = org_list

    def reset_filter(self):
        """Reset về tất cả BTC"""
        self.org_var.set("Tất cả Ban tổ chức")
        self.refresh_stats()

    def refresh_stats(self):
        """Tải dữ liệu các sự kiện ĐÃ DUYỆT, đưa vào Bảng so sánh và Vẽ biểu đồ"""
        self.tree.delete(*self.tree.get_children())
        selected_org = self.org_var.get()

        # 🔥 CHỈ LỌC CÁC SỰ KIỆN ĐÃ ĐƯỢC PHÊ DUYỆT (status == "approved")
        query = {"status": "approved"}

        if selected_org != "Tất cả Ban tổ chức":
            query["$and"] = [
                {"status": "approved"},
                {
                    "$or": [
                        {"organizer_name": selected_org},
                        {"organizer": selected_org},
                    ]
                }
            ]
            self.lbl_table_title.config(text=f"📋 Bảng so sánh sự kiện Đã duyệt - BTC: {selected_org}")
        else:
            self.lbl_table_title.config(text="📋 Bảng so sánh doanh thu sự kiện Đã duyệt")

        approved_events = list(events.find(query))

        total_events_count = len(approved_events)
        total_sold_tickets = 0
        total_revenue = 0

        event_data_list = []

        # 1. Thu thập và tính toán số liệu cho từng sự kiện
        for e in approved_events:
            e_id_str = str(e["_id"])
            e_name = e.get("name", "Không tên")

            ticket_doc = tickets.find_one({"event_id": e_id_str})
            if ticket_doc:
                price = float(ticket_doc.get("price", 0))
                total_tickets = int(ticket_doc.get("total", 0))
                sold_count = int(ticket_doc.get("sold", 0))
            else:
                price = float(e.get("price", 0))
                total_tickets = int(e.get("total_tickets", 0))
                sold_count = 0

            # Đếm thực tế từ user_tickets
            if db is not None and "user_tickets" in db.list_collection_names():
                real_sold = db["user_tickets"].count_documents({
                    "$or": [
                        {"event_id": e_id_str},
                        {"event_id": ObjectId(e["_id"])},
                        {"event_name": e_name},
                    ]
                })
                if real_sold > 0:
                    sold_count = real_sold

            e_revenue = sold_count * price
            fill_rate = (sold_count / total_tickets * 100) if total_tickets > 0 else 0

            total_sold_tickets += sold_count
            total_revenue += e_revenue

            event_data_list.append({
                "name": e_name,
                "price": price,
                "sold": sold_count,
                "total": total_tickets,
                "rate": fill_rate,
                "revenue": e_revenue
            })

        # 2. Ưu tiên sắp xếp theo Doanh thu, nếu bằng nhau thì theo Lượt bán/tham gia
        event_data_list.sort(key=lambda x: (x["revenue"], x["sold"]), reverse=True)

        chart_labels = []
        chart_revenues = []

        best_event_name = "Chưa có"

        for idx, item in enumerate(event_data_list):
            rank_str = f"🥇 Top {idx+1}" if idx == 0 else (f"🥈 Top {idx+1}" if idx == 1 else f"🥉 Top {idx+1}" if idx == 2 else f"Top {idx+1}")
            
            # Chọn sự kiện Hot nhất (có lượt tham gia hoặc doanh thu lớn nhất)
            if idx == 0 and (item["revenue"] > 0 or item["sold"] > 0):
                best_event_name = item["name"]

            # Format hiển thị giá vé và doanh thu
            price_display = "Miễn phí" if item["price"] == 0 else f"{item['price']:,.0f}"
            revenue_display = "0 đ (Free)" if item["price"] == 0 else f"{item['revenue']:,.0f}"

            self.tree.insert(
                "",
                "end",
                values=(
                    item["name"],
                    price_display,
                    f"{item['sold']}/{item['total']}",
                    f"{item['rate']:.1f}%",
                    revenue_display,
                    rank_str
                ),
            )

            # Chỉ đưa các sự kiện có doanh thu vào Biểu đồ Doanh Thu
            if item["revenue"] > 0:
                short_name = item["name"][:12] + "..." if len(item["name"]) > 12 else item["name"]
                chart_labels.append(short_name)
                chart_revenues.append(item["revenue"] / 1000000) # Triệu VNĐ

        # 3. Cập nhật số liệu KPI
        self.card_events.config(text=str(total_events_count))
        self.card_tickets.config(text=f"{total_sold_tickets:,}")
        self.card_revenue.config(text=f"{total_revenue:,.0f} đ")
        self.card_best_event.config(text=best_event_name)

        # 4. Vẽ lại Biểu đồ Cột So sánh Doanh thu
        self.draw_chart(chart_labels[:5], chart_revenues[:5])

    def draw_chart(self, labels, values):
        """Vẽ biểu đồ cột bằng Matplotlib"""
        self.ax.clear()

        if not labels or sum(values) == 0:
            self.ax.text(0.5, 0.5, "Chưa có dữ liệu doanh thu\n(Hoặc các SK đều Miễn phí)", ha="center", va="center", color="gray", fontsize=9)
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        else:
            bars = self.ax.bar(labels, values, color="#3b82f6", width=0.5)

            # Thêm con số doanh thu trên đầu mỗi cột
            for bar in bars:
                yval = bar.get_height()
                self.ax.text(
                    bar.get_x() + bar.get_width()/2.0, yval + (max(values)*0.02),
                    f"{yval:.1f}M", ha='center', va='bottom', fontsize=8, fontweight='bold'
                )

            self.ax.set_ylabel("Doanh thu (Triệu VNĐ)", fontsize=9)
            self.ax.tick_params(axis='x', rotation=15, labelsize=8)
            self.ax.tick_params(axis='y', labelsize=8)

            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)

        self.fig.tight_layout()
        self.chart_canvas.draw()