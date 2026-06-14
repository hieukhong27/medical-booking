"""
Streamlit Web App: Hệ thống Đặt lịch khám sức khỏe online
Toàn bộ business logic vẫn nằm trong services/ và models/ (Clean Architecture),
file này chỉ đóng vai trò GUI (giao diện web) tương đương các file cũ trong gui/.
"""

import streamlit as st

from services.auth_service import AuthService
from services.geolocation_service import GeolocationService
from services.clinic_service import ClinicService
from services.doctor_service import DoctorService
from services.appointment_service import AppointmentService, AVAILABLE_TIME_SLOTS


# ----------------------------------------------------------------------
# CẤU HÌNH TRANG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Đặt lịch khám sức khỏe online",
    page_icon="🏥",
    layout="centered",
)


# ----------------------------------------------------------------------
# KHỞI TẠO SESSION STATE
# ----------------------------------------------------------------------
def init_session_state():
    """Khởi tạo các biến lưu trạng thái phiên làm việc (giống biến toàn cục của app desktop)."""
    if "current_user" not in st.session_state:
        st.session_state.current_user = None  # User object khi đã đăng nhập

    if "page" not in st.session_state:
        st.session_state.page = "login"  # login | register | dashboard | booking | result | history

    # Kết quả tra cứu trung gian trong form đặt lịch
    if "user_coordinates" not in st.session_state:
        st.session_state.user_coordinates = None
    if "nearest_clinic" not in st.session_state:
        st.session_state.nearest_clinic = None
    if "nearest_distance" not in st.session_state:
        st.session_state.nearest_distance = None
    if "matched_specialty" not in st.session_state:
        st.session_state.matched_specialty = None
    if "suggested_doctor" not in st.session_state:
        st.session_state.suggested_doctor = None

    # Kết quả đặt lịch thành công gần nhất (để hiển thị ở trang result)
    if "booking_result" not in st.session_state:
        st.session_state.booking_result = None
    # Đề xuất giờ thay thế khi trùng lịch
    if "suggested_times" not in st.session_state:
        st.session_state.suggested_times = None


def go_to(page_name: str):
    """Chuyển trang (tương đương _switch_frame trong bản desktop)."""
    st.session_state.page = page_name


def reset_booking_state():
    """Reset các biến tra cứu trung gian khi vào lại form đặt lịch."""
    st.session_state.user_coordinates = None
    st.session_state.nearest_clinic = None
    st.session_state.nearest_distance = None
    st.session_state.matched_specialty = None
    st.session_state.suggested_doctor = None
    st.session_state.suggested_times = None


# ----------------------------------------------------------------------
# TRANG: ĐĂNG NHẬP
# ----------------------------------------------------------------------
def render_login_page():
    st.title("🏥 Đặt lịch khám sức khỏe online")
    st.subheader("Đăng nhập")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Đăng nhập", use_container_width=True)

    if submitted:
        success, result = AuthService.login(username, password)
        if success:
            st.session_state.current_user = result
            go_to("dashboard")
            st.rerun()
        else:
            st.error(result)

    st.divider()
    if st.button("Chưa có tài khoản? Đăng ký ngay", use_container_width=True):
        go_to("register")
        st.rerun()


# ----------------------------------------------------------------------
# TRANG: ĐĂNG KÝ
# ----------------------------------------------------------------------
def render_register_page():
    st.title("🏥 Đặt lịch khám sức khỏe online")
    st.subheader("Đăng ký tài khoản")

    with st.form("register_form"):
        fullname = st.text_input("Họ tên")
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Đăng ký", use_container_width=True)

    if submitted:
        success, message = AuthService.register(
            fullname, email, username, password, confirm_password
        )
        if success:
            st.success(message)
            st.info("Vui lòng quay lại trang đăng nhập để đăng nhập.")
        else:
            st.error(message)

    st.divider()
    if st.button("Đã có tài khoản? Đăng nhập", use_container_width=True):
        go_to("login")
        st.rerun()


# ----------------------------------------------------------------------
# TRANG: DASHBOARD
# ----------------------------------------------------------------------
def render_dashboard_page():
    user = st.session_state.current_user

    st.title(f"Xin chào, {user.fullname} 👋")

    with st.container(border=True):
        st.write(f"**Họ tên:** {user.fullname}")
        st.write(f"**Email:** {user.email}")
        st.write(f"**Username:** {user.username}")

    st.write("")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📅 Đặt lịch khám", use_container_width=True):
            reset_booking_state()
            go_to("booking")
            st.rerun()
    with col2:
        if st.button("📋 Lịch đã đặt", use_container_width=True):
            go_to("history")
            st.rerun()
    with col3:
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.current_user = None
            go_to("login")
            st.rerun()

    st.divider()
    st.markdown("#### 💡 Hướng dẫn nhanh")
    st.markdown(
        """
1. Nhấn **'Đặt lịch khám'** để bắt đầu.
2. Nhập địa chỉ hiện tại để hệ thống tìm bệnh viện gần nhất.
3. Nhập triệu chứng để hệ thống đề xuất chuyên khoa & bác sĩ.
4. Chọn ngày/giờ khám và xác nhận đặt lịch.
5. Xem lại lịch đã đặt trong mục **'Lịch đã đặt'**.
"""
    )


