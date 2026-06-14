"""
Service: Auth Service
Xử lý logic đăng ký và đăng nhập người dùng.
Dữ liệu được lưu/đọc từ file users.csv
"""

from models.user import User
from utils.helper import (
    read_csv_safe,
    append_row_csv,
    get_next_id,
    is_valid_email,
    is_not_empty,
)


USERS_FILE = "users.csv"
USERS_COLUMNS = ["user_id", "fullname", "email", "username", "password"]


class AuthService:
    """Service xử lý xác thực: đăng ký và đăng nhập tài khoản."""

    @staticmethod
    def register(fullname: str, email: str, username: str,
                  password: str, confirm_password: str) -> tuple:
        """
        Đăng ký tài khoản mới.

        Returns:
            tuple (success: bool, message: str)
        """
        # 1. Kiểm tra dữ liệu rỗng
        if not is_not_empty(fullname, email, username, password, confirm_password):
            return False, "Vui lòng điền đầy đủ tất cả các trường."

        # 2. Kiểm tra định dạng email
        if not is_valid_email(email):
            return False, "Email không hợp lệ."

        # 3. Kiểm tra password khớp confirm password
        if password != confirm_password:
            return False, "Mật khẩu và xác nhận mật khẩu không khớp."

        # 4. Kiểm tra username đã tồn tại chưa
        df = read_csv_safe(USERS_FILE, USERS_COLUMNS)
        if not df.empty and username in df["username"].astype(str).values:
            return False, f"Username '{username}' đã tồn tại. Vui lòng chọn username khác."

        # 5. Tạo user mới
        new_id = get_next_id(USERS_FILE, USERS_COLUMNS, "user_id")
        new_user = User(
            user_id=new_id,
            fullname=fullname.strip(),
            email=email.strip(),
            username=username.strip(),
            password=password,
        )

        # 6. Lưu vào CSV
        try:
            append_row_csv(USERS_FILE, USERS_COLUMNS, new_user.to_dict())
        except IOError as e:
            return False, f"Lỗi khi lưu dữ liệu: {e}"

        return True, "Đăng ký thành công! Vui lòng đăng nhập."

    @staticmethod
    def login(username: str, password: str) -> tuple:
        """
        Đăng nhập hệ thống.

        Returns:
            tuple (success: bool, message_or_user)
            - Nếu thành công: (True, User object)
            - Nếu thất bại: (False, error_message)
        """
        if not is_not_empty(username, password):
            return False, "Vui lòng nhập username và password."

        df = read_csv_safe(USERS_FILE, USERS_COLUMNS)
        if df.empty:
            return False, "Chưa có tài khoản nào được đăng ký."

        # Tìm user theo username
        matched = df[df["username"].astype(str) == username.strip()]
        if matched.empty:
            return False, "Tài khoản không tồn tại."

        user_row = matched.iloc[0]
        if str(user_row["password"]) != password:
            return False, "Sai mật khẩu."

        user = User.from_dict(user_row.to_dict())
        return True, user
