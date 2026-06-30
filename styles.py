"""适老化大字体 UI 样式"""

import streamlit as st

SENIOR_CSS = """
<style>
    /* 1. 彻底蒸发右上角工具栏（包含 Fork、GitHub 图标、三点菜单） */
    [data-testid="stHeaderToolbar"], .stHeaderToolbar, #MainMenu, .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    /* 保持顶部容器背景透明，仅允许左侧侧边栏折叠/展开按钮正常可见 */
    header, [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* 2. 彻底拆除右下角所有官方残留（包含 Created by、Hosted with Streamlit 红色大滑块） */
    footer, [data-testid="stFooter"], .viewerBadge, [data-testid="stViewerBadge"] {
        display: none !important;
        visibility: hidden !important;
    }
    /* 强行压制可能浮现的平台管理面板底衬 */
    iframe[title="Manage app"], .manage-app-button {
        display: none !important;
        visibility: hidden !important;
    }
    button[data-testid="stBaseButton-primary"],
    button[data-testid="stBaseButton-primary"] p,
    button[data-testid="stBaseButton-primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover p,
    div.stButton button[kind="primary"],
    div.stButton button[kind="primary"] p,
    div.stButton button[kind="primary"]:hover,
    div.stButton button[kind="primary"]:hover p,
    [data-testid="stFormSubmitButton"] button[kind="primary"],
    [data-testid="stFormSubmitButton"] button[kind="primary"] p,
    [data-testid="stFormSubmitButton"] button[kind="primary"]:hover,
    [data-testid="stFormSubmitButton"] button[kind="primary"]:hover p {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 18px !important;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(4px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main .block-container {
        animation: fadeIn 0.3s ease-out forwards;
    }
    div.block-container {padding-top: 2rem !important;}
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
    [data-testid="stExpander"] {
        animation: fadeIn 0.3s ease-out forwards;
    }
    [data-testid="stExpander"] details {
        background: #F8FAFC !important;
        border-color: rgba(148, 163, 184, 0.28) !important;
        border-radius: 14px !important;
        transition: background-color 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease, transform 0.22s ease;
    }
    [data-testid="stExpander"] details:hover,
    [data-testid="stExpander"] details:active,
    [data-testid="stExpander"] details[open] {
        background: #F1F5F9 !important;
        border-color: rgba(30, 64, 175, 0.18) !important;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.05) !important;
    }
    [data-testid="stTextInput"] div[data-baseweb="input"],
    [data-testid="stTextArea"] textarea,
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        border-radius: 8px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
    }
    [data-testid="stTextInput"]:focus-within div[data-baseweb="input"],
    [data-testid="stTextArea"]:focus-within textarea,
    [data-testid="stSelectbox"]:focus-within div[data-baseweb="select"] {
        border-color: #1E40AF !important;
        box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.10) !important;
    }
    [data-baseweb="popover"] {
        transform-style: preserve-3d !important;
        backface-visibility: hidden !important;
        filter: blur(0) !important;
    }
    [data-baseweb="popover"] ul,
    [data-baseweb="popover"] li,
    [role="listbox"] [role="option"] {
        font-family: "Segoe UI", "Microsoft YaHei", "微软雅黑", sans-serif !important;
        font-size: 15px !important;
        color: #0F172A !important;
        font-weight: 600 !important;
        -webkit-font-smoothing: subpixel-antialiased !important;
        -moz-osx-font-smoothing: auto !important;
    }
    [data-baseweb="popover"] li > div,
    [role="listbox"] [role="option"] > div {
        font-family: "Segoe UI", "Microsoft YaHei", "微软雅黑", sans-serif !important;
        font-size: 15px !important;
        color: #0F172A !important;
        font-weight: 600 !important;
    }
    [data-baseweb="popover"] li:hover,
    [data-baseweb="popover"] li[aria-selected="true"],
    [role="listbox"] [role="option"]:hover,
    [role="listbox"] [role="option"][aria-selected="true"] {
        background: #E2E8F0 !important;
        color: #0F172A !important;
    }
    [data-baseweb="popover"] li:hover *,
    [data-baseweb="popover"] li[aria-selected="true"] *,
    [role="listbox"] [role="option"]:hover *,
    [role="listbox"] [role="option"][aria-selected="true"] * {
        color: #0F172A !important;
        font-weight: 600 !important;
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
        font-size: 18px !important;
        font-weight: 800 !important;
        min-height: 3.5rem !important;
        color: #FFFFFF !important;
    }
    div.stButton > button[kind="primary"] *,
    button[data-testid="stBaseButton-primary"] *,
    [data-testid="stFormSubmitButton"] button[kind="primary"] * {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 18px !important;
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
    st.markdown(f'<div class="semester-banner">{label}</div>', unsafe_allow_html=True)
