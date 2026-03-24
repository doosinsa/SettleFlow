import streamlit as st

from config.settings import DELIVERY_FEE_OPTIONS, REASON_OPTIONS
from services.sheets_client import append_return, get_all_vendors

def render():
    st.markdown("### 📦 반품/교환 등록")
    st.caption("새로운 반품이나 교환 건을 접수합니다.")
    
    with st.form("return_form", clear_on_submit=True, border=True):
        st.markdown("#### 1. 기본 정보")
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("날짜 *")
        with col2:
            product_name = st.text_input("상품명 *", placeholder="예: 화이트 라운드 티")
        with col3:
            customer_name = st.text_input("고객명 *", placeholder="예: 홍길동")
            
        st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
        
        st.markdown("#### 2. 반품/교환 상세")
        col4, col5, col6 = st.columns(3)
        with col4:
            contact = st.text_input("연락처", placeholder="예: 010-1234-5678")
            tracking_number = st.text_input("송장번호", placeholder="교환/회수 송장번호")
        with col5:
            reason = st.selectbox("사유 *", REASON_OPTIONS)
            delivery_fee = st.radio("택배비", DELIVERY_FEE_OPTIONS, horizontal=True)
        with col6:
            vendors = get_all_vendors()
            if vendors:
                vendor = st.selectbox("거래처 *", options=vendors, index=None, placeholder="검색 또는 선택...")
            else:
                vendor = st.text_input("거래처 *", placeholder="먼저 거래처 탭에서 등록하세요")
            notes = st.text_input("비고", placeholder="요청 사항 및 특이점 메모")

        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 등록하기", type="primary", use_container_width=True)

    if submitted:
        if not product_name or not customer_name or not vendor:
            st.error("⚠️ 상품명, 고객명, 거래처는 필수 정보입니다. 모두 기입해 주세요.")
            return

        append_return({
            "date": date.strftime("%Y-%m-%d"),
            "product_name": product_name,
            "customer_name": customer_name,
            "contact": contact,
            "reason": reason,
            "vendor": vendor,
            "tracking_number": tracking_number,
            "delivery_fee": delivery_fee,
            "notes": notes,
        })
        st.success(f"✅ [{vendor}] {customer_name} 님의 **{product_name}** 건이 성공적으로 등록되었습니다.")
