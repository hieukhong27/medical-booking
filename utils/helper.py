"""
Module helper: chứa các hàm tiện ích chung dùng cho toàn hệ thống.
- Đọc/ghi file CSV bằng pandas (local hoặc qua GitHub API)
- Tạo ID mới tự động
- Validate dữ liệu nhập (email, rỗng,...)
"""

import os
import re
from io import StringIO
import pandas as pd

from utils import github_storage


# Đường dẫn gốc tới thư mục data (tương đối theo vị trí file helper.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def get_data_path(filename: str) -> str:
    """Trả về đường dẫn tuyệt đối tới file CSV trong thư mục data (dùng cho local)."""
    return os.path.join(DATA_DIR, filename)


def _get_repo_path(filename: str) -> str:
    """Trả về đường dẫn file trong repo GitHub, ví dụ 'data/users.csv'."""
    return f"data/{filename}"


def read_csv_safe(filename: str, columns: list) -> pd.DataFrame:
    """
    Đọc file CSV an toàn.

    Tự động chọn nguồn dữ liệu:
    - Nếu có cấu hình GitHub Storage (st.secrets: GITHUB_TOKEN, GITHUB_REPO)
      -> đọc trực tiếp từ file trong repo GitHub (dữ liệu bền, không mất khi
      Streamlit Cloud "ngủ").
    - Nếu không -> đọc file CSV local trong thư mục data/ (dùng cho desktop
      hoặc chạy thử ở máy local).

    Nếu file không tồn tại hoặc trống -> trả về DataFrame rỗng với đúng cột.

    Args:
        filename: tên file CSV (ví dụ "users.csv")
        columns: danh sách tên cột mong đợi

    Returns:
        pandas.DataFrame
    """
    try:
        if github_storage.is_github_storage_enabled():
            content, _sha = github_storage.read_file_content(_get_repo_path(filename))
            if content is None or not content.strip():
                return pd.DataFrame(columns=columns)
            df = pd.read_csv(StringIO(content), dtype=str)
        else:
            path = get_data_path(filename)
            if not os.path.exists(path):
                return pd.DataFrame(columns=columns)
            df = pd.read_csv(path, dtype=str)

        if df.empty:
            return pd.DataFrame(columns=columns)

        # Đảm bảo đủ cột, nếu thiếu thì thêm cột rỗng
        for col in columns:
            if col not in df.columns:
                df[col] = ""

        return df[columns]
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=columns)
    except Exception as e:
        raise IOError(f"Lỗi đọc file {filename}: {e}")


def write_csv_safe(filename: str, df: pd.DataFrame) -> None:
    """
    Ghi DataFrame ra file CSV.

    Tự động chọn nơi lưu:
    - Nếu có cấu hình GitHub Storage -> commit nội dung CSV mới lên repo
      GitHub (data/<filename>), đảm bảo dữ liệu bền vĩnh viễn.
    - Nếu không -> ghi file CSV local trong thư mục data/.

    Args:
        filename: tên file CSV
        df: DataFrame cần ghi
    """
    try:
        if github_storage.is_github_storage_enabled():
            csv_content = df.to_csv(index=False)
            github_storage.write_file_content(
                _get_repo_path(filename),
                csv_content,
                commit_message=f"Update {filename} from app",
            )
        else:
            path = get_data_path(filename)
            os.makedirs(DATA_DIR, exist_ok=True)
            df.to_csv(path, index=False)
    except Exception as e:
        raise IOError(f"Lỗi ghi file {filename}: {e}")


def append_row_csv(filename: str, columns: list, row: dict) -> None:
    """
    Thêm một dòng mới vào file CSV.

    Args:
        filename: tên file CSV
        columns: danh sách tên cột
        row: dict dữ liệu dòng mới
    """
    df = read_csv_safe(filename, columns)
    new_row = pd.DataFrame([row])
    df = pd.concat([df, new_row], ignore_index=True)
    write_csv_safe(filename, df)


def get_next_id(filename: str, columns: list, id_field: str) -> int:
    """
    Tạo ID tự động tiếp theo (max(id) + 1) cho 1 file CSV.

    Args:
        filename: tên file CSV
        columns: danh sách tên cột
        id_field: tên cột ID (ví dụ "user_id")

    Returns:
        int: ID mới
    """
    df = read_csv_safe(filename, columns)
    if df.empty:
        return 1

    try:
        ids = pd.to_numeric(df[id_field], errors="coerce").dropna()
        if ids.empty:
            return 1
        return int(ids.max()) + 1
    except Exception:
        return 1


def is_valid_email(email: str) -> bool:
    """Kiểm tra định dạng email cơ bản bằng regex."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def is_not_empty(*values: str) -> bool:
    """Kiểm tra tất cả giá trị truyền vào không rỗng (sau khi strip)."""
    return all(str(v).strip() != "" for v in values)


def normalize_text(text: str) -> str:
    """
    Chuẩn hóa văn bản: chuyển về chữ thường, loại bỏ khoảng trắng dư thừa.
    Dùng để so khớp triệu chứng -> chuyên khoa không phân biệt hoa/thường.
    """
    return " ".join(str(text).strip().lower().split())
