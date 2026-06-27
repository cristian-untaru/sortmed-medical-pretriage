"""Legal document views used by the Streamlit app."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from backend.auth import get_current_user, is_guest_session, is_logged_in
from ui.helpers import BRAND_TEXT, inject_theme_toggle_script, render_navbar

LEGAL_CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "legal"


@st.cache_data(show_spinner=False)
def load_legal_document(filename: str) -> str:
    return (LEGAL_CONTENT_DIR / filename).read_text(encoding="utf-8")


def render_legal_page(page_mode: str) -> None:
    authed = is_logged_in() or is_guest_session()
    if authed:
        render_navbar(
            brand_text=BRAND_TEXT,
            current_user=get_current_user(),
            is_guest=is_guest_session(),
            current_page="main",
        )
        inject_theme_toggle_script()

    doc = "terms_of_service.md" if page_mode == "terms_of_service" else "privacy_policy.md"
    title = "Terms of Service" if page_mode == "terms_of_service" else "Privacy Policy"
    back_key = "legal_terms_back" if page_mode == "terms_of_service" else "legal_privacy_back"

    st.title(title, anchor=False)
    st.markdown('<p class="legal-page-updated">Last updated: June 2026</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(load_legal_document(doc))

    _, button_col, _ = st.columns([3, 2, 3])
    with button_col:
        if st.button("Back", key=back_key, use_container_width=True):
            previous = st.session_state.pop("prev_auth_mode", "__main__")
            if previous == "__main__":
                st.session_state.pop("auth_mode", None)
                return_to = st.session_state.pop("legal_return_to", "main")
                if return_to == "about":
                    st.switch_page("pages/About.py")
                elif return_to == "results":
                    st.switch_page("pages/Results.py")
                elif return_to == "account":
                    st.switch_page("pages/Account.py")
                else:
                    st.rerun()
            else:
                st.session_state["auth_mode"] = previous
                st.rerun()

    st.markdown(
        '<div class="footer-centered">&copy; 2026 SortMed. All rights reserved.</div>',
        unsafe_allow_html=True,
    )
    st.stop()
