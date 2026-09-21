"""
services/email_service.py — Async email delivery via SMTP (smtplib/aiosmtplib).
Provides send_email() and pre-built template senders used across all modules.
Falls back gracefully when SMTP is not configured (logs instead of crashing).
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


def _build_message(to: str, subject: str, html_body: str, text_body: str = "") -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to
    if text_body:
        msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    return msg


def send_email(to: str, subject: str, html_body: str, text_body: str = "") -> bool:
    """
    Send an email synchronously via SMTP.
    Returns True on success, False on failure (never raises).
    """
    if not settings.SMTP_USERNAME or not settings.SMTP_FROM_EMAIL:
        logger.warning("SMTP not configured — email NOT sent to %s | Subject: %s", to, subject)
        logger.info("EMAIL BODY (dev preview):\n%s", text_body or html_body)
        return False

    try:
        msg = _build_message(to, subject, html_body, text_body)
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to, msg.as_string())
        logger.info("Email sent to %s | Subject: %s", to, subject)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to, exc)
        return False


# ─── Template senders ─────────────────────────────────────────────────────────

def send_verification_email(to: str, username: str, token: str) -> bool:
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    subject = "Verify Your Smart University Account"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:520px;margin:auto;padding:32px 24px;border:1px solid #E5E7EB;border-radius:12px;">
      <div style="background:#1A56DB;width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;margin-bottom:20px;">
        <span style="color:#fff;font-size:20px;font-weight:800;">S</span>
      </div>
      <h2 style="color:#111827;font-size:20px;margin:0 0 8px;">Welcome, {username}!</h2>
      <p style="color:#6B7280;font-size:14px;line-height:1.6;margin:0 0 24px;">
        Please verify your email address to activate your Smart University account.
      </p>
      <a href="{verify_url}"
         style="display:inline-block;background:#1A56DB;color:#fff;padding:10px 24px;border-radius:8px;font-size:14px;font-weight:600;text-decoration:none;">
        Verify Email Address
      </a>
      <p style="color:#9CA3AF;font-size:12px;margin:24px 0 0;">
        If you did not create this account, you can ignore this email.
        This link expires in 24 hours.
      </p>
    </div>
    """
    text = f"Welcome, {username}!\n\nVerify your account: {verify_url}\n\nLink expires in 24 hours."
    return send_email(to, subject, html, text)


def send_password_reset_email(to: str, username: str, token: str) -> bool:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    subject = "Reset Your Smart University Password"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:520px;margin:auto;padding:32px 24px;border:1px solid #E5E7EB;border-radius:12px;">
      <h2 style="color:#111827;font-size:20px;margin:0 0 8px;">Reset Password</h2>
      <p style="color:#6B7280;font-size:14px;line-height:1.6;margin:0 0 24px;">
        Hi {username}, we received a request to reset your password.
        Click the button below to create a new password.
      </p>
      <a href="{reset_url}"
         style="display:inline-block;background:#1A56DB;color:#fff;padding:10px 24px;border-radius:8px;font-size:14px;font-weight:600;text-decoration:none;">
        Reset Password
      </a>
      <p style="color:#9CA3AF;font-size:12px;margin:24px 0 0;">
        This link expires in 1 hour. If you did not request a password reset, please ignore this email.
      </p>
    </div>
    """
    text = f"Hi {username},\n\nReset your password: {reset_url}\n\nLink expires in 1 hour."
    return send_email(to, subject, html, text)


def send_admission_confirmation_email(
    to: str,
    student_name: str,
    enrollment_no: str,
    course: str,
    department: str,
    temp_password: str,
    login_url: Optional[str] = None,
) -> bool:
    login_url = login_url or f"{settings.FRONTEND_URL}/login"
    subject = f"Admission Confirmed — {enrollment_no}"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:560px;margin:auto;padding:32px 24px;border:1px solid #E5E7EB;border-radius:12px;">
      <h2 style="color:#111827;font-size:20px;margin:0 0 4px;">Congratulations, {student_name}!</h2>
      <p style="color:#6B7280;font-size:14px;margin:0 0 24px;">Your admission to Smart University has been confirmed.</p>
      <table style="width:100%;border-collapse:collapse;font-size:14px;margin-bottom:24px;">
        <tr><td style="padding:8px 0;color:#6B7280;width:40%;">Enrollment No.</td><td style="color:#111827;font-weight:600;">{enrollment_no}</td></tr>
        <tr><td style="padding:8px 0;color:#6B7280;">Course</td><td style="color:#111827;">{course}</td></tr>
        <tr><td style="padding:8px 0;color:#6B7280;">Department</td><td style="color:#111827;">{department}</td></tr>
        <tr><td style="padding:8px 0;color:#6B7280;">Temporary Password</td><td style="color:#1A56DB;font-weight:600;font-family:monospace;">{temp_password}</td></tr>
      </table>
      <a href="{login_url}"
         style="display:inline-block;background:#1A56DB;color:#fff;padding:10px 24px;border-radius:8px;font-size:14px;font-weight:600;text-decoration:none;">
        Login to Student Portal
      </a>
      <p style="color:#9CA3AF;font-size:12px;margin:24px 0 0;">
        Please change your password immediately after first login.
      </p>
    </div>
    """
    text = (
        f"Congratulations {student_name}!\n\n"
        f"Enrollment No: {enrollment_no}\nCourse: {course}\nDepartment: {department}\n"
        f"Temporary Password: {temp_password}\n\nLogin: {login_url}\n\n"
        "Please change your password immediately."
    )
    return send_email(to, subject, html, text)


