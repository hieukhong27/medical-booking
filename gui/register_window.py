"""
GUI: Register Window
Giao diện đăng ký tài khoản mới.
Toàn bộ logic xử lý nằm trong services/auth_service.py.
"""

import customtkinter as ctk
from services.auth_service import AuthService


class RegisterWindow(ctk.CTkFrame):
    """Frame đăng ký tài khoản, được nhúng vào cửa sổ chính (App)."""

    def __init__(self, master, on_register_success, on_go_login):
        """
        Args:
            master: widget cha (App)
            on_register_success: callback gọi khi đăng ký thành công
            on_go_login: callback chuyển về màn hình đăng nhập
        """
        super().__init__(master, fg_color="transparent")
        self.on_register_success = on_register_success
        self.on_go_login = on_go_login

        self._build_ui()

    def _build_ui(self):
        """Xây dựng giao diện đăng ký."""
        container = ctk.CTkFrame(self, corner_radius=16)
        container.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            container,
            text="ĐĂNG KÝ TÀI KHOẢN",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.grid(row=0, column=0, columnspan=2, padx=40, pady=(30, 20))

        # Họ tên
        ctk.CTkLabel(container, text="Họ tên").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=40, pady=(5, 0)
        )
        self.entry_fullname = ctk.CTkEntry(
            container, placeholder_text="Nguyễn Văn A", width=280, height=36
        )
        self.entry_fullname.grid(row=2, column=0, columnspan=2, padx=40, pady=(0, 8))

        # Email
        ctk.CTkLabel(container, text="Email").grid(
            row=3, column=0, columnspan=2, sticky="w", padx=40, pady=(5, 0)
        )
        self.entry_email = ctk.CTkEntry(
            container, placeholder_text="email@gmail.com", width=280, height=36
        )
        self.entry_email.grid(row=4, column=0, columnspan=2, padx=40, pady=(0, 8))

        # Username
        ctk.CTkLabel(container, text="Username").grid(
            row=5, column=0, columnspan=2, sticky="w", padx=40, pady=(5, 0)
        )
        self.entry_username = ctk.CTkEntry(
            container, placeholder_text="Tên đăng nhập", width=280, height=36
        )
        self.entry_username.grid(row=6, column=0, columnspan=2, padx=40, pady=(0, 8))

        # Password
        ctk.CTkLabel(container, text="Password").grid(
            row=7, column=0, columnspan=2, sticky="w", padx=40, pady=(5, 0)
        )
        self.entry_password = ctk.CTkEntry(
            container, placeholder_text="Mật khẩu", show="*", width=280, height=36
        )
        self.entry_password.grid(row=8, column=0, columnspan=2, padx=40, pady=(0, 8))

        # Confirm Password
        ctk.CTkLabel(container, text="Confirm Password").grid(
            row=9, column=0, columnspan=2, sticky="w", padx=40, pady=(5, 0)
        )
        self.entry_confirm_password = ctk.CTkEntry(
            container, placeholder_text="Nhập lại mật khẩu", show="*", width=280, height=36
        )
        self.entry_confirm_password.grid(row=10, column=0, columnspan=2, padx=40, pady=(0, 8))

        # Thông báo
        self.label_message = ctk.CTkLabel(container, text="", text_color="red")
        self.label_message.grid(row=11, column=0, columnspan=2, padx=40, pady=(0, 5))

        # Nút đăng ký
        btn_register = ctk.CTkButton(
            container, text="Đăng ký", width=280, height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._handle_register,
        )
        btn_register.grid(row=12, column=0, columnspan=2, padx=40, pady=(5, 10))

        # Link về đăng nhập
        btn_back = ctk.CTkButton(
            container, text="Đã có tài khoản? Đăng nhập",
            width=280, height=32, fg_color="transparent",
            text_color=("gray10", "gray80"), hover_color=("gray80", "gray30"),
            command=self.on_go_login,
        )
        btn_back.grid(row=13, column=0, columnspan=2, padx=40, pady=(0, 30))

    def _handle_register(self):
        """Xử lý sự kiện click nút Đăng ký - gọi AuthService."""
        fullname = self.entry_fullname.get()
        email = self.entry_email.get()
        username = self.entry_username.get()
        password = self.entry_password.get()
        confirm_password = self.entry_confirm_password.get()

        success, message = AuthService.register(
            fullname, email, username, password, confirm_password
        )

        if success:
            self.label_message.configure(text=message, text_color="green")
            self._clear_fields()
            # Sau 1.2s tự động chuyển sang màn hình đăng nhập
            self.after(1200, self.on_go_login)
        else:
            self.label_message.configure(text=message, text_color="red")

    def _clear_fields(self):
        """Xóa toàn bộ dữ liệu trong các ô nhập sau khi đăng ký thành công."""
        for entry in (
            self.entry_fullname, self.entry_email, self.entry_username,
            self.entry_password, self.entry_confirm_password,
        ):
            entry.delete(0, "end")
