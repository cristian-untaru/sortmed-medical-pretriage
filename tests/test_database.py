"""Database integration tests for account and analysis persistence."""

from __future__ import annotations

from datetime import datetime, timedelta

from backend import database


def test_analysis_history_is_limited_and_sorted(
    isolated_storage,
    sample_analysis,
    unique_email,
) -> None:
    database.init_db()
    user = database.create_user(
        first_name="Test",
        last_name="User",
        email=unique_email,
        password_hash="hash",
    )

    try:
        for index in range(3):
            analysis = sample_analysis | {"confidence": 0.50 + index / 10}
            database.save_analysis(user["user_id"], f"symptom text {index}", analysis)

        history = database.get_user_analysis_history(user["user_id"], limit=2)

        assert len(history) == 2
        assert history[0]["input_text"] == "symptom text 2"
        assert history[1]["input_text"] == "symptom text 1"
    finally:
        database.delete_user_account(user["user_id"], unique_email)


def test_auth_session_is_restored_and_removed_with_account(
    isolated_storage,
    unique_email,
) -> None:
    database.init_db()
    user = database.create_user(
        first_name="Session",
        last_name="User",
        email=unique_email,
        password_hash="hash",
    )
    session_hash = "test-session-token-hash"
    expires_at = (
        datetime.now(database.LOCAL_TIMEZONE) + timedelta(days=1)
    ).strftime(database.DISPLAY_TIMESTAMP_FORMAT)

    try:
        database.create_auth_session(user["user_id"], session_hash, expires_at)
        restored_user = database.get_active_auth_session(session_hash)

        assert restored_user is not None
        assert restored_user["user_id"] == user["user_id"]
        assert restored_user["email"] == unique_email
    finally:
        database.delete_user_account(user["user_id"], unique_email)

    assert database.get_active_auth_session(session_hash) is None


def test_account_statistics_group_peft_models_by_base_model(
    isolated_storage,
    sample_analysis,
    unique_email,
) -> None:
    database.init_db()
    user = database.create_user(
        first_name="Test",
        last_name="User",
        email=unique_email,
        password_hash="hash",
    )

    try:
        database.save_analysis(user["user_id"], "first input", sample_analysis)
        database.save_analysis(
            user["user_id"],
            "second input",
            sample_analysis
            | {
                "active_model_key": "bottleneck-mlp-distilbert",
                "model_method_key": "bottleneck_mlp",
            },
        )
        database.save_analysis(
            user["user_id"],
            "third input",
            sample_analysis
            | {
                "active_model_key": "frozen-encoder-biobert",
                "base_model_key": "biobert",
                "model_method_key": "frozen_encoder",
            },
        )

        stats = database.get_user_account_statistics(user["user_id"])

        assert stats["total_analyses"] == 3
        assert stats["models_used_count"] == 2
        assert stats["model_breakdown"] == {"distilbert": 2, "biobert": 1}
        assert stats["most_used_model"] == "distilbert"
    finally:
        database.delete_user_account(user["user_id"], unique_email)
