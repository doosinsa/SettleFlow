import streamlit as st

def apply():
    """
    복잡한 인라인 CSS 오버라이드를 제거하고,
    마진, 패딩, 테두리, 카드 레이아웃과 같은 구조적인 글로벌 디자인만 최소한으로 주입합니다.
    색상 등은 .streamlit/config.toml 에서 네이티브하게 컨트롤됩니다.
    """
    st.markdown("""
    <style>
        /* 컨테이너 상/하단 여백 최소화하여 콤팩트한 뷰 제공 */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
            max-width: 1400px;
        }

        /* st.dataframe 및 data_editor 테이블 모서리 둥글게 */
        div[data-testid="stDataFrame"] {
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid rgba(128,128,128,0.2) !important;
        }
        
        /* 탭 디자인 정갈하게 - 밑줄 간격 및 굵기 조정 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding-top: 1rem;
            padding-bottom: 1rem;
            font-size: 1.05rem;
            font-weight: 600;
        }

        /* 알림 메시지나 에러 패널 등 곡률 추가 */
        .stAlert {
            border-radius: 8px !important;
        }
        
        form[data-testid="stForm"] {
            border-radius: 12px;
            border: 1px solid rgba(128,128,128,0.1) !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            padding: 1.5rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

def toggle_button():
    """
    기존에 수동으로 다크/라이트 버튼을 오버라이딩 하던 기능을 제거했습니다.
    Streamlit 1.30+ 에서는 앱 우측 상단 '점 세개 아이콘 -> Settings' 메뉴에서 
    기기에 맞춰 자동으로 테마(라이트/다크)를 부드럽게 전환할 수 있도록 네이티브 기능을 활용합니다.
    (app.py 호환성을 유지하기 위해 껍데기만 남겨둡니다.)
    """
    pass
