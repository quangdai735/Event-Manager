from auth.auth import AuthWindow
from admin.admin_dashboard import AdminDashboard
from organizer.organizer_dashboard import OrganizerDashboard
from user.user_dashboard import UserDashboard

# Biến toàn cục để quản lý cửa sổ đang hiển thị
current_window = None

def on_login(username, role, full_name):
    global current_window

    # Đóng cửa sổ đăng nhập
    if current_window:
        current_window.destroy()
        current_window = None

    # Chuẩn hóa role về chữ thường để tránh lỗi viết hoa/thường
    clean_role = str(role).lower().strip()

    # Điều hướng theo quyền
    if clean_role == "admin":
        current_window = AdminDashboard(
            username,
            full_name,
            logout_handler,
            role
        )
    elif clean_role == "organizer":
        current_window = OrganizerDashboard(
            username,
            full_name,
            logout_handler
        )
    else:
        current_window = UserDashboard(
            username,
            full_name,
            logout_handler
        )

    current_window.mainloop()


def logout_handler():
    global current_window

    if current_window:
        current_window.destroy()
        current_window = None

    start()

def start():
    global current_window
    current_window = AuthWindow(on_login_success=on_login)
    current_window.mainloop()


if __name__ == "__main__":
    start()