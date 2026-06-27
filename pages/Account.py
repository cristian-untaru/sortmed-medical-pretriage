"""Account details and usage statistics page."""

import streamlit as st

from backend.auth import get_current_user, is_guest_session, is_logged_in
from backend.database import ensure_db_initialized, get_user_account_statistics
from backend.model_config import BASE_MODEL_DISPLAY_NAMES, BASE_MODEL_KEYS
from ui.helpers import (
    BRAND_TEXT,
    handle_auth_query_params,
    inject_theme_toggle_script,
    load_css_bundle,
    load_favicon,
    render_navbar,
)

st.set_page_config(
    page_title="SortMed - Account",
    page_icon=load_favicon(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_css_bundle([
    "assets/css/base.css",
    "assets/css/streamlit-overrides.css",
    "assets/css/components.css",
    "assets/css/account.css",
    "assets/css/responsive.css",
])

handle_auth_query_params()
render_navbar(brand_text=BRAND_TEXT, current_user=get_current_user(), is_guest=is_guest_session(), current_page="account")
inject_theme_toggle_script()
ensure_db_initialized()


def _fmt_pct(val) -> str:
    if val is None:
        return "N/A"
    try:
        return f"{float(val):.1%}"
    except (TypeError, ValueError):
        return "N/A"


def render_profile_section(user: dict) -> None:
    first = user.get("first_name") or ""
    last = user.get("last_name") or ""
    full_name = f"{first} {last}".strip() or "N/A"

    st.subheader("Profile Information", anchor=False)
    st.markdown(
        f"""
<div class="account-card">
    <div class="account-grid">
        <div class="account-field">
            <div class="account-field-label">First name</div>
            <div class="account-field-value">{first or "N/A"}</div>
        </div>
        <div class="account-field">
            <div class="account-field-label">Last name</div>
            <div class="account-field-value">{last or "N/A"}</div>
        </div>
        <div class="account-field">
            <div class="account-field-label">Email</div>
            <div class="account-field-value">{user.get("email") or "N/A"}</div>
        </div>
        <div class="account-field">
            <div class="account-field-label">Account created at</div>
            <div class="account-field-value">{user.get("created_at") or "N/A"}</div>
        </div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_stats_section(user_id: str) -> None:
    st.subheader("Usage Statistics", anchor=False)

    stats = get_user_account_statistics(user_id)
    total = int(stats.get("total_analyses") or 0)

    if total == 0:
        st.info(
            "No saved analyses yet. Once you analyze symptoms while logged in, "
            "your account statistics will appear here."
        )
        return

    most_used_key = stats.get("most_used_model")
    most_used_model = BASE_MODEL_DISPLAY_NAMES.get(most_used_key, most_used_key or "N/A")
    most_common_rec = stats.get("most_common_recommendation") or "N/A"
    avg_conf = _fmt_pct(stats.get("avg_confidence"))
    max_conf = _fmt_pct(stats.get("max_confidence"))
    models_used = int(stats.get("models_used_count") or 0)
    urgent_count = int(stats.get("urgent_count") or 0)
    consult_gp_count = int(stats.get("consult_gp_count") or 0)
    self_monitor_count = int(stats.get("self_monitor_count") or 0)
    latest_date = stats.get("latest_analysis_date") or "N/A"
    first_date = stats.get("first_analysis_date") or "N/A"
    avg_words = int(stats.get("avg_word_count") or 0)
    conf_high = int(stats.get("conf_high") or 0)
    conf_medium = int(stats.get("conf_medium") or 0)
    conf_low = int(stats.get("conf_low") or 0)

    model_breakdown = stats.get("model_breakdown") or {}
    all_models = list(BASE_MODEL_KEYS)

    model_cards = "".join(
        f'<div class="stat-card">'
        f'<span class="stat-value">{model_breakdown.get(key, 0)}</span>'
        f'<span class="stat-label">{BASE_MODEL_DISPLAY_NAMES.get(key, key)}</span>'
        f"</div>"
        for key in all_models
    )

    st.markdown(
        f"""
<div class="stats-sections">

  <div class="stats-section">
    <input type="checkbox" id="toggle-overview" class="section-toggle">
    <div class="stats-section-header">
      <p class="stats-section-title">Overview</p>
      <label for="toggle-overview" class="section-toggle-btn" title="Hide / show section">&#128065;</label>
    </div>
    <div class="stats-grid section-content">
      <div class="stat-card stat-card-primary">
        <span class="stat-value">{total}</span>
        <span class="stat-label">Total Analyses</span>
      </div>
      <div class="stat-card stat-card-primary">
        <span class="stat-value stat-value-sm">{most_used_model}</span>
        <span class="stat-label">Most Used Model</span>
      </div>
      <div class="stat-card stat-card-primary">
        <span class="stat-value">{avg_conf}</span>
        <span class="stat-label">Average Confidence</span>
      </div>
      <div class="stat-card stat-card-primary">
        <span class="stat-value">{max_conf}</span>
        <span class="stat-label">Highest Confidence</span>
      </div>
    </div>
  </div>

  <div class="stats-section">
    <input type="checkbox" id="toggle-triage" class="section-toggle">
    <div class="stats-section-header">
      <p class="stats-section-title">Triage Outcomes</p>
      <label for="toggle-triage" class="section-toggle-btn" title="Hide / show section">&#128065;</label>
    </div>
    <div class="stats-grid section-content">
      <div class="stat-card">
        <span class="stat-value stat-value-sm">{most_common_rec}</span>
        <span class="stat-label">Most Common Recommendation</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{urgent_count}</span>
        <span class="stat-label">Urgent Recommendations</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{consult_gp_count}</span>
        <span class="stat-label">Consult GP Recommendations</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{self_monitor_count}</span>
        <span class="stat-label">Self-Monitor Recommendations</span>
      </div>
    </div>
  </div>

  <div class="stats-section">
    <input type="checkbox" id="toggle-activity" class="section-toggle">
    <div class="stats-section-header">
      <p class="stats-section-title">Activity</p>
      <label for="toggle-activity" class="section-toggle-btn" title="Hide / show section">&#128065;</label>
    </div>
    <div class="stats-grid section-content">
      <div class="stat-card">
        <span class="stat-value">{models_used}</span>
        <span class="stat-label">Models Used</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">~{avg_words}</span>
        <span class="stat-label">Avg. Symptom Words</span>
      </div>
      <div class="stat-card">
        <span class="stat-value stat-value-sm">{latest_date}</span>
        <span class="stat-label">Latest Analysis</span>
      </div>
      <div class="stat-card">
        <span class="stat-value stat-value-sm">{first_date}</span>
        <span class="stat-label">First Analysis</span>
      </div>
    </div>
  </div>

  <div class="stats-section">
    <input type="checkbox" id="toggle-confidence" class="section-toggle">
    <div class="stats-section-header">
      <p class="stats-section-title">Confidence Distribution</p>
      <label for="toggle-confidence" class="section-toggle-btn" title="Hide / show section">&#128065;</label>
    </div>
    <div class="stats-grid-3 section-content">
      <div class="stat-card">
        <span class="stat-value stat-conf-high">{conf_high}</span>
        <span class="stat-label">High Confidence</span>
      </div>
      <div class="stat-card">
        <span class="stat-value stat-conf-medium">{conf_medium}</span>
        <span class="stat-label">Medium Confidence</span>
      </div>
      <div class="stat-card">
        <span class="stat-value stat-conf-low">{conf_low}</span>
        <span class="stat-label">Low Confidence</span>
      </div>
    </div>
  </div>

  <div class="stats-section">
    <input type="checkbox" id="toggle-models" class="section-toggle">
    <div class="stats-section-header">
      <p class="stats-section-title">Analyses by Model</p>
      <label for="toggle-models" class="section-toggle-btn" title="Hide / show section">&#128065;</label>
    </div>
    <div class="stats-grid section-content">{model_cards}</div>
  </div>

</div>
        """,
        unsafe_allow_html=True,
    )


# Page content.

st.title("Account Details", anchor=False)

if is_guest_session():
    st.warning("Guest users do not have account details or saved analysis history.")
    st.stop()

if not is_logged_in():
    st.warning("Please log in to view your account details.")
    if st.button("Go to login", type="primary"):
        st.switch_page("app.py")
    st.stop()

st.markdown("Review your profile information and saved analysis activity.")
st.markdown("---")

current_user = get_current_user()
render_profile_section(current_user)

st.markdown("---")
render_stats_section(current_user["user_id"])

st.markdown(
    '<div class="footer-centered" style="margin-top: 2rem;">'
    "© 2026 SortMed. All rights reserved."
    "</div>",
    unsafe_allow_html=True,
)
