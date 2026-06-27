"""Detailed results page for saved and current analyses."""

import html
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from backend.auth import get_current_user, is_guest_session, is_logged_in
from backend.database import ensure_db_initialized, get_user_analysis_history
from backend.model_config import (
    LABEL_DISPLAY,
    get_base_model_display_name,
    get_model_method_display_name,
    get_model_method_key,
)
from ui.helpers import BRAND_TEXT, format_semantic_score, handle_auth_query_params, inject_theme_toggle_script, load_css_bundle, load_favicon, render_navbar

MODEL_METHOD_EXPLANATIONS = {
    "full": "The whole model was trained on medical triage examples.",
    "lora": "A lighter training method was used to adapt the base model for triage.",
    "bottleneck_mlp": "Small additional layers were trained to adapt the base model for triage.",
    "frozen_encoder": "Only the final decision layer was trained for this triage task.",
}

# Page configuration.
st.set_page_config(
    page_title="SortMed - Results",
    page_icon=load_favicon(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Shared styling and navigation.
load_css_bundle(
    [
        "assets/css/base.css",
        "assets/css/streamlit-overrides.css",
        "assets/css/components.css",
        "assets/css/results.css",
        "assets/css/responsive.css",
    ]
)
handle_auth_query_params()
render_navbar(brand_text=BRAND_TEXT, current_user=get_current_user(), is_guest=is_guest_session(), current_page="results")
inject_theme_toggle_script()

ensure_db_initialized()

# Heroicons v2 SVG helpers used by result cards.
def _svg(path: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" '
        'stroke-width="1.5" stroke="currentColor">'
        f'<path stroke-linecap="round" stroke-linejoin="round" d="{path}"/></svg>'
    )

_SVG_BOLT   = _svg("M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z")
_SVG_CHECK  = _svg("M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z")
_SVG_SHIELD = _svg("M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z")

_SVG_CHEVRON = (
    '<svg class="res-chevron" xmlns="http://www.w3.org/2000/svg" fill="none" '
    'viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M9 18l6-6-6-6"/>'
    '</svg>'
)

_RESULT_CARD = {
    "error": {
        "icon": _SVG_BOLT,
        "cls": "result-card-urgent",
        "body": "Seek immediate medical assistance or call emergency services.",
    },
    "success": {
        "icon": _SVG_CHECK,
        "cls": "result-card-gp",
        "body": "A non-emergency condition is suggested. Medical evaluation recommended.",
    },
    "warning": {
        "icon": _SVG_SHIELD,
        "cls": "result-card-self",
        "body": "Symptoms appear mild. Monitor and rest.",
    },
}

SESSION_KEY_HISTORY    = "history"
SESSION_KEY_USER_INPUT = "user_input"
SESSION_KEY_ANALYSIS   = "last_analysis"

_LABEL_TO_LEVEL = {
    "urgent":       "error",
    "consult_gp":   "success",
    "self_monitor": "warning",
}

_SCORE_CLS = {
    "urgent":       "score-urgent",
    "consult_gp":   "score-gp",
    "self_monitor": "score-self",
}


# Rendering helpers.

def render_intro() -> None:
    st.title("Analysis Results", anchor=False)
    st.markdown(
        '<p class="res-subtitle">Review your latest pre-triage analysis, understand the recommendation, and revisit previous symptom checks saved to your account.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")


def render_user_input_summary() -> None:
    if SESSION_KEY_USER_INPUT in st.session_state:
        st.markdown("<h3>Your symptom description:</h3>", unsafe_allow_html=True)
        st.markdown(f"> {st.session_state[SESSION_KEY_USER_INPUT]}")
    else:
        st.warning("No analysis found. Please go back to the main page and analyze your symptoms first.")
        st.stop()


def render_triage_result(analysis: dict) -> None:
    """Render the main triage recommendation for the active model."""
    st.markdown("---")
    st.subheader("Triage Recommendation", anchor=False)

    level  = analysis.get("level", "info")
    result = analysis.get("result", "N/A")
    conf   = analysis.get("confidence", "N/A")
    scores = analysis.get("scores", {})

    card = _RESULT_CARD.get(level)
    if card:
        st.markdown(
            f'<div class="result-card {card["cls"]}">'
            f'<span class="result-card-icon">{card["icon"]}</span>'
            f'<span class="result-card-body"><strong>{result}</strong>'
            f'<span>{card["body"]}</span></span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.info(f"**{result}**")
    confidence = analysis.get("confidence", 0.0)
    confidence_message = analysis.get("confidence_message", "Confidence unavailable")
    confidence_margin = analysis.get("confidence_margin", 0.0)

    st.markdown(
        f"**Confidence:** `{confidence:.1%}`  \n"
        f"**{confidence_message}**"
    )

    st.caption(
        f"Confidence margin: {confidence_margin:.1%} "
        "(difference between the top two class scores)"
    )

    # Show all class scores in descending order.
    if scores:
        st.markdown("**Score breakdown (all classes):**")
        col1, col2, col3 = st.columns(3)
        for col, (label, score) in zip(
            [col1, col2, col3],
            sorted(scores.items(), key=lambda x: x[1], reverse=True),
        ):
            col.metric(
            label=LABEL_DISPLAY.get(label, label),
            value=f"{score:.1%}",
        )


def render_medquad_context(analysis: dict) -> None:
    """Render MedQuAD context retrieved with semantic similarity."""
    context = analysis.get("context", [])
    if not context:
        st.info("No related medical information was retrieved from the MedQuAD dataset for this query.")
        return

    st.markdown("---")
    st.subheader("Related Medical Information (MedQuAD Semantic Retrieval)", anchor=False)
    st.caption(
        "These Q&A pairs were retrieved from the MedQuAD dataset using semantic "
        "similarity with your symptom description. They provide contextual information "
        "about possible conditions - not a diagnosis."
    )

    for i, item in enumerate(context, 1):
        question = item.get("question", "Related medical question")
    
        with st.expander(f"{i}. {question}"):
            st.markdown(f"**Topic:** {item.get('focus', 'General')}")
            st.markdown(f"**Question:** {question}")
            st.markdown("**Answer:**")
            st.markdown(item.get("answer", "No answer available."))
            st.markdown(f"**Semantic relevance:** `{format_semantic_score(item.get('score'))}`")


def format_percent(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1%}"


def format_timestamp(value: str | None) -> str:
    if not value:
        return "N/A"

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value

    local_time = parsed.astimezone(ZoneInfo("Europe/Bucharest"))
    return local_time.strftime("%d %B %Y, %H:%M")


def parse_medquad_context(raw_context: str | None) -> list[dict] | None:
    if not raw_context:
        return []
    try:
        parsed = json.loads(raw_context)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, list) else []


def render_saved_medquad_context(row: dict) -> None:
    context = parse_medquad_context(row.get("medquad_context_json"))

    if context is None:
        st.warning("Saved MedQuAD context could not be parsed.")
        return

    if not context:
        st.markdown(
            '<div class="res-section-card">'
            '<p class="res-section-label">Related Medical Information</p>'
            '<p class="res-details-note">'
            'No related medical information was found in the MedQuAD dataset with sufficient semantic relevance for this symptom description.'
            '</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    items_html = ""
    for i, item in enumerate(context, 1):
        if not isinstance(item, dict):
            continue
        question = html.escape(item.get("question", "Related medical question"))
        topic    = html.escape(item.get("focus", "General"))
        answer   = html.escape(item.get("answer", "No answer available."))
        score    = html.escape(format_semantic_score(item.get("score")))
        items_html += (
            f'<details class="res-detail-item">'
            f'<summary class="res-detail-summary">{_SVG_CHEVRON}{i}. {question}</summary>'
            f'<div class="res-details-body">'
            f'<p class="res-medquad-topic"><strong>Topic:</strong> {topic}</p>'
            f'<div style="height:8px"></div>'
            f'<p class="res-medquad-answer-label"><strong>Answer:</strong></p>'
            f'<div style="height:2px"></div>'
            f'<p class="res-medquad-answer">{answer}</p>'
            f'<div style="height:8px"></div>'
            f'<p class="res-medquad-score"><strong>Semantic relevance:</strong> <code class="sim-score">{score}</code></p>'
            f'</div>'
            f'</details>'
        )

    st.markdown(
        f'<div class="res-section-card">'
        f'<p class="res-section-label">Related Medical Information</p>'
        f'{items_html}'
        f'</div>',
        unsafe_allow_html=True,
    )




def render_saved_model_info(row: dict) -> None:
    model_key  = row.get("active_model_key") or "N/A"
    model_name = get_base_model_display_name(model_key)
    method_name = get_model_method_display_name(model_key)
    method_key = get_model_method_key(model_key)
    method_description = MODEL_METHOD_EXPLANATIONS.get(
        method_key,
        "This model was fine-tuned for the medical pre-triage task.",
    )

    st.markdown(
        f'<div class="res-section-card res-collapsible-card">'
        f'<details>'
        f'<summary>About this AI Analysis{_SVG_CHEVRON}</summary>'
        f'<div class="res-details-body">'
        f'<div class="res-model-overview">'
        # Model summary badge.
        f'<div style="padding:18px 22px;border-radius:14px;background:linear-gradient(135deg,rgba(59,130,246,0.07),rgba(143,0,255,0.11));border:1px solid rgba(143,0,255,0.2);box-shadow:0 2px 20px rgba(143,0,255,0.07)">'
        f'<p style="margin:0 0 4px;font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted)">AI model used</p>'
        f'<p style="margin:0;font-size:1.35rem;font-weight:900;color:var(--heading);line-height:1.2;letter-spacing:-0.01em">{html.escape(model_name)}</p>'
        f'</div>'
        # High-level model detail cards.
        f'<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:4px">'
        f'<div style="padding:14px 16px;border:1px solid var(--navbar-border);border-radius:10px;background:rgba(148,163,184,0.07)">'
        f'<p style="margin:0 0 5px 0;font-size:0.68rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--muted)">Purpose</p>'
        f'<p style="margin:0 0 5px 0;font-weight:700;color:var(--heading);font-size:0.93rem">Medical pre-triage classification</p>'
        f'<p style="margin:0;color:var(--muted);font-size:0.82rem;line-height:1.5">Classifies the symptom description into one of three care levels.</p>'
        f'</div>'
        f'<div style="padding:14px 16px;border:1px solid var(--navbar-border);border-radius:10px;background:rgba(148,163,184,0.07)">'
        f'<p style="margin:0 0 5px 0;font-size:0.68rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--muted)">Training approach</p>'
        f'<p style="margin:0 0 5px 0;font-weight:700;color:var(--heading);font-size:0.93rem">{html.escape(method_name)}</p>'
        f'<p style="margin:0;color:var(--muted);font-size:0.82rem;line-height:1.5">{html.escape(method_description)}</p>'
        f'</div>'
        f'<div style="padding:14px 16px;border:1px solid var(--navbar-border);border-radius:10px;background:rgba(148,163,184,0.07)">'
        f'<p style="margin:0 0 5px 0;font-size:0.68rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--muted)">Possible results</p>'
        f'<p style="margin:0 0 5px 0;font-weight:700;color:var(--heading);font-size:0.93rem">Self-monitor, Consult GP, Urgent</p>'
        f'<p style="margin:0;color:var(--muted);font-size:0.82rem;line-height:1.5">Three triage levels, from mild to emergency.</p>'
        f'</div>'
        f'<div style="padding:14px 16px;border:1px solid var(--navbar-border);border-radius:10px;background:rgba(148,163,184,0.07)">'
        f'<p style="margin:0 0 5px 0;font-size:0.68rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--muted)">Related medical information</p>'
        f'<p style="margin:0 0 5px 0;font-weight:700;color:var(--heading);font-size:0.93rem">MedQuAD dataset</p>'
        f'<p style="margin:0;color:var(--muted);font-size:0.82rem;line-height:1.5">When relevant, the app shows related medical Q&amp;A from MedQuAD.</p>'
        f'</div>'
        f'</div>'
        f'</div>'
        # Medical safety limitation notice.
        f'<p class="res-details-note"><strong>Important limitation:</strong> This is not a diagnosis '
        f'and does not replace professional medical advice.</p>'
        f'</div>'
        f'</details>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_saved_analysis(row: dict, *, expanded: bool = True) -> None:
    timestamp     = row.get("timestamp") or "N/A"
    model_key     = row.get("active_model_key") or "N/A"
    model_name    = get_base_model_display_name(model_key)
    method_name   = get_model_method_display_name(model_key)
    predicted_label = row.get("predicted_label") or ""
    display_label = row.get("display_label") or "N/A"
    confidence    = row.get("confidence")       # float | None
    conf_message  = row.get("confidence_message") or ""
    conf_margin   = row.get("confidence_margin")  # float | None
    input_text    = html.escape(row.get("input_text") or "")

    # Meta: date + model - section card
    st.markdown(
        f'<div class="res-section-card">'
        f'<p class="res-section-label">Analysis Info</p>'
        f'<div class="res-meta-grid">'
        f'<span class="res-meta-key">Date</span>'
        f'<span class="res-meta-val">{html.escape(timestamp)}</span>'
        f'<span class="res-meta-key">Model</span>'
        f'<span class="res-meta-val">{html.escape(model_name)} - {html.escape(method_name)}</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Symptom description
    st.markdown(
        f'<div class="res-section-card">'
        f'<p class="res-section-label">Symptom Description</p>'
        f'<p class="res-symptom-text">&ldquo;{input_text}&rdquo;</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Recommendation - section card
    level = _LABEL_TO_LEVEL.get(predicted_label, "info")
    card  = _RESULT_CARD.get(level)
    if card:
        st.markdown(
            f'<div class="res-section-card">'
            f'<p class="res-section-label">Recommendation</p>'
            f'<div class="result-card {card["cls"]}">'
            f'<span class="result-card-icon">{card["icon"]}</span>'
            f'<div class="result-card-body"><strong>{html.escape(display_label)}</strong>'
            f'<span>{card["body"]}</span></div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<p class="res-section-label">Recommendation</p>', unsafe_allow_html=True)
        st.info(f"**{display_label}**")

    # Confidence + Score Breakdown - grouped in one section card
    scores_raw = [
        ("self_monitor", row.get("score_self_monitor")),
        ("consult_gp",   row.get("score_consult_gp")),
        ("urgent",       row.get("score_urgent")),
    ]
    valid_scores = [(lbl, s) for lbl, s in scores_raw if s is not None]
    has_confidence = confidence is not None
    has_scores     = bool(valid_scores)

    if has_confidence or has_scores:
        stats_html = '<div class="res-section-card">'

        if has_confidence:
            bar_pct = f"{confidence * 100:.1f}%"
            stats_html += (
                f'<p class="res-section-label">Confidence</p>'
                f'<div class="res-confidence-wrap">'
                f'<div class="res-confidence-row">'
                f'<div class="res-confidence-bar">'
                f'<div class="res-confidence-fill" style="width:{bar_pct}"></div>'
                f'</div>'
                f'<span class="res-confidence-value">{confidence:.1%}</span>'
                f'</div>'
            )
            if conf_message:
                stats_html += f'<p class="res-confidence-msg">{html.escape(conf_message)}</p>'
            if conf_margin is not None:
                stats_html += f'<p class="res-stats-margin">Margin between top two scores: {conf_margin:.1%}</p>'
            stats_html += '</div>'

        if has_scores:
            sep_cls = ' res-section-label-sep' if has_confidence else ''
            top_label     = max(valid_scores, key=lambda x: x[1])[0]
            sorted_scores = sorted(valid_scores, key=lambda x: x[1], reverse=True)
            stats_html += f'<p class="res-section-label{sep_cls}">Score Breakdown</p>'
            stats_html += '<div class="res-scores">'
            for lbl, score in sorted_scores:
                disp   = LABEL_DISPLAY.get(lbl, lbl)
                cls    = _SCORE_CLS.get(lbl, "")
                active = " active" if lbl == top_label else ""
                stats_html += (
                    f'<div class="res-score {cls}{active}">'
                    f'<div class="res-score-label">{disp}</div>'
                    f'<div class="res-score-value">{score:.1%}</div>'
                    f'</div>'
                )
            stats_html += '</div>'

        stats_html += '</div>'
        st.markdown(stats_html, unsafe_allow_html=True)

    render_saved_model_info(row)

    if expanded:
        render_saved_medquad_context(row)


def render_saved_history(history: list[dict]) -> None:
    if not history:
        st.markdown(
            """<div class="res-empty-state">
  <p class="res-empty-title">No saved analyses yet</p>
  <p class="res-empty-desc">Run a symptom analysis to build your history. Your results will appear here after your first check.</p>
</div>""",
            unsafe_allow_html=True,
        )
        return

    latest = history[0]
    st.subheader("Latest Analysis", anchor=False)
    render_saved_analysis(latest)

    if len(history) == 1:
        return

    st.markdown("---")
    st.subheader("Saved Analyses", anchor=False)

    for item in history[1:]:
        label      = item.get("display_label") or item.get("predicted_label") or "Analysis"
        timestamp  = item.get("timestamp") or "N/A"
        conf       = item.get("confidence")
        conf_str   = f"{conf:.1%}" if conf is not None else ""
        model_key  = item.get("active_model_key") or ""
        model_name = get_base_model_display_name(model_key)
        method_name = get_model_method_display_name(model_key)

        parts = [timestamp, label]
        if conf_str:
            parts.append(conf_str)
        if model_name:
            parts.append(f"{model_name} - {method_name}")

        with st.expander("  -  ".join(parts)):
            render_saved_analysis(item)


def render_footer() -> None:
    st.markdown(
        '<div class="footer-centered">© 2026 SortMed. All rights reserved.</div>',
        unsafe_allow_html=True,
    )


# Page content.
render_intro()

if not is_logged_in():
    st.warning("Please log in from the main page to view your saved results.")
    st.stop()

current_user = get_current_user()
history = get_user_analysis_history(current_user["user_id"])
render_saved_history(history)
render_footer()
