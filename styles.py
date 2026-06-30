"""适老化大字体 UI 样式"""

import streamlit as st

SENIOR_CSS = """
<style>
    html, body, [class*="css"] {
        font-size: 20px !important;
        color: #475569 !important;
    }
    h1, h2, h3 { color: #1E293B !important; }
    h1 { font-size: 2.4rem !important; font-weight: 700 !important; }
    h2 { font-size: 2rem !important; font-weight: 700 !important; }
    h3 { font-size: 1.6rem !important; font-weight: 600 !important; }
    .big-label {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #475569 !important;
        margin-bottom: 0.2rem !important;
    }
    .step-title {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #1E293B !important;
        border-left: 6px solid #1E40AF;
        padding-left: 12px;
        margin: 1.2rem 0 0.8rem 0;
    }
    .semester-banner {
        background: linear-gradient(90deg, #1E40AF, #3B82F6);
        color: white;
        font-size: 1.4rem !important;
        font-weight: 700;
        text-align: center;
        padding: 14px 20px;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .birthday-card {
        background: #fff8e1;
        border: 2px solid #ffb300;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 1rem;
    }
    .birthday-card h3 { color: #e65100 !important; }
    .timeline-card {
        background: #e8f5e9;
        border: 2px solid #43a047;
        border-radius: 12px;
        padding: 20px 24px;
        font-size: 1.5rem !important;
        font-weight: 700;
        color: #1b5e20;
        text-align: center;
        margin: 1rem 0;
    }
    .highlight-city { background-color: #fff3cd !important; font-weight: 700 !important; }
    .highlight-hobby { background-color: #d1ecf1 !important; font-weight: 600 !important; }
    div.stButton > button {
        font-size: 1.2rem !important;
        padding: 0.65rem 1.4rem !important;
        min-height: 3rem !important;
        border-radius: 10px !important;
    }
    div.stButton > button[kind="primary"] {
        font-size: 1.35rem !important;
        min-height: 3.5rem !important;
    }
    .save-btn div.stButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        font-size: 1.5rem !important;
        min-height: 4rem !important;
        width: 100%;
    }
    .login-box {
        max-width: 520px;
        margin: 2rem auto;
        padding: 2rem;
        border: 2px solid #1E40AF;
        border-radius: 16px;
        background: #f5f9ff;
    }
    .login-title {
        font-size: 2rem !important;
        font-weight: 800 !important;
        text-align: center;
        color: #1E293B;
        margin-bottom: 1.5rem;
    }
    [data-testid="stSidebar"] { min-width: 280px !important; }
    [data-testid="stSidebar"] label { font-size: 1.15rem !important; }
</style>
"""


def inject_styles() -> None:
    st.markdown(SENIOR_CSS, unsafe_allow_html=True)


def big_label(text: str) -> None:
    st.markdown(f'<p class="big-label">{text}</p>', unsafe_allow_html=True)


def step_title(text: str) -> None:
    st.markdown(f'<p class="step-title">{text}</p>', unsafe_allow_html=True)


def semester_banner(label: str) -> None:
    st.markdown(f'<div class="semester-banner">📅 {label}</div>', unsafe_allow_html=True)
