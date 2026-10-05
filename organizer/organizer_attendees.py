import tkinter as tk
from tkinter import ttk

try:
    from config.ui_config import BG_COLOR, PRIMARY
except Exception:
    BG_COLOR = "#f4f6f9"
    PRIMARY = "#1e88e5"

try:
    from database.db import db, events, users

    user_tickets = db["user_tickets"] if db is not None else None
except Exception:
    events = None
    users = None
    user_tickets = None


class OrganizerAttendeesFrame(tk.Frame):

    def __init__(self, parent, username, *args, **kwargs):
        super().__init__(parent, bg=BG_COLOR)
        self.username = username
        self.event_map = {}
        self.current_attendees = []

        # Tiêu đề
        tk.Label(
            self,
            text="Danh sách Khách mua vé & Người tham gia",
            font=("Arial", 16, "bold"),
            bg=BG_COLOR,
            fg="#2c3e50",
        ).pack(anchor="w", padx=25, pady=(15, 5))

        # --- BỘ LỌC ---
        filter_card = tk.Frame(
            self, bg="white", bd=1, relief="solid", padx=15, pady=10
        )
        filter_card.pack(fill="x", padx=25, pady=(5, 10))

        # Chọn sự kiện
        tk.Label(
            filter_card,
            text="Chọn sự kiện:",
            font=("Arial", 9, "bold"),
            bg="white",
        ).grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.combo_event = ttk.Combobox(filter_card, state="readonly", width=30)
        self.combo_event.grid(row=0, column=1, sticky="w", padx=(0, 15))
        self.combo_event.bind("<<ComboboxSelected>>", self.on_event_change)

        # Tìm kiếm (lọc theo tên khách hàng hoặc email)
        tk.Label(
            filter_card, text="Tìm kiếm:", font=("Arial", 9, "bold"), bg="white"
        ).grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.entry_search = tk.Entry(
            filter_card,
            textvariable=self.search_var,
            font=("Arial", 9),
            width=20,
            bd=1,
            relief="solid",
        )
        self.entry_search.grid(row=0, column=3, sticky="w", padx=(0, 10))

        # Lọc theo thời gian thực
        self.search_var.trace_add(
            "write", lambda *args: self.filter_attendees()
        )
        self.entry_search.bind("<Return>", lambda e: self.filter_attendees())

        btn_search = tk.Button(
            filter_card,
            text="Tìm",
            font=("Arial", 9, "bold"),
            bg=PRIMARY,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.filter_attendees,
        )
        btn_search.grid(row=0, column=4, sticky="w")

        # --- BẢNG DANH SÁCH ---
        table_frame = tk.Frame(self, bg="white", bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        self.tree = ttk.Treeview(
            table_frame,
            columns=("customer_name", "email", "ticket_count"),
            show="headings",
        )

        self.tree.heading("customer_name", text="Tên Khách Hàng")
        self.tree.heading("email", text="Email")
        self.tree.heading("ticket_count", text="Số Vé Đã Mua")

        self.tree.column("customer_name", width=280)
        self.tree.column("email", width=280)
        self.tree.column("ticket_count", width=140, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        self.lbl_summary = tk.Label(
            self,
            text="Tổng số khách hàng: 0 | Tổng số vé đã mua: 0",
            font=("Arial", 9, "bold"),
            bg=BG_COLOR,
            fg="#2c3e50",
        )
        self.lbl_summary.pack(anchor="w", padx=25, pady=(0, 10))

        self.load_organizer_events()

    def load_organizer_events(self):
        self.event_map.clear()
        event_names = []

        if events is not None:
            try:
                my_events = events.find(
                    {
                        "$or": [
                            {"organizer": self.username},
                            {"created_by": self.username},
                        ]
                    }
                )
                for e in my_events:
                    e_name = e.get("name", "Không tên")
                    self.event_map[e_name] = str(e["_id"])
                    event_names.append(e_name)
            except Exception as err:
                print("Lỗi tải sự kiện:", err)

        self.combo_event["values"] = event_names
        if event_names:
            self.combo_event.set(event_names[0])
            self.load_attendees_by_event()
        else:
            self.render_table([])

    def on_event_change(self, event=None):
        self.search_var.set("")
        self.load_attendees_by_event()

    def load_attendees_by_event(self):
        self.current_attendees.clear()

        selected_event_name = self.combo_event.get()
        event_id = self.event_map.get(selected_event_name)

        if not event_id or user_tickets is None:
            self.render_table([])
            return

        try:
            tickets_list = list(user_tickets.find({"event_id": event_id}))

            grouped_data = {}
            for t in tickets_list:
                uname = t.get("username", "N/A")

                # Lấy số lượng vé trong bản ghi (hỗ trợ các tên trường: quantity, qty, soluong, so_luong)
                qty = int(
                    t.get(
                        "quantity",
                        t.get("qty", t.get("soluong", t.get("so_luong", 1))),
                    )
                )

                if uname not in grouped_data:
                    full_name = uname
                    email = "N/A"
                    if users is not None and uname != "N/A":
                        u = users.find_one({"username": uname})
                        if u:
                            full_name = (
                                u.get("full_name")
                                or u.get("fullname")
                                or u.get("ten_nguoi_dung")
                                or uname
                            )
                            email = u.get("email", "N/A")

                    grouped_data[uname] = {
                        "customer_name": full_name,
                        "email": email,
                        "ticket_count": 0,
                    }

                # Cộng dồn đúng số lượng vé đã mua
                grouped_data[uname]["ticket_count"] += qty

            self.current_attendees = list(grouped_data.values())

            # Thực hiện render theo ô tìm kiếm hiện tại (nếu đang có từ khóa)
            self.filter_attendees()

        except Exception as e:
            print("Lỗi khi tải danh sách vé:", e)
            self.render_table([])

    def render_table(self, data_list):
        self.tree.delete(*self.tree.get_children())
        total_tickets = 0

        for row in data_list:
            total_tickets += row["ticket_count"]
            self.tree.insert(
                "",
                "end",
                values=(
                    row["customer_name"],
                    row["email"],
                    row["ticket_count"],
                ),
            )

        # Cập nhật chính xác số khách hàng thực tế hiển thị trên bảng
        self.lbl_summary.config(
            text=f"Tổng số khách hàng: {len(data_list)} | Tổng số vé đã mua: {total_tickets}"
        )

    def filter_attendees(self):
        query = self.search_var.get().strip().lower()
        if not query:
            self.render_table(self.current_attendees)
            return

        filtered = [
            item
            for item in self.current_attendees
            if query in str(item.get("customer_name", "")).lower()
            or query in str(item.get("email", "")).lower()
        ]
        self.render_table(filtered)