def send_low_attendance_warning(
    to: str,
    student_name: str,
    subject_name: str,
    percentage: float,
    threshold: float,
) -> bool:
    email_subject = f"Low Attendance Warning — {subject_name}"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:520px;margin:auto;padding:32px 24px;border:1px solid #FDE68A;border-radius:12px;background:#FFFBEB;">
      <h2 style="color:#B45309;font-size:18px;margin:0 0 8px;">⚠️ Low Attendance Warning</h2>
      <p style="color:#6B7280;font-size:14px;line-height:1.6;margin:0 0 16px;">
        Dear {student_name}, your attendance in <strong>{subject_name}</strong> has fallen below
        the required <strong>{threshold:.0f}%</strong>.
      </p>
      <p style="font-size:24px;font-weight:700;color:#B45309;margin:0 0 16px;">{percentage:.1f}%</p>
      <p style="color:#6B7280;font-size:14px;line-height:1.6;margin:0;">
        Please attend upcoming lectures regularly to avoid academic penalties.
      </p>
      <p style="color:#9CA3AF;font-size:12px;margin:24px 0 0;">
        Regards,<br>University Administration
      </p>
    </div>
    """
    text = (
        f"Dear {student_name},\n\n"
        f"Your attendance in {subject_name} has fallen below the required {threshold:.0f}%.\n"
        f"Current Attendance: {percentage:.1f}%\n\n"
        "Please attend upcoming lectures regularly to avoid academic penalties.\n\n"
        "Regards,\nUniversity Administration"
    )
    return send_email(to, email_subject, html, text)


def send_result_published_email(
    to: str,
    student_name: str,
    semester: int,
    sgpa: float,
    cgpa: float,
    portal_url: Optional[str] = None,
) -> bool:
    portal_url = portal_url or f"{settings.FRONTEND_URL}/dashboard/student"
    email_subject = f"Semester {semester} Results Published"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:520px;margin:auto;padding:32px 24px;border:1px solid #E5E7EB;border-radius:12px;">
      <h2 style="color:#111827;font-size:20px;margin:0 0 8px;">Results Published</h2>
      <p style="color:#6B7280;font-size:14px;margin:0 0 24px;">
        Dear {student_name}, your Semester {semester} results have been published.
      </p>
      <table style="width:100%;border-collapse:collapse;font-size:14px;margin-bottom:24px;">
        <tr><td style="padding:8px 0;color:#6B7280;">SGPA</td><td style="color:#111827;font-weight:700;font-size:20px;">{sgpa:.2f}</td></tr>
        <tr><td style="padding:8px 0;color:#6B7280;">CGPA</td><td style="color:#111827;font-weight:700;font-size:20px;">{cgpa:.2f}</td></tr>
      </table>
      <a href="{portal_url}"
         style="display:inline-block;background:#1A56DB;color:#fff;padding:10px 24px;border-radius:8px;font-size:14px;font-weight:600;text-decoration:none;">
        View Full Marksheet
      </a>
    </div>
    """
    text = (
        f"Dear {student_name},\n\n"
        f"Your Semester {semester} results have been published.\n"
        f"SGPA: {sgpa:.2f}  |  CGPA: {cgpa:.2f}\n\n"
        f"View marksheet: {portal_url}"
    )
    return send_email(to, email_subject, html, text)
