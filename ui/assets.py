"""Static assets and CSS helpers for the Streamlit UI."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Sequence

import streamlit as st

BRAND_TEXT = "SortMed"
BRAND_LOGO_PATH = Path("assets/media/sortmed-logo-dark-theme.png")
BRAND_LOGO_INVERTED_PATH = Path("assets/media/sortmed-logo-light-theme.png")
FAVICON_PATH = Path("assets/media/sortmed-favicon.png")


def format_semantic_score(value: Any) -> str:
    """Format semantic relevance scores consistently in the UI."""
    if value is None:
        return "N/A"

    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return str(value)


@st.cache_resource(show_spinner=False)
def load_favicon():
    """Load the favicon with autocrop to remove any transparent padding."""
    try:
        from PIL import Image
        img = Image.open(FAVICON_PATH).convert("RGBA")
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        return img
    except Exception:
        return str(FAVICON_PATH)

def load_css(css_path: str) -> None:
    """
    Read a CSS file and inject it into the Streamlit page.
    The path is relative to the project root.
    """
    file_path = Path(css_path)
    if not file_path.exists():
        st.warning(f"CSS file not found. Please make sure {css_path} exists.")
        return

    with open(file_path, encoding="utf-8") as css_file:
        css = css_file.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _read_css_bundle(css_paths: tuple[str, ...]) -> str:
    parts = []
    for css_path in css_paths:
        file_path = Path(css_path)
        if file_path.exists():
            with open(file_path, encoding="utf-8") as f:
                parts.append(f.read())
    return "".join(parts)


def load_css_bundle(css_paths: Sequence[str]) -> None:
    """
    Load multiple CSS files and inject them as a single <style> block.

    A single st.markdown() call instead of N separate calls avoids creating
    N invisible stMarkdown elements in Streamlit's flex layout, which would
    accumulate gap spacing and push visible content down the page.
    """
    combined = _read_css_bundle(tuple(css_paths))
    if combined:
        st.markdown(f"<style>{combined}</style>", unsafe_allow_html=True)

def _image_data_uri(image_path: str, modified_at: float) -> str:
    path = Path(image_path)
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"

def get_brand_logo_src() -> str:
    """Return the brand logo as a base64 data URI (cached), or empty string if not found."""
    logo_mtime = BRAND_LOGO_PATH.stat().st_mtime if BRAND_LOGO_PATH.exists() else 0
    return _image_data_uri(str(BRAND_LOGO_PATH), logo_mtime)


def get_brand_logo_inverted_src() -> str:
    """Return the inverted brand logo as a base64 data URI (for light mode), or empty string."""
    inv_mtime = BRAND_LOGO_INVERTED_PATH.stat().st_mtime if BRAND_LOGO_INVERTED_PATH.exists() else 0
    return _image_data_uri(str(BRAND_LOGO_INVERTED_PATH), inv_mtime)
