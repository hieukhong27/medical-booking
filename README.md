# Hệ thống Đặt lịch khám sức khỏe online

Ứng dụng có 2 phiên bản giao diện, dùng chung toàn bộ `services/`, `models/`, `utils/`:

- **Desktop (CustomTkinter)**: `main.py`
- **Web (Streamlit)**: `streamlit_app.py` — chạy được trong trình duyệt, deploy miễn phí qua GitHub + Streamlit Cloud.

---

## 0. CHẠY BẢN WEB (STREAMLIT) — DEPLOY LÊN INTERNET

### Chạy thử ở máy local:
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
Trình duyệt tự mở `http://localhost:8501`.

### Đưa lên Internet bằng GitHub + Streamlit Community Cloud (miễn phí):

1. Tạo repo mới trên GitHub, push toàn bộ project lên (bao gồm `streamlit_app.py`, `requirements.txt`, toàn bộ `services/`, `models/`, `utils/`, `data/`).
2. Vào https://share.streamlit.io → đăng nhập bằng GitHub.
3. Bấm **"New app"** → chọn repo vừa tạo.
4. Mục **"Main file path"** điền: `streamlit_app.py`
5. Bấm **Deploy** → chờ vài phút → Streamlit cấp cho bạn 1 link dạng `https://ten-app.streamlit.app`, ai có link đều dùng được.

### ⚠️ LƯU DỮ LIỆU CSV BỀN VĨNH VIỄN (GitHub Storage) — KHUYẾN NGHỊ CHO BÀI TẬP LỚN

Mặc định, filesystem của Streamlit Cloud là **tạm thời (ephemeral)**: mỗi khi app
"ngủ" hoặc redeploy, các thay đổi ghi vào CSV (user mới đăng ký, lịch đặt mới...)
sẽ **bị mất**.

Để dữ liệu CSV được lưu **bền vĩnh viễn**, hệ thống hỗ trợ tự động commit file CSV
lên repo GitHub mỗi khi có thay đổi (qua `utils/github_storage.py`). Cách bật:

**1. Tạo Personal Access Token (PAT) trên GitHub:**
- Vào https://github.com/settings/tokens → **Generate new token (classic)**.
- Chỉ tick quyền **`repo`** (Full control of private repositories).
- Generate → copy token (dạng `ghp_xxxxxxxxxxxx`), chỉ hiện 1 lần.

**2. Vào app trên Streamlit Cloud → Settings → Secrets, thêm:**
```toml
GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"
GITHUB_REPO = "ten-user-github/ten-repo"
GITHUB_BRANCH = "main"
```

**3. Lưu Secrets → Reboot app.**

Sau khi cấu hình:
- Mọi lần `read_csv_safe()` sẽ đọc file `data/<tên file>.csv` trực tiếp từ repo GitHub (qua GitHub API).
- Mọi lần `write_csv_safe()` sẽ tự động **commit** nội dung CSV mới lên repo (commit message dạng "Update users.csv from app").
- Khi app ngủ/redeploy, dữ liệu vẫn còn trên GitHub → đọc lại đúng dữ liệu mới nhất.

**Khi chạy desktop (`main.py`) hoặc chạy local không có Secrets**, hệ thống tự động
fallback về đọc/ghi file CSV local trong `data/` như bình thường — không cần sửa gì thêm.

> Lưu ý: mỗi lần ghi sẽ tạo 1 commit mới trên GitHub. Với bài tập lớn (lượng truy
> cập nhỏ) thì không vấn đề gì, nhưng không phù hợp cho hệ thống có lượng ghi rất lớn/giây.

### Cấu hình Gmail trên Streamlit Cloud:
Không nên để `SENDER_EMAIL`/`SENDER_APP_PASSWORD` trực tiếp trong code khi public repo. Thay vào đó:
1. Trong Streamlit Cloud, vào app → **Settings → Secrets**, thêm:
   ```toml
   SENDER_EMAIL = "your_email@gmail.com"
   SENDER_APP_PASSWORD = "your_app_password"
   ```
