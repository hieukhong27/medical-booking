"""
Model: Appointment
Đại diện cho một lịch khám đã đặt.
"""

from dataclasses import dataclass


@dataclass
class Appointment:
    """Đại diện cho thông tin một lịch khám."""

    appointment_id: int
    patient_name: str
    doctor_id: int
    date: str          # định dạng: YYYY-MM-DD
    time: str           # định dạng: HH:MM
    email: str
    reminder_sent: bool = False

    def to_dict(self) -> dict:
        """Chuyển đối tượng Appointment thành dict để lưu vào CSV."""
        return {
            "appointment_id": self.appointment_id,
            "patient_name": self.patient_name,
            "doctor_id": self.doctor_id,
            "date": self.date,
            "time": self.time,
            "email": self.email,
            "reminder_sent": str(self.reminder_sent),
        }

    @staticmethod
    def from_dict(data: dict) -> "Appointment":
        """Tạo đối tượng Appointment từ một dict (1 dòng dữ liệu CSV)."""
        # reminder_sent có thể lưu dưới dạng "True"/"False" hoặc True/False
        raw_reminder = data.get("reminder_sent", False)
        if isinstance(raw_reminder, str):
            reminder_sent = raw_reminder.strip().lower() == "true"
        else:
            reminder_sent = bool(raw_reminder)

        return Appointment(
            appointment_id=int(data["appointment_id"]),
            patient_name=str(data["patient_name"]),
            doctor_id=int(data["doctor_id"]),
            date=str(data["date"]),
            time=str(data["time"]),
            email=str(data["email"]),
            reminder_sent=reminder_sent,
        )
