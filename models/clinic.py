"""
Model: Clinic
Đại diện cho một bệnh viện / phòng khám.
"""

from dataclasses import dataclass


@dataclass
class Clinic:
    """Đại diện cho thông tin bệnh viện/phòng khám."""

    clinic_id: int
    clinic_name: str
    address: str
    latitude: float
    longitude: float

    def to_dict(self) -> dict:
        """Chuyển đối tượng Clinic thành dict."""
        return {
            "clinic_id": self.clinic_id,
            "clinic_name": self.clinic_name,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    @staticmethod
    def from_dict(data: dict) -> "Clinic":
        """Tạo đối tượng Clinic từ một dict (1 dòng dữ liệu CSV)."""
        return Clinic(
            clinic_id=int(data["clinic_id"]),
            clinic_name=str(data["clinic_name"]),
            address=str(data["address"]),
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
        )

    @property
    def coordinates(self) -> tuple:
        """Trả về tuple (latitude, longitude) - dùng cho tính khoảng cách."""
        return (self.latitude, self.longitude)