2. Sửa `services/email_service.py`, thay 2 dòng cấu hình bằng:
   ```python
   import streamlit as st
   SENDER_EMAIL = st.secrets.get("SENDER_EMAIL", "your_email@gmail.com")
   SENDER_APP_PASSWORD = st.secrets.get("SENDER_APP_PASSWORD", "your_app_password")
   ```

---

## 1. CẤU TRÚC PROJECT

```
medical_booking/
│
├── data/                   # Dữ liệu CSV
│   ├── users.csv
│   ├── clinics.csv
│   ├── doctors.csv
│   ├── appointments.csv
│   └── specialties.csv
│
├── gui/                     # Giao diện (KHÔNG chứa business logic)
│   ├── login_window.py
│   ├── register_window.py
│   ├── dashboard.py
│   ├── booking_form.py
│   └── result_window.py
│
├── services/                # Business logic (Clean Architecture)
│   ├── auth_service.py
│   ├── geolocation_service.py
│   ├── clinic_service.py
│   ├── doctor_service.py
│   ├── appointment_service.py
│   └── email_service.py
│
├── models/                  # Các class dữ liệu (dataclass)
│   ├── user.py
│   ├── clinic.py
│   ├── doctor.py
│   └── appointment.py
│
├── utils/
│   └── helper.py            # Hàm tiện ích: đọc/ghi CSV, validate...
│
├── main.py                  # Entry point bản desktop (CustomTkinter)
├── streamlit_app.py         # Entry point bản web (Streamlit)
└── requirements.txt
```

---

## 2. CÀI ĐẶT THƯ VIỆN

Yêu cầu Python 3.9+.

```bash
cd medical_booking
pip install -r requirements.txt
```

`requirements.txt` gồm:
```
customtkinter>=5.2.0
pandas>=2.0.0
requests>=2.31.0
geopy>=2.4.0
```

---

## 3. CHẠY ỨNG DỤNG

```bash
python main.py
```

Cửa sổ ứng dụng (1000x650, dark mode) sẽ hiển thị màn hình **Đăng nhập**.

Tài khoản mẫu có sẵn trong `users.csv`:
- Username: `vana`
- Password: `123456`

---

## 4. CẤU HÌNH GỬI EMAIL (GMAIL SMTP)

Mở file `services/email_service.py`, sửa 2 biến:

```python
SENDER_EMAIL = "your_email@gmail.com"
SENDER_APP_PASSWORD = "your_app_password"
```

### Cách lấy App Password Gmail:
1. Vào tài khoản Google → **Bảo mật (Security)**.
2. Bật **Xác minh 2 bước (2-Step Verification)** (bắt buộc).
3. Vào **Mật khẩu ứng dụng (App passwords)**.
4. Tạo mật khẩu ứng dụng mới (chọn "Mail" hoặc "Other") → Google sinh ra 1 chuỗi 16 ký tự.
5. Dán chuỗi đó vào `SENDER_APP_PASSWORD` (không dùng password Gmail thường vì sẽ bị từ chối SMTPAuthenticationError).

Code sử dụng `smtplib.SMTP("smtp.gmail.com", 587)` với `server.starttls()` để bảo mật kết nối, sau đó `server.login()` và `server.send_message()` bằng `email.message.EmailMessage`.

Nếu chưa cấu hình, hệ thống vẫn đặt lịch thành công, chỉ hiển thị cảnh báo "không gửi được email" — không làm crash ứng dụng.

---

## 5. GIẢI THÍCH FLOW HỆ THỐNG

