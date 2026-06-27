"""Main analysis form and result rendering for the Streamlit app."""

from __future__ import annotations

import html
from typing import Any, Dict

import streamlit as st

from backend import input_guard, predictor
from backend.auth import get_current_user
from backend.database import save_analysis
from backend.model_config import (
    ACTIVE_MODEL_KEY,
    BASE_MODEL_DISPLAY_NAMES,
    BASE_MODEL_KEYS,
    ENABLE_PEFT_MODEL_SELECTION,
    LABEL_DISPLAY,
    MODEL_DISPLAY_NAMES,
    MODEL_METHOD_DISPLAY_NAMES,
    MODEL_METHOD_OPTIONS,
    MODEL_REGISTRY,
    USER_CAN_SELECT_MODEL,
    build_model_key,
    get_model_base_key,
    get_model_history_display_name,
    get_model_method_display_name,
    get_model_method_key,
)
from ui.auth_views import is_guest_user
from ui.helpers import format_semantic_score
from ui.icons import _RESULT_CARD, _SCORE_CLS, _SVG_CHEVRON

def render_page_header(model_key: str) -> None:
    st.title("Intelligent Assistant for Medical Pre-Triage", anchor=False)
    st.markdown(
        "Welcome! Describe your symptoms below in plain language and the AI assistant "
        "will suggest an appropriate level of medical care."
    )
    st.markdown(
        '<div class="disclaimer-block">'
        '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"'
        ' stroke-width="1.5" stroke="currentColor" class="disclaimer-icon">'
        '<path stroke-linecap="round" stroke-linejoin="round"'
        ' d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0'
        " 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898"
        ' 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/>'
        "</svg>"
        '<p class="disclaimer-text"><strong>Disclaimer:</strong> This tool does'
        " <strong>not</strong> replace professional medical advice. "
        "Always consult a qualified healthcare provider for diagnosis and treatment.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    model_status = predictor.get_model_status(model_key)

    if model_status["ok"]:
        active_key = model_status["active_key"]
        model_id = model_status["model_id"]
        model_url = f"https://huggingface.co/{model_id}"
        model_name = get_model_history_display_name(active_key)
        method_name = get_model_method_display_name(active_key)

        # In developer mode the active model is shown here; otherwise the selector below shows the same details.
        if not USER_CAN_SELECT_MODEL:
            st.markdown(
                f"""
                <div class="active-model-box">
                    <span class="active-model-label">Active model:</span>
                    <span class="active-model-name">{html.escape(model_name)}</span>
                    <span class="active-model-separator">&middot;</span>
                    <span class="active-model-label">{html.escape(method_name)}</span>
                    <span class="active-model-separator">&middot;</span>
                    <a class="active-model-link" href="{model_url}" target="_blank">
                        {html.escape(model_id)}
                    </a>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.error("Active model configuration is invalid.")

        with st.expander("Developer details"):
            st.code(model_status["message"])


def render_model_selector() -> str:
    """
    Displays model controls and returns the backend model key.

    If PEFT selection is disabled in backend.model_config, this falls back to the
    original single-dropdown behavior with the four base models.
    """
    if not USER_CAN_SELECT_MODEL:
        return ACTIVE_MODEL_KEY

    current_key = st.session_state.get("selected_model_key", ACTIVE_MODEL_KEY)

    if ENABLE_PEFT_MODEL_SELECTION:
        current_method = get_model_method_key(current_key)
        if current_method not in MODEL_METHOD_OPTIONS:
            current_method = get_model_method_key(ACTIVE_MODEL_KEY)

        current_base = get_model_base_key(current_key) or get_model_base_key(ACTIVE_MODEL_KEY)
        if current_base not in BASE_MODEL_KEYS:
            current_base = BASE_MODEL_KEYS[0]

        method_options = list(MODEL_METHOD_OPTIONS)
        base_options = list(BASE_MODEL_KEYS)

        selected_method = st.selectbox(
            "Select fine-tuning method:",
            options=method_options,
            index=method_options.index(current_method),
            format_func=lambda key: MODEL_METHOD_DISPLAY_NAMES.get(key, key),
            key="selected_model_method_key",
            help=(
                "Choose how the model was fine-tuned. Full fine-tuning updates the "
                "whole model, while PEFT methods train fewer parameters."
            ),
        )

        selected_base = st.selectbox(
            "Select base model:",
            options=base_options,
            index=base_options.index(current_base),
            format_func=lambda key: BASE_MODEL_DISPLAY_NAMES.get(key, key),
            key="selected_base_model_key",
            help="Choose the transformer architecture used for the analysis.",
        )

        selected_key = build_model_key(selected_method, selected_base)
        st.session_state["selected_model_key"] = selected_key
    else:
        options = list(MODEL_REGISTRY.keys())
        fallback_key = ACTIVE_MODEL_KEY if ACTIVE_MODEL_KEY in options else options[0]
        if current_key not in options:
            st.session_state["selected_model_key"] = fallback_key
            current_key = fallback_key
        default_index = options.index(current_key)

        selected_key = st.selectbox(
            "Select analysis model:",
            options=options,
            index=default_index,
            format_func=lambda k: MODEL_DISPLAY_NAMES.get(k, k),
            key="selected_model_key",
            help=(
                "Choose the AI model used to classify your symptoms. "
                "Each model is fine-tuned on medical data and may produce slightly different triage results."
            ),
        )

    model_id = MODEL_REGISTRY[selected_key]
    model_url = f"https://huggingface.co/{model_id}"
    model_name = get_model_history_display_name(selected_key)
    method_name = get_model_method_display_name(selected_key)
    st.markdown(
        f"""
        <div class="active-model-box">
            <span class="active-model-label">Active model:</span>
            <span class="active-model-name">{html.escape(model_name)}</span>
            <span class="active-model-separator">&middot;</span>
            <span class="active-model-label">{html.escape(method_name)}</span>
            <span class="active-model-separator">&middot;</span>
            <a class="active-model-link" href="{model_url}" target="_blank">
                {html.escape(model_id)}
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return selected_key


def render_symptom_input() -> str:
    return st.text_area(
        "Describe your symptoms below:",
        placeholder="e.g. I've been coughing for three days and feel chest tightness...",
        height=150,
    )


def ensure_history_exists() -> None:
    if "history" not in st.session_state:
        st.session_state["history"] = []


def save_analysis_to_session(user_input: str, analysis: Dict[str, Any]) -> None:
    ensure_history_exists()
    st.session_state["user_input"] = user_input
    st.session_state["last_analysis"] = analysis
    st.session_state["history"].append(
        {
            "input":      user_input[:80] + "..." if len(user_input) > 80 else user_input,
            "result":     analysis["result"],
            "confidence": analysis["confidence"],
            "symptoms":   ", ".join(analysis["symptoms"]),
        }
    )


def render_analysis_feedback(analysis: Dict[str, Any]) -> None:
    """Render the triage result on the main analysis page."""

    level              = analysis["level"]
    result             = analysis["result"]
    scores             = analysis["scores"]
    context            = analysis["context"]
    confidence         = analysis.get("confidence")
    confidence_message = analysis.get("confidence_message", "")
    confidence_margin  = analysis.get("confidence_margin")

    st.markdown("---")
    st.subheader("Analysis Result", anchor=False)

    # Recommendation - section card
    card = _RESULT_CARD.get(level)
    if card:
        st.markdown(
            f'<div class="res-section-card">'
            f'<p class="res-section-label">Recommendation</p>'
            f'<div class="result-card {card["cls"]}">'
            f'<span class="result-card-icon">{card["icon"]}</span>'
            f'<div class="result-card-body"><strong>{html.escape(result)}</strong>'
            f'<span>{card["body"]}</span></div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<p class="res-section-label">Recommendation</p>', unsafe_allow_html=True)
        st.info(f"**{result}**")

    # Confidence + Score Breakdown - grouped section card
    valid_scores = [
        (lbl, scores[lbl])
        for lbl in ["self_monitor", "consult_gp", "urgent"]
        if scores.get(lbl) is not None
    ]
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
            if confidence_message:
                stats_html += f'<p class="res-confidence-msg">{html.escape(confidence_message)}</p>'
            if confidence_margin is not None:
                stats_html += f'<p class="res-stats-margin">Margin between top two scores: {confidence_margin:.1%}</p>'
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

    # Related Medical Information - section card
    if context:
        items_html = ""
        for i, item in enumerate(context, 1):
            question  = html.escape(item.get("question", "Related medical question"))
            topic     = html.escape(item.get("focus", "General"))
            answer    = html.escape(item.get("answer", "No answer available."))
            score_val = html.escape(format_semantic_score(item.get("score")))
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
                f'<p class="res-medquad-score"><strong>Semantic relevance:</strong> <code class="sim-score">{score_val}</code></p>'
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
    else:
        st.markdown(
            '<div class="res-section-card">'
            '<p class="res-section-label">Related Medical Information</p>'
            '<p class="res-details-note">'
            'No related medical information was found in the MedQuAD dataset with sufficient semantic relevance for this symptom description.'
            '</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.caption("This is not a medical diagnosis. Consult a specialist if symptoms persist or worsen.")


def handle_analyze_button(user_input: str, model_key: str) -> None:
    model_status = predictor.get_model_status(model_key)
    normalized_input = user_input.strip()
    already_analyzed = (
        bool(normalized_input)
        and normalized_input == st.session_state.get("last_analyzed_input")
        and model_key == st.session_state.get("last_analyzed_model_key")
        and input_guard.INPUT_GUARD_RULE_VERSION == st.session_state.get("last_input_guard_rule_version")
        and "last_analysis" in st.session_state
    )

    if not model_status["ok"]:
        st.error(
            "Model configuration error. "
            "The active model key is not registered in the backend."
        )

        with st.expander("Developer details"):
            st.code(model_status["message"])

        st.markdown('<span class="analyze-button-anchor"></span>', unsafe_allow_html=True)
        st.button("Analyze Symptoms", type="primary", disabled=True)
        return

    st.markdown('<span class="analyze-button-anchor"></span>', unsafe_allow_html=True)
    analyze_clicked = st.button(
        "Analyze Symptoms",
        type="primary",
        disabled=already_analyzed,
    )

    if not analyze_clicked:
        if already_analyzed:
            render_analysis_feedback(st.session_state["last_analysis"])
            save_warning = st.session_state.pop("analysis_save_warning", None)
            if save_warning:
                st.warning(save_warning)
            st.markdown("---")
        return

    if not normalized_input:
        st.warning("Please enter your symptoms before continuing.")
        return

    guard_result = input_guard.validate_symptom_input(normalized_input)
    if not guard_result.allowed:
        st.warning(guard_result.message)
        return

    with st.spinner("Analyzing your symptoms..."):
        try:
            # Pass the resolved model key explicitly, whether it came from the UI or ACTIVE_MODEL_KEY.
            analysis = predictor.run_full_analysis(normalized_input, model_key=model_key)
        except ValueError as e:
            st.error(str(e))
            return
        except FileNotFoundError as e:
            st.error(str(e))
            return
        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
            return

    st.session_state["last_analyzed_input"] = normalized_input
    st.session_state["last_analyzed_model_key"] = model_key
    st.session_state["last_input_guard_rule_version"] = input_guard.INPUT_GUARD_RULE_VERSION
    save_analysis_to_session(normalized_input, analysis)

    current_user = get_current_user()
    if current_user and not is_guest_user():
        try:
            save_analysis(current_user["user_id"], normalized_input, analysis)
        except Exception as e:
            st.session_state["analysis_save_warning"] = (
                f"Analysis was shown but could not be saved: {e}"
            )

    st.rerun()
