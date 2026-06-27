"""Shared SVG snippets used by the Streamlit UI."""

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

_SCORE_CLS = {
    "urgent":       "score-urgent",
    "consult_gp":   "score-gp",
    "self_monitor": "score-self",
}

_RESULT_CARD = {
    "error": {
        "icon": _SVG_BOLT,
        "cls": "result-card-urgent",
        "body": "Your symptoms may indicate a serious condition. Please seek immediate medical assistance or call emergency services.",
    },
    "success": {
        "icon": _SVG_CHECK,
        "cls": "result-card-gp",
        "body": "Your symptoms suggest a non-emergency condition, but a medical evaluation is recommended.",
    },
    "warning": {
        "icon": _SVG_SHIELD,
        "cls": "result-card-self",
        "body": "Your symptoms appear mild. Rest, stay hydrated, and monitor any changes.",
    },
}
