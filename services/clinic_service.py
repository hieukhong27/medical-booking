"""
Service: Clinic Service
Xử lý logic liên quan tới bệnh viện/phòng khám:
- Đọc danh sách bệnh viện từ clinics.csv
- Tìm bệnh viện gần nhất dựa trên tọa độ người dùng (geopy.distance.geodesic)
"""

from geopy.distance import geodesic

from models.clinic import Clinic
from utils.helper import read_csv_safe


CLINICS_FILE = "clinics.csv"
CLINICS_COLUMNS = ["clinic_id", "clinic_name", "address", "latitude", "longitude"]


class ClinicService:
    """Service xử lý dữ liệu bệnh viện/phòng khám."""

    @staticmethod
    def get_all_clinics() -> list:
        """
        Đọc toàn bộ danh sách bệnh viện từ clinics.csv.

        Returns:
            list[Clinic]
        """
        df = read_csv_safe(CLINICS_FILE, CLINICS_COLUMNS)
        clinics = []
        for _, row in df.iterrows():
            try:
                clinics.append(Clinic.from_dict(row.to_dict()))
            except (ValueError, KeyError):
                # Bỏ qua dòng dữ liệu lỗi
                continue
        return clinics

    @staticmethod
    def find_nearest_clinic(user_coordinates: tuple) -> tuple:
        """
        Tìm bệnh viện gần nhất so với tọa độ người dùng.

        Thuật toán:
        - Lấy toàn bộ danh sách bệnh viện
        - Với mỗi bệnh viện, tính khoảng cách geodesic (km) giữa
          tọa độ người dùng và tọa độ bệnh viện
        - Trả về bệnh viện có khoảng cách nhỏ nhất

        Args:
            user_coordinates: tuple (latitude, longitude) của người dùng

        Returns:
            tuple (success: bool, result)
            - Nếu thành công: (True, (Clinic, distance_km))
            - Nếu thất bại: (False, error_message)
        """
        clinics = ClinicService.get_all_clinics()
        if not clinics:
            return False, "Không có dữ liệu bệnh viện trong hệ thống."

        nearest_clinic = None
        min_distance = None

        for clinic in clinics:
            try:
                distance_km = geodesic(user_coordinates, clinic.coordinates).km
            except Exception:
                continue

            if min_distance is None or distance_km < min_distance:
                min_distance = distance_km
                nearest_clinic = clinic

        if nearest_clinic is None:
            return False, "Không thể tính khoảng cách tới bất kỳ bệnh viện nào."

        return True, (nearest_clinic, round(min_distance, 2))

    @staticmethod
    def get_clinics_sorted_by_distance(user_coordinates: tuple) -> list:
        """
        Trả về danh sách tất cả bệnh viện, sắp xếp theo khoảng cách tăng dần
        so với tọa độ người dùng.

        Args:
            user_coordinates: tuple (latitude, longitude)

        Returns:
            list[tuple(Clinic, distance_km)]
        """
        clinics = ClinicService.get_all_clinics()
        result = []

        for clinic in clinics:
            try:
                distance_km = geodesic(user_coordinates, clinic.coordinates).km
                result.append((clinic, round(distance_km, 2)))
            except Exception:
                continue

        result.sort(key=lambda item: item[1])
        return result