1. **Đăng ký / Đăng nhập** → xác thực qua `auth_service.py`, dữ liệu trong `users.csv`.
2. Sau khi đăng nhập → **Dashboard** hiển thị thông tin user + 3 nút: Đặt lịch khám, Lịch đã đặt, Đăng xuất.
3. **Form đặt lịch** (`booking_form.py`):
   - Người dùng nhập **địa chỉ** → bấm "Tìm bệnh viện gần nhất" → gọi `geolocation_service` (Nominatim) lấy lat/lon → gọi `clinic_service` tìm bệnh viện gần nhất bằng `geopy.distance.geodesic`.
   - Người dùng nhập **triệu chứng** → bấm "Tìm bác sĩ phù hợp" → `doctor_service` tra `specialties.csv` để suy ra chuyên khoa, sau đó chọn bác sĩ đúng chuyên khoa, ưu tiên bác sĩ ở bệnh viện gần nhất vừa tìm.
   - Người dùng chọn ngày/giờ → bấm "Đặt lịch khám" → `appointment_service.book_appointment()`:
     - Validate dữ liệu (rỗng, email, ngày/giờ hợp lệ, không ở quá khứ).
     - Kiểm tra trùng lịch (`is_slot_taken`).
     - Nếu trùng → trả về danh sách giờ trống đề xuất (`suggest_available_times`).
     - Nếu không trùng → lưu vào `appointments.csv` và gửi email xác nhận.
4. **Kết quả đặt lịch** hiển thị ở `result_window.py` (thông tin bác sĩ, bệnh viện, ngày giờ, trạng thái email).
5. **Xem lịch đã đặt**: lọc `appointments.csv` theo email người dùng, hiển thị bảng kèm trạng thái nhắc lịch.
6. **Reminder email**: một thread nền (`main.py`) chạy định kỳ gọi `send_due_reminders()` để gửi email nhắc lịch trước 1 ngày.

---

## 6. GIẢI THÍCH GEOLOCATION SYSTEM

- Sử dụng **OpenStreetMap Nominatim API** (miễn phí, không cần API key, không billing):
  `https://nominatim.openstreetmap.org/search?q=<địa chỉ>&format=json&limit=1`
- `geolocation_service.py` gửi request bằng `requests`, kèm header `User-Agent` (Nominatim yêu cầu).
- Kết quả JSON trả về `lat`, `lon` của địa chỉ khớp đầu tiên.
- Nếu không tìm thấy địa chỉ, hoặc lỗi mạng/timeout → trả về thông báo lỗi rõ ràng, GUI hiển thị cho người dùng, không crash app.

---

## 7. THUẬT TOÁN TÌM BỆNH VIỆN GẦN NHẤT

File: `services/clinic_service.py` → `find_nearest_clinic()`

```
Input: tọa độ người dùng (lat_user, lon_user)

1. Đọc toàn bộ clinics.csv → danh sách Clinic (clinic_id, name, address, lat, lon)
2. Với mỗi clinic:
     distance = geodesic((lat_user, lon_user), (clinic.lat, clinic.lon)).km
3. Tìm clinic có distance nhỏ nhất
4. Trả về (clinic, distance_km)
```

- `geodesic` từ `geopy.distance` tính khoảng cách thực tế trên bề mặt Trái Đất (đơn vị km), chính xác hơn khoảng cách Euclid thông thường.
- Độ phức tạp: O(n) với n = số bệnh viện trong CSV.

---

## 8. THUẬT TOÁN CHỐNG TRÙNG LỊCH

File: `services/appointment_service.py` → `is_slot_taken()` và `suggest_available_times()`

**Kiểm tra trùng lịch:**
```
Với mỗi appointment trong appointments.csv:
    Nếu appointment.doctor_id == doctor_id
       AND appointment.date == date
       AND appointment.time == time
    → đã trùng lịch (return True)
```

**Đề xuất giờ thay thế:**
```
AVAILABLE_TIME_SLOTS = [08:00, 09:00, 10:00, 11:00, 13:30, 14:30, 15:30, 16:30]

booked_times = { tất cả appointment.time có cùng doctor_id và date }

available_times = AVAILABLE_TIME_SLOTS - booked_times
```

