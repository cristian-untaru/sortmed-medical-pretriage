"""Authentication, session persistence, and account recovery helpers."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import smtplib
import threading
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bcrypt
import streamlit as st
import streamlit.components.v1 as components

from backend.database import (
    DISPLAY_TIMESTAMP_FORMAT,
    LOCAL_TIMEZONE,
    create_auth_session,
    create_reset_code,
    create_user,
    delete_auth_session,
    delete_user_account,
    get_active_auth_session,
    get_active_reset_code,
    get_user_by_email,
    get_user_by_id,
    increment_reset_attempts,
    init_db,
    is_integrity_error,
    mark_reset_code_used,
    update_user_password,
)

SESSION_CURRENT_USER = "current_user"
SESSION_TOKEN_STATE_KEY = "auth_session_token"
SESSION_COOKIE_NAME = "sortmed_session"
SESSION_EXPIRY_DAYS = 30


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _session_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "user_id": user["user_id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "created_at": user["created_at"],
    }


def _hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _browser_cookies_enabled() -> bool:
    return os.getenv("SORTMED_DISABLE_BROWSER_COOKIES") != "1"


def _is_secure_context() -> bool:
    try:
        return str(st.context.url).startswith("https://")
    except Exception:
        return False


def _write_session_cookie(token: str, expires_at: datetime) -> None:
    st.session_state[SESSION_TOKEN_STATE_KEY] = token
    if not _browser_cookies_enabled():
        return

    expires_gmt = expires_at.astimezone(timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    secure_flag = " Secure;" if _is_secure_context() else ""
    cookie_value = (
        f"{SESSION_COOKIE_NAME}={token};"
        f" Expires={expires_gmt};"
        " Path=/;"
        " SameSite=Lax;"
        f"{secure_flag}"
    )
    components.html(
        f"<script>document.cookie = {json.dumps(cookie_value)};</script>",
        height=0,
        width=0,
    )


def _read_session_cookie() -> str | None:
    state_token = st.session_state.get(SESSION_TOKEN_STATE_KEY)
    if isinstance(state_token, str) and state_token:
        return state_token

    if not _browser_cookies_enabled():
        return None

    try:
        cookie_token = st.context.cookies.get(SESSION_COOKIE_NAME)
    except Exception:
        return None

    if isinstance(cookie_token, str) and cookie_token:
        st.session_state[SESSION_TOKEN_STATE_KEY] = cookie_token
        return cookie_token
    return None


def _clear_session_cookie() -> None:
    st.session_state.pop(SESSION_TOKEN_STATE_KEY, None)
    if not _browser_cookies_enabled():
        return

    secure_flag = " Secure;" if _is_secure_context() else ""
    expired_cookie = (
        f"{SESSION_COOKIE_NAME}=;"
        " Max-Age=0;"
        " Expires=Thu, 01 Jan 1970 00:00:00 GMT;"
        " Path=/;"
        " SameSite=Lax;"
        f"{secure_flag}"
    )
    components.html(
        f"<script>document.cookie = {json.dumps(expired_cookie)};</script>",
        height=0,
        width=0,
    )


def _start_authenticated_session(user: dict) -> dict:
    session_user = _session_user(user)
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(LOCAL_TIMEZONE) + timedelta(days=SESSION_EXPIRY_DAYS)

    create_auth_session(
        user_id=session_user["user_id"],
        session_token_hash=_hash_session_token(token),
        expires_at=expires_at.strftime(DISPLAY_TIMESTAMP_FORMAT),
    )
    st.session_state[SESSION_CURRENT_USER] = session_user
    _write_session_cookie(token, expires_at)
    return session_user


def _restore_user_from_browser_session() -> dict | None:
    token = _read_session_cookie()
    if not token:
        return None

    record = get_active_auth_session(_hash_session_token(token))
    if not record:
        _clear_session_cookie()
        return None

    session_user = _session_user(record)
    st.session_state[SESSION_CURRENT_USER] = session_user
    return session_user


def start_guest_session() -> None:
    """Begin a guest session for the current Streamlit browser session."""
    st.session_state["guest_user"] = True


def end_guest_session() -> None:
    """End the guest session for the current Streamlit browser session."""
    st.session_state.pop("guest_user", None)


def is_guest_session() -> bool:
    """True if the current Streamlit browser session is a guest session."""
    return bool(st.session_state.get("guest_user"))


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return password_hash.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (TypeError, ValueError):
        return False


def register_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
) -> tuple[bool, str]:
    init_db()

    first_name = first_name.strip()
    last_name = last_name.strip()
    email = _normalize_email(email)

    if not first_name or not last_name or not email or not password:
        return False, "Please complete all fields."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    if get_user_by_email(email):
        return False, "An account with this email already exists."

    try:
        user = create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=hash_password(password),
        )
    except Exception as exc:
        if is_integrity_error(exc):
            return False, "An account with this email already exists."
        return False, f"Could not create account: {exc}"

    _start_authenticated_session(user)
    return True, "Account created successfully."


def login_user(email: str, password: str) -> tuple[bool, str]:
    init_db()

    email = _normalize_email(email)

    if not email or not password:
        return False, "Please enter your email and password."

    user = get_user_by_email(email)
    if not user or not verify_password(password, user.get("password_hash", "")):
        return False, "Invalid email or password."

    _start_authenticated_session(user)
    return True, "Logged in successfully."


def logout_user() -> None:
    token = _read_session_cookie()
    if token:
        delete_auth_session(_hash_session_token(token))
    _clear_session_cookie()
    st.session_state.pop(SESSION_CURRENT_USER, None)


def get_current_user() -> dict | None:
    current_user = st.session_state.get(SESSION_CURRENT_USER)
    if current_user:
        return current_user

    restored_user = _restore_user_from_browser_session()
    if restored_user:
        return restored_user
    return None


def is_logged_in() -> bool:
    return get_current_user() is not None


# Password reset flow.

_RESET_EXPIRY_MINUTES = 10
_MAX_RESET_ATTEMPTS = 5


def _send_registration_email(email: str, first_name: str, code: str) -> None:
    """Send the 6-digit registration verification code by email."""
    try:
        cfg = st.secrets.get("email", {})
        smtp_host: str = cfg.get("smtp_host", "")
        smtp_port: int = int(cfg.get("smtp_port", 587))
        smtp_user: str = cfg.get("smtp_user", "")
        smtp_password: str = cfg.get("smtp_password", "")
        from_address: str = cfg.get("from_address") or smtp_user
    except Exception:
        return

    if not (smtp_host and smtp_user and smtp_password):
        return

    body_text = (
        f"Hi {first_name}!\n\n"
        f"Your SortMed account verification code is: {code}\n\n"
        f"This code expires in 10 minutes.\n"
        f"If you didn't request this, ignore this email."
    )
    body_html = f"""
    <html>
    <body style="font-family:Segoe UI,sans-serif;background:#f1f5f9;padding:40px 0;">
      <div style="max-width:420px;margin:0 auto;background:#fff;border-radius:12px;
                  padding:36px 40px;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
        <h2 style="margin:0 0 6px;font-size:1.5rem;color:#16181d;">Verify your email</h2>
        <p style="color:#6b7280;margin:0 0 6px;font-size:0.95rem;">Hi {first_name}!</p>
        <p style="color:#6b7280;margin:0 0 28px;font-size:0.95rem;">
          Use the code below to verify your SortMed account.
          It expires in&nbsp;10&nbsp;minutes.
        </p>
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
                    padding:22px 0;text-align:center;
                    letter-spacing:10px;font-size:2.2rem;font-weight:700;color:#16181d;">
          {code}
        </div>
        <p style="color:#9ca3af;font-size:0.82rem;margin:24px 0 0;line-height:1.5;">
          If you didn't create a SortMed account, you can safely ignore this email.
        </p>
      </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify your SortMed account"
    msg["From"] = from_address
    msg["To"] = email
    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    msg_string = msg.as_string()

    def _send() -> None:
        try:
            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15) as server:
                    server.login(smtp_user, smtp_password)
                    server.sendmail(from_address, email, msg_string)
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                    server.ehlo()
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    server.sendmail(from_address, email, msg_string)
        except Exception:
            return

    threading.Thread(target=_send, daemon=True).start()


