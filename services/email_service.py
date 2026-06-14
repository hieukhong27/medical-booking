"""
Service: Email Service
Gửi email xác nhận lịch khám và email nhắc lịch
thông qua Gmail SMTP (smtplib + email.message).

LƯU Ý:
- Cần sử dụng "App Password" của Gmail (không dùng password thường)
  do Google yêu cầu bảo mật 2 lớp.
- Thông tin tài khoản gửi mail được cấu hình trong các biến
  SENDER_EMAIL và SENDER_APP_PASSWORD dưới đây.
"""

import smtplib
from email.message import EmailMessage


# ===== CẤU HÌNH GMAIL SMTP =====
# Thay bằng email Gmail thật và App Password của bạn
SENDER_EMAIL = "hieuhieu27306@gmail.com"
SENDER_APP_PASSWORD = "pghm ffpz noqg ubyy"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


class EmailService:
    """Service xử lý gửi email xác nhận và email nhắc lịch khám."""

    @staticmethod
    def _send_email(to_email: str, subject: str, body: str) -> tuple:
        """
        Gửi email thông qua Gmail SMTP.

        Args:
            to_email: email người nhận
            subject: tiêu đề email
            body: nội dung email (plain text)

        Returns:
            tuple (success: bool, message: str)
        """
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = SENDER_EMAIL
            msg["To"] = to_email
            msg.set_content(body)

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()  # bảo mật kết nối TLS
                server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
                server.send_message(msg)

            return True, "Gửi email thành công."

        except smtplib.SMTPAuthenticationError:
            return False, (
                "Lỗi xác thực Gmail. Vui lòng kiểm tra lại SENDER_EMAIL "
                "và SENDER_APP_PASSWORD (cần dùng App Password)."
            )
        except smtplib.SMTPException as e:
            return False, f"Lỗi gửi email (SMTP): {e}"
        except Exception as e:
            return False, f"Lỗi không xác định khi gửi email: {e}"

    @staticmethod
    def send_confirmation_email(to_email: str, patient_name: str,
                                  doctor_name: str, specialty: str,
                                  clinic_name: str, date: str, time: str) -> tuple:
        """
        Gửi email xác nhận đặt lịch khám thành công.

        Args:
            to_email: email bệnh nhân
            patient_name: tên bệnh nhân
            doctor_name: tên bác sĩ
            specialty: chuyên khoa
            clinic_name: tên bệnh viện
            date: ngày khám (YYYY-MM-DD)
            time: giờ khám (HH:MM)

        Returns:
            tuple (success: bool, message: str)
        """
        subject = "Xác nhận lịch khám sức khỏe"
        body = (
            f"Xin chào {patient_name},\n\n"
            f"Bạn đã đặt lịch khám thành công với thông tin sau:\n\n"
            f"- Bác sĩ: {doctor_name}\n"
            f"- Chuyên khoa: {specialty}\n"
            f"- Bệnh viện: {clinic_name}\n"
            f"- Ngày khám: {date}\n"
            f"- Giờ khám: {time}\n\n"
            f"Vui lòng đến đúng giờ. Xin cảm ơn!\n\n"
            f"-- Hệ thống Đặt lịch khám sức khỏe online --"
        )
        return EmailService._send_email(to_email, subject, body)

    @staticmethod
    def send_reminder_email(to_email: str, patient_name: str,
                              doctor_name: str, date: str, time: str) -> tuple:
        """
        Gửi email nhắc lịch khám (trước 1 ngày).

        Args:
            to_email: email bệnh nhân
            patient_name: tên bệnh nhân
            doctor_name: tên bác sĩ
            date: ngày khám (YYYY-MM-DD)
            time: giờ khám (HH:MM)

        Returns:
            tuple (success: bool, message: str)
        """
        subject = "Nhắc lịch khám sức khỏe - Ngày mai"
        body = (
            f"Xin chào {patient_name},\n\n"
            f"Đây là email nhắc lịch khám của bạn vào NGÀY MAI:\n\n"
            f"- Bác sĩ: {doctor_name}\n"
            f"- Ngày khám: {date}\n"
            f"- Giờ khám: {time}\n\n"
            f"Vui lòng sắp xếp thời gian đến khám đúng giờ. Xin cảm ơn!\n\n"
            f"-- Hệ thống Đặt lịch khám sức khỏe online --"
        )
        return EmailService._send_email(to_email, subject, body)
