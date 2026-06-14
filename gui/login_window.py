"""
GUI: Login Window
Giao diện đăng nhập hệ thống.
Toàn bộ logic xác thực nằm trong services/auth_service.py (Clean Architecture).
"""

import customtkinter as ctk
from services.auth_service import AuthService


class LoginWindow(ctk.CTkFrame):
    """Frame đăng nhập, được nhúng vào cửa sổ chính (App)."""

    def __init__(self, master, on_login_success, on_go_register):
        """
        Args:
            master: widget cha (App)
            on_login_success: callback nhận (user) khi đăng nhập thành công
            on_go_register: callback chuyển sang màn hình đăng ký
        """
        super().__init__(master, fg_color="transparent")
        self.on_login_success = on_login_success
        self.on_go_register = on_go_register

        self._build_ui()

    def _build_ui(self):
        """Xây dựng giao diện đăng nhập."""
        container = ctk.CTkFrame(self, corner_radius=16)
        container.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            container,
            text="ĐĂNG NHẬP",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.grid(row=0, column=0, columnspan=2, padx=40, pady=(30, 20))

        subtitle = ctk.CTkLabel(
            container,
            text="Hệ thống Đặt lịch khám sức khỏe online",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        subtitle.grid(row=1, column=0, columnspan=2, padx=40, pady=(0, 20))

        # Username
        ctk.CTkLabel(container, text="Username").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=40, pady=(5, 0)
        )
        self.entry_username = ctk.CTkEntry(
            container, placeholder_text="Nhập username", width=280, height=38
        )
        self.entry_username.grid(row=3, column=0, columnspan=2, padx=40, pady=(0, 10))

        # Password
        ctk.CTkLabel(container, text="Password").grid(
            row=4, column=0, columnspan=2, sticky="w", padx=40, pady=(5, 0)
        )
        self.entry_password = ctk.CTkEntry(
            container, placeholder_text="Nhập password", show="*", width=280, height=38
        )
        self.entry_password.grid(row=5, column=0, columnspan=2, padx=40, pady=(0, 10))

        # Thông báo lỗi/thành công
        self.label_message = ctk.CTkLabel(container, text="", text_color="red")
        self.label_message.grid(row=6, column=0, columnspan=2, padx=40, pady=(0, 5))

        # Nút đăng nhập
        btn_login = ctk.CTkButton(
            container, text="Đăng nhập", width=280, height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._handle_login,
        )
        btn_login.grid(row=7, column=0, columnspan=2, padx=40, pady=(5, 10))

        # Link sang đăng ký
        btn_register = ctk.CTkButton(
            container, text="Chưa có tài khoản? Đăng ký ngay",
            width=280, height=32, fg_color="transparent",
            text_color=("gray10", "gray80"), hover_color=("gray80", "gray30"),
            command=self.on_go_register,
        )
        btn_register.grid(row=8, column=0, columnspan=2, padx=40, pady=(0, 30))

        # Cho phép nhấn Enter để đăng nhập
        self.entry_password.bind("<Return>", lambda e: self._handle_login())
        self.entry_username.bind("<Return>", lambda e: self._handle_login())

    def _handle_login(self):
        """Xử lý sự kiện click nút Đăng nhập - gọi AuthService."""
        username = self.entry_username.get()
        password = self.entry_password.get()

        success, result = AuthService.login(username, password)

        if success:
            self.label_message.configure(text="", text_color="red")
            self.on_login_success(result)  # result là User object
        else:
            self.label_message.configure(text=result, text_color="red")
