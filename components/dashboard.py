import streamlit as st
from services.sheets_client import get_all_returns, get_all_settlements

def render():
    st.markdown("### 📊 SettleFlow 요약 대시보드")
    
    returns_df = get_all_returns()
    settlements_df = get_all_settlements()
    
    active_returns = 0
    total_unpaid = 0
    
    # 환불/완료가 아닌 처리 중인 상태의 건수 계산
    if not returns_df.empty and "logistics_status" in returns_df.columns:
        active_returns = len(returns_df[returns_df["logistics_status"] != "환불완료"])
        
    # 입금완료가 아닌 미정산 금액 합산
    if not settlements_df.empty and "settlement_status" in settlements_df.columns and "amount" in settlements_df.columns:
        unpaid_df = settlements_df[settlements_df["settlement_status"] != "입금완료"]
        total_unpaid = unpaid_df["amount"].astype(float).sum()
        
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="📦 처리 중인 교환/반품 건", value=f"{active_returns} 건", delta="관심 필요", delta_color="inverse")
        with col2:
            st.metric(label="💳 총 미입금 정산 잔액", value=f"{total_unpaid:,.0f} 원", delta="확인 필요", delta_color="inverse")
            
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
