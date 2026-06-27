"""Main Streamlit entry point for SortMed."""

from __future__ import annotations

import streamlit as st

from backend.auth import get_current_user, is_guest_session, is_logged_in
from backend.database import ensure_db_initialized
from backend.model_config import ACTIVE_MODEL_KEY
from ui.analysis_views import (
    handle_analyze_button,
    render_model_selector,
    render_page_header,
    render_symptom_input,
)
from ui.auth_views import AUTH_FORMS, is_guest_user, render_account_interface, render_auth_interface
from ui.helpers import (
    BRAND_TEXT,
    handle_auth_query_params,
    inject_selectbox_lock_script,
    inject_theme_toggle_script,
    load_css_bundle,
    load_favicon,
    render_navbar,
)
from ui.landing import render_landing_page
from ui.legal_views import render_legal_page

st.set_page_config(
    page_title="SortMed",
    page_icon=load_favicon(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_css_bundle(
    [
        "assets/css/base.css",
        "assets/css/streamlit-overrides.css",
        "assets/css/components.css",
        "assets/css/app.css",
        "assets/css/auth.css",
        "assets/css/results.css",
        "assets/css/landing.css",
        "assets/css/responsive.css",
    ]
)

ensure_db_initialized()
handle_auth_query_params()

if st.query_params.get("account") == "change_password":
    if is_logged_in():
        st.session_state["account_mode"] = "confirm_current_password"
        st.session_state["account_return_to"] = st.query_params.get("return_to", "main")
        st.session_state.pop("password_change_verified", None)
    st.query_params.clear()
    st.rerun()

if st.query_params.get("account") == "delete_account":
    if is_logged_in():
        st.session_state["account_mode"] = "delete_account"
        st.session_state["account_return_to"] = st.query_params.get("return_to", "main")
    st.query_params.clear()
    st.rerun()

legal_param = st.query_params.get("legal", "")
if legal_param in ("terms", "privacy"):
    is_unauthenticated = not is_logged_in() and not is_guest_user()
    if is_unauthenticated:
        st.session_state["prev_auth_mode"] = st.session_state.get("auth_mode", "sign_in")
    else:
        st.session_state["prev_auth_mode"] = "__main__"
        st.session_state["legal_return_to"] = st.query_params.get("return_to", "main")
    st.session_state["auth_mode"] = "terms_of_service" if legal_param == "terms" else "privacy_policy"
    st.query_params.clear()
    st.rerun()

page_mode = st.session_state.get("auth_mode", "")
if page_mode in ("terms_of_service", "privacy_policy"):
    render_legal_page(page_mode)

if st.query_params.get("forgot") == "1":
    if not is_logged_in() and not is_guest_user():
        st.session_state["auth_mode"] = "forgot_password"
    st.query_params.clear()
    st.rerun()

if not is_logged_in() and not is_guest_user():
    if st.session_state.get("auth_mode", "") in AUTH_FORMS:
        render_auth_interface()
    else:
        render_landing_page()
    st.stop()

render_navbar(
    brand_text=BRAND_TEXT,
    current_user=get_current_user(),
    is_guest=is_guest_user(),
    current_page="main",
)
inject_theme_toggle_script()

selected_model_key = st.session_state.get("selected_model_key", ACTIVE_MODEL_KEY)

if st.session_state.get("account_mode") in (
    "confirm_current_password",
    "set_new_password",
    "password_changed_success",
    "delete_account",
):
    render_account_interface()
    st.stop()

render_page_header(selected_model_key)
selected_model_key = render_model_selector()
inject_selectbox_lock_script()
user_input = render_symptom_input()
handle_analyze_button(user_input, selected_model_key)

st.markdown(
    '<div class="footer-centered">&copy; 2026 SortMed. All rights reserved.</div>',
    unsafe_allow_html=True,
)
