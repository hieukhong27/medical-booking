"""
Main Entry Point
Khởi tạo cửa sổ ứng dụng chính (App) và điều phối chuyển đổi
giữa các màn hình: Login -> Register -> Dashboard -> BookingForm -> ResultWindow.

Ngoài ra, khởi động một luồng nền (background thread) định kỳ kiểm tra
và gửi email nhắc lịch khám trước 1 ngày (send_due_reminders).
"""

import threading
import time

import customtkinter as ctk

from gui.login_window import LoginWindow
from gui.register_window import RegisterWindow
from gui.dashboard import Dashboard
from gui.booking_form import BookingForm
from gui.result_window import ResultWindow
from services.appointment_service import AppointmentService


# Cấu hình giao diện chung
ctk.set_appearance_mode("dark")       # Dark mode
ctk.set_default_color_theme("blue")   # Theme màu hiện đại


# Số giây giữa mỗi lần kiểm tra gửi reminder (ví dụ 1 giờ)
REMINDER_CHECK_INTERVAL_SECONDS = 3600


class App(ctk.CTk):
    """Cửa sổ ứng dụng chính - điều phối các Frame (màn hình)."""

    def __init__(self):
        super().__init__()

        self.title("Hệ thống Đặt lịch khám sức khỏe online")
        self.geometry("1000x650")
        self.minsize(800, 550)

        self.current_user = None      # User đang đăng nhập
        self.current_frame = None      # Frame hiện tại đang hiển thị

        # Khởi động luồng nền gửi reminder email
        self._start_reminder_thread()

        # Bắt đầu với màn hình đăng nhập
        self.show_login()

    # ------------------------------------------------------------------
    # ĐIỀU PHỐI MÀN HÌNH
    # ------------------------------------------------------------------
    def _switch_frame(self, frame_class, **kwargs):
        """Hủy frame hiện tại và hiển thị frame mới."""
        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = frame_class(self, **kwargs)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        """Hiển thị màn hình đăng nhập."""
        self._switch_frame(
            LoginWindow,
            on_login_success=self._handle_login_success,
            on_go_register=self.show_register,
        )

    def show_register(self):
        """Hiển thị màn hình đăng ký."""
        self._switch_frame(
            RegisterWindow,
            on_register_success=self.show_login,
            on_go_login=self.show_login,
        )

    def show_dashboard(self):
        """Hiển thị Dashboard sau khi đăng nhập."""
        self._switch_frame(
            Dashboard,
            current_user=self.current_user,
            on_book_appointment=self.show_booking_form,
            on_view_appointments=self.show_appointment_list,
            on_logout=self._handle_logout,
        )

    def show_booking_form(self):
        """Hiển thị form đặt lịch khám."""
        self._switch_frame(
            BookingForm,
            current_user=self.current_user,
            on_back=self.show_dashboard,
            on_booking_success=self._handle_booking_success,
        )

    def show_appointment_list(self):
        """Hiển thị danh sách lịch khám đã đặt."""
        self._switch_frame(ResultWindow, on_back=self.show_dashboard)
        self.current_frame.show_appointment_list(self.current_user.email)

    def show_booking_result(self, booking_result):
        """Hiển thị kết quả đặt lịch thành công."""
        self._switch_frame(ResultWindow, on_back=self.show_dashboard)
        self.current_frame.show_booking_result(booking_result)

    # ------------------------------------------------------------------
    # XỬ LÝ CALLBACK
    # ------------------------------------------------------------------
    def _handle_login_success(self, user):
        """Callback khi đăng nhập thành công."""
        self.current_user = user
        self.show_dashboard()

    def _handle_logout(self):
        """Callback khi người dùng đăng xuất."""
        self.current_user = None
        self.show_login()

    def _handle_booking_success(self, booking_result):
        """Callback khi đặt lịch thành công."""
        self.show_booking_result(booking_result)

    # ------------------------------------------------------------------
    # LUỒNG NỀN GỬI EMAIL NHẮC LỊCH
    # ------------------------------------------------------------------
    def _start_reminder_thread(self):
        """
        Khởi động một daemon thread chạy định kỳ, kiểm tra và gửi
        email nhắc lịch cho các lịch khám diễn ra vào ngày mai.
        """
        def reminder_loop():
            while True:
                try:
                    AppointmentService.send_due_reminders()
                except Exception as e:
                    # Không làm crash ứng dụng nếu gửi mail lỗi
                    print(f"[Reminder Thread] Lỗi: {e}")
                time.sleep(REMINDER_CHECK_INTERVAL_SECONDS)

        thread = threading.Thread(target=reminder_loop, daemon=True)
        thread.start()


def main():
    """Hàm khởi chạy ứng dụng."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
