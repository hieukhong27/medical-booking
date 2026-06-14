"""
GUI: Result Window
Hiển thị:
- Kết quả đặt lịch thành công (thông tin bác sĩ, bệnh viện, thời gian)
- Danh sách lịch khám đã đặt của người dùng
Toàn bộ dữ liệu được lấy từ service layer, GUI chỉ hiển thị.
"""

import customtkinter as ctk
from services.appointment_service import AppointmentService
from services.doctor_service import DoctorService
from services.clinic_service import ClinicService


class ResultWindow(ctk.CTkFrame):
    """Frame hiển thị kết quả đặt lịch hoặc danh sách lịch đã đặt."""

    def __init__(self, master, on_back):
        """
        Args:
            master: widget cha (App)
            on_back: callback quay lại Dashboard
        """
        super().__init__(master, fg_color="transparent")
        self.on_back = on_back
        self._build_ui()

    def _build_ui(self):
        """Xây dựng layout cơ bản (header + khu vực nội dung scroll)."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        self.label_title = ctk.CTkLabel(
            header, text="", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.label_title.pack(side="left")

        btn_back = ctk.CTkButton(
            header, text="← Quay lại Dashboard", width=160,
            command=self.on_back,
        )
        btn_back.pack(side="right")

        # Khu vực nội dung dạng scroll
        self.scroll_frame = ctk.CTkScrollableFrame(self, corner_radius=12)
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    def _clear_content(self):
        """Xóa toàn bộ widget cũ trong khu vực nội dung."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

    # ------------------------------------------------------------------
    # HIỂN THỊ KẾT QUẢ ĐẶT LỊCH THÀNH CÔNG
    # ------------------------------------------------------------------
    def show_booking_result(self, booking_result: dict):
        """
        Hiển thị thông tin sau khi đặt lịch thành công.

        Args:
            booking_result: dict trả về từ AppointmentService.book_appointment
                gồm appointment, doctor, clinic, email_sent, email_message
        """
        self.label_title.configure(text="✅ Đặt lịch thành công")
        self._clear_content()

        appointment = booking_result["appointment"]
        doctor = booking_result["doctor"]
        clinic = booking_result["clinic"]
        email_sent = booking_result["email_sent"]
        email_message = booking_result["email_message"]

        clinic_name = clinic.clinic_name if clinic else "Đang cập nhật"

        info_card = ctk.CTkFrame(self.scroll_frame, corner_radius=12)
        info_card.pack(fill="x", padx=10, pady=10)

        rows = [
            ("Mã lịch hẹn", str(appointment.appointment_id)),
            ("Bệnh nhân", appointment.patient_name),
            ("Bác sĩ", doctor.name),
            ("Chuyên khoa", doctor.specialty),
            ("Bệnh viện", clinic_name),
            ("Ngày khám", appointment.date),
            ("Giờ khám", appointment.time),
            ("Email", appointment.email),
        ]

        for i, (label, value) in enumerate(rows):
            ctk.CTkLabel(
                info_card, text=f"{label}:", font=ctk.CTkFont(weight="bold"),
                anchor="w", width=140,
            ).grid(row=i, column=0, sticky="w", padx=20, pady=6)

            ctk.CTkLabel(info_card, text=value, anchor="w").grid(
                row=i, column=1, sticky="w", padx=10, pady=6
            )

        # Trạng thái gửi email
        status_text = (
            "📧 Email xác nhận đã được gửi tới " + appointment.email
            if email_sent
            else f"⚠️ Không gửi được email xác nhận: {email_message}"
        )
        status_color = "green" if email_sent else "orange"

        ctk.CTkLabel(
            self.scroll_frame, text=status_text, text_color=status_color,
            wraplength=600, justify="left",
        ).pack(padx=20, pady=(10, 5), anchor="w")

    # ------------------------------------------------------------------
    # HIỂN THỊ DANH SÁCH LỊCH ĐÃ ĐẶT
    # ------------------------------------------------------------------
    def show_appointment_list(self, email: str):
        """
        Hiển thị danh sách lịch khám đã đặt theo email người dùng.

        Args:
            email: email của người dùng đang đăng nhập
        """
        self.label_title.configure(text="📋 Lịch khám đã đặt")
        self._clear_content()

        appointments = AppointmentService.get_appointments_by_email(email)

        if not appointments:
            ctk.CTkLabel(
                self.scroll_frame, text="Bạn chưa có lịch khám nào.",
                font=ctk.CTkFont(size=14),
            ).pack(padx=20, pady=20)
            return

        # Header bảng
        header_row = ctk.CTkFrame(self.scroll_frame, corner_radius=8)
        header_row.pack(fill="x", padx=5, pady=(5, 2))

        headers = ["Mã", "Bác sĩ", "Chuyên khoa", "Bệnh viện", "Ngày", "Giờ", "Nhắc lịch"]
        widths = [50, 160, 130, 200, 100, 70, 90]

        for i, h in enumerate(headers):
            ctk.CTkLabel(
                header_row, text=h, font=ctk.CTkFont(weight="bold"), width=widths[i]
            ).grid(row=0, column=i, padx=5, pady=8)

        # Dữ liệu từng lịch khám
        for appt in appointments:
            doctor = DoctorService.get_doctor_by_id(appt.doctor_id)
            doctor_name = doctor.name if doctor else f"ID {appt.doctor_id}"
            specialty = doctor.specialty if doctor else "-"

            clinic_name = "-"
            if doctor:
                for clinic in ClinicService.get_all_clinics():
                    if clinic.clinic_id == doctor.clinic_id:
                        clinic_name = clinic.clinic_name
                        break

            row_frame = ctk.CTkFrame(self.scroll_frame, corner_radius=8)
            row_frame.pack(fill="x", padx=5, pady=2)

            values = [
                str(appt.appointment_id),
                doctor_name,
                specialty,
                clinic_name,
                appt.date,
                appt.time,
                "Đã gửi" if appt.reminder_sent else "Chưa gửi",
            ]

            for i, v in enumerate(values):
                ctk.CTkLabel(row_frame, text=v, width=widths[i], wraplength=widths[i]).grid(
                    row=0, column=i, padx=5, pady=8
                )
