"""
Service: Doctor Service
Xử lý logic liên quan tới bác sĩ và chuyên khoa:
- Tra cứu chuyên khoa phù hợp dựa trên triệu chứng (specialties.csv)
- Tìm bác sĩ phù hợp theo chuyên khoa, ưu tiên bác sĩ thuộc bệnh viện gần nhất
"""

from models.doctor import Doctor
from utils.helper import read_csv_safe, normalize_text


SPECIALTIES_FILE = "specialties.csv"
SPECIALTIES_COLUMNS = ["symptom", "specialty"]

DOCTORS_FILE = "doctors.csv"
DOCTORS_COLUMNS = ["doctor_id", "name", "specialty", "clinic_id"]


class DoctorService:
    """Service xử lý dữ liệu bác sĩ và tra cứu chuyên khoa theo triệu chứng."""

    @staticmethod
    def get_specialty_by_symptom(symptom: str) -> tuple:
        """
        Tìm chuyên khoa phù hợp dựa trên triệu chứng người dùng nhập.

        Thuật toán (KHÔNG hardcode if/else):
        - Đọc bảng ánh xạ symptom -> specialty từ specialties.csv
        - Chuẩn hóa (lowercase, strip) cả triệu chứng nhập vào và
          dữ liệu trong CSV để so khớp
        - Hỗ trợ khớp gần đúng: nếu từ khóa triệu chứng nằm trong
          (hoặc chứa) chuỗi triệu chứng trong CSV thì coi là khớp

        Args:
            symptom: triệu chứng người dùng nhập (ví dụ "dau hong")

        Returns:
            tuple (success: bool, result)
            - Nếu thành công: (True, specialty_name)
            - Nếu thất bại: (False, error_message)
        """
        if not symptom or not symptom.strip():
            return False, "Vui lòng nhập triệu chứng."

        df = read_csv_safe(SPECIALTIES_FILE, SPECIALTIES_COLUMNS)
        if df.empty:
            return False, "Hệ thống chưa có dữ liệu chuyên khoa."

        user_symptom = normalize_text(symptom)

        # Bước 1: tìm khớp chính xác
        for _, row in df.iterrows():
            csv_symptom = normalize_text(row["symptom"])
            if csv_symptom == user_symptom:
                return True, str(row["specialty"]).strip()

        # Bước 2: tìm khớp gần đúng (chứa nhau)
        for _, row in df.iterrows():
            csv_symptom = normalize_text(row["symptom"])
            if csv_symptom in user_symptom or user_symptom in csv_symptom:
                return True, str(row["specialty"]).strip()

        return False, (
            "Không tìm thấy chuyên khoa phù hợp với triệu chứng này. "
            "Vui lòng thử mô tả khác (ví dụ: dau hong, dau bung, dau dau...)."
        )

    @staticmethod
    def get_all_doctors() -> list:
        """
        Đọc toàn bộ danh sách bác sĩ từ doctors.csv.

        Returns:
            list[Doctor]
        """
        df = read_csv_safe(DOCTORS_FILE, DOCTORS_COLUMNS)
        doctors = []
        for _, row in df.iterrows():
            try:
                doctors.append(Doctor.from_dict(row.to_dict()))
            except (ValueError, KeyError):
                continue
        return doctors

    @staticmethod
    def get_doctors_by_specialty(specialty: str) -> list:
        """
        Lấy danh sách bác sĩ theo chuyên khoa.

        Args:
            specialty: tên chuyên khoa (ví dụ "Tai mui hong")

        Returns:
            list[Doctor]
        """
        all_doctors = DoctorService.get_all_doctors()
        target = normalize_text(specialty)
        return [d for d in all_doctors if normalize_text(d.specialty) == target]

    @staticmethod
    def get_doctor_by_id(doctor_id: int) -> Doctor:
        """Tìm bác sĩ theo doctor_id. Trả về None nếu không tìm thấy."""
        all_doctors = DoctorService.get_all_doctors()
        for d in all_doctors:
            if d.doctor_id == int(doctor_id):
                return d
        return None

    @staticmethod
    def find_best_doctor(specialty: str, nearest_clinic_id: int = None) -> tuple:
        """
        Tìm bác sĩ phù hợp nhất:
        - Đúng chuyên khoa
        - Ưu tiên bác sĩ thuộc bệnh viện gần nhất (nearest_clinic_id)
          Nếu không có bác sĩ nào ở bệnh viện gần nhất, chọn bác sĩ
          đầu tiên cùng chuyên khoa (ở bệnh viện khác).

        Args:
            specialty: chuyên khoa cần tìm
            nearest_clinic_id: clinic_id của bệnh viện gần nhất (có thể None)

        Returns:
            tuple (success: bool, result)
            - Nếu thành công: (True, Doctor)
            - Nếu thất bại: (False, error_message)
        """
        candidates = DoctorService.get_doctors_by_specialty(specialty)
        if not candidates:
            return False, f"Không tìm thấy bác sĩ chuyên khoa '{specialty}'."

        # Ưu tiên bác sĩ thuộc bệnh viện gần nhất
        if nearest_clinic_id is not None:
            for doctor in candidates:
                if doctor.clinic_id == int(nearest_clinic_id):
                    return True, doctor

        # Nếu không có -> trả về bác sĩ đầu tiên cùng chuyên khoa
        return True, candidates[0]
