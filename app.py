import streamlit as st

st.set_page_config(
    page_title="SettleFlow",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from components import dashboard, return_form, return_list, settlement_form, settlement_list, vendor_manager, theme

theme.apply()

title_col, toggle_col = st.columns([8, 1])
with title_col:
    st.title("💰 SettleFlow")
    st.caption("1인 커머스 교환/반품 및 거래처 정산 관리")
with toggle_col:
    st.write("")
    st.write("")
    theme.toggle_button()

# 탭 구조 위에 전역 대시보드 렌더링
dashboard.render()

tab1, tab2, tab3 = st.tabs(["📦 교환/반품 센터", "💳 정산 매니저", "🏢 거래처 관리"])

with tab1:
    return_form.render()
    st.divider()
    return_list.render()

with tab2:
    settlement_form.render()
    st.divider()
    settlement_list.render()

with tab3:
    vendor_manager.render()
