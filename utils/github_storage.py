"""
Module: GitHub Storage
Cho phép đọc/ghi file CSV trực tiếp lên 1 repo GitHub thông qua GitHub REST API.

Mục đích:
- Streamlit Community Cloud có filesystem TẠM THỜI (ephemeral): mỗi khi app
  "ngủ" hoặc redeploy, mọi thay đổi ghi vào file local sẽ bị mất.
- Bằng cách commit file CSV lên GitHub mỗi khi có thay đổi (đăng ký user mới,
  đặt lịch mới...), dữ liệu được lưu bền vĩnh viễn trên GitHub.
- Khi app khởi động lại, đọc CSV mới nhất từ GitHub -> không mất dữ liệu.

Cấu hình (đặt trong Streamlit Secrets, KHÔNG hardcode trong code):
    GITHUB_TOKEN  = "ghp_xxx..."          # Personal Access Token (scope: repo)
    GITHUB_REPO   = "username/medical-booking"
    GITHUB_BRANCH = "main"                 # (tùy chọn, mặc định "main")

Nếu KHÔNG có cấu hình GitHub (chạy desktop / chạy local) -> module này
không được dùng, hệ thống tự fallback về đọc/ghi file local (xem helper.py).
"""

import base64
import json
import requests


GITHUB_API_BASE = "https://api.github.com"


def is_github_storage_enabled() -> bool:
    """
    Kiểm tra xem có cấu hình GitHub Storage (qua st.secrets) hay không.

    Returns:
        bool: True nếu đã cấu hình đầy đủ GITHUB_TOKEN và GITHUB_REPO.
    """
    try:
        import streamlit as st
        token = st.secrets.get("GITHUB_TOKEN", None)
        repo = st.secrets.get("GITHUB_REPO", None)
        return bool(token) and bool(repo)
    except Exception:
        # Không chạy trong môi trường Streamlit, hoặc chưa cấu hình secrets
        return False


def _get_config() -> dict:
    """Lấy cấu hình GitHub từ st.secrets."""
    import streamlit as st
    return {
        "token": st.secrets["GITHUB_TOKEN"],
        "repo": st.secrets["GITHUB_REPO"],
        "branch": st.secrets.get("GITHUB_BRANCH", "main"),
    }


def _headers(token: str) -> dict:
    """Header chuẩn cho GitHub API request."""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def read_file_content(path_in_repo: str) -> tuple:
    """
    Đọc nội dung text của 1 file trong repo GitHub.

    Args:
        path_in_repo: đường dẫn file trong repo, ví dụ "data/users.csv"

    Returns:
        tuple (content: str hoặc None, sha: str hoặc None)
        - Nếu file không tồn tại -> (None, None)
    """
    config = _get_config()
    url = f"{GITHUB_API_BASE}/repos/{config['repo']}/contents/{path_in_repo}"
    params = {"ref": config["branch"]}

    response = requests.get(url, headers=_headers(config["token"]), params=params, timeout=15)

    if response.status_code == 404:
        return None, None

    response.raise_for_status()
    data = response.json()

    content_b64 = data["content"]
    sha = data["sha"]
    content = base64.b64decode(content_b64).decode("utf-8")
    return content, sha


def write_file_content(path_in_repo: str, content: str, commit_message: str) -> None:
    """
    Ghi (tạo mới hoặc cập nhật) 1 file trong repo GitHub bằng cách tạo commit mới.

    Args:
        path_in_repo: đường dẫn file trong repo, ví dụ "data/users.csv"
        content: nội dung text mới của file (toàn bộ nội dung CSV)
        commit_message: message cho commit

    Raises:
        IOError: nếu có lỗi khi gọi GitHub API
    """
    config = _get_config()
    url = f"{GITHUB_API_BASE}/repos/{config['repo']}/contents/{path_in_repo}"

    # Lấy sha hiện tại của file (nếu có) - bắt buộc khi update file đã tồn tại
    _, sha = read_file_content(path_in_repo)

    content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": commit_message,
        "content": content_b64,
        "branch": config["branch"],
    }
    if sha:
        payload["sha"] = sha

    response = requests.put(
        url, headers=_headers(config["token"]), data=json.dumps(payload), timeout=15
    )

    if response.status_code not in (200, 201):
        raise IOError(
            f"Lỗi ghi file '{path_in_repo}' lên GitHub: "
            f"{response.status_code} - {response.text}"
        )