# ----------------------------------------------------------------------
# TRANG: ĐẶT LỊCH KHÁM
# ----------------------------------------------------------------------
def render_booking_page():
    user = st.session_state.current_user

    col_title, col_back = st.columns([3, 1])
    with col_title:
        st.title("🗓️ Đặt lịch khám")
    with col_back:
        if st.button("← Dashboard", use_container_width=True):
            go_to("dashboard")
            st.rerun()

    # ---------------- THÔNG TIN CƠ BẢN ----------------
    fullname = st.text_input("Họ tên *", value=user.fullname)
    email = st.text_input("Email *", value=user.email)

    st.divider()

    # ---------------- ĐỊA CHỈ -> BỆNH VIỆN GẦN NHẤT ----------------
    st.markdown("##### 📍 Địa chỉ hiện tại")
    address = st.text_input(
        "Địa chỉ *", placeholder="Ví dụ: 123 Cầu Giấy Hà Nội", key="address_input"
    )

    if st.button("🔍 Tìm bệnh viện gần nhất"):
        if not address.strip():
            st.warning("Vui lòng nhập địa chỉ trước.")
        else:
            with st.spinner("Đang tra cứu địa chỉ..."):
                success, result = GeolocationService.get_coordinates(address)

            if not success:
                st.error(result)
                st.session_state.user_coordinates = None
                st.session_state.nearest_clinic = None
            else:
                st.session_state.user_coordinates = result

                success, result = ClinicService.find_nearest_clinic(result)
                if not success:
                    st.error(result)
                    st.session_state.nearest_clinic = None
                else:
                    clinic, distance_km = result
                    st.session_state.nearest_clinic = clinic
                    st.session_state.nearest_distance = distance_km

    if st.session_state.nearest_clinic:
        clinic = st.session_state.nearest_clinic
        st.success(
            f"✅ Bệnh viện gần nhất: **{clinic.clinic_name}**\n\n"
            f"Địa chỉ: {clinic.address}\n\n"
            f"Khoảng cách: {st.session_state.nearest_distance} km"
        )

    st.divider()

    # ---------------- TRIỆU CHỨNG -> BÁC SĨ ----------------
    st.markdown("##### 🩺 Triệu chứng")
    symptom = st.text_input(
        "Triệu chứng *",
        placeholder="Ví dụ: dau hong, dau bung, dau dau...",
        key="symptom_input",
    )

    if st.button("🔍 Tìm bác sĩ phù hợp"):
        if not symptom.strip():
            st.warning("Vui lòng nhập triệu chứng trước.")
        else:
            success, result = DoctorService.get_specialty_by_symptom(symptom)
            if not success:
                st.error(result)
                st.session_state.matched_specialty = None
                st.session_state.suggested_doctor = None
            else:
                specialty = result
                st.session_state.matched_specialty = specialty

                nearest_clinic_id = (
                    st.session_state.nearest_clinic.clinic_id
                    if st.session_state.nearest_clinic
                    else None
                )
                success, result = DoctorService.find_best_doctor(specialty, nearest_clinic_id)
                if not success:
                    st.error(result)
                    st.session_state.suggested_doctor = None
                else:
                    st.session_state.suggested_doctor = result

    if st.session_state.suggested_doctor:
        doctor = st.session_state.suggested_doctor
        clinic_name = "Đang cập nhật"
        for clinic in ClinicService.get_all_clinics():
            if clinic.clinic_id == doctor.clinic_id:
                clinic_name = clinic.clinic_name
                break

        st.success(
            f"✅ Chuyên khoa phù hợp: **{st.session_state.matched_specialty}**\n\n"
            f"Bác sĩ đề xuất: **{doctor.name}**\n\n"
            f"Bệnh viện: {clinic_name}"
        )

    st.divider()

    # ---------------- NGÀY GIỜ KHÁM ----------------
    st.markdown("##### 📅 Thời gian khám")
    col_date, col_time = st.columns(2)
    with col_date:
        booking_date = st.date_input("Ngày khám *")
    with col_time:
        booking_time = st.selectbox("Giờ khám *", AVAILABLE_TIME_SLOTS)

    st.divider()

    # ---------------- ĐẶT LỊCH ----------------
    if st.button("✅ Đặt lịch khám", type="primary", use_container_width=True):
        if st.session_state.suggested_doctor is None:
            st.warning("Vui lòng nhập triệu chứng và bấm 'Tìm bác sĩ phù hợp' trước.")
        else:
            doctor_id = st.session_state.suggested_doctor.doctor_id
            date_str = booking_date.strftime("%Y-%m-%d")
            time_str = booking_time

            success, result = AppointmentService.book_appointment(
                patient_name=fullname,
                doctor_id=doctor_id,
                date_str=date_str,
                time_str=time_str,
                email=email,
            )

            if success:
                st.session_state.booking_result = result
                go_to("result")
                st.rerun()
            else:
                error_type = result.get("error")
                if error_type == "trung_lich":
                    suggested = result.get("suggested_times", [])
                    st.warning(result["message"])
                    if suggested:
                        st.info(f"Các giờ còn trống trong ngày: {', '.join(suggested)}")
                    else:
                        st.info("Bác sĩ đã hết lịch trống trong ngày này. Vui lòng chọn ngày khác.")
                else:
                    st.error(result.get("message", "Lỗi không xác định."))


