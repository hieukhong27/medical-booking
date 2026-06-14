"""
GUI: Dashboard
Hiển thị sau khi đăng nhập thành công:
- Thông tin người dùng
- Nút đặt lịch khám
- Nút xem lịch đã đặt
- Nút đăng xuất
"""

import customtkinter as ctk


class Dashboard(ctk.CTkFrame):
    """Frame Dashboard chính sau khi đăng nhập."""

    def __init__(self, master, current_user, on_book_appointment,
                 on_view_appointments, on_logout):
        """
        Args:
            master: widget cha (App)
            current_user: User object đang đăng nhập
            on_book_appointment: callback chuyển sang form đặt lịch
            on_view_appointments: callback chuyển sang xem lịch đã đặt
            on_logout: callback đăng xuất
        """
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user
        self.on_book_appointment = on_book_appointment
        self.on_view_appointments = on_view_appointments
        self.on_logout = on_logout

        self._build_ui()

    def _build_ui(self):
        """Xây dựng giao diện dashboard với sidebar + nội dung chính."""
        # Sidebar
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            sidebar, text="🏥 Medical\nBooking",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(padx=20, pady=(30, 30))

        ctk.CTkButton(
            sidebar, text="📅  Đặt lịch khám", width=180, height=42,
            anchor="w", command=self.on_book_appointment,
        ).pack(padx=20, pady=8)

        ctk.CTkButton(
            sidebar, text="📋  Lịch đã đặt", width=180, height=42,
            anchor="w", command=self.on_view_appointments,
        ).pack(padx=20, pady=8)

        ctk.CTkButton(
            sidebar, text="🚪  Đăng xuất", width=180, height=42,
            anchor="w", fg_color="#b3261e", hover_color="#8c1e18",
            command=self.on_logout,
        ).pack(padx=20, pady=(40, 8))

        # Nội dung chính - thông tin người dùng
        main_area = ctk.CTkFrame(self, fg_color="transparent")
        main_area.pack(side="left", fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(
            main_area, text=f"Xin chào, {self.current_user.fullname} 👋",
            font=ctk.CTkFont(size=26, weight="bold"),
        ).pack(anchor="w", pady=(10, 20))

        info_card = ctk.CTkFrame(main_area, corner_radius=12)
        info_card.pack(fill="x", pady=10)

        info_rows = [
            ("Họ tên", self.current_user.fullname),
            ("Email", self.current_user.email),
            ("Username", self.current_user.username),
        ]

        for i, (label, value) in enumerate(info_rows):
            ctk.CTkLabel(
                info_card, text=f"{label}:", font=ctk.CTkFont(weight="bold"),
                anchor="w", width=120,
            ).grid(row=i, column=0, sticky="w", padx=20, pady=10)

            ctk.CTkLabel(info_card, text=value, anchor="w").grid(
                row=i, column=1, sticky="w", padx=10, pady=10
            )

        # Hướng dẫn nhanh
        guide_card = ctk.CTkFrame(main_area, corner_radius=12)
        guide_card.pack(fill="x", pady=20)

        ctk.CTkLabel(
            guide_card, text="💡 Hướng dẫn nhanh",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(15, 5))

        guide_text = (
            "1. Nhấn 'Đặt lịch khám' để bắt đầu.\n"
            "2. Nhập địa chỉ hiện tại để hệ thống tìm bệnh viện gần nhất.\n"
            "3. Nhập triệu chứng để hệ thống đề xuất chuyên khoa & bác sĩ.\n"
            "4. Chọn ngày/giờ khám và xác nhận đặt lịch.\n"
            "5. Xem lại lịch đã đặt trong mục 'Lịch đã đặt'."
        )
        ctk.CTkLabel(
            guide_card, text=guide_text, justify="left", anchor="w",
        ).pack(anchor="w", padx=20, pady=(0, 15))
