import streamlit as st

DARK = {
    "bg": "#0E1117",
    "secondary_bg": "#1E2130",
    "text": "#FAFAFA",
    "subtext": "#A0AEC0",
    "border": "#2D3748",
    "input_bg": "#262730",
    "primary": "#3B82F6",
}

LIGHT = {
    "bg": "#F8FAFC",
    "secondary_bg": "#FFFFFF",
    "text": "#1E293B",
    "subtext": "#64748B",
    "border": "#E2E8F0",
    "input_bg": "#FFFFFF",
    "primary": "#3B82F6",
}


def apply():
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True  # 기본값: 다크모드

    c = DARK if st.session_state.dark_mode else LIGHT

    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {c['bg']} !important;
        }}
        section[data-testid="stSidebar"],
        .stTabs [data-baseweb="tab-panel"],
        div[data-testid="stForm"] {{
            background-color: {c['bg']} !important;
        }}
        div[data-testid="stVerticalBlock"],
        div[data-testid="column"] {{
            color: {c['text']} !important;
        }}
        .stMarkdown, .stText, p, span, label, div {{
            color: {c['text']} !important;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {c['text']} !important;
        }}
        .stTextInput input,
        .stSelectbox div[data-baseweb="select"] > div,
        .stNumberInput input,
        .stDateInput input,
        textarea {{
            background-color: {c['input_bg']} !important;
            color: {c['text']} !important;
            border-color: {c['border']} !important;
        }}
        div[data-baseweb="popover"] > div,
        div[data-baseweb="menu"] {{
            background-color: {c['secondary_bg']} !important;
            color: {c['text']} !important;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {c['bg']} !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: {c['bg']} !important;
            color: {c['subtext']} !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: {c['primary']} !important;
            border-bottom-color: {c['primary']} !important;
        }}
        hr {{
            border-color: {c['border']} !important;
        }}
        .stAlert {{
            background-color: {c['secondary_bg']} !important;
        }}
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricLabel"] {{
            color: {c['text']} !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def toggle_button():
    label = "☀️ 라이트" if st.session_state.get("dark_mode", True) else "🌙 다크"
    if st.button(label, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.get("dark_mode", True)
        st.rerun()
