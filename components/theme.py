import streamlit as st

def apply():
    """
    모든 '수동 텍스트/배경 색상(CSS) 오버라이드'를 지워버리고 (버그의 온상)
    Streamlit 공식 테마(System Auto/Query Param)를 존중하도록 구조적 여백/모서리만 유지합니다.
    """
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
            /* 테마변경에 방해되지 않도록 색상 지정 삭제 */
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


def toggle_button():
    """
    Streamlit 공식 URL 테마 파라미터를 쿼리로 조작하여
    강제 CSS 주입 없이 100% 완벽한 라이트/다크 모드 디자인 스위칭을 달성합니다.
    """
    # 현재 URL 주소에 세팅된 파라미터 조회 (없으면 "dark"로 간주)
    current_theme = st.query_params.get("theme", "dark")
    
    # 지금 모드와 반대되는 버튼 띄우기
    label = "☀️ 라이트" if current_theme == "dark" else "🌙 다크 모드"
    
    # 버튼 클릭 시 URL 파라미터 강제 치환 후 새로고침
    if st.button(label, key="theme_official_toggle"):
        new_theme = "light" if current_theme == "dark" else "dark"
        st.query_params["theme"] = new_theme
        st.rerun()
