"""
Service: Appointment Service
Xử lý logic đặt lịch khám:
- Kiểm tra trùng lịch (cùng doctor_id, date, time)
- Đề xuất giờ khám thay thế nếu trùng lịch
- Lưu lịch khám vào appointments.csv
- Gửi email xác nhận sau khi đặt lịch
- Kiểm tra & gửi email nhắc lịch trước 1 ngày
"""

from datetime import datetime

from models.appointment import Appointment
from models.doctor import Doctor
from models.clinic import Clinic
from services.email_service import EmailService
from services.doctor_service import DoctorService
from services.clinic_service import ClinicService
from utils.helper import read_csv_safe, write_csv_safe, get_next_id, is_not_empty


APPOINTMENTS_FILE = "appointments.csv"
APPOINTMENTS_COLUMNS = [
    "appointment_id", "patient_name", "doctor_id",
    "date", "time", "email", "reminder_sent",
]

# Danh sách các khung giờ khám có thể trong 1 ngày
AVAILABLE_TIME_SLOTS = [
    "08:00", "09:00", "10:00", "11:00",
    "13:30", "14:30", "15:30", "16:30",
]


class AppointmentService:
    """Service xử lý logic đặt lịch khám và quản lý lịch hẹn."""

    # ------------------------------------------------------------------
    # ĐỌC DỮ LIỆU
    # ------------------------------------------------------------------
    @staticmethod
    def get_all_appointments() -> list:
        """
        Đọc toàn bộ lịch khám từ appointments.csv.

        Returns:
            list[Appointment]
        """
        df = read_csv_safe(APPOINTMENTS_FILE, APPOINTMENTS_COLUMNS)
        appointments = []
        for _, row in df.iterrows():
            try:
                appointments.append(Appointment.from_dict(row.to_dict()))
            except (ValueError, KeyError):
                continue
        return appointments

    @staticmethod
    def get_appointments_by_email(email: str) -> list:
        """Lấy danh sách lịch khám theo email người dùng (xem lịch đã đặt)."""
        all_appointments = AppointmentService.get_all_appointments()
        return [a for a in all_appointments if a.email.strip().lower() == email.strip().lower()]

    # ------------------------------------------------------------------
    # KIỂM TRA NGÀY/GIỜ HỢP LỆ
    # ------------------------------------------------------------------
    @staticmethod
    def validate_date_time(date_str: str, time_str: str) -> tuple:
        """
        Kiểm tra định dạng ngày (YYYY-MM-DD) và giờ (HH:MM) hợp lệ,
        và ngày khám không được ở quá khứ.

        Returns:
            tuple (success: bool, message: str)
        """
        if not is_not_empty(date_str, time_str):
            return False, "Vui lòng chọn ngày và giờ khám."

        try:
            appointment_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            return False, "Ngày khám không hợp lệ. Định dạng đúng: YYYY-MM-DD."

        try:
            datetime.strptime(time_str.strip(), "%H:%M")
        except ValueError:
            return False, "Giờ khám không hợp lệ. Định dạng đúng: HH:MM."

        if appointment_date < datetime.now().date():
            return False, "Ngày khám không được ở trong quá khứ."

        return True, "OK"

    # ------------------------------------------------------------------
    # KIỂM TRA TRÙNG LỊCH
    # ------------------------------------------------------------------
    @staticmethod
    def is_slot_taken(doctor_id: int, date_str: str, time_str: str) -> bool:
        """
        Kiểm tra xem bác sĩ đã có lịch vào ngày/giờ này chưa.

        Thuật toán chống trùng lịch:
        - Lấy toàn bộ appointments
        - Lọc các bản ghi có cùng doctor_id, date, time
        - Nếu tồn tại -> đã trùng lịch

        Returns:
            bool: True nếu đã trùng lịch
        """
        all_appointments = AppointmentService.get_all_appointments()
        for appt in all_appointments:
            if (
                appt.doctor_id == int(doctor_id)
                and appt.date == date_str.strip()
                and appt.time == time_str.strip()
            ):
                return True
        return False

    @staticmethod
    def suggest_available_times(doctor_id: int, date_str: str) -> list:
        """
        Đề xuất các giờ khám còn trống cho 1 bác sĩ trong 1 ngày cụ thể.

        Thuật toán:
        - Lấy danh sách AVAILABLE_TIME_SLOTS (các khung giờ chuẩn trong ngày)
        - Lấy danh sách các giờ đã bị đặt (cùng doctor_id, date) từ appointments
        - Trả về các giờ thuộc AVAILABLE_TIME_SLOTS nhưng KHÔNG có trong
          danh sách đã đặt

        Args:
            doctor_id: id bác sĩ
            date_str: ngày khám (YYYY-MM-DD)

        Returns:
            list[str]: danh sách giờ còn trống, ví dụ ["08:00", "10:00"]
        """
        all_appointments = AppointmentService.get_all_appointments()

        booked_times = {
            appt.time
            for appt in all_appointments
            if appt.doctor_id == int(doctor_id) and appt.date == date_str.strip()
        }

        available = [slot for slot in AVAILABLE_TIME_SLOTS if slot not in booked_times]
        return available

    # ------------------------------------------------------------------
    # ĐẶT LỊCH
    # ------------------------------------------------------------------
    @staticmethod
    def book_appointment(patient_name: str, doctor_id: int, date_str: str,
                          time_str: str, email: str) -> tuple:
        """
        Đặt lịch khám mới.

        Quy trình:
        1. Validate dữ liệu đầu vào (rỗng, email, ngày/giờ hợp lệ)
        2. Kiểm tra trùng lịch (is_slot_taken)
           - Nếu trùng -> trả về danh sách giờ trống đề xuất
        3. Nếu không trùng -> lưu lịch vào appointments.csv
        4. Gửi email xác nhận

        Args:
            patient_name: tên bệnh nhân
            doctor_id: id bác sĩ
            date_str: ngày khám (YYYY-MM-DD)
            time_str: giờ khám (HH:MM)
            email: email bệnh nhân

        Returns:
            tuple (success: bool, result)
            - Nếu thành công: (True, Appointment)
            - Nếu trùng lịch: (False, {"error": "trung_lich", "suggested_times": [...]})
            - Nếu lỗi khác: (False, {"error": "khac", "message": "..."})
        """
        from utils.helper import is_valid_email

        # 1. Validate dữ liệu cơ bản
        if not is_not_empty(patient_name, email):
            return False, {"error": "khac", "message": "Vui lòng nhập đầy đủ họ tên và email."}

        if not is_valid_email(email):
            return False, {"error": "khac", "message": "Email không hợp lệ."}

        valid, msg = AppointmentService.validate_date_time(date_str, time_str)
        if not valid:
            return False, {"error": "khac", "message": msg}

        doctor = DoctorService.get_doctor_by_id(doctor_id)
        if doctor is None:
            return False, {"error": "khac", "message": "Không tìm thấy bác sĩ."}

        # 2. Kiểm tra trùng lịch
        if AppointmentService.is_slot_taken(doctor_id, date_str, time_str):
            suggested = AppointmentService.suggest_available_times(doctor_id, date_str)
            return False, {
                "error": "trung_lich",
                "message": "Bác sĩ đã có lịch vào thời gian này.",
                "suggested_times": suggested,
            }

        # 3. Lưu lịch khám mới
        new_id = get_next_id(APPOINTMENTS_FILE, APPOINTMENTS_COLUMNS, "appointment_id")
        appointment = Appointment(
            appointment_id=new_id,
            patient_name=patient_name.strip(),
            doctor_id=int(doctor_id),
            date=date_str.strip(),
            time=time_str.strip(),
            email=email.strip(),
            reminder_sent=False,
        )

        try:
            df = read_csv_safe(APPOINTMENTS_FILE, APPOINTMENTS_COLUMNS)
            new_row = appointment.to_dict()
            import pandas as pd
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            write_csv_safe(APPOINTMENTS_FILE, df)
        except IOError as e:
            return False, {"error": "khac", "message": f"Lỗi khi lưu lịch khám: {e}"}

        # 4. Gửi email xác nhận (không làm fail toàn bộ nếu gửi mail lỗi)
        clinic = AppointmentService._get_clinic_of_doctor(doctor)
        clinic_name = clinic.clinic_name if clinic else "Đang cập nhật"

        email_success, email_msg = EmailService.send_confirmation_email(
            to_email=appointment.email,
            patient_name=appointment.patient_name,
            doctor_name=doctor.name,
            specialty=doctor.specialty,
            clinic_name=clinic_name,
            date=appointment.date,
            time=appointment.time,
        )

        result = {
            "appointment": appointment,
            "doctor": doctor,
            "clinic": clinic,
            "email_sent": email_success,
            "email_message": email_msg,
        }
        return True, result

    @staticmethod
    def _get_clinic_of_doctor(doctor: Doctor) -> Clinic:
        """Helper: lấy thông tin bệnh viện của 1 bác sĩ."""
        all_clinics = ClinicService.get_all_clinics()
        for clinic in all_clinics:
            if clinic.clinic_id == doctor.clinic_id:
                return clinic
        return None

    # ------------------------------------------------------------------
    # GỬI EMAIL NHẮC LỊCH
    # ------------------------------------------------------------------
    @staticmethod
    def send_due_reminders() -> tuple:
        """
        Kiểm tra toàn bộ lịch khám và gửi email nhắc lịch cho các lịch khám
        diễn ra vào NGÀY MAI (appointment_date - today == 1 ngày) và
        chưa được gửi reminder (reminder_sent == False).

        Sau khi gửi thành công -> cập nhật reminder_sent = True
        để tránh gửi lặp lại nhiều lần.

        Returns:
            tuple (sent_count: int, results: list[dict])
            results: danh sách thông tin các email đã/được thử gửi
        """
        df = read_csv_safe(APPOINTMENTS_FILE, APPOINTMENTS_COLUMNS)
        if df.empty:
            return 0, []

        today = datetime.now().date()
        sent_count = 0
        results = []

        for idx, row in df.iterrows():
            try:
                appointment = Appointment.from_dict(row.to_dict())
            except (ValueError, KeyError):
                continue

            # Bỏ qua nếu đã gửi reminder rồi
            if appointment.reminder_sent:
                continue

            try:
                appt_date = datetime.strptime(appointment.date, "%Y-%m-%d").date()
            except ValueError:
                continue

            # Logic: appointment_date - today == 1 ngày
            delta_days = (appt_date - today).days
            if delta_days != 1:
                continue

            doctor = DoctorService.get_doctor_by_id(appointment.doctor_id)
            doctor_name = doctor.name if doctor else "Bác sĩ"

            success, msg = EmailService.send_reminder_email(
                to_email=appointment.email,
                patient_name=appointment.patient_name,
                doctor_name=doctor_name,
                date=appointment.date,
                time=appointment.time,
            )

            results.append({
                "appointment_id": appointment.appointment_id,
                "email": appointment.email,
                "success": success,
                "message": msg,
            })

            if success:
                # Cập nhật reminder_sent = True để tránh gửi lặp
                # (DataFrame được đọc với dtype=str nên gán chuỗi "True")
                df.at[idx, "reminder_sent"] = "True"
                sent_count += 1

        if sent_count > 0:
            write_csv_safe(APPOINTMENTS_FILE, df)

        return sent_count, results
