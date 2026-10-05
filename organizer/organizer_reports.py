import tkinter as tk
from tkinter import ttk, messagebox
from bson import ObjectId

# Nhúng Matplotlib vào Tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

try:
    from config.ui_config import BG_COLOR, PRIMARY
except Exception:
    BG_COLOR = "#f4f6f9"
    PRIMARY = "#1e88e5"

try:
    from database.db import db, events, tickets
    user_tickets = db["user_tickets"] if db is not None else None
except Exception:
    events = None
    tickets = None
    user_tickets = None


# ==============================================================================
# 🎪 POPUP XEM THỐNG KÊ CHI TIẾT TỪNG SỰ KIỆN 
# ==============================================================================
# ==============================================================================
# 🎪 POPUP XEM THỐNG KÊ CHI TIẾT TỪNG SỰ KIỆN (ĐÃ TỐI ƯU MÀU SẮC & CHỐNG ĐÈ CHỮ)
# ==============================================================================
class EventDetailStatsDialog(tk.Toplevel):
    def __init__(self, parent, event_doc):
        super().__init__(parent)
        self.event_doc = event_doc
        self.e_id_str = str(event_doc["_id"])
        self.e_name = event_doc.get("name", "Sự kiện")

        self.title(f"📊 Thống kê chi tiết - {self.e_name}")
        self.geometry("880x660")
        self.minsize(800, 580)
        self.configure(bg=BG_COLOR)

        # Căn giữa popup
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        cx = int((self.winfo_screenwidth() - w) / 2)
        cy = int((self.winfo_screenheight() - h) / 2)
        self.geometry(f"{w}x{h}+{cx}+{cy}")

        self.transient(parent)
        self.grab_set()

        self.build_ui()

    def build_ui(self):
        # Header
        header = tk.Frame(self, bg="white", bd=1, relief="solid", padx=15, pady=10)
        header.pack(fill="x", padx=15, pady=(15, 10))

        tk.Label(header, text=f"🎫 {self.e_name}", font=("Segoe UI", 15, "bold"), fg="#1F2937", bg="white").pack(anchor="w")
        
        date_str = f"⏰ Thời gian: {self.event_doc.get('time', '19:00')} - {self.event_doc.get('date', 'N/A')} | 📍 Địa điểm: {self.event_doc.get('location', 'N/A')}"
        tk.Label(header, text=date_str, font=("Segoe UI", 10), fg="#6B7280", bg="white").pack(anchor="w", pady=(2, 0))

        # Tính toán dữ liệu vé
        ticket_doc = tickets.find_one({"event_id": self.e_id_str}) if tickets is not None else None
        price = float(ticket_doc.get("price", 0)) if ticket_doc else float(self.event_doc.get("price", 0))
        total_tickets = int(ticket_doc.get("total", 0)) if ticket_doc else int(self.event_doc.get("total_tickets", 0))

        paid_count = 0
        pending_count = 0
        customer_tickets_list = []

        if db is not None and "user_tickets" in db.list_collection_names():
            tickets_cursor = db["user_tickets"].find({
                "$or": [
                    {"event_id": self.e_id_str},
                    {"event_id": ObjectId(self.e_id_str)},
                    {"event_name": self.e_name},
                ]
            })
            customer_tickets_list = list(tickets_cursor)

            for t in customer_tickets_list:
                status = t.get("payment_status", "Đã thanh toán")
                if status == "Chờ thanh toán tại quầy":
                    pending_count += 1
                else:
                    paid_count += 1

        if paid_count == 0 and pending_count == 0 and ticket_doc:
            paid_count = int(ticket_doc.get("sold", 0))

        remaining_tickets = max(0, total_tickets - (paid_count + pending_count))
        actual_revenue = paid_count * price

        # KPI Cards trong Dialog
        kpi_frame = tk.Frame(self, bg=BG_COLOR)
        kpi_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.create_mini_card(kpi_frame, "Tổng Vé Phát Hành", f"{total_tickets:,} vé", "#2563EB")
        self.create_mini_card(kpi_frame, "Đã Thanh Toán", f"{paid_count:,} vé", "#059669")
        self.create_mini_card(kpi_frame, "Chờ Tại Quầy", f"{pending_count:,} vé", "#D97706")
        self.create_mini_card(kpi_frame, "Vé Còn Trống", f"{remaining_tickets:,} vé", "#DC2626")
        self.create_mini_card(kpi_frame, "Doanh Thu Thực", f"{actual_revenue:,.0f} đ", "#059669")

        # Body
        body = tk.Frame(self, bg=BG_COLOR)
        body.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=3)
        body.grid_rowconfigure(0, weight=1)

        # ---------------- BIỂU ĐỒ TRÒN (ĐÃ TỐI ƯU MÀU SẮC & CHỐNG CHỒNG CHỮ) ----------------
        # ---------------- BIỂU ĐỒ TRÒN (ĐÃ FIX SẠCH CHỮ, BỎ VIỀN TRẮNG, KHÔNG ĐÈ LỖI) ----------------
        chart_card = tk.Frame(body, bg="white", bd=1, relief="solid", padx=10, pady=10)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(chart_card, text="🎯 Tỷ lệ Phân bổ Vé", font=("Segoe UI", 11, "bold"), bg="white", fg="#1F2937").pack(anchor="w")

        fig = Figure(figsize=(3.5, 3.8), dpi=95)
        fig.patch.set_facecolor("white")
        ax = fig.add_subplot(111)

        legend_labels = []
        sizes = []
        colors = []

        total_v = paid_count + pending_count + remaining_tickets

        # Tính toán phần trăm và đưa thẳng vào Chú thích (Legend)
        if paid_count > 0:
            pct = (paid_count / total_v * 100) if total_v > 0 else 0
            legend_labels.append(f"Đã thanh toán: {paid_count:,} ({pct:.1f}%)")
            sizes.append(paid_count)
            colors.append("#10B981")  # Xanh lá

        if pending_count > 0:
            pct = (pending_count / total_v * 100) if total_v > 0 else 0
            legend_labels.append(f"Chờ tại quầy: {pending_count:,} ({pct:.1f}%)")
            sizes.append(pending_count)
            colors.append("#F59E0B")  # Cam

        if remaining_tickets > 0:
            pct = (remaining_tickets / total_v * 100) if total_v > 0 else 0
            legend_labels.append(f"Vé còn trống: {remaining_tickets:,} ({pct:.1f}%)")
            sizes.append(remaining_tickets)
            colors.append("#3B82F6")  # Xanh dương

        if sum(sizes) == 0:
            ax.text(0.5, 0.5, "Chưa có dữ liệu vé", ha="center", va="center", color="#9CA3AF", fontsize=10, fontstyle="italic")
            ax.axis('off')
        else:
            # Vẽ Doughnut không viền trắng (edgecolor='none', linewidth=0)
            wedges, _ = ax.pie(
                sizes, 
                colors=colors, 
                startangle=90,
                counterclock=False,
                wedgeprops=dict(width=0.45, edgecolor='none', linewidth=0) # Không viền cắt trắng
            )

            # Đặt chú thích ngay ngắn phía dưới (Hiển thị rõ cả Số vé + %)
            ax.legend(
                wedges, 
                legend_labels, 
                loc="lower center", 
                bbox_to_anchor=(0.5, -0.22), 
                fontsize=8.5, 
                frameon=False,
                handlelength=1.0,
                handletextpad=0.6,
                labelspacing=0.4
            )
            ax.axis('equal')

        # Căn chỉnh lề tự động chống tràn khung
        fig.tight_layout()
        fig.subplots_adjust(bottom=0.25, top=0.98, left=0.05, right=0.95)

        canvas = FigureCanvasTkAgg(fig, master=chart_card)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # ---------------- BẢNG KHÁCH HÀNG ----------------
        cust_card = tk.Frame(body, bg="white", bd=1, relief="solid", padx=10, pady=10)
        cust_card.grid(row=0, column=1, sticky="nsew")

        tk.Label(cust_card, text="📜 Danh sách Lượt mua vé", font=("Segoe UI", 11, "bold"), bg="white", fg="#1F2937").pack(anchor="w", pady=(0, 5))

        cust_tree = ttk.Treeview(cust_card, columns=("code", "user", "date", "status"), show="headings", height=8)
        cust_tree.heading("code", text="Mã Vé")
        cust_tree.heading("user", text="Tài Khoản")
        cust_tree.heading("date", text="Ngày Mua")
        cust_tree.heading("status", text="Trạng Thái")

        cust_tree.column("code", width=85, anchor="center")
        cust_tree.column("user", width=100, anchor="w")
        cust_tree.column("date", width=110, anchor="center")
        cust_tree.column("status", width=130, anchor="center")

        cust_tree.pack(fill="both", expand=True)

        for t_item in customer_tickets_list:
            cust_tree.insert("", "end", values=(
                t_item.get("ticket_code", "N/A"),
                t_item.get("username", "N/A"),
                t_item.get("purchase_date", "N/A"),
                t_item.get("payment_status", "Đã thanh toán")
            ))

    def create_mini_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg="white", bd=1, relief="solid", padx=8, pady=6)
        card.pack(side="left", fill="both", expand=True, padx=2)

        tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), bg="white", fg="#6B7280").pack(anchor="w")
        tk.Label(card, text=value, font=("Segoe UI", 10, "bold"), bg="white", fg=color).pack(anchor="w", pady=(2, 0))