→ Nếu đặt lịch trùng, hệ thống tự động liệt kê các giờ còn trống trong ngày đó cho bác sĩ đó, giúp người dùng chọn giờ khác ngay.

---

## 9. GIẢI THÍCH REMINDER EMAIL SYSTEM

File: `services/appointment_service.py` → `send_due_reminders()`
Được gọi định kỳ bởi thread nền trong `main.py`.

```
today = ngày hiện tại

Với mỗi appointment trong appointments.csv:
    Nếu appointment.reminder_sent == True → bỏ qua (đã gửi)
    delta = appointment.date - today (số ngày)
    Nếu delta == 1:
        → gửi email nhắc lịch (send_reminder_email)
        Nếu gửi thành công:
            → cập nhật appointment.reminder_sent = True
            → ghi lại vào appointments.csv
```

- Cờ `reminder_sent` đảm bảo mỗi lịch khám **chỉ nhận 1 email nhắc lịch duy nhất**, dù thread chạy lại nhiều lần.
- Thread nền (`daemon thread`) chạy mỗi `REMINDER_CHECK_INTERVAL_SECONDS` (mặc định 3600s = 1 giờ), không chặn giao diện chính.

---

## 10. GIẢI THÍCH LOGIN / REGISTER SYSTEM

File: `services/auth_service.py`

**Đăng ký (`register`)**:
1. Kiểm tra không có trường nào rỗng.
2. Kiểm tra định dạng email hợp lệ (regex).
3. Kiểm tra `password == confirm_password`.
4. Kiểm tra `username` chưa tồn tại trong `users.csv`.
5. Sinh `user_id` mới = `max(user_id hiện có) + 1`.
6. Ghi dòng mới vào `users.csv`.

**Đăng nhập (`login`)**:
1. Kiểm tra username/password không rỗng.
2. Tìm dòng trong `users.csv` có `username` khớp.
3. So sánh `password` (plaintext, theo đúng yêu cầu CSV của đề bài).
4. Nếu khớp → trả về object `User`, GUI chuyển sang Dashboard.
5. Nếu sai → trả về thông báo lỗi cụ thể ("Tài khoản không tồn tại" / "Sai mật khẩu").

> **Lưu ý bảo mật**: theo yêu cầu đề bài, password lưu dạng plaintext trong CSV để đơn giản hóa. Trong môi trường thực tế nên dùng hashing (bcrypt/argon2) trước khi lưu.

---

## 11. THUẬT TOÁN TRIỆU CHỨNG → CHUYÊN KHOA (KHÔNG HARDCODE)

File: `services/doctor_service.py` → `get_specialty_by_symptom()`

```
Đọc specialties.csv (symptom, specialty)
Chuẩn hóa (lowercase, trim) triệu chứng người nhập và dữ liệu CSV

Bước 1: tìm khớp chính xác (symptom_user == symptom_csv)
Bước 2: nếu không có, tìm khớp gần đúng (chuỗi này chứa chuỗi kia)

→ Trả về specialty tương ứng, hoặc thông báo không tìm thấy
```

Toàn bộ ánh xạ nằm trong file CSV → có thể mở rộng thêm triệu chứng/chuyên khoa mà **không cần sửa code**.

---

## 12. CHỌN BÁC SĨ PHÙ HỢP

File: `services/doctor_service.py` → `find_best_doctor(specialty, nearest_clinic_id)`

```
candidates = tất cả bác sĩ có specialty khớp

Nếu nearest_clinic_id có giá trị:
    Tìm bác sĩ trong candidates có clinic_id == nearest_clinic_id
    → nếu có, trả về bác sĩ đó (ưu tiên gần nhất)

Nếu không có bác sĩ ở bệnh viện gần nhất:
    → trả về bác sĩ đầu tiên cùng chuyên khoa (ở bệnh viện khác)
```
