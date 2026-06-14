"""
Service: Geolocation Service
Sử dụng OpenStreetMap Nominatim API (miễn phí, không cần API key)
để chuyển địa chỉ (dạng text) thành tọa độ latitude/longitude.
"""

import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Nominatim yêu cầu phải có User-Agent hợp lệ trong header,
# nếu không request có thể bị từ chối.
HEADERS = {
    "User-Agent": "medical_booking_app (educational project)"
}


class GeolocationService:
    """Service xử lý chuyển đổi địa chỉ <-> tọa độ địa lý."""

    @staticmethod
    def get_coordinates(address: str) -> tuple:
        """
        Chuyển một địa chỉ dạng text thành tọa độ (latitude, longitude).

        Args:
            address: địa chỉ cần tra cứu (ví dụ "Cau Giay Ha Noi")

        Returns:
            tuple (success: bool, result)
            - Nếu thành công: (True, (lat, lon))
            - Nếu thất bại: (False, error_message)
        """
        if not address or not address.strip():
            return False, "Địa chỉ không được để trống."

        params = {
            "q": address.strip(),
            "format": "json",
            "limit": 1,
        }

        try:
            response = requests.get(
                NOMINATIM_URL,
                params=params,
                headers=HEADERS,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            if not data:
                return False, "Không tìm thấy địa chỉ này. Vui lòng nhập địa chỉ khác."

            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return True, (lat, lon)

        except requests.exceptions.Timeout:
            return False, "Hết thời gian chờ kết nối tới dịch vụ định vị. Vui lòng thử lại."
        except requests.exceptions.ConnectionError:
            return False, "Không thể kết nối tới dịch vụ định vị. Vui lòng kiểm tra Internet."
        except requests.exceptions.RequestException as e:
            return False, f"Lỗi khi gọi dịch vụ định vị: {e}"
        except (KeyError, ValueError, IndexError) as e:
            return False, f"Lỗi xử lý kết quả định vị: {e}"