# ==============================================================================
# 📊 BẢNG BÁO CÁO & SO SÁNH CHÍNH CHO BAN TỔ CHỨC
# ==============================================================================
class OrganizerReportsFrame(tk.Frame):

    def __init__(self, parent, username, *args, **kwargs):
        super().__init__(parent, bg=BG_COLOR)
        self.username = username
        self.my_events_cache = []

        # --- 1. TIÊU ĐỀ MÀN HÌNH ---
        tk.Label(
            self,
            text="📊 Báo cáo & So sánh Doanh thu Ban tổ chức",
            font=("Segoe UI", 16, "bold"),
            bg=BG_COLOR,
            fg="#1F2937",
        ).pack(anchor="w", padx=20, pady=(12, 8))

        # --- 2. THẺ KPI TỔNG QUAN ---
        kpi_frame = tk.Frame(self, bg=BG_COLOR)
        kpi_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.card_events = self.create_kpi_card(kpi_frame, "Số Sự Kiện", "0", "#3b82f6")
        self.card_total_all_tickets = self.create_kpi_card(kpi_frame, "Tổng Vé Phát Hành", "0", "#6366f1")
        self.card_tickets = self.create_kpi_card(kpi_frame, "Vé Đã TT (Online)", "0", "#10b981")
        self.card_pending_tickets = self.create_kpi_card(kpi_frame, "Vé Chờ TT (Tại quầy)", "0", "#f59e0b")
        self.card_revenue = self.create_kpi_card(kpi_frame, "Doanh Thu Thực Tế", "0 VNĐ", "#10b981")
        self.card_best_event = self.create_kpi_card(kpi_frame, "Sự Kiện Hot Nhất", "Chưa có", "#8b5cf6")

        # --- 3. KHUNG CHÍNH (Đã tối ưu tỉ lệ 65% : 35% chống đè chữ) ---
        main_body = tk.Frame(self, bg=BG_COLOR)
        main_body.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        main_body.grid_columnconfigure(0, weight=13) # Bảng rộng rãi chiếm 65%
        main_body.grid_columnconfigure(1, weight=7)  # Biểu đồ chiếm 35%
        main_body.grid_rowconfigure(0, weight=1)

        # ---------------- BẢNG SO SÁNH (CỘT RỘNG THOÁNG CHỐNG TRỒNG CHỮ) ----------------
        left_table_card = tk.Frame(main_body, bg="white", bd=1, relief="solid", padx=10, pady=10)
        left_table_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(
            left_table_card,
            text="📋 Bảng so sánh hiệu suất (Nhấp đúp dòng để xem chi tiết)",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#1F2937",
        ).pack(anchor="w", pady=(0, 6))

        style = ttk.Style()
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

        self.tree = ttk.Treeview(
            left_table_card,
            columns=("name", "price", "total_tickets", "paid_sold", "pending_sold", "rate", "revenue", "rank"),
            show="headings",
        )
        self.tree.heading("name", text="Tên Sự Kiện")
        self.tree.heading("price", text="Giá Vé")
        self.tree.heading("total_tickets", text="Tổng Vé")
        self.tree.heading("paid_sold", text="Đã TT")
        self.tree.heading("pending_sold", text="Chờ TT")
        self.tree.heading("rate", text="Tỷ Lệ")
        self.tree.heading("revenue", text="Doanh Thu Thực")
        self.tree.heading("rank", text="Xếp Hạng")

        # 🔥 CHỈNH LẠI ĐỘ RỘNG CÁC CỘT RỘNG RÃI RÕ RÀNG
        self.tree.column("name", width=160, anchor="w")
        self.tree.column("price", width=80, anchor="e")
        self.tree.column("total_tickets", width=70, anchor="center")
        self.tree.column("paid_sold", width=70, anchor="center")
        self.tree.column("pending_sold", width=70, anchor="center")
        self.tree.column("rate", width=70, anchor="center")
        self.tree.column("revenue", width=120, anchor="e")
        self.tree.column("rank", width=75, anchor="center")

        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", self.open_detail_stats)

        btn_bar = tk.Frame(left_table_card, bg="white")
        btn_bar.pack(fill="x", pady=(6, 0))

        tk.Button(
            btn_bar, text="🔍 Xem Thống Kê Chi Tiết Sự Kiện", bg=PRIMARY, fg="white",
            font=("Segoe UI", 9, "bold"), padx=10, pady=4, cursor="hand2", command=self.open_detail_stats
        ).pack(side="left")

        # ---------------- BIỂU ĐỒ SO SÁNH ----------------
        chart_card = tk.Frame(main_body, bg="white", bd=1, relief="solid", padx=10, pady=10)
        chart_card.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            chart_card,
            text="📊 Doanh Thu Thực Tế (Triệu VNĐ)",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#1F2937",
        ).pack(anchor="w", pady=(0, 5))

        self.fig = Figure(figsize=(3.5, 3), dpi=95)
        self.fig.patch.set_facecolor("white")
        self.ax = self.fig.add_subplot(111)

        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=chart_card)
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

        self.load_report_data()

    def create_kpi_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg="white", bd=1, relief="solid", padx=8, pady=8)
        card.pack(side="left", fill="both", expand=True, padx=2)

        top_bar = tk.Frame(card, bg=color, height=3)
        top_bar.pack(fill="x", side="top", pady=(0, 5))

        lbl_title = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), bg="white", fg="#6B7280")
        lbl_title.pack(anchor="w")

        lbl_val = tk.Label(card, text=value, font=("Segoe UI", 10, "bold"), bg="white", fg=color)
        lbl_val.pack(anchor="w", pady=(2, 0))

        return lbl_val

    def load_report_data(self):
        """Tải dữ liệu báo cáo"""
        self.tree.delete(*self.tree.get_children())

        if events is None:
            return

        try:
            self.my_events_cache = list(
                events.find({
                    "$or": [
                        {"organizer": self.username},
                        {"created_by": self.username},
                    ]
                })
            )

            total_events_count = len(self.my_events_cache)
            sum_total_tickets = 0
            total_paid_tickets = 0
            total_pending_tickets = 0
            total_actual_revenue = 0

            event_stat_list = []

            for e in self.my_events_cache:
                e_id_str = str(e["_id"])
                e_name = e.get("name", "Không tên")

                ticket_doc = tickets.find_one({"event_id": e_id_str}) if tickets is not None else None

                if ticket_doc:
                    price = float(ticket_doc.get("price", 0))
                    total_tickets = int(ticket_doc.get("total", 0))
                else:
                    price = float(e.get("price", 0))
                    total_tickets = int(e.get("total_tickets", 0))

                paid_count = 0
                pending_count = 0

                if db is not None and "user_tickets" in db.list_collection_names():
                    paid_count = db["user_tickets"].count_documents({
                        "$and": [
                            {
                                "$or": [
                                    {"event_id": e_id_str},
                                    {"event_id": ObjectId(e["_id"])},
                                    {"event_name": e_name},
                                ]
                            },
                            {
                                "$or": [
                                    {"payment_status": "Đã thanh toán"},
                                    {"payment_status": {"$exists": False}},
                                ]
                            },
                        ]
                    })

                    pending_count = db["user_tickets"].count_documents({
                        "$and": [
                            {
                                "$or": [
                                    {"event_id": e_id_str},
                                    {"event_id": ObjectId(e["_id"])},
                                    {"event_name": e_name},
                                ]
                            },
                            {"payment_status": "Chờ thanh toán tại quầy"},
                        ]
                    })

                if paid_count == 0 and pending_count == 0 and ticket_doc:
                    paid_count = int(ticket_doc.get("sold", 0))

                e_actual_revenue = paid_count * price
                fill_rate = (paid_count / total_tickets * 100) if total_tickets > 0 else 0

                sum_total_tickets += total_tickets
                total_paid_tickets += paid_count
                total_pending_tickets += pending_count
                total_actual_revenue += e_actual_revenue

                event_stat_list.append({
                    "id": e_id_str,
                    "doc": e,
                    "name": e_name,
                    "price": price,
                    "paid": paid_count,
                    "pending": pending_count,
                    "total": total_tickets,
                    "rate": fill_rate,
                    "revenue": e_actual_revenue
                })

            event_stat_list.sort(key=lambda x: x["revenue"], reverse=True)

            chart_labels = []
            chart_values = []
            best_event_name = "Chưa có"

            for idx, item in enumerate(event_stat_list):
                rank_str = f"🥇 Top {idx+1}" if idx == 0 else (f"🥈 Top {idx+1}" if idx == 1 else f"🥉 Top {idx+1}" if idx == 2 else f"Top {idx+1}")
                if idx == 0 and item["revenue"] > 0:
                    best_event_name = item["name"]

                self.tree.insert(
                    "",
                    "end",
                    iid=item["id"],
                    values=(
                        item["name"],
                        f"{item['price']:,.0f}",
                        f"{item['total']:,}",
                        f"{item['paid']:,}",
                        f"{item['pending']:,}",
                        f"{item['rate']:.1f}%",
                        f"{item['revenue']:,.0f}",
                        rank_str
                    ),
                )

                short_name = item["name"][:10] + "..." if len(item["name"]) > 10 else item["name"]
                chart_labels.append(short_name)
                chart_values.append(item["revenue"] / 1000000)

            # Cập nhật KPI
            self.card_events.config(text=str(total_events_count))
            self.card_total_all_tickets.config(text=f"{sum_total_tickets:,}")
            self.card_tickets.config(text=f"{total_paid_tickets:,}")
            self.card_pending_tickets.config(text=f"{total_pending_tickets:,}")
            self.card_revenue.config(text=f"{total_actual_revenue:,.0f} đ")
            self.card_best_event.config(text=best_event_name)

            self.draw_chart(chart_labels[:5], chart_values[:5])

        except Exception as err:
            print("Lỗi tải báo cáo:", err)

    def open_detail_stats(self, event=None):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Thông báo", "Vui lòng chọn 1 sự kiện trong bảng để xem chi tiết!")
            return

        selected_id = sel[0]
        event_doc = next((e for e in self.my_events_cache if str(e["_id"]) == selected_id), None)

        if event_doc:
            EventDetailStatsDialog(self, event_doc)

    def draw_chart(self, labels, values):
        self.ax.clear()

        if not labels or sum(values) == 0:
            self.ax.text(0.5, 0.5, "Chưa có dữ liệu", ha="center", va="center", color="gray")
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        else:
            bars = self.ax.bar(labels, values, color="#10b981", width=0.45)

            for bar in bars:
                yval = bar.get_height()
                self.ax.text(
                    bar.get_x() + bar.get_width()/2.0, yval + (max(values)*0.02),
                    f"{yval:.1f}M", ha='center', va='bottom', fontsize=8, fontweight='bold'
                )

            self.ax.set_ylabel("Triệu VNĐ", fontsize=8)
            self.ax.tick_params(axis='x', rotation=15, labelsize=8)
            self.ax.tick_params(axis='y', labelsize=8)

            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)

        self.fig.tight_layout()
        self.chart_canvas.draw()