"""
Model: User
Đại diện cho một người dùng trong hệ thống.
"""

from dataclasses import dataclass


@dataclass
class User:
    """Đại diện cho thông tin tài khoản người dùng."""

    user_id: int
    fullname: str
    email: str
    username: str
    password: str

    def to_dict(self) -> dict:
        """Chuyển đối tượng User thành dict để lưu vào CSV."""
        return {
            "user_id": self.user_id,
            "fullname": self.fullname,
            "email": self.email,
            "username": self.username,
            "password": self.password,
        }

    @staticmethod
    def from_dict(data: dict) -> "User":
        """Tạo đối tượng User từ một dict (1 dòng dữ liệu CSV)."""
        return User(
            user_id=int(data["user_id"]),
            fullname=str(data["fullname"]),
            email=str(data["email"]),
            username=str(data["username"]),
            password=str(data["password"]),
        )
