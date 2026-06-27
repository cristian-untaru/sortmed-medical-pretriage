"""Browser-side theme and favicon injection helpers."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from ui.assets import FAVICON_PATH

THEME_TOGGLE_SCRIPT = """
<script>
(function () {
    // Keep the sticky footer flex layout stable across Streamlit rerenders.
    // The navbar now lives in the normal page flow, so no artificial top offset is needed.
    const doc = window.parent.document;

    function collapseUtilityRows() {
        if (!doc.body) {
            return;
        }

        const rows = doc.querySelectorAll(
            'div[data-testid="stElementContainer"],div.stElementContainer'
        );

        rows.forEach(function (row) {
            if (!row || row.dataset.sortmedUtilityCollapsed === '1') {
                return;
            }

            if (row.querySelector('.navbar,.lp-page,.footer-centered')) {
                return;
            }

            const frames = Array.from(row.querySelectorAll('iframe'));
            const frameIsZeroSized = function (frame) {
                const attrHeight = (frame.getAttribute('height') || '').trim();
                const attrWidth = (frame.getAttribute('width') || '').trim();
                const styleHeight = frame.style ? frame.style.height : '';
                const styleWidth = frame.style ? frame.style.width : '';
                const rect = frame.getBoundingClientRect
                    ? frame.getBoundingClientRect()
                    : { height: 0, width: 0 };

                return (
                    attrHeight === '0'
                    || attrWidth === '0'
                    || styleHeight === '0px'
                    || styleWidth === '0px'
                    || (rect.height <= 1 && rect.width <= 1)
                );
            };

            const onlyZeroSizedFrames = frames.length > 0 && frames.every(frameIsZeroSized);

            const clone = row.cloneNode(true);
            clone.querySelectorAll('style,script,iframe').forEach(function (node) {
                node.remove();
            });

            const remainingText = (clone.textContent || '').trim();
            const visibleSelectors = [
                'img',
                'svg',
                'canvas',
                'button',
                'input',
                'textarea',
                'select',
                'a',
                'nav',
                '[role="button"]',
                '[data-baseweb]',
            ].join(',');
            const hasVisibleContent = Boolean(clone.querySelector(visibleSelectors));
            const styleOnly = Boolean(row.querySelector('style')) && !remainingText && !hasVisibleContent;

            if (!styleOnly && !onlyZeroSizedFrames) {
                return;
            }

            row.dataset.sortmedUtilityCollapsed = '1';
            row.style.setProperty('position', 'absolute', 'important');
            row.style.setProperty('width', '0', 'important');
            row.style.setProperty('height', '0', 'important');
            row.style.setProperty('min-height', '0', 'important');
            row.style.setProperty('max-height', '0', 'important');
            row.style.setProperty('flex', '0 0 0', 'important');
            row.style.setProperty('margin', '0', 'important');
            row.style.setProperty('padding', '0', 'important');
            row.style.setProperty('overflow', 'hidden', 'important');

            frames.forEach(function (frame) {
                frame.style.setProperty('position', 'absolute', 'important');
                frame.style.setProperty('width', '0', 'important');
                frame.style.setProperty('height', '0', 'important');
                frame.style.setProperty('border', '0', 'important');
            });
        });
    }

    collapseUtilityRows();
    [50, 250, 1000].forEach(function (delay) {
        setTimeout(collapseUtilityRows, delay);
    });

    if (doc.body && !doc.body.dataset.sortmedUtilityRowObserver) {
        doc.body.dataset.sortmedUtilityRowObserver = '1';
        new MutationObserver(collapseUtilityRows).observe(doc.body, {
            childList: true,
            subtree: true,
        });
    }

    // Scrollbar: Chrome 121+ ignores ::-webkit-scrollbar-* when scrollbar-color/
    // scrollbar-width (standard CSS) are set on the same element. Streamlit sets
    // scrollbar-width internally, which silently disables our webkit rules.
    // Fix: use the standard properties - they take priority in Chrome 121+.
    if (!doc.getElementById('sortmed-scrollbar-fix')) {
        const sb = doc.createElement('style');
        sb.id = 'sortmed-scrollbar-fix';
        sb.textContent = (
            'html,body,section[data-testid="stMain"]{'
            + 'scrollbar-width:auto!important;'
            + 'scrollbar-color:rgba(255,255,255,0.32) #191923!important;}'
            + '::-webkit-scrollbar{width:10px!important;}'
            + '::-webkit-scrollbar-track{background:#191923!important;}'
            + '::-webkit-scrollbar-thumb{'
            + 'background:rgba(255,255,255,0.32)!important;'
            + 'border-radius:5px!important;}'
            + '::-webkit-scrollbar-thumb:hover{'
            + 'background:rgba(255,255,255,0.50)!important;}'
        );
        (doc.head || doc.documentElement).appendChild(sb);
    }

    if (!doc.getElementById('sortmed-layout-fix')) {
        const s = doc.createElement('style');
        s.id = 'sortmed-layout-fix';
        s.textContent = (
            '#MainMenu,'
            + 'header[data-testid="stHeader"],'
            + 'header[data-testid="stAppHeader"],'
            + 'div[data-testid="stHeader"],'
            + 'div[data-testid="stAppHeader"],'
            + 'div[data-testid="stToolbar"],'
            + 'div[data-testid="stDecoration"],'
            + 'div[data-testid="stHeaderActionElements"]{'
            + 'display:none!important;height:0!important;min-height:0!important;'
            + 'max-height:0!important;margin:0!important;padding:0!important;border:0!important;}'
            + 'div[data-testid="stMainBlockContainer"],'
            + 'div.stMainBlockContainer,'
            + 'div.block-container{'
            + 'padding-top:0!important;'
            + 'display:flex!important;'
            + 'flex-direction:column!important;'
            + 'min-height:100vh!important;'
            + 'box-sizing:border-box!important;}'
            + 'html body div[data-testid="stMainBlockContainer"]>div[data-testid="stVerticalBlock"]{'
            + 'flex:1 0 auto!important;'
            + 'display:flex!important;'
            + 'flex-direction:column!important;}'
            + 'div[data-testid="stElementContainer"]:has(.footer-centered){'
            + 'margin-top:auto!important;'
            + 'padding-bottom:2.5rem!important;}'
            + 'html,body,.stApp,div[data-testid="stApp"],div[data-testid="stAppViewContainer"],div[data-testid="stAppViewContainer"]>.main,section.main,section[data-testid="stMain"]{'
            + 'max-width:100vw!important;'
            + 'overflow-x:hidden!important;}'
        );
        (doc.head || doc.documentElement).appendChild(s);
    }

    if (!doc.getElementById('sortmed-light-mode-overrides')) {
        const lm = doc.createElement('style');
        lm.id = 'sortmed-light-mode-overrides';
        lm.textContent = (
            ':root[data-theme="light"] li[role="option"]:hover,'
            + ':root[data-theme="light"] [data-baseweb="option"]:hover{'
            + 'background-color:rgba(0,0,0,0.05)!important;color:#1f2328!important;}'
            + ':root[data-theme="light"] li[role="option"][aria-selected="true"],'
            + ':root[data-theme="light"] [data-baseweb="option"][aria-selected="true"]{'
            + 'background-color:rgba(37,99,235,0.1)!important;color:#111827!important;}'
            + ':root[data-theme="light"] div[data-baseweb="notification"]{'
            + 'background-color:#ffffff!important;color:#1f2328!important;border-color:#d1d5db!important;}'
            + ':root[data-theme="light"] div[data-baseweb="notification"] *{'
            + 'color:#1f2328!important;}'
            + ':root[data-theme="light"] details[data-testid="stExpander"] summary,'
            + ':root[data-theme="light"] details[data-testid="stExpander"][open] summary{'
            + 'background:transparent!important;color:#111827!important;}'
            + ':root[data-theme="light"] details[data-testid="stExpander"] summary *,'
            + ':root[data-theme="light"] details[data-testid="stExpander"][open] summary *{'
            + 'background:transparent!important;color:#111827!important;}'
            + ':root[data-theme="light"] [data-testid="stExpander"],'
            + ':root[data-theme="light"] details[data-testid="stExpander"]{'
            + 'border:1px solid #ded8cf!important;border-radius:8px!important;'
            + 'background:#fbf8f2!important;color:#111827!important;overflow:hidden!important;}'
            + ':root[data-theme="light"] [data-testid="stExpander"] summary,'
            + ':root[data-theme="light"] details[data-testid="stExpander"] summary,'
            + ':root[data-theme="light"] [data-testid="stExpander"][open] summary,'
            + ':root[data-theme="light"] details[data-testid="stExpander"][open] summary,'
            + ':root[data-theme="light"] [data-testid="stExpander"] summary:focus,'
            + ':root[data-theme="light"] details[data-testid="stExpander"] summary:focus,'
            + ':root[data-theme="light"] [data-testid="stExpander"] summary:focus-visible,'
            + ':root[data-theme="light"] details[data-testid="stExpander"] summary:focus-visible{'
            + 'background:#fbf8f2!important;color:#111827!important;border-radius:8px!important;}'
            + ':root[data-theme="light"] [data-testid="stExpander"] summary *,'
            + ':root[data-theme="light"] details[data-testid="stExpander"] summary *,'
            + ':root[data-theme="light"] [data-testid="stExpander"][open] summary *,'
            + ':root[data-theme="light"] details[data-testid="stExpander"][open] summary *{'
            + 'background:transparent!important;color:#111827!important;}'
            + ':root[data-theme="light"] [data-testid="stExpander"] summary:hover,'
            + ':root[data-theme="light"] details[data-testid="stExpander"] summary:hover{'
            + 'background:#f0ece4!important;color:#111827!important;}'
            + ':root[data-theme="light"] [data-testid="stExpander"] summary:hover *,'
            + ':root[data-theme="light"] details[data-testid="stExpander"] summary:hover *{'
            + 'background:transparent!important;color:#111827!important;}'
            + ':root[data-theme="light"] [data-testid="stExpander"] summary svg,'
            + ':root[data-theme="light"] details[data-testid="stExpander"] summary svg,'
            + ':root[data-theme="light"] [data-testid="stExpander"][open] summary svg,'
            + ':root[data-theme="light"] details[data-testid="stExpander"][open] summary svg,'
            + ':root[data-theme="light"] [data-testid="stExpander"] summary svg path,'
            + ':root[data-theme="light"] details[data-testid="stExpander"] summary svg path,'
            + ':root[data-theme="light"] [data-testid="stExpander"][open] summary svg path,'
            + ':root[data-theme="light"] details[data-testid="stExpander"][open] summary svg path{'
            + 'color:#111827!important;fill:#111827!important;stroke:#111827!important;}'
            + ':root[data-theme="light"] div[data-baseweb="select"]>div{'
            + 'background-color:#fbf8f2!important;border-color:#ded8cf!important;color:#1f2328!important;}'
            + ':root[data-theme="light"] div[data-baseweb="select"] *{color:#1f2328!important;}'
            + ':root[data-theme="light"] div[data-baseweb="popover"],'
            + ':root[data-theme="light"] div[data-baseweb="popover"]>div,'
            + ':root[data-theme="light"] ul[role="listbox"],'
            + ':root[data-theme="light"] [role="listbox"]{'
            + 'background-color:#fbf8f2!important;border-color:#ded8cf!important;color:#1f2328!important;}'
            + ':root[data-theme="light"] li[role="option"],'
            + ':root[data-theme="light"] [role="option"],'
            + ':root[data-theme="light"] [data-baseweb="option"]{'
            + 'background-color:#fbf8f2!important;color:#1f2328!important;}'
            + ':root[data-theme="light"] li[role="option"] *,'
            + ':root[data-theme="light"] [role="option"] *,'
            + ':root[data-theme="light"] [data-baseweb="option"] *{'
            + 'background-color:transparent!important;color:#1f2328!important;}'
            + ':root[data-theme="light"] li[role="option"]:hover,'
            + ':root[data-theme="light"] [role="option"]:hover,'
            + ':root[data-theme="light"] [data-baseweb="option"]:hover,'
            + ':root[data-theme="light"] li[role="option"][aria-selected="true"],'
            + ':root[data-theme="light"] [role="option"][aria-selected="true"],'
            + ':root[data-theme="light"] [data-baseweb="option"][aria-selected="true"]{'
            + 'background-color:#f0ece4!important;color:#111827!important;}'
            + ':root[data-theme="light"] li[role="option"]:hover *,'
            + ':root[data-theme="light"] [role="option"]:hover *,'
            + ':root[data-theme="light"] [data-baseweb="option"]:hover *,'
            + ':root[data-theme="light"] li[role="option"][aria-selected="true"] *,'
            + ':root[data-theme="light"] [role="option"][aria-selected="true"] *,'
            + ':root[data-theme="light"] [data-baseweb="option"][aria-selected="true"] *{'
            + 'background-color:transparent!important;color:#111827!important;}'
            + ':root[data-theme="light"] div[data-baseweb="notification"],'
            + ':root[data-theme="light"] div[data-baseweb="toast"],'
            + ':root[data-theme="light"] [data-testid="stNotification"],'
            + ':root[data-theme="light"] [data-testid="stNotificationContent"],'
            + ':root[data-theme="light"] [data-testid="stStatusContainer"],'
            + ':root[data-theme="light"] [data-testid="stStatusWidget"]{'
            + 'background-color:#fbf8f2!important;border-color:#ded8cf!important;color:#1f2328!important;}'
            + ':root[data-theme="light"] div[data-baseweb="notification"] *,'
            + ':root[data-theme="light"] div[data-baseweb="toast"] *,'
            + ':root[data-theme="light"] [data-testid="stNotification"] *,'
            + ':root[data-theme="light"] [data-testid="stNotificationContent"] *,'
            + ':root[data-theme="light"] [data-testid="stStatusContainer"] *,'
            + ':root[data-theme="light"] [data-testid="stStatusWidget"] *,'
            + ':root[data-theme="light"] [data-testid="stSpinner"],'
            + ':root[data-theme="light"] [data-testid="stSpinner"] *{'
            + 'background-color:transparent!important;color:#1f2328!important;}'
            + ':root[data-theme="light"] div[data-testid="stElementContainer"]:has([data-testid="stSpinner"]),'
            + ':root[data-theme="light"] div[data-testid="stElementContainer"]:has([data-testid="stSpinner"])>div,'
            + ':root[data-theme="light"] div[data-testid="stElementContainer"]:has([data-testid="stSpinner"]) [data-testid="stMarkdownContainer"],'
            + ':root[data-theme="light"] div[data-testid="stElementContainer"]:has([data-testid="stSpinner"]) [data-testid="stMarkdownContainer"] *,'
            + ':root[data-theme="light"] [data-testid="stSpinner"],'
            + ':root[data-theme="light"] [data-testid="stSpinner"]>div,'
            + ':root[data-theme="light"] [data-testid="stSpinner"] [role="status"],'
            + ':root[data-theme="light"] [data-testid="stSpinner"] [data-testid="stMarkdownContainer"],'
            + ':root[data-theme="light"] [data-testid="stSpinner"] [data-testid="stMarkdownContainer"] *{'
            + 'background:transparent!important;background-color:transparent!important;color:#1f2328!important;}'
            + ':root[data-theme="light"] [data-testid="stSpinner"] svg,'
            + ':root[data-theme="light"] [data-testid="stSpinner"] svg *,'
            + ':root[data-theme="light"] [data-testid="stSpinner"] [role="status"] svg,'
            + ':root[data-theme="light"] [data-testid="stSpinner"] [role="status"] svg *{'
            + 'color:#0b5ed7!important;fill:none!important;stroke:#0b5ed7!important;}'
            + ':root[data-theme="light"] [data-testid="stSpinner"] [style*="border"],'
            + ':root[data-theme="light"] div[data-testid="stElementContainer"]:has([data-testid="stSpinner"]) [style*="border"]{'
            + 'border-color:rgba(11,94,215,0.22)!important;border-top-color:#0b5ed7!important;}'
            + ':root[data-theme="light"] .navbar{'
            + 'background:#ffffff!important;background-color:#ffffff!important;}'
            + ':root:not([data-theme="light"]) div[data-baseweb="select"]>div{'
            + 'background-color:#262730!important;border-color:#3a3d45!important;color:#e7e7ea!important;}'
            + ':root:not([data-theme="light"]) div[data-baseweb="select"] *{color:#e7e7ea!important;}'
            + ':root:not([data-theme="light"]) div[data-baseweb="popover"],'
            + ':root:not([data-theme="light"]) div[data-baseweb="popover"]>div,'
            + ':root:not([data-theme="light"]) ul[role="listbox"],'
            + ':root:not([data-theme="light"]) [role="listbox"]{'
            + 'background-color:#262730!important;border-color:#3a3d45!important;color:#e7e7ea!important;}'
            + ':root:not([data-theme="light"]) li[role="option"],'
            + ':root:not([data-theme="light"]) [role="option"],'
            + ':root:not([data-theme="light"]) [data-baseweb="option"]{'
            + 'background-color:#262730!important;color:#e7e7ea!important;}'
            + ':root:not([data-theme="light"]) li[role="option"] *,'
            + ':root:not([data-theme="light"]) [role="option"] *,'
            + ':root:not([data-theme="light"]) [data-baseweb="option"] *{'
            + 'background-color:transparent!important;color:#e7e7ea!important;}'
            + ':root:not([data-theme="light"]) li[role="option"]:hover,'
            + ':root:not([data-theme="light"]) [role="option"]:hover,'
            + ':root:not([data-theme="light"]) [data-baseweb="option"]:hover,'
            + ':root:not([data-theme="light"]) li[role="option"][aria-selected="true"],'
            + ':root:not([data-theme="light"]) [role="option"][aria-selected="true"],'
            + ':root:not([data-theme="light"]) [data-baseweb="option"][aria-selected="true"]{'
            + 'background-color:rgba(143,0,255,0.14)!important;color:#ffffff!important;}'
            + ':root:not([data-theme="light"]) li[role="option"]:hover *,'
            + ':root:not([data-theme="light"]) [role="option"]:hover *,'
            + ':root:not([data-theme="light"]) [data-baseweb="option"]:hover *,'
            + ':root:not([data-theme="light"]) li[role="option"][aria-selected="true"] *,'
            + ':root:not([data-theme="light"]) [role="option"][aria-selected="true"] *,'
            + ':root:not([data-theme="light"]) [data-baseweb="option"][aria-selected="true"] *{'
            + 'background-color:transparent!important;color:#ffffff!important;}'
            + ':root[data-theme="light"] [data-testid="stTooltipIcon"],'
            + ':root[data-theme="light"] [data-testid="stTooltipHoverTarget"]{'
            + 'color:#111827!important;background:transparent!important;border:0!important;}'
            + ':root[data-theme="light"] [data-testid="stTooltipHoverTarget"]{'
            + 'display:inline-flex!important;align-items:center!important;justify-content:center!important;'
            + 'width:18px!important;height:18px!important;}'
            + ':root[data-theme="light"] [data-testid="stTooltipHoverTarget"] [data-testid="stTooltipIcon"]{display:none!important;}'
            + ':root[data-theme="light"] [data-testid="stTooltipIcon"] svg,'
            + ':root[data-theme="light"] [data-testid="stTooltipHoverTarget"] svg{display:none!important;}'
            + ':root[data-theme="light"] [data-testid="stTooltipHoverTarget"]::before{'
            + 'content:"-";display:inline-flex;align-items:center;justify-content:center;'
            + 'width:16px;height:16px;border:2px solid #111827;border-radius:50%;'
            + 'color:#111827;background:transparent;font-size:11px;font-weight:800;'
            + 'line-height:1;box-sizing:border-box;}'
            + ':root[data-theme="light"] [data-baseweb="tooltip"],'
            + ':root[data-theme="light"] [data-baseweb="tooltip"]>div,'
            + ':root[data-theme="light"] div[role="tooltip"],'
            + ':root[data-theme="light"] [data-testid="stTooltipContent"]{'
            + 'background-color:#ffffff!important;color:#1f2328!important;'
            + 'border:1px solid rgba(0,0,0,0.13)!important;border-radius:6px!important;'
            + 'box-shadow:0 4px 14px rgba(0,0,0,0.13)!important;}'
            + ':root[data-theme="light"] [data-baseweb="tooltip"] *,'
            + ':root[data-theme="light"] div[role="tooltip"] *,'
            + ':root[data-theme="light"] [data-testid="stTooltipContent"] *{'
            + 'color:#1f2328!important;background-color:transparent!important;}'
            + ':root[data-theme="light"] [role="option"][data-testid="stTooltipHoverTarget"],'
            + ':root[data-theme="light"] [data-baseweb="option"][data-testid="stTooltipHoverTarget"],'
            + ':root[data-theme="light"] [role="option"] [data-testid="stTooltipHoverTarget"],'
            + ':root[data-theme="light"] [data-baseweb="option"] [data-testid="stTooltipHoverTarget"]{'
            + 'display:inline-flex!important;width:auto!important;height:auto!important;'
            + 'min-width:0!important;max-width:none!important;overflow:visible!important;'
            + 'color:#1f2328!important;}'
            + ':root[data-theme="light"] [role="option"][data-testid="stTooltipHoverTarget"]::before,'
            + ':root[data-theme="light"] [data-baseweb="option"][data-testid="stTooltipHoverTarget"]::before,'
            + ':root[data-theme="light"] [role="option"] [data-testid="stTooltipHoverTarget"]::before,'
            + ':root[data-theme="light"] [data-baseweb="option"] [data-testid="stTooltipHoverTarget"]::before{'
            + 'content:none!important;display:none!important;}'
            + ':root[data-theme="light"] [role="option"] *,'
            + ':root[data-theme="light"] [data-baseweb="option"] *{'
            + 'opacity:1!important;visibility:visible!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading):not(:has(.auth-form-heading-danger)) div[data-testid="stFormSubmitButton"] button[kind="primary"],'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading):not(:has(.auth-form-heading-danger)) div[data-testid="stButton"] button[kind="primary"]{'
            + 'background:linear-gradient(90deg,#4f46e5 0%,#7c3aed 100%)!important;'
            + 'border:none!important;color:#ffffff!important;'
            + 'box-shadow:0 6px 18px rgba(79,70,229,0.30)!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading):not(:has(.auth-form-heading-danger)) div[data-testid="stFormSubmitButton"] button[kind="primary"] p,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading):not(:has(.auth-form-heading-danger)) div[data-testid="stFormSubmitButton"] button[kind="primary"] span,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading):not(:has(.auth-form-heading-danger)) div[data-testid="stFormSubmitButton"] button[kind="primary"] div{'
            + 'color:#ffffff!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading):not(:has(.auth-form-heading-danger)) div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading):not(:has(.auth-form-heading-danger)) div[data-testid="stButton"] button[kind="primary"]:hover{'
            + 'box-shadow:0 8px 26px rgba(79,70,229,0.50)!important;'
            + 'transform:translateY(-1px)!important;filter:brightness(1.08)!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button[kind="secondary"],'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button[kind="secondary"]{'
            + 'background:#ffffff!important;background-color:#ffffff!important;'
            + 'border:1px solid rgba(0,0,0,0.22)!important;color:#1f2328!important;box-shadow:none!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button[kind="secondary"] p,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button[kind="secondary"] span,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button[kind="secondary"] div,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button[kind="secondary"] p,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button[kind="secondary"] span,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button[kind="secondary"] div{'
            + 'color:#1f2328!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button[kind="secondary"]:hover,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button[kind="secondary"]:hover{'
            + 'background:#f2f2f4!important;background-color:#f2f2f4!important;border-color:rgba(0,0,0,0.32)!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button:not([kind*="primary" i]),'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button:not([kind*="primary" i]){'
            + 'background:#ffffff!important;background-color:#ffffff!important;'
            + 'border:1px solid rgba(15,23,42,0.28)!important;color:#111827!important;'
            + 'box-shadow:0 2px 8px rgba(15,23,42,0.08)!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button:not([kind*="primary" i]) p,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button:not([kind*="primary" i]) span,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button:not([kind*="primary" i]) div,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button:not([kind*="primary" i]) p,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button:not([kind*="primary" i]) span,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button:not([kind*="primary" i]) div{'
            + 'color:#111827!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button:not([kind*="primary" i]):hover,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button:not([kind*="primary" i]):hover{'
            + 'background:#f8fafc!important;background-color:#f8fafc!important;'
            + 'border-color:rgba(15,23,42,0.42)!important;box-shadow:0 4px 14px rgba(15,23,42,0.12)!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button[kind*="primary" i],'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button[kind*="primary" i]{'
            + 'background:linear-gradient(90deg,#ff4b4b,#c13ca6)!important;border:none!important;'
            + 'color:#ffffff!important;box-shadow:0 10px 24px rgba(255,75,75,0.22)!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button[kind*="primary" i] p,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button[kind*="primary" i] span,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stFormSubmitButton"] button[kind*="primary" i] div,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button[kind*="primary" i] p,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button[kind*="primary" i] span,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-testid="stButton"] button[kind*="primary" i] div{'
            + 'color:#ffffff!important;}'
            + 'div[data-testid="stForm"]:has(.auth-change-password-confirm) div[data-testid="stFormSubmitButton"] button[kind="primary"]{'
            + 'background:linear-gradient(90deg,#dc2626,#b91c1c)!important;'
            + 'box-shadow:0 0 10px rgba(220,38,38,0.28)!important;border:none!important;}'
            + 'div[data-testid="stForm"]:has(.auth-change-password-confirm) div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover{'
            + 'background:linear-gradient(90deg,#ef4444,#dc2626)!important;'
            + 'box-shadow:0 0 18px rgba(220,38,38,0.45)!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading-danger) div[data-testid="stFormSubmitButton"] button[kind*="primary" i]{'
            + 'background:linear-gradient(90deg,#ef4444,#dc2626)!important;box-shadow:0 10px 24px rgba(220,38,38,0.22)!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading-danger) div[data-testid="stFormSubmitButton"] button[kind*="primary" i]:hover{'
            + 'background:linear-gradient(90deg,#f04444,#c81e1e)!important;'
            + 'box-shadow:0 10px 22px rgba(220,38,38,0.28)!important;'
            + 'filter:brightness(1.02)!important;transform:none!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-change-password-confirm) div[data-testid="stFormSubmitButton"] button[kind*="primary" i]{'
            + 'background:linear-gradient(90deg,#ef4444,#dc2626)!important;'
            + 'box-shadow:0 10px 24px rgba(220,38,38,0.22)!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-change-password-confirm) div[data-testid="stFormSubmitButton"] button[kind*="primary" i]:hover{'
            + 'background:linear-gradient(90deg,#f04444,#c81e1e)!important;'
            + 'box-shadow:0 10px 22px rgba(220,38,38,0.28)!important;'
            + 'filter:brightness(1.02)!important;transform:none!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading):not(:has(.auth-form-heading-danger)) div[data-testid="stFormSubmitButton"] button[kind*="primary" i]:hover,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading):not(:has(.auth-form-heading-danger)) div[data-testid="stButton"] button[kind*="primary" i]:hover{'
            + 'box-shadow:0 10px 22px rgba(255,75,75,0.28)!important;'
            + 'filter:brightness(1.02)!important;transform:none!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-baseweb="input"]:has(button) button,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-baseweb="input"]:has(button) button *{'
            + 'color:#111827!important;opacity:1!important;}'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-baseweb="input"]:has(button) button svg,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-baseweb="input"]:has(button) button svg *,'
            + ':root[data-theme="light"] div[data-testid="stForm"]:has(.auth-form-heading) div[data-baseweb="input"]:has(button) button path{'
            + 'color:#111827!important;fill:#111827!important;stroke:#111827!important;opacity:1!important;}'
        );
        (doc.body || doc.documentElement).appendChild(lm);
    }

    const root = doc.documentElement;
    function initToggle() {
        const toggle = doc.getElementById('theme-toggle');
        if (!toggle) {
            setTimeout(initToggle, 100);
            return;
        }
        if (toggle.dataset.bound === '1') return;
        toggle.dataset.bound = '1';

        const saved = window.parent.localStorage.getItem('theme') || 'dark';
        root.setAttribute('data-theme', saved);
        toggle.checked = saved === 'light';

        toggle.addEventListener('change', () => {
            const next = toggle.checked ? 'light' : 'dark';
            root.setAttribute('data-theme', next);
            window.parent.localStorage.setItem('theme', next);
        });

        // Close user-menu dropdown when clicking outside of it
        if (!doc.body.dataset.menuClickOutside) {
            doc.body.dataset.menuClickOutside = '1';
            doc.addEventListener('click', function (e) {
                doc.querySelectorAll('details.user-menu[open]').forEach(function (menu) {
                    if (!menu.contains(e.target)) {
                        menu.removeAttribute('open');
                    }
                });
            }, true);
        }

        // Light mode: fix BaseWeb dark hover on selectbox options
        if (!doc.body.dataset.lightDropdownHoverFix) {
            doc.body.dataset.lightDropdownHoverFix = '1';
            var pWin = window.parent;
            function isLM() { return doc.documentElement.getAttribute('data-theme') === 'light'; }
            function optionIsSelected(el) {
                return el && (
                    el.getAttribute('aria-selected') === 'true' ||
                    el.getAttribute('aria-current') === 'true'
                );
            }
            function forceLight(el, active) {
                el.style.setProperty('background-color', active ? '#f0ece4' : '#fbf8f2', 'important');
                el.style.setProperty('color', active ? '#111827' : '#1f2328', 'important');
                el.querySelectorAll('*').forEach(function(child) {
                    child.style.setProperty('background-color', 'transparent', 'important');
                    child.style.setProperty('color', active ? '#111827' : '#1f2328', 'important');
                });
            }
            function unforce(el) {
                if (optionIsSelected(el)) {
                    forceLight(el, true);
                    return;
                }
                el.style.removeProperty('background-color');
                el.style.removeProperty('color');
                el.querySelectorAll('*').forEach(function(child) {
                    child.style.removeProperty('background-color');
                    child.style.removeProperty('color');
                });
            }
            function getOpt(target) {
                return target.closest && (
                    target.closest('[data-baseweb="option"]') ||
                    target.closest('[role="option"]')
                );
            }
            function forceDark(el, active) {
                el.style.setProperty('background-color', active ? 'rgba(143,0,255,0.18)' : '#262730', 'important');
                el.style.setProperty('color', active ? '#ffffff' : '#e7e7ea', 'important');
                el.querySelectorAll('*').forEach(function(child) {
                    child.style.setProperty('background-color', 'transparent', 'important');
                    child.style.setProperty('color', active ? '#ffffff' : '#e7e7ea', 'important');
                });
            }
            function undark(el) {
                if (optionIsSelected(el)) { forceDark(el, true); return; }
                el.style.removeProperty('background-color');
                el.style.removeProperty('color');
                el.querySelectorAll('*').forEach(function(child) {
                    child.style.removeProperty('background-color');
                    child.style.removeProperty('color');
                });
            }
            // Watch inline style + class changes on individual option elements (handles both modes)
            var optObs = new MutationObserver(function(muts) {
                muts.forEach(function(m) {
                    var el = m.target;
                    if (isLM()) {
                        if (m.attributeName === 'style') {
                            forceLight(el, optionIsSelected(el));
                        } else {
                            try {
                                var cbg = pWin.getComputedStyle(el).backgroundColor;
                                var dark = cbg && cbg !== 'rgba(0, 0, 0, 0)' && cbg !== 'transparent' &&
                                           !cbg.startsWith('rgb(255') && cbg !== 'rgb(251, 248, 242)' &&
                                           cbg !== 'rgb(240, 236, 228)';
                                if (dark || optionIsSelected(el)) { forceLight(el, optionIsSelected(el)); }
                                else { unforce(el); }
                            } catch(ex) {}
                        }
                    } else {
                        // Dark mode: override any light inline style BaseWeb may inject
                        if (m.attributeName === 'style') { forceDark(el, optionIsSelected(el)); }
                    }
                });
            });
            // Watch body for new dropdown portals, apply dark/light styles and attach optObs
            var domObs = new MutationObserver(function(muts) {
                muts.forEach(function(m) {
                    m.addedNodes.forEach(function(node) {
                        if (node.nodeType !== 1) return;
                        // Dark mode: force dark background on popover container + listbox
                        if (!isLM()) {
                            var pops = (node.matches && node.matches('[data-baseweb="popover"]')) ? [node] : [];
                            node.querySelectorAll && node.querySelectorAll('[data-baseweb="popover"]').forEach(function(p) { pops.push(p); });
                            pops.forEach(function(pop) {
                                pop.style.setProperty('background-color', '#262730', 'important');
                                pop.style.setProperty('border-color', '#3a3d45', 'important');
                                pop.querySelectorAll('ul[role="listbox"],[role="listbox"]').forEach(function(lb) {
                                    lb.style.setProperty('background-color', '#262730', 'important');
                                    lb.style.setProperty('color', '#e7e7ea', 'important');
                                });
                            });
                        }
                        node.querySelectorAll('[role="option"],[data-baseweb="option"]').forEach(function(o) {
                            if (isLM()) forceLight(o, optionIsSelected(o));
                            else forceDark(o, optionIsSelected(o));
                            optObs.observe(o, {attributes: true, attributeFilter: ['style','class']});
                        });
                        if (node.matches && (node.matches('[role="option"]') || node.matches('[data-baseweb="option"]'))) {
                            if (isLM()) forceLight(node, optionIsSelected(node));
                            else forceDark(node, optionIsSelected(node));
                            optObs.observe(node, {attributes: true, attributeFilter: ['style','class']});
                        }
                    });
                });
            });
            domObs.observe(doc.body, {childList: true, subtree: true});
            // Event delegation: apply immediately + deferred (covers React batched updates)
            var hovOpt = null;
            doc.addEventListener('mouseover', function(e) {
                var opt = getOpt(e.target);
                if (!opt) return;
                hovOpt = opt;
                if (isLM()) { forceLight(opt, true); setTimeout(function() { if (hovOpt === opt) forceLight(opt, true); }, 0); }
                else { forceDark(opt, true); setTimeout(function() { if (hovOpt === opt) forceDark(opt, true); }, 0); }
            }, false);
            doc.addEventListener('mouseout', function(e) {
                var opt = getOpt(e.target);
                if (!opt || (e.relatedTarget && opt.contains(e.relatedTarget))) return;
                if (hovOpt === opt) hovOpt = null;
                if (isLM()) { unforce(opt); setTimeout(function() { if (hovOpt !== opt) unforce(opt); }, 0); }
                else { undark(opt); setTimeout(function() { if (hovOpt !== opt) undark(opt); }, 0); }
            }, false);
        }

        // Light mode: fix transient Streamlit cache/spinner loading blocks.
        if (!doc.body.dataset.loadingMessageLightFix) {
            doc.body.dataset.loadingMessageLightFix = '1';
            var loadingTexts = [
                'Loading AI model from Hugging Face',
                'Loading medical knowledge base',
                'Building MedQuAD retrieval index'
            ];
            function isLoadingMessage(el) {
                if (!el || !el.textContent) return false;
                // Limit to short text nodes - prevents matching large parent containers
                // whose descendants happen to include loading text
                var t = el.textContent.trim();
                if (t.length > 300) return false;
                return loadingTexts.some(function(text) {
                    return t.indexOf(text) !== -1;
                });
            }
            function forceLoadingLight(rootEl) {
                if (!isLM() || !rootEl) return;
                // Never touch the navbar or its container
                if (rootEl.closest && rootEl.closest('.navbar')) return;
                var block = rootEl.closest && (
                    rootEl.closest('[data-testid="stSpinner"]') ||
                    rootEl.closest('[data-baseweb="notification"]') ||
                    rootEl.closest('[data-baseweb="toast"]') ||
                    rootEl.closest('[data-testid="stStatusWidget"]') ||
                    rootEl.closest('[data-testid="stStatusContainer"]')
                    // Note: stElementContainer fallback removed - it was too broad and
                    // caused navbar background to become transparent via inline !important
                );
                if (!block) return;
                // Skip if the matched block somehow contains the navbar
                if (block.querySelector && block.querySelector('.navbar')) return;
                [block].concat(Array.from(block.querySelectorAll('*'))).forEach(function(el) {
                    if (el.classList && el.classList.contains('navbar')) return;
                    el.style.setProperty('background', 'transparent', 'important');
                    el.style.setProperty('background-color', 'transparent', 'important');
                    el.style.setProperty('color', '#1f2328', 'important');
                });
                block.querySelectorAll('svg, svg *').forEach(function(el) {
                    el.style.setProperty('color', '#0b5ed7', 'important');
                    el.style.setProperty('stroke', '#0b5ed7', 'important');
                    el.style.setProperty('fill', 'none', 'important');
                });
                block.querySelectorAll('[style*="border"]').forEach(function(el) {
                    el.style.setProperty('border-color', 'rgba(11,94,215,0.22)', 'important');
                    el.style.setProperty('border-top-color', '#0b5ed7', 'important');
                });
            }
            function scanLoadingMessages() {
                if (!isLM()) return;
                doc.querySelectorAll('div,span,p,[data-testid="stSpinner"],[data-baseweb="notification"],[data-baseweb="toast"]').forEach(function(el) {
                    if (isLoadingMessage(el)) forceLoadingLight(el);
                });
            }
            var loadingObs = new MutationObserver(function() {
                scanLoadingMessages();
            });
            loadingObs.observe(doc.body, {childList: true, subtree: true, characterData: true});
            scanLoadingMessages();
        }
    }
    initToggle();
})();
</script>
"""

def _favicon_b64(modified_at: float) -> str:
    """Crop PNG to content bbox, resize to 128×128 with uniform padding, return base64.
    modified_at is the file mtime - changing it busts the cache when the file is replaced."""
    png_path = Path("assets/media/sortmed-favicon.png")
    if not png_path.exists():
        return ""
    try:
        import io
        import numpy as np
        from PIL import Image
        img = Image.open(png_path).convert("RGBA")
        # PIL getbbox() counts alpha=1 pixels as non-zero and returns the full canvas.
        # Use numpy with threshold >10 to find the real content boundary.
        alpha = np.array(img)[:, :, 3]
        rows = np.any(alpha > 10, axis=1)
        cols = np.any(alpha > 10, axis=0)
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        img = img.crop((cmin, rmin, cmax + 1, rmax + 1))
        size = 128
        pad_x, pad_top, pad_bot = 3, 6, 0
        img = img.resize((size - 2 * pad_x, size - pad_top - pad_bot), Image.LANCZOS)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        canvas.paste(img, (pad_x, pad_top))
        buf = io.BytesIO()
        canvas.save(buf, format="PNG", optimize=True)
        return base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        return base64.b64encode(png_path.read_bytes()).decode("ascii")


def _build_favicon_html() -> str:
    png_path = Path("assets/media/sortmed-favicon.png")
    mtime = png_path.stat().st_mtime if png_path.exists() else 0.0
    png_b64 = _favicon_b64(mtime)
    if not png_b64:
        return ""
    return f"""<script>
(function () {{
    var HREF = 'data:image/png;base64,{png_b64}';
    function applyFavicon(doc) {{
        if (doc.getElementById('sortmed-favicon')) return;
        doc.querySelectorAll('link[rel*="icon"]').forEach(function (el) {{ el.remove(); }});
        var lnk = doc.createElement('link');
        lnk.id = 'sortmed-favicon'; lnk.rel = 'icon'; lnk.type = 'image/png'; lnk.sizes = '128x128'; lnk.href = HREF;
        (doc.head || doc.documentElement).appendChild(lnk);
    }}
    var doc = window.parent.document;
    applyFavicon(doc);
    if (!doc.body.dataset.sortmedFaviconObserver) {{
        doc.body.dataset.sortmedFaviconObserver = '1';
        new MutationObserver(function () {{
            if (!doc.getElementById('sortmed-favicon')) {{ applyFavicon(doc); }}
        }}).observe(doc.head || doc.documentElement, {{ childList: true, subtree: true }});
    }}
}})();
</script>"""


def inject_theme_toggle_script() -> None:
    """Inject theme toggle + PNG favicon in a single components.html() call.
    One iframe - no extra visible container anywhere on the page."""
    components.html(_build_favicon_html() + "\n" + THEME_TOGGLE_SCRIPT, height=0, width=0)


_SELECTBOX_LOCK_SCRIPT = """
<script>
(function () {
    var PASS = { ArrowDown: 1, ArrowUp: 1, Enter: 1, Escape: 1, Tab: 1 };
    function lock(el) {
        if (el._sbLocked) return;
        el._sbLocked = true;
        el.addEventListener('keydown', function (e) {
            if (!PASS[e.key]) {
                e.preventDefault();
                e.stopImmediatePropagation();
            }
        }, true);
        el.style.caretColor = 'transparent';
        el.style.cursor = 'pointer';
    }
    function lockAll() {
        var doc = window.parent ? window.parent.document : document;
        doc.querySelectorAll('[data-baseweb="select"] input').forEach(lock);
    }
    var rootDoc = window.parent ? window.parent.document : document;
    new MutationObserver(lockAll).observe(rootDoc.body, { subtree: true, childList: true });
    lockAll();
})();
</script>
"""

def inject_selectbox_lock_script() -> None:
    """Prevent users from typing/searching inside Streamlit selectbox widgets."""
    components.html(_SELECTBOX_LOCK_SCRIPT, height=0, width=0)
