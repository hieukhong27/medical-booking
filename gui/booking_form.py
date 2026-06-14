"""
GUI: Booking Form
Form đặt lịch khám gồm:
- Họ tên, Email, Địa chỉ, Triệu chứng, Ngày khám, Giờ khám
Toàn bộ business logic (geocoding, tìm bệnh viện, tìm bác sĩ, đặt lịch...)
được gọi từ service layer - GUI chỉ thu thập input và hiển thị kết quả.
"""

import customtkinter as ctk
from tkinter import messagebox

from services.geolocation_service import GeolocationService
from services.clinic_service import ClinicService
from services.doctor_service import DoctorService
from services.appointment_service import AppointmentService


class BookingForm(ctk.CTkFrame):
    """Frame form đặt lịch khám."""

    def __init__(self, master, current_user, on_back, on_booking_success):
        """
        Args:
            master: widget cha (App)
            current_user: User object đang đăng nhập
            on_back: callback quay lại Dashboard
            on_booking_success: callback nhận (booking_result) khi đặt lịch xong
        """
        super().__init__(master, fg_color="transparent")
        self.current_user = current_user
        self.on_back = on_back
        self.on_booking_success = on_booking_success

        # Lưu trữ kết quả tra cứu trung gian
        self.user_coordinates = None
        self.nearest_clinic = None
        self.nearest_distance = None
        self.matched_specialty = None
        self.suggested_doctor = None

        self._build_ui()

    # ------------------------------------------------------------------
    # XÂY DỰNG GIAO DIỆN
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        ctk.CTkLabel(
            header, text="🗓️ Đặt lịch khám", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header, text="← Quay lại Dashboard", width=160, command=self.on_back
        ).pack(side="right")

        # Khu vực form (scrollable để hỗ trợ responsive cơ bản)
        form = ctk.CTkScrollableFrame(self, corner_radius=12)
        form.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # ----- Họ tên -----
        ctk.CTkLabel(form, text="Họ tên *").grid(row=0, column=0, sticky="w", padx=20, pady=(15, 0))
        self.entry_fullname = ctk.CTkEntry(form, width=400, height=36,
                                            placeholder_text="Nguyễn Văn A")
        self.entry_fullname.grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 10))
        self.entry_fullname.insert(0, self.current_user.fullname)

        # ----- Email -----
        ctk.CTkLabel(form, text="Email *").grid(row=2, column=0, sticky="w", padx=20, pady=(5, 0))
        self.entry_email = ctk.CTkEntry(form, width=400, height=36,
                                         placeholder_text="email@gmail.com")
        self.entry_email.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 10))
        self.entry_email.insert(0, self.current_user.email)

        # ----- Địa chỉ -----
        ctk.CTkLabel(form, text="Địa chỉ hiện tại *").grid(row=4, column=0, sticky="w", padx=20, pady=(5, 0))
        self.entry_address = ctk.CTkEntry(form, width=400, height=36,
                                           placeholder_text="Ví dụ: 123 Cầu Giấy Hà Nội")
        self.entry_address.grid(row=5, column=0, sticky="w", padx=20, pady=(0, 10))

        self.btn_find_clinic = ctk.CTkButton(
            form, text="🔍 Tìm bệnh viện gần nhất", width=180,
            command=self._handle_find_clinic,
        )
        self.btn_find_clinic.grid(row=5, column=1, sticky="w", padx=10, pady=(0, 10))

        self.label_clinic_result = ctk.CTkLabel(
            form, text="", text_color="lightgreen", wraplength=500, justify="left"
        )
        self.label_clinic_result.grid(row=6, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 10))

        # ----- Triệu chứng -----
        ctk.CTkLabel(form, text="Triệu chứng *").grid(row=7, column=0, sticky="w", padx=20, pady=(5, 0))
        self.entry_symptom = ctk.CTkEntry(form, width=400, height=36,
                                           placeholder_text="Ví dụ: dau hong, dau bung, dau dau...")
        self.entry_symptom.grid(row=8, column=0, sticky="w", padx=20, pady=(0, 10))

        self.btn_find_doctor = ctk.CTkButton(
            form, text="🩺 Tìm bác sĩ phù hợp", width=180,
            command=self._handle_find_doctor,
        )
        self.btn_find_doctor.grid(row=8, column=1, sticky="w", padx=10, pady=(0, 10))

        self.label_doctor_result = ctk.CTkLabel(
            form, text="", text_color="lightgreen", wraplength=500, justify="left"
        )
        self.label_doctor_result.grid(row=9, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 10))

        # ----- Ngày khám -----
        ctk.CTkLabel(form, text="Ngày khám (YYYY-MM-DD) *").grid(row=10, column=0, sticky="w", padx=20, pady=(5, 0))
        self.entry_date = ctk.CTkEntry(form, width=400, height=36,
                                        placeholder_text="2026-06-20")
        self.entry_date.grid(row=11, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 10))

        # ----- Giờ khám -----
        ctk.CTkLabel(form, text="Giờ khám (HH:MM) *").grid(row=12, column=0, sticky="w", padx=20, pady=(5, 0))
        self.entry_time = ctk.CTkEntry(form, width=400, height=36,
                                        placeholder_text="08:00")
        self.entry_time.grid(row=13, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 10))

        # ----- Thông báo lỗi -----
        self.label_message = ctk.CTkLabel(form, text="", text_color="red",
                                           wraplength=500, justify="left")
        self.label_message.grid(row=14, column=0, columnspan=2, sticky="w", padx=20, pady=(5, 5))

        # ----- Nút đặt lịch -----
        self.btn_book = ctk.CTkButton(
            form, text="✅ Đặt lịch khám", width=400, height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._handle_book_appointment,
        )
        self.btn_book.grid(row=15, column=0, columnspan=2, padx=20, pady=(10, 20))

    # ------------------------------------------------------------------
    # XỬ LÝ TÌM BỆNH VIỆN GẦN NHẤT
    # ------------------------------------------------------------------
    def _handle_find_clinic(self):
        """Gọi GeolocationService + ClinicService để tìm bệnh viện gần nhất."""
        address = self.entry_address.get().strip()
        if not address:
            self.label_clinic_result.configure(
                text="Vui lòng nhập địa chỉ trước.", text_color="orange"
            )
            return

        self.label_clinic_result.configure(text="Đang tra cứu địa chỉ...", text_color="gray")
        self.update_idletasks()

        # 1. Geocoding địa chỉ -> tọa độ
        success, result = GeolocationService.get_coordinates(address)
        if not success:
            self.label_clinic_result.configure(text=f"❌ {result}", text_color="red")
            self.user_coordinates = None
            return

        self.user_coordinates = result  # (lat, lon)

        # 2. Tìm bệnh viện gần nhất
        success, result = ClinicService.find_nearest_clinic(self.user_coordinates)
        if not success:
            self.label_clinic_result.configure(text=f"❌ {result}", text_color="red")
            self.nearest_clinic = None
            return

        clinic, distance_km = result
        self.nearest_clinic = clinic
        self.nearest_distance = distance_km

        self.label_clinic_result.configure(
            text=(
                f"✅ Bệnh viện gần nhất: {clinic.clinic_name}\n"
                f"   Địa chỉ: {clinic.address}\n"
                f"   Khoảng cách: {distance_km} km"
            ),
            text_color="lightgreen",
        )

    # ------------------------------------------------------------------
    # XỬ LÝ TÌM BÁC SĨ PHÙ HỢP
    # ------------------------------------------------------------------
    def _handle_find_doctor(self):
        """Gọi DoctorService để tìm chuyên khoa và bác sĩ phù hợp."""
        symptom = self.entry_symptom.get().strip()
        if not symptom:
            self.label_doctor_result.configure(
                text="Vui lòng nhập triệu chứng trước.", text_color="orange"
            )
            return

        # 1. Tìm chuyên khoa từ triệu chứng
        success, result = DoctorService.get_specialty_by_symptom(symptom)
        if not success:
            self.label_doctor_result.configure(text=f"❌ {result}", text_color="red")
            self.matched_specialty = None
            self.suggested_doctor = None
            return

        specialty = result
        self.matched_specialty = specialty

        # 2. Tìm bác sĩ phù hợp (ưu tiên bệnh viện gần nhất nếu đã tìm)
        nearest_clinic_id = self.nearest_clinic.clinic_id if self.nearest_clinic else None
        success, result = DoctorService.find_best_doctor(specialty, nearest_clinic_id)

        if not success:
            self.label_doctor_result.configure(text=f"❌ {result}", text_color="red")
            self.suggested_doctor = None
            return

        doctor = result
        self.suggested_doctor = doctor

        # Lấy tên bệnh viện của bác sĩ
        clinic_name = "Đang cập nhật"
        for clinic in ClinicService.get_all_clinics():
            if clinic.clinic_id == doctor.clinic_id:
                clinic_name = clinic.clinic_name
                break

        self.label_doctor_result.configure(
            text=(
                f"✅ Chuyên khoa phù hợp: {specialty}\n"
                f"   Bác sĩ đề xuất: {doctor.name}\n"
                f"   Bệnh viện: {clinic_name}"
            ),
            text_color="lightgreen",
        )

    # ------------------------------------------------------------------
    # XỬ LÝ ĐẶT LỊCH
    # ------------------------------------------------------------------
    def _handle_book_appointment(self):
        """Validate dữ liệu và gọi AppointmentService để đặt lịch."""
        self.label_message.configure(text="")

        fullname = self.entry_fullname.get().strip()
        email = self.entry_email.get().strip()
        date_str = self.entry_date.get().strip()
        time_str = self.entry_time.get().strip()

        # Phải tìm bác sĩ trước khi đặt lịch
        if self.suggested_doctor is None:
            self.label_message.configure(
                text="Vui lòng nhập triệu chứng và bấm 'Tìm bác sĩ phù hợp' trước.",
                text_color="orange",
            )
            return

        doctor_id = self.suggested_doctor.doctor_id

        success, result = AppointmentService.book_appointment(
            patient_name=fullname,
            doctor_id=doctor_id,
            date_str=date_str,
            time_str=time_str,
            email=email,
        )

        if success:
            self.label_message.configure(text="", text_color="red")
            self.on_booking_success(result)
            return

        # Xử lý các loại lỗi
        error_type = result.get("error")

        if error_type == "trung_lich":
            suggested = result.get("suggested_times", [])
            if suggested:
                suggested_str = ", ".join(suggested)
                message = (
                    f"⚠️ {result['message']}\n"
                    f"Các giờ còn trống trong ngày: {suggested_str}"
                )
            else:
                message = (
                    f"⚠️ {result['message']}\n"
                    f"Bác sĩ đã hết lịch trống trong ngày này. Vui lòng chọn ngày khác."
                )
            self.label_message.configure(text=message, text_color="orange")
        else:
            self.label_message.configure(text=f"❌ {result.get('message', 'Lỗi không xác định.')}",
                                           text_color="red")
