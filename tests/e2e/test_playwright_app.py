"""Browser-level smoke tests for the running Streamlit application."""

from __future__ import annotations

import os

import pytest
from playwright.sync_api import Page, expect


if not os.getenv("SORTMED_E2E_BASE_URL"):
    pytest.skip("Set SORTMED_E2E_BASE_URL to run browser tests.", allow_module_level=True)

pytestmark = pytest.mark.e2e


@pytest.fixture
def sortmed_base_url() -> str:
    return os.environ["SORTMED_E2E_BASE_URL"].rstrip("/")


def test_guest_user_can_reach_analysis_form(sortmed_base_url: str, page: Page) -> None:
    page.goto(f"{sortmed_base_url}/?action=guest")

    expect(page.get_by_text("Intelligent Assistant for Medical Pre-Triage")).to_be_visible(timeout=15000)
    expect(page.get_by_label("Describe your symptoms below:")).to_be_visible(timeout=15000)
    expect(page.get_by_role("button", name="Analyze Symptoms")).to_be_visible(timeout=15000)


def test_invalid_input_is_blocked_in_browser(sortmed_base_url: str, page: Page) -> None:
    page.goto(f"{sortmed_base_url}/?action=guest")

    page.get_by_label("Describe your symptoms below:").fill("head tac toe pain")
    page.get_by_role("button", name="Analyze Symptoms").click()

    expect(page.get_by_text("Please describe your symptoms as a clear sentence")).to_be_visible()
