"""About page with project scope, usage flow, and safety information."""

import streamlit as st

from backend.auth import get_current_user, is_guest_session
from ui.helpers import BRAND_TEXT, get_brand_logo_inverted_src, get_brand_logo_src, handle_auth_query_params, inject_theme_toggle_script, load_css_bundle, load_favicon, render_navbar

st.set_page_config(
    page_title="SortMed - About",
    page_icon=load_favicon(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_css_bundle([
    "assets/css/base.css",
    "assets/css/streamlit-overrides.css",
    "assets/css/components.css",
    "assets/css/about.css",
    "assets/css/responsive.css",
])
handle_auth_query_params()
render_navbar(brand_text=BRAND_TEXT, current_user=get_current_user(), is_guest=is_guest_session(), current_page="about")
inject_theme_toggle_script()

# Heroicons v2 outline SVGs used by the About page.

def _svg(path: str, cls: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" '
        f'stroke-width="1.5" stroke="currentColor" class="about-svg-icon {cls}">'
        f'<path stroke-linecap="round" stroke-linejoin="round" d="{path}"/></svg>'
    )

ICO_CHAT     = _svg("M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155")
ICO_CHECK    = _svg("M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z")
ICO_CHART    = _svg("M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z")
ICO_CPU      = _svg("M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25zm.75-12h9v9h-9v-9z")
ICO_ARCHIVE  = _svg("M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z")

ICO_WARNING  = _svg("M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z", "ico-safety")
ICO_LOCK     = _svg("M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z", "ico-privacy")
ICO_ACADEMIC = _svg("M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5", "ico-academic")
ICO_ENVELOPE = _svg("M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75", "ico-contact")

ICO_BOLT     = _svg("M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z", "ico-urgent")
ICO_CLIP     = _svg("M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z", "ico-gp")
ICO_SHIELD   = _svg("M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z", "ico-self")

# Page content.

_logo_src = get_brand_logo_src()
_logo_inv_src = get_brand_logo_inverted_src()
if _logo_src:
    _inv_img = (
        f'<img src="{_logo_inv_src}" class="about-hero-logo about-hero-logo-light" alt="SortMed" />'
        if _logo_inv_src else ""
    )
    _logo_tag = (
        f'<img src="{_logo_src}" class="about-hero-logo about-hero-logo-dark" alt="SortMed" />'
        f"{_inv_img}"
    )
else:
    _logo_tag = '<span class="about-gradient-text">SortMed</span>'

st.markdown(f"""
<div class="about-page">

  <div class="about-hero">
    <p class="about-hero-title">About{_logo_tag}</p>
    <div class="about-hero-badge">Medical Pre-Triage Assistant</div>
  </div>

  <div class="about-section">
    <p class="about-section-title">What is SortMed?</p>
    <p class="about-section-lead">An AI-assisted platform designed to help you describe your symptoms in plain language and receive an indicative recommendation about the level of medical attention that may be appropriate. Built to support early orientation, not to replace professional medical judgment.</p>
  </div>

  <div class="about-section">
    <p class="about-section-title">What SortMed Does</p>
    <p class="about-section-lead">SortMed analyzes symptom descriptions and provides indicative pre-triage recommendations based on the selected AI model.</p>
    <div class="about-feature-grid">
      <div class="about-feature-card">
        <span class="about-feature-icon">{ICO_CHAT}</span>
        <span>Describe symptoms in natural language</span>
      </div>
      <div class="about-feature-card">
        <span class="about-feature-icon">{ICO_CHECK}</span>
        <span>Receive an indicative triage recommendation</span>
      </div>
      <div class="about-feature-card">
        <span class="about-feature-icon">{ICO_CHART}</span>
        <span>View the confidence level of each prediction</span>
      </div>
      <div class="about-feature-card">
        <span class="about-feature-icon">{ICO_CPU}</span>
        <span>Compare results from multiple AI models</span>
      </div>
      <div class="about-feature-card">
        <span class="about-feature-icon">{ICO_ARCHIVE}</span>
        <span>Save and review previous analyses with an account</span>
      </div>
    </div>
  </div>

  <div class="about-section">
    <p class="about-section-title">How It Works</p>
    <div class="about-steps">
      <div class="about-step">
        <div class="about-step-num">1</div>
        <div class="about-step-body">
          <strong>Enter your symptoms</strong>
          <span>Describe how you feel in plain language — no medical vocabulary required.</span>
        </div>
      </div>
      <div class="about-step-arrow">→</div>
      <div class="about-step">
        <div class="about-step-num">2</div>
        <div class="about-step-body">
          <strong>AI processes the input</strong>
          <span>A fine-tuned medical language model classifies the text and returns a confidence score.</span>
        </div>
      </div>
      <div class="about-step-arrow">→</div>
      <div class="about-step">
        <div class="about-step-num">3</div>
        <div class="about-step-body">
          <strong>Receive a recommendation</strong>
          <span>Review the suggested level of care alongside related medical context from MedQuAD.</span>
        </div>
      </div>
    </div>
  </div>

  <div class="about-section">
    <p class="about-section-title">Understanding the Recommendations</p>
    <p class="about-section-lead">SortMed classifies symptoms into one of three indicative levels of care:</p>
    <div class="about-rec-grid">
      <div class="about-rec-card about-rec-urgent">
        <div class="about-rec-label">{ICO_BOLT} Urgent</div>
        <div class="about-rec-desc">Symptoms may require immediate medical attention or emergency services.</div>
      </div>
      <div class="about-rec-card about-rec-gp">
        <div class="about-rec-label">{ICO_CLIP} Consult a GP</div>
        <div class="about-rec-desc">A non-emergency condition is suggested. Medical evaluation is recommended.</div>
      </div>
      <div class="about-rec-card about-rec-self">
        <div class="about-rec-label">{ICO_SHIELD} Self-Monitor</div>
        <div class="about-rec-desc">Symptoms appear mild. Rest and monitor your condition at home.</div>
      </div>
    </div>
    <p class="about-disclaimer">These recommendations are informational only and should not be used as a final medical decision.</p>
  </div>

  <div class="about-section">
    <p class="about-section-title">Important to Know</p>
    <div class="about-info-grid">
      <div class="about-info-card">
        <div class="about-info-icon">{ICO_WARNING}</div>
        <p class="about-info-title">Safety &amp; Limitations</p>
        <p>SortMed does not provide a medical diagnosis, prescribe treatment, or replace consultation with a qualified healthcare professional.</p>
        <p>If symptoms are severe, rapidly worsening, or potentially life-threatening, contact emergency medical services immediately.</p>
      </div>
      <div class="about-info-card">
        <div class="about-info-icon">{ICO_LOCK}</div>
        <p class="about-info-title">Data &amp; Privacy</p>
        <p>SortMed uses local account functionality to save profiles and analysis history. Passwords are protected using hashing.</p>
        <p>Users can delete their account and all associated data at any time. See the <a href="/?legal=privacy" target="_self">Privacy Policy</a> and <a href="/?legal=terms" target="_self">Terms of Service</a> for details.</p>
      </div>
      <div class="about-info-card">
        <div class="about-info-icon">{ICO_ACADEMIC}</div>
        <p class="about-info-title">Academic Context</p>
        <p>SortMed was developed as part of a bachelor's degree project at the <strong>Faculty of Computer Science, West University of Timișoara</strong>.</p>
        <p>The project explores the use of fine-tuned AI models for medical pre-triage and user-facing decision-support applications.</p>
      </div>
      <div class="about-info-card">
        <div class="about-info-icon">{ICO_ENVELOPE}</div>
        <p class="about-info-title">Contact</p>
        <p><strong>Cristian Untaru</strong><br>Faculty of Computer Science<br>West University of Timișoara</p>
        <p><a href="mailto:untarucristi89@gmail.com">untarucristi89@gmail.com</a></p>
      </div>
    </div>
  </div>

</div>

<div class="footer-centered" style="margin-top: 2rem;">
  © 2026 SortMed. All rights reserved.
</div>
""", unsafe_allow_html=True)
