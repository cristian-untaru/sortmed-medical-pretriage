"""Public landing page shown before authentication."""

from __future__ import annotations

import streamlit as st

from backend.auth import start_guest_session
from ui.helpers import inject_theme_toggle_script
from ui.icons import _SVG_CHECK

def _build_landing_html() -> str:
    def _ico(d: str) -> str:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"'
            ' stroke-width="1.5" stroke="currentColor">'
            f'<path stroke-linecap="round" stroke-linejoin="round" d="{d}"/>'
            '</svg>'
        )

    I_SEARCH  = "M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 15.803 7.5 7.5 0 0015.803 15.803z"
    I_CLIP    = "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
    I_SPARK   = "M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456z"
    I_ARCHIVE = "M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"
    I_MOON    = "M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z"
    I_LOCK    = "M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"
    I_EXCL    = "M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
    I_USER    = "M17.982 18.725A7.488 7.488 0 0012 15.75a7.488 7.488 0 00-5.982 2.975m11.963 0a9 9 0 10-11.963 0m11.963 0A8.966 8.966 0 0112 21a8.966 8.966 0 01-5.982-2.275M15 9.75a3 3 0 11-6 0 3 3 0 016 0z"
    I_HEART   = "M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"
    I_SHIELD  = "M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"
    I_INFO    = "M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"
    I_CAP     = "M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5"

    return (
        '<div class="lp-page">'

        # Main landing section with the demo analysis preview.
        '<section class="lp-section lp-hero">'
        '<div class="lp-hero-inner">'

        '<div class="lp-hero-text">'
        f'<div class="lp-hero-badge">{_ico(I_SPARK)} Medical Triage Support Powered by AI</div>'
        '<h1 class="lp-hero-headline">A clearer first step<br>'
        '<span class="lp-gradient-text">before seeking medical care.</span></h1>'
        '<p class="lp-hero-sub">Describe your symptoms in plain language and SortMed will '
        'suggest the appropriate level of medical attention. Instantly, privately, and for free.</p>'
        '<div class="lp-hero-ctas">'
        '<a class="lp-btn lp-btn-primary lp-btn-lg" href="?action=get_started" target="_self">Get Started</a>'
        '<a class="lp-btn lp-btn-outline lp-btn-lg" href="?action=login" target="_self">Log in</a>'
        '</div>'
        '<a class="lp-guest-link" href="?action=guest" target="_self">or continue as Guest &rarr;</a>'
        '<p class="lp-hero-disclaimer">Not a medical diagnosis. Always consult a qualified healthcare provider for serious symptoms.</p>'
        '</div>'

        '<div class="lp-hero-preview">'
        '<div class="lp-preview-float">'
        '<div class="lp-preview-card">'
        '<div class="res-section-card">'
        '<p class="res-section-label">Symptom Description</p>'
        '<p class="res-symptom-text">&ldquo;Mild cough and fatigue for two days&rdquo;</p>'
        '</div>'
        '<div class="res-section-card">'
        '<p class="res-section-label">Recommendation</p>'
        '<div class="result-card result-card-gp">'
        f'<span class="result-card-icon">{_SVG_CHECK}</span>'
        '<div class="result-card-body"><strong>Consult a GP</strong>'
        '<span>A medical evaluation is recommended for your symptoms.</span></div>'
        '</div>'
        '</div>'
        '<div class="res-section-card">'
        '<p class="res-section-label">Confidence</p>'
        '<div class="res-confidence-wrap">'
        '<div class="res-confidence-row">'
        '<div class="res-confidence-bar"><div class="res-confidence-fill" style="width:82.4%"></div></div>'
        '<span class="res-confidence-value">82.4%</span>'
        '</div>'
        '<p class="res-confidence-msg">High confidence prediction</p>'
        '</div>'
        '<p class="res-section-label res-section-label-sep">Score Breakdown</p>'
        '<div class="res-scores">'
        '<div class="res-score score-gp active"><div class="res-score-label">Consult GP</div><div class="res-score-value">82.4%</div></div>'
        '<div class="res-score score-self"><div class="res-score-label">Self-Monitor</div><div class="res-score-value">12.4%</div></div>'
        '<div class="res-score score-urgent"><div class="res-score-label">Urgent</div><div class="res-score-value">5.2%</div></div>'
        '</div>'
        '</div>'
        '</div>'
        '<p class="lp-preview-label">DEMO ANALYSIS &middot; NOT REAL MEDICAL ADVICE</p>'
        '</div>'
        '</div>'

        '</div>'
        '</section>'

        # Short product flow shown before account creation.
        '<section class="lp-section lp-section-alt">'
        '<div class="lp-section-inner">'
        '<p class="lp-eyebrow">How it works</p>'
        '<h2 class="lp-section-title">Four simple steps</h2>'
        '<p class="lp-section-sub">From symptom description to triage recommendation in seconds. No medical jargon and no account required to try.</p>'
        '<div class="lp-steps">'
        '<div class="lp-step"><div class="lp-step-number">01</div><div>'
        '<p class="lp-step-title">Describe your symptoms</p>'
        '<p class="lp-step-desc">Type how you feel in plain language. No medical terminology is needed.</p>'
        '</div></div>'
        '<div class="lp-step-arrow">&rsaquo;</div>'
        '<div class="lp-step"><div class="lp-step-number">02</div><div>'
        '<p class="lp-step-title">AI analysis</p>'
        '<p class="lp-step-desc">Our fine-tuned language model classifies the triage level with a confidence score.</p>'
        '</div></div>'
        '<div class="lp-step-arrow">&rsaquo;</div>'
        '<div class="lp-step"><div class="lp-step-number">03</div><div>'
        '<p class="lp-step-title">Get a recommendation</p>'
        '<p class="lp-step-desc">See a clear triage outcome: Urgent, Consult GP, or Self-Monitor. Each result includes a full score breakdown.</p>'
        '</div></div>'
        '<div class="lp-step-arrow">&rsaquo;</div>'
        '<div class="lp-step"><div class="lp-step-number">04</div><div>'
        '<p class="lp-step-title">Save &amp; review</p>'
        '<p class="lp-step-desc">Create an account to store your analysis history and review past results anytime.</p>'
        '</div></div>'
        '</div>'
        '</div>'
        '</section>'

        # Product benefits and trust signals.
        '<section class="lp-section">'
        '<div class="lp-section-inner">'
        '<p class="lp-eyebrow">Why SortMed</p>'
        '<h2 class="lp-section-title">Focused on what matters</h2>'
        '<p class="lp-section-sub">Built with simplicity and privacy in mind. No unnecessary features, no data collection beyond what the app needs.</p>'
        '<div class="lp-features-grid">'
        f'<div class="lp-feature-card"><div class="lp-feature-icon">{_ico(I_SEARCH)}</div><p class="lp-feature-title">Symptom Analysis</p><p class="lp-feature-desc">Describe symptoms in everyday language and receive an immediate triage classification.</p></div>'
        f'<div class="lp-feature-card"><div class="lp-feature-icon">{_ico(I_CLIP)}</div><p class="lp-feature-title">Triage Classification</p><p class="lp-feature-desc">Three clear outcomes: Urgent, Consult GP, or Self-Monitor. Each outcome includes confidence scores.</p></div>'
        f'<div class="lp-feature-card"><div class="lp-feature-icon">{_ico(I_SPARK)}</div><p class="lp-feature-title">Powered by AI</p><p class="lp-feature-desc">Transformer models fine tuned on medical triage data to support reliable classification.</p></div>'
        f'<div class="lp-feature-card"><div class="lp-feature-icon">{_ico(I_ARCHIVE)}</div><p class="lp-feature-title">Analysis History</p><p class="lp-feature-desc">Create a free account to save and review all your past symptom analyses.</p></div>'
        f'<div class="lp-feature-card"><div class="lp-feature-icon">{_ico(I_MOON)}</div><p class="lp-feature-title">Dark &amp; Light Mode</p><p class="lp-feature-desc">A polished interface in both dark and light themes, optimised for any device.</p></div>'
        f'<div class="lp-feature-card"><div class="lp-feature-icon">{_ico(I_LOCK)}</div><p class="lp-feature-title">Privacy First</p><p class="lp-feature-desc">Your symptom data stays local. No sharing with third parties, no ads, ever.</p></div>'
        '</div>'
        '</div>'
        '</section>'

        # Explanation of the three recommendation levels.
        '<section class="lp-section lp-section-alt">'
        '<div class="lp-section-inner">'
        '<p class="lp-eyebrow">Triage System</p>'
        '<h2 class="lp-section-title">Three clear outcomes</h2>'
        '<p class="lp-section-sub">SortMed classifies every analysis into one of three triage levels, each with actionable guidance on what to do next.</p>'
        '<div class="lp-triage-grid">'
        f'<div class="lp-triage-card lp-triage-urgent"><div class="lp-triage-icon">{_ico(I_EXCL)}</div><h3>Urgent</h3><p>Symptoms may indicate a serious condition. Seek immediate medical attention or call emergency services.</p></div>'
        f'<div class="lp-triage-card lp-triage-gp"><div class="lp-triage-icon">{_ico(I_USER)}</div><h3>Consult a GP</h3><p>A non-emergency condition that warrants a visit to your general practitioner for evaluation and advice.</p></div>'
        f'<div class="lp-triage-card lp-triage-self"><div class="lp-triage-icon">{_ico(I_HEART)}</div><h3>Self-Monitor</h3><p>Symptoms appear mild. Rest, stay hydrated, and monitor for any changes over the next few days.</p></div>'
        '</div>'
        '</div>'
        '</section>'

        # Safety and academic context.
        '<section class="lp-section">'
        '<div class="lp-section-inner">'
        '<p class="lp-eyebrow">Our Principles</p>'
        '<h2 class="lp-section-title">Built responsibly</h2>'
        '<p class="lp-section-sub">SortMed is an academic research tool, not a medical device. Every design decision reflects that responsibility.</p>'
        '<div class="lp-responsible-grid">'
        f'<div class="lp-responsible-item"><h3>{_ico(I_SHIELD)} Not a diagnostic tool</h3><p>SortMed provides initial triage suggestions, never diagnoses. Every result includes a clear reminder to consult a healthcare professional.</p></div>'
        f'<div class="lp-responsible-item"><h3>{_ico(I_INFO)} Transparent AI</h3><p>Confidence scores and full score breakdowns are always shown so you understand exactly how the model reached its recommendation.</p></div>'
        f'<div class="lp-responsible-item"><h3>{_ico(I_LOCK)} Local data only</h3><p>Analysis history is stored in a local database. No data is sent to external analytics or advertising services.</p></div>'
        f'<div class="lp-responsible-item"><h3>{_ico(I_CAP)} Academic project</h3><p>Developed as a Bachelor\'s thesis at the Faculty of Computer Science, West University of Timişoara.</p></div>'
        '</div>'
        '</div>'
        '</section>'

        # Final call to action and legal links.
        '<section class="lp-section lp-footer-section">'
        '<div class="lp-section-inner">'
        '<div class="lp-footer-cta">'
        '<h2>Ready to get started?</h2>'
        '<p>Create a free account to save your analyses, or try it right away as a guest.</p>'
        '<div class="lp-hero-ctas">'
        '<a class="lp-btn lp-btn-primary lp-btn-lg" href="?action=get_started" target="_self">Create Account</a>'
        '<a class="lp-btn lp-btn-outline lp-btn-lg" href="?action=login" target="_self">Log in</a>'
        '</div>'
        '<a class="lp-guest-link" href="?action=guest" target="_self">or continue as Guest &rarr;</a>'
        '</div>'
        '<div class="lp-footer-bottom">'
        '<p>&copy; 2026 SortMed &nbsp;&middot;&nbsp;'
        ' <a href="?legal=terms" target="_self">Terms of Service</a>'
        ' &nbsp;&middot;&nbsp;'
        ' <a href="?legal=privacy" target="_self">Privacy Policy</a></p>'
        '</div>'
        '</div>'
        '</section>'

        '</div>'
    )


def render_landing_page() -> None:
    action = st.query_params.get("action", "")
    if action == "get_started":
        st.query_params.clear()
        st.session_state["auth_mode"] = "register"
        st.rerun()
    elif action == "login":
        st.query_params.clear()
        st.session_state["auth_mode"] = "sign_in"
        st.rerun()
    elif action == "guest":
        st.query_params.clear()
        start_guest_session()
        st.rerun()

    st.markdown(_build_landing_html(), unsafe_allow_html=True)
    inject_theme_toggle_script()
