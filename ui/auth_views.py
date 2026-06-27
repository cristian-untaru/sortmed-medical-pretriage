"""Authentication and account management views for the Streamlit app."""

from __future__ import annotations

import streamlit as st

from backend.auth import (
    confirm_registration,
    delete_account,
    get_current_user,
    hash_password,
    is_guest_session,
    login_user,
    logout_user,
    request_password_reset,
    reset_password,
    send_registration_code,
    set_new_password,
    start_guest_session,
    verify_current_password,
)

def is_guest_user() -> bool:
    return is_guest_session()


def render_auth_interface() -> None:
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "sign_in"

    auth_mode = st.session_state["auth_mode"]

    _, auth_col, _ = st.columns([1, 1.05, 1])

    with auth_col:
        # Login form.
        if auth_mode == "sign_in":
            with st.form("login_form"):
                st.markdown(
                    """
                    <div class="auth-form-heading">
                        <div class="auth-card-title">Log in</div>
                        <p>Use your email and password to access your private workspace.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                email = st.text_input("Email", key="login_email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", key="login_password")
                st.markdown(
                    '<p class="auth-forgot-text">'
                    '<a href="?forgot=1" target="_self">Forgot your password?</a>'
                    "</p>",
                    unsafe_allow_html=True,
                )
                submitted = st.form_submit_button("Log in", type="primary")
                guest_submitted = st.form_submit_button("Continue as a Guest")
                st.markdown(
                    '<p class="auth-switch-text">Don\'t have an account?</p>',
                    unsafe_allow_html=True,
                )
                switch_submitted = st.form_submit_button("Create account")

            if submitted:
                ok, message = login_user(email, password)
                if ok:
                    st.session_state.pop("guest_user", None)
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

            if guest_submitted:
                logout_user()
                start_guest_session()
                st.rerun()

            if switch_submitted:
                st.session_state["auth_mode"] = "register"
                st.rerun()

        # Registration form.
        elif auth_mode == "register":
            with st.form("register_form"):
                st.markdown(
                    """
                    <div class="auth-form-heading">
                        <div class="auth-card-title">Create account</div>
                        <p>Create a local account to save your analysis history.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                first_name = st.text_input("First name", key="register_first_name")
                last_name = st.text_input("Last name", key="register_last_name")
                email = st.text_input("Email", key="register_email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", key="register_password")
                confirm_password = st.text_input("Confirm password", type="password", key="register_confirm_password")
                _chk_col, _txt_col = st.columns([0.07, 0.93])
                with _chk_col:
                    terms_agreed = st.checkbox(
                        "Accept Terms of Service and Privacy Policy",
                        key="register_terms_checkbox",
                        label_visibility="collapsed",
                    )
                with _txt_col:
                    st.markdown(
                        '<p class="auth-terms-inline">'
                        "I agree to the "
                        '<a href="?legal=terms" target="_self">Terms of Service</a>'
                        " and "
                        '<a href="?legal=privacy" target="_self">Privacy Policy</a>'
                        "</p>",
                        unsafe_allow_html=True,
                    )
                submitted = st.form_submit_button("Create account", type="primary")
                guest_submitted = st.form_submit_button("Continue as a Guest")
                st.markdown(
                    '<p class="auth-switch-text">Already have an account?</p>',
                    unsafe_allow_html=True,
                )
                switch_submitted = st.form_submit_button("Log in")

            if submitted:
                first_name_s = first_name.strip()
                last_name_s = last_name.strip()
                email_s = email.strip().lower()
                if not terms_agreed:
                    st.error("Please accept the Terms of Service and Privacy Policy before creating an account.")
                elif not first_name_s or not last_name_s or not email_s or not password:
                    st.error("Please complete all fields.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    ok, message = send_registration_code(first_name_s, email_s)
                    if ok:
                        st.session_state["reg_first_name"] = first_name_s
                        st.session_state["reg_last_name"] = last_name_s
                        st.session_state["reg_email"] = email_s
                        st.session_state["reg_password_hash"] = hash_password(password)
                        st.session_state["auth_mode"] = "verify_registration_email"
                        st.rerun()
                    else:
                        st.error(message)

            if guest_submitted:
                logout_user()
                start_guest_session()
                st.rerun()

            if switch_submitted:
                st.session_state["auth_mode"] = "sign_in"
                st.rerun()

        # Password reset request form.
        elif auth_mode == "forgot_password":
            with st.form("forgot_password_form"):
                st.markdown(
                    """
                    <div class="auth-form-heading">
                        <div class="auth-card-title">Reset password</div>
                        <p>Enter your email and we'll send a 6-digit reset code.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                reset_email_input = st.text_input(
                    "Email", key="forgot_email_input", placeholder="you@example.com"
                )
                submitted = st.form_submit_button("Send reset code", type="primary")
                back_submitted = st.form_submit_button("Back to Log in")

            if submitted:
                request_password_reset(reset_email_input)
                st.session_state["reset_email"] = reset_email_input.strip().lower()
                st.session_state["auth_mode"] = "verify_reset_code"
                st.rerun()

            if back_submitted:
                st.session_state.pop("reset_email", None)
                st.session_state["auth_mode"] = "sign_in"
                st.rerun()

        # Password reset confirmation form.
        elif auth_mode == "verify_reset_code":
            stored_email = st.session_state.get("reset_email", "")
            if not stored_email:
                st.session_state["auth_mode"] = "forgot_password"
                st.rerun()

            with st.form("verify_reset_form"):
                st.markdown(
                    """
                    <div class="auth-form-heading">
                        <div class="auth-card-title">Enter reset code</div>
                        <p>If an account with that email exists, a reset code was sent.
                        Check your email inbox for the code.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                code_input = st.text_input(
                    "6-digit code",
                    key="reset_code_input",
                    placeholder="000000",
                    max_chars=6,
                )
                new_pw = st.text_input("New password", type="password", key="reset_new_pw")
                confirm_pw = st.text_input(
                    "Confirm new password", type="password", key="reset_confirm_pw"
                )
                submitted = st.form_submit_button("Reset password", type="primary")
                st.markdown(
                    '<p class="auth-switch-text">Didn\'t receive a code?</p>',
                    unsafe_allow_html=True,
                )
                resend_submitted = st.form_submit_button("Request new code")

            if submitted:
                ok, message = reset_password(stored_email, code_input, new_pw, confirm_pw)
                if ok:
                    st.success(message)
                    st.session_state.pop("reset_email", None)
                    st.session_state["auth_mode"] = "sign_in"
                    st.rerun()
                else:
                    st.error(message)

            if resend_submitted:
                st.session_state["auth_mode"] = "forgot_password"
                st.rerun()

        # Registration verification form.
        elif auth_mode == "verify_registration_email":
            reg_email = st.session_state.get("reg_email", "")
            if not reg_email:
                st.session_state["auth_mode"] = "register"
                st.rerun()

            with st.form("verify_registration_form"):
                st.markdown(
                    f"""
                    <div class="auth-form-heading">
                        <div class="auth-card-title">Verify your email</div>
                        <p>A 6-digit code was sent to <strong>{reg_email}</strong>.
                        Enter it below to complete your registration.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                code_input = st.text_input(
                    "6-digit code",
                    key="reg_code_input",
                    placeholder="000000",
                    max_chars=6,
                )
                submitted = st.form_submit_button(
                    "Verify & create account", type="primary"
                )
                st.markdown(
                    '<p class="auth-switch-text">Didn\'t receive a code?</p>',
                    unsafe_allow_html=True,
                )
                resend_submitted = st.form_submit_button("Resend code")
                back_submitted = st.form_submit_button("Back")

            if submitted:
                ok, message = confirm_registration(
                    reg_email,
                    code_input,
                    st.session_state.get("reg_first_name", ""),
                    st.session_state.get("reg_last_name", ""),
                    st.session_state.get("reg_password_hash", ""),
                )
                if ok:
                    st.session_state.pop("guest_user", None)
                    for key in ("reg_email", "reg_first_name", "reg_last_name", "reg_password_hash"):
                        st.session_state.pop(key, None)
                    st.rerun()
                else:
                    st.error(message)

            if resend_submitted:
                ok, _ = send_registration_code(
                    st.session_state.get("reg_first_name", ""), reg_email
                )
                if ok:
                    st.session_state["reg_code_resent"] = True
                st.rerun()

            if back_submitted:
                for key in ("reg_email", "reg_first_name", "reg_last_name", "reg_password_hash", "reg_code_resent"):
                    st.session_state.pop(key, None)
                st.session_state["auth_mode"] = "register"
                st.rerun()

            if st.session_state.pop("reg_code_resent", False):
                st.info("A new verification code was sent to your email.")



def _go_to_return_page(return_to: str) -> None:
    if return_to == "about":
        st.switch_page("pages/About.py")
    elif return_to == "results":
        st.switch_page("pages/Results.py")
    elif return_to == "account":
        st.switch_page("pages/Account.py")
    else:
        st.rerun()


def render_account_interface() -> None:
    current_user = get_current_user()
    if not current_user:
        st.session_state.pop("account_mode", None)
        st.rerun()

    account_mode = st.session_state.get("account_mode", "")
    _, col, _ = st.columns([1, 1.05, 1])

    with col:
        if account_mode == "confirm_current_password":
            with st.form("confirm_current_pw_form"):
                st.markdown(
                    """
                    <div class="auth-form-heading auth-change-password-confirm">
                        <div class="auth-card-title">Change password</div>
                        <p>Please confirm your current password before setting a new one.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                current_pw = st.text_input(
                    "Current password", type="password", key="chpw_current"
                )
                submitted = st.form_submit_button("Continue", type="primary")
                back_submitted = st.form_submit_button("Back")

            if submitted:
                ok, message = verify_current_password(current_user["user_id"], current_pw)
                if ok:
                    st.session_state["password_change_verified"] = True
                    st.session_state["account_mode"] = "set_new_password"
                    st.rerun()
                else:
                    st.error(message)

            if back_submitted:
                _rt = st.session_state.pop("account_return_to", "main")
                st.session_state.pop("account_mode", None)
                st.session_state.pop("password_change_verified", None)
                _go_to_return_page(_rt)

        elif account_mode == "set_new_password":
            if not st.session_state.get("password_change_verified"):
                st.session_state["account_mode"] = "confirm_current_password"
                st.rerun()

            with st.form("set_new_pw_form"):
                st.markdown(
                    """
                    <div class="auth-form-heading">
                        <div class="auth-card-title">Set new password</div>
                        <p>Choose a strong password with at least 6 characters.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                new_pw = st.text_input("New password", type="password", key="chpw_new")
                confirm_pw = st.text_input(
                    "Confirm new password", type="password", key="chpw_confirm"
                )
                submitted = st.form_submit_button("Update password", type="primary")
                back_submitted = st.form_submit_button("Back")

            if submitted:
                ok, message = set_new_password(current_user["user_id"], new_pw, confirm_pw)
                if ok:
                    st.session_state["account_mode"] = "password_changed_success"
                    st.session_state.pop("password_change_verified", None)
                    st.rerun()
                else:
                    st.error(message)

            if back_submitted:
                st.session_state["account_mode"] = "confirm_current_password"
                st.session_state.pop("password_change_verified", None)
                st.rerun()

        elif account_mode == "password_changed_success":
            st.success(
                "Password updated successfully. You can continue using the app."
            )
            if st.button("Continue", type="primary"):
                st.session_state.pop("account_return_to", None)
                st.session_state.pop("account_mode", None)
                st.rerun()

        elif account_mode == "delete_account":
            with st.form("delete_account_form"):
                st.markdown(
                    """
                    <div class="auth-form-heading auth-form-heading-danger">
                        <div class="auth-card-title">Delete account</div>
                        <p>This action is permanent and cannot be undone.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    """
                    <div class="delete-warning-list">
                        <strong>The following will be permanently deleted:</strong>
                        <ul>
                            <li>Profile information (name, email)</li>
                            <li>Saved symptom analysis history</li>
                            <li>Password reset records</li>
                            <li>Current session</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                current_pw = st.text_input(
                    "Current password", type="password", key="del_current_pw"
                )
                confirm_text = st.text_input(
                    'Type "DELETE" to confirm',
                    key="del_confirm_text",
                    placeholder="DELETE",
                )
                delete_submitted = st.form_submit_button(
                    "Delete my account", type="primary"
                )
                cancel_submitted = st.form_submit_button("Cancel")

            if delete_submitted:
                ok, message = delete_account(
                    current_user["user_id"], current_pw, confirm_text
                )
                if ok:
                    st.session_state.pop("account_mode", None)
                    st.switch_page("app.py")
                else:
                    st.error(message)

            if cancel_submitted:
                _rt = st.session_state.pop("account_return_to", "main")
                st.session_state.pop("account_mode", None)
                _go_to_return_page(_rt)


_AUTH_FORMS = {
    "sign_in",
    "register",
    "forgot_password",
    "verify_reset_code",
    "verify_registration_email",
}

AUTH_FORMS = _AUTH_FORMS