def send_registration_code(first_name: str, email: str) -> tuple[bool, str]:
    """Validate registration inputs, store a verification code, send it by email."""
    init_db()
    email = _normalize_email(email)
    if get_user_by_email(email):
        return False, "An account with this email already exists."
    code = f"{secrets.randbelow(10 ** 6):06d}"
    code_hash = hash_password(code)
    expires_at = (
        datetime.now(LOCAL_TIMEZONE) + timedelta(minutes=_RESET_EXPIRY_MINUTES)
    ).strftime(DISPLAY_TIMESTAMP_FORMAT)
    create_reset_code(email, code_hash, expires_at)
    _send_registration_email(email, first_name, code)
    return True, "Verification code sent."


def confirm_registration(
    email: str,
    code: str,
    first_name: str,
    last_name: str,
    password_hash: str,
) -> tuple[bool, str]:
    """Verify the emailed code, then create and log in the account."""
    init_db()
    email = _normalize_email(email)
    if not code:
        return False, "Please enter the verification code."
    record = get_active_reset_code(email)
    if not record:
        return False, "Code expired or invalid. Please request a new one."
    increment_reset_attempts(record["id"])
    if not verify_password(code, record["code_hash"]):
        remaining = _MAX_RESET_ATTEMPTS - (record["attempts"] + 1)
        if remaining <= 0:
            return False, "Too many incorrect attempts. Please request a new code."
        return False, f"Incorrect code. {remaining} attempt(s) remaining."
    mark_reset_code_used(record["id"])
    if get_user_by_email(email):
        return False, "An account with this email already exists."
    try:
        user = create_user(first_name, last_name, email, password_hash)
    except Exception as exc:
        if is_integrity_error(exc):
            return False, "An account with this email already exists."
        return False, f"Could not create account: {exc}"
    _start_authenticated_session(user)
    return True, "Account created successfully."


