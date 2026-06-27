"""Compatibility imports for shared UI helpers."""

from __future__ import annotations

from ui.assets import (
    BRAND_LOGO_INVERTED_PATH,
    BRAND_LOGO_PATH,
    BRAND_TEXT,
    FAVICON_PATH,
    format_semantic_score,
    get_brand_logo_inverted_src,
    get_brand_logo_src,
    load_css,
    load_css_bundle,
    load_favicon,
)
from ui.navbar import handle_auth_query_params, render_navbar
from ui.theme import inject_selectbox_lock_script, inject_theme_toggle_script

__all__ = [
    "BRAND_LOGO_INVERTED_PATH",
    "BRAND_LOGO_PATH",
    "BRAND_TEXT",
    "FAVICON_PATH",
    "format_semantic_score",
    "get_brand_logo_inverted_src",
    "get_brand_logo_src",
    "handle_auth_query_params",
    "inject_selectbox_lock_script",
    "inject_theme_toggle_script",
    "load_css",
    "load_css_bundle",
    "load_favicon",
    "render_navbar",
]
