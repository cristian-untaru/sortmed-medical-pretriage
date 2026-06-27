"""Streamlit AppTest coverage for authentication and analysis flows."""

from __future__ import annotations

import pytest
from streamlit.testing.v1 import AppTest

from backend.input_guard.models import InputGuardResult


def test_main_app_allows_registered_user_login(isolated_storage, unique_email) -> None:
    from backend.auth import hash_password
    from backend.database import create_user, delete_user_account, init_db

    init_db()
    user = create_user(
        first_name="Test",
        last_name="User",
        email=unique_email,
        password_hash=hash_password("secret123"),
    )

    try:
        at = AppTest.from_file("app.py", default_timeout=15)
        at.session_state["auth_mode"] = "sign_in"

        at.run()
        at.text_input[0].input(unique_email)
        at.text_input[1].input("secret123")
        at.button[0].click().run()

        assert not at.exception
        assert at.session_state["current_user"]["email"] == unique_email
    finally:
        delete_user_account(user["user_id"], unique_email)


def test_main_app_renders_guest_analysis_form(isolated_storage) -> None:
    at = AppTest.from_file("app.py", default_timeout=15)
    at.session_state["guest_user"] = True

    at.run()

    assert not at.exception
    assert len(at.selectbox) == 2
    assert at.selectbox[0].label == "Select fine-tuning method:"
    assert at.selectbox[1].label == "Select base model:"
    assert at.text_area[0].label == "Describe your symptoms below:"
    assert any(button.label == "Analyze Symptoms" for button in at.button)


def test_main_app_blocks_invalid_input_before_model_inference(
    isolated_storage,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = {"analysis": False}

    def fake_run_full_analysis(*args, **kwargs):
        called["analysis"] = True
        return {}

    monkeypatch.setattr(
        "backend.predictor.run_full_analysis",
        fake_run_full_analysis,
    )

    at = AppTest.from_file("app.py", default_timeout=15)
    at.session_state["guest_user"] = True

    at.run()
    at.text_area[0].input("head tac toe pain").run()
    at.button[0].click().run()

    assert not called["analysis"]
    assert any("clear sentence" in warning.value for warning in at.warning)


def test_main_app_shows_analysis_result_after_valid_input(
    isolated_storage,
    sample_analysis,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "backend.input_guard.validate_symptom_input",
        lambda text: InputGuardResult(
            allowed=True,
            intent="symptom_description",
            confidence=0.91,
            reason="valid_symptom_description",
        ),
    )
    monkeypatch.setattr(
        "backend.predictor.run_full_analysis",
        lambda text, model_key=None: sample_analysis
        | {"active_model_key": model_key or "distilbert"},
    )

    at = AppTest.from_file("app.py", default_timeout=15)
    at.session_state["guest_user"] = True

    at.run()
    at.text_area[0].input("I have a headache and feel dizzy today.").run()
    at.button[0].click().run()

    page_text = "\n".join(markdown.value for markdown in at.markdown)
    assert "Analysis Result" in page_text
    assert "Self-monitor" in page_text
    assert "Related Medical Information" in page_text