def send_password_reset_code(email: str, code: str) -> None:
    """Send the 6-digit reset code by email when SMTP is configured."""
    try:
        cfg = st.secrets.get("email", {})
        smtp_host: str = cfg.get("smtp_host", "")
        smtp_port: int = int(cfg.get("smtp_port", 587))
        smtp_user: str = cfg.get("smtp_user", "")
        smtp_password: str = cfg.get("smtp_password", "")
        from_address: str = cfg.get("from_address") or smtp_user
    except Exception:
        return

    if not (smtp_host and smtp_user and smtp_password):
        return

    body_text = (
        f"Your password reset code is: {code}\n\n"
        f"This code expires in 10 minutes.\n"
        f"If you didn't request a password reset, ignore this email."
    )
    body_html = f"""
    <html>
    <body style="font-family:Segoe UI,sans-serif;background:#f1f5f9;padding:40px 0;">
      <div style="max-width:420px;margin:0 auto;background:#fff;border-radius:12px;
                  padding:36px 40px;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
        <h2 style="margin:0 0 6px;font-size:1.5rem;color:#16181d;">Password Reset</h2>
        <p style="color:#6b7280;margin:0 0 28px;font-size:0.95rem;">
          Use the code below to reset your password. It expires in&nbsp;10&nbsp;minutes.
        </p>
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
                    padding:22px 0;text-align:center;
                    letter-spacing:10px;font-size:2.2rem;font-weight:700;color:#16181d;">
          {code}
        </div>
        <p style="color:#9ca3af;font-size:0.82rem;margin:24px 0 0;line-height:1.5;">
          If you didn't request this, you can safely ignore the email.
        </p>
      </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your password reset code"
    msg["From"] = from_address
    msg["To"] = email
    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    msg_string = msg.as_string()

    def _send() -> None:
        try:
            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15) as server:
                    server.login(smtp_user, smtp_password)
                    server.sendmail(from_address, email, msg_string)
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                    server.ehlo()
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    server.sendmail(from_address, email, msg_string)
        except Exception:
            return

    threading.Thread(target=_send, daemon=True).start()


def request_password_reset(email: str) -> None:
    """
    Generates and stores a hashed reset code.
    Always silent - never reveals whether the email exists.
    """
    init_db()
    email = _normalize_email(email)
    code = f"{secrets.randbelow(10 ** 6):06d}"
    code_hash = hash_password(code)
    expires_at = (
        datetime.now(LOCAL_TIMEZONE) + timedelta(minutes=_RESET_EXPIRY_MINUTES)
    ).strftime(DISPLAY_TIMESTAMP_FORMAT)

    if get_user_by_email(email):
        create_reset_code(email, code_hash, expires_at)
        send_password_reset_code(email, code)


_MIN_PASSWORD_LENGTH = 6


def verify_current_password(user_id: str, current_password: str) -> tuple[bool, str]:
    """Check that current_password matches the stored hash for user_id."""
    if not current_password:
        return False, "Please enter your current password."
    user = get_user_by_id(user_id)
    if not user:
        return False, "Account not found."
    if not verify_password(current_password, user.get("password_hash", "")):
        return False, "Current password is incorrect."
    return True, "Password verified."


def set_new_password(
    user_id: str,
    new_password: str,
    confirm_password: str,
) -> tuple[bool, str]:
    """Apply a new password for user_id.  Current password must already be verified."""
    if not new_password or not confirm_password:
        return False, "Please fill in all password fields."
    if new_password != confirm_password:
        return False, "Passwords do not match."
    if len(new_password) < _MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {_MIN_PASSWORD_LENGTH} characters long."
    user = get_user_by_id(user_id)
    if not user:
        return False, "Account not found."
    if verify_password(new_password, user.get("password_hash", "")):
        return False, "New password must be different from the current password."
    if not update_user_password(user["email"], hash_password(new_password)):
        return False, "Could not update password. Please try again."
    return True, "Password updated successfully."


def change_password(
    user_id: str,
    current_password: str,
    new_password: str,
    confirm_password: str,
) -> tuple[bool, str]:
    """Single-step password change: verify current, validate new, apply."""
    ok, msg = verify_current_password(user_id, current_password)
    if not ok:
        return False, msg
    return set_new_password(user_id, new_password, confirm_password)


def reset_password(
    email: str,
    code: str,
    new_password: str,
    confirm_password: str,
) -> tuple[bool, str]:
    init_db()
    email = _normalize_email(email)

    if not code or not new_password or not confirm_password:
        return False, "Please fill in all fields."
    if new_password != confirm_password:
        return False, "Passwords do not match."
    if len(new_password) < 6:
        return False, "Password must be at least 6 characters long."

    record = get_active_reset_code(email)
    if not record:
        return False, "This code is expired or invalid. Please request a new one."

    increment_reset_attempts(record["id"])

    if not verify_password(code, record["code_hash"]):
        remaining = _MAX_RESET_ATTEMPTS - (record["attempts"] + 1)
        if remaining <= 0:
            return False, "Too many incorrect attempts. Please request a new reset code."
        return False, f"Incorrect code. {remaining} attempt(s) remaining."

    mark_reset_code_used(record["id"])

    if not update_user_password(email, hash_password(new_password)):
        return False, "Could not update password. Please try again."

    return True, "Password updated successfully. You can now log in."


def delete_account(
    user_id: str,
    current_password: str,
    confirmation_text: str,
) -> tuple[bool, str]:
    if not current_password:
        return False, "Please enter your current password."
    if confirmation_text != "DELETE":
        return False, 'Please type "DELETE" (all caps) to confirm.'
    user = get_user_by_id(user_id)
    if not user:
        return False, "Account not found."
    if not verify_password(current_password, user.get("password_hash", "")):
        return False, "Current password is incorrect."
    if not delete_user_account(user_id, user["email"]):
        return False, "Could not delete account. Please try again."
    logout_user()
    return True, "Account deleted successfully."
