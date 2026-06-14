"""
Model: Doctor
Đại diện cho một bác sĩ.
"""

from dataclasses import dataclass


@dataclass
class Doctor:
    """Đại diện cho thông tin bác sĩ."""

    doctor_id: int
    name: str
    specialty: str
    clinic_id: int

    def to_dict(self) -> dict:
        """Chuyển đối tượng Doctor thành dict."""
        return {
            "doctor_id": self.doctor_id,
            "name": self.name,
            "specialty": self.specialty,
            "clinic_id": self.clinic_id,
        }

    @staticmethod
    def from_dict(data: dict) -> "Doctor":
        """Tạo đối tượng Doctor từ một dict (1 dòng dữ liệu CSV)."""
        return Doctor(
            doctor_id=int(data["doctor_id"]),
            name=str(data["name"]),
            specialty=str(data["specialty"]),
            clinic_id=int(data["clinic_id"]),
        )
