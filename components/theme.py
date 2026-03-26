import streamlit as st


def apply():
    """레이아웃 기본 스타일."""
    st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
            max-width: 1400px;
        }
        form[data-testid="stForm"] {
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding-top: 1rem;
            padding-bottom: 1rem;
            font-size: 1.05rem;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)