# ----------------------------------------------------------------------
# TRANG: KẾT QUẢ ĐẶT LỊCH THÀNH CÔNG
# ----------------------------------------------------------------------
def render_result_page():
    booking_result = st.session_state.booking_result

    st.title("✅ Đặt lịch thành công")

    if booking_result is None:
        st.info("Chưa có thông tin đặt lịch.")
    else:
        appointment = booking_result["appointment"]
        doctor = booking_result["doctor"]
        clinic = booking_result["clinic"]
        email_sent = booking_result["email_sent"]
        email_message = booking_result["email_message"]

        clinic_name = clinic.clinic_name if clinic else "Đang cập nhật"

        with st.container(border=True):
            st.write(f"**Mã lịch hẹn:** {appointment.appointment_id}")
            st.write(f"**Bệnh nhân:** {appointment.patient_name}")
            st.write(f"**Bác sĩ:** {doctor.name}")
            st.write(f"**Chuyên khoa:** {doctor.specialty}")
            st.write(f"**Bệnh viện:** {clinic_name}")
            st.write(f"**Ngày khám:** {appointment.date}")
            st.write(f"**Giờ khám:** {appointment.time}")
            st.write(f"**Email:** {appointment.email}")

        if email_sent:
            st.success(f"📧 Email xác nhận đã được gửi tới {appointment.email}")
        else:
            st.warning(f"⚠️ Không gửi được email xác nhận: {email_message}")

    if st.button("← Quay lại Dashboard", use_container_width=True):
        go_to("dashboard")
        st.rerun()


# ----------------------------------------------------------------------
# TRANG: LỊCH SỬ ĐẶT LỊCH
# ----------------------------------------------------------------------
def render_history_page():
    user = st.session_state.current_user

    st.title("📋 Lịch khám đã đặt")

    appointments = AppointmentService.get_appointments_by_email(user.email)

    if not appointments:
        st.info("Bạn chưa có lịch khám nào.")
    else:
        rows = []
        for appt in appointments:
            doctor = DoctorService.get_doctor_by_id(appt.doctor_id)
            doctor_name = doctor.name if doctor else f"ID {appt.doctor_id}"
            specialty = doctor.specialty if doctor else "-"

            clinic_name = "-"
            if doctor:
                for clinic in ClinicService.get_all_clinics():
                    if clinic.clinic_id == doctor.clinic_id:
                        clinic_name = clinic.clinic_name
                        break

            rows.append({
                "Mã": appt.appointment_id,
                "Bác sĩ": doctor_name,
                "Chuyên khoa": specialty,
                "Bệnh viện": clinic_name,
                "Ngày": appt.date,
                "Giờ": appt.time,
                "Nhắc lịch": "Đã gửi" if appt.reminder_sent else "Chưa gửi",
            })

        st.dataframe(rows, use_container_width=True, hide_index=True)

    if st.button("← Quay lại Dashboard", use_container_width=True):
        go_to("dashboard")
        st.rerun()


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
def main():
    init_session_state()

    # Nếu chưa đăng nhập, chỉ cho vào login/register
    if st.session_state.current_user is None:
        if st.session_state.page == "register":
            render_register_page()
        else:
            render_login_page()
        return

    # Đã đăng nhập
    page = st.session_state.page
    if page == "booking":
        render_booking_page()
    elif page == "result":
        render_result_page()
    elif page == "history":
        render_history_page()
    else:
        render_dashboard_page()


if __name__ == "__main__":
    main()
