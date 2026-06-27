"""Top navigation bar and account menu rendering."""

from __future__ import annotations

from typing import Dict, List, Optional

import streamlit as st

from ui.assets import BRAND_LOGO_INVERTED_PATH, BRAND_LOGO_PATH, BRAND_TEXT, _image_data_uri

NAV_LINKS = [
    {"label": "Medical Assistance", "href": "/"},
    {"label": "About", "href": "/About"},
    {"label": "Results", "href": "/Results"},
]

def _build_nav_links_html(nav_links: List[Dict[str, str]]) -> str:
    html_lines = []
    for link in nav_links:
        label = link["label"]
        href = link["href"]
        html_lines.append(f'        <a href="{href}" target="_self">{label}</a>')
    return "\n".join(html_lines) + "\n"

def _build_brand_html(brand_text: str) -> str:
    logo_mtime = BRAND_LOGO_PATH.stat().st_mtime if BRAND_LOGO_PATH.exists() else 0
    logo_src = _image_data_uri(str(BRAND_LOGO_PATH), logo_mtime)
    inv_mtime = BRAND_LOGO_INVERTED_PATH.stat().st_mtime if BRAND_LOGO_INVERTED_PATH.exists() else 0
    inv_src = _image_data_uri(str(BRAND_LOGO_INVERTED_PATH), inv_mtime)
    if logo_src:
        inv_img = (
            f'<img class="brand-logo brand-logo-light" src="{inv_src}" alt="{brand_text}" />'
            if inv_src else ""
        )
        return (
            f'<a class="brand brand-logo-link" href="/" target="_self" aria-label="{brand_text} home">'
            f'<img class="brand-logo brand-logo-dark" src="{logo_src}" alt="{brand_text}" />'
            f"{inv_img}"
            "</a>"
        )
    return f'<a class="brand" href="/" target="_self">{brand_text}</a>'


_THEME_ROW_HTML = """                <div class="user-menu-theme-row">
                    <span>Toggle Theme</span>
                    <div class="theme-toggle">
                        <input type="checkbox" id="theme-toggle" />
                        <label for="theme-toggle"></label>
                    </div>
                </div>"""

def _build_user_menu_html(current_user: Optional[dict], is_guest: bool, current_page: str = "main") -> str:
    """Right side of navbar: user dropdown when authenticated, plain toggle otherwise."""
    if not current_user and not is_guest:
        return (
            '        <div class="theme-toggle">\n'
            '            <input type="checkbox" id="theme-toggle" />\n'
            '            <label for="theme-toggle"></label>\n'
            '        </div>'
        )

    rt = current_page
    legal_links = (
        f'                <a href="/?legal=privacy&return_to={rt}" class="user-menu-action" target="_self">Privacy Policy</a>\n'
        f'                <a href="/?legal=terms&return_to={rt}" class="user-menu-action" target="_self">Terms of Service</a>'
    )

    if is_guest:
        display_name = "Guest"
        top_links = ""
        exit_link = '<a href="?exit_guest=1" class="user-menu-action user-menu-danger" target="_self">Exit Guest</a>'
    else:
        first = (current_user or {}).get("first_name", "")
        last = (current_user or {}).get("last_name", "")
        display_name = f"{first} {last}".strip() or "Account"
        top_links = (
            '                <a href="/Account" class="user-menu-action" target="_self">Account Details</a>\n'
            f'                <a href="/?account=change_password&return_to={rt}" class="user-menu-action" target="_self">Change Password</a>\n'
        )
        exit_link = '<a href="?logout=1" class="user-menu-action user-menu-danger" target="_self">Logout</a>'

    delete_link = (
        f'                <a href="/?account=delete_account&return_to={rt}" class="user-menu-action user-menu-danger" target="_self">Delete Account</a>\n'
        if not is_guest else ""
    )

    return f"""        <details class="user-menu">
            <summary class="user-menu-trigger">{display_name}</summary>
            <div class="user-menu-dropdown">
{top_links}{_THEME_ROW_HTML}
{legal_links}
{delete_link}                {exit_link}
            </div>
        </details>"""


def handle_auth_query_params() -> None:
    """
    Handle ?logout=1 and ?exit_guest=1 links produced by the navbar dropdown.
    Call this at the top of every page that shows the authenticated navbar.
    """
    if st.query_params.get("logout") == "1":
        from backend.auth import logout_user  # local import to avoid circular deps
        logout_user()
        st.query_params.clear()
        st.switch_page("app.py")
    if st.query_params.get("exit_guest") == "1":
        from backend.auth import end_guest_session  # local import - avoids circular dep
        end_guest_session()
        st.query_params.clear()
        st.switch_page("app.py")


def render_navbar(
    brand_text: str = BRAND_TEXT,
    nav_links: Optional[List[Dict[str, str]]] = None,
    current_user: Optional[dict] = None,
    is_guest: bool = False,
    current_page: str = "main",
) -> None:
    """Render the shared navbar. Pass current_user / is_guest to show user menu."""
    if nav_links is None:
        nav_links = NAV_LINKS

    nav_links_html = _build_nav_links_html(nav_links)
    user_menu_html = _build_user_menu_html(current_user, is_guest, current_page)
    brand_html = _build_brand_html(brand_text)

    # Keep the flex layout stable even while Streamlit replaces markdown/style nodes.
    # The navbar is sticky in normal document flow, so no top padding offset is needed.
    navbar_html = f"""
<style>
#MainMenu,header[data-testid="stHeader"],header[data-testid="stAppHeader"],div[data-testid="stHeader"],div[data-testid="stAppHeader"],div[data-testid="stToolbar"],div[data-testid="stDecoration"],div[data-testid="stHeaderActionElements"]{{display:none!important;height:0!important;min-height:0!important;max-height:0!important;margin:0!important;padding:0!important;border:0!important;top:0!important;}}
div[data-testid="stMainBlockContainer"],div.stMainBlockContainer,.block-container{{padding-top:0!important;display:flex!important;flex-direction:column!important;min-height:100vh!important;box-sizing:border-box!important;}}
html body div[data-testid="stMainBlockContainer"]>div[data-testid="stVerticalBlock"]{{flex:1 0 auto!important;display:flex!important;flex-direction:column!important;}}
div[data-testid="stElementContainer"]:has(.footer-centered){{margin-top:auto!important;padding-bottom:2.5rem!important;}}
html,body,.stApp,div[data-testid="stApp"],div[data-testid="stAppViewContainer"],div[data-testid="stAppViewContainer"]>.main,section.main,section[data-testid="stMain"]{{max-width:100vw!important;overflow-x:hidden!important;}}
div[data-testid="stElementContainer"]:has(.navbar){{position:sticky!important;top:0!important;z-index:999!important;width:100vw!important;max-width:100vw!important;margin-left:calc(50% - 50vw)!important;margin-right:calc(50% - 50vw)!important;background:var(--navbar-bg)!important;background-color:var(--navbar-bg)!important;opacity:1!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;}}
.navbar{{background:var(--navbar-bg)!important;background-color:var(--navbar-bg)!important;opacity:1!important;}}
</style>
<nav class="navbar">
    <div class="navbar-left">
        {brand_html}
    </div>
    <input type="checkbox" id="nav-toggle" class="nav-toggle" />
    <label for="nav-toggle" class="nav-toggle-label"><span></span></label>
    <div class="navbar-right">
{nav_links_html}{user_menu_html}
    </div>
</nav>
"""
    st.markdown(navbar_html, unsafe_allow_html=True)
