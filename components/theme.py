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
        st.session_state.dark_mode = True

    c = DARK if st.session_state.dark_mode else LIGHT

    # 너무 자잘한 span, div 등 모든 태그에 강제 주입을 걸어 화면 레이아웃이 깨지던 현상 수정.
    # 꼭 필요한 큰 컨테이너나 배경, 그리고 기본 텍스트에만 조심스럽게 오버라이딩합니다.
    st.markdown(f"""
    <style>
        /* 메인 배경색 */
        .stApp {{
            background-color: {c['bg']} !important;
            color: {c['text']};
        }}
        
        header[data-testid="stHeader"] {{
            background-color: transparent !important;
        }}

        /* 하우스 및 컨테이너 (카드 디자인) 영역 */
        div[data-testid="stSidebar"],
        .stTabs [data-baseweb="tab-panel"],
        div[data-testid="stForm"],
        div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] {{
            background-color: {c['secondary_bg']} !important;
            border-color: {c['border']} !important;
        }}

        /* 글씨 타겟팅 (범위 최소화) */
        .stMarkdown, .stText, label, p, h1, h2, h3, h4, h5, h6 {{
            color: {c['text']} !important;
        }}
        
        .stCaptionContainer * {{
            color: {c['subtext']} !important;
        }}

        /* 위젯 및 입력 칸 */
        div[data-baseweb="input"], 
        div[data-baseweb="base-input"],
        div[data-baseweb="select"] > div {{
            background-color: {c['input_bg']} !important;
            border-color: {c['border']} !important;
        }}
        
        input, textarea, .stSelectbox div[data-baseweb="select"] div {{
            color: {c['text']} !important;
        }}

        /* 버튼 및 툴팁 메뉴 배경 등 */
        div[data-baseweb="popover"] > div,
        div[data-baseweb="menu"] {{
            background-color: {c['secondary_bg']} !important;
        }}

        /* 구조적 여백 유지 */
        .block-container {{
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
            max-width: 1400px;
        }}
        form[data-testid="stForm"], div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] {{
            border-radius: 12px;
            border: 1px solid {c['border']} !important;
        }}
        
        /* 탭 가독성 */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2rem;
            background-color: {c['bg']} !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            padding-top: 1rem;
            padding-bottom: 1rem;
            font-size: 1.05rem;
            font-weight: 600;
            background-color: {c['bg']} !important;
            color: {c['subtext']} !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: {c['primary']} !important;
            border-bottom-color: {c['primary']} !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def toggle_button():
    label = "☀️ 라이트" if st.session_state.dark_mode else "🌙 다크 모드"
    if st.button(label, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
