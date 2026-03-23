import streamlit as st

from config.settings import DELIVERY_FEE_OPTIONS, REASON_OPTIONS
from services.sheets_client import append_return, get_all_vendors


def render():
    st.subheader("반품/교환 등록")
    with st.form("return_form", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            date = st.date_input("날짜 *")
        with col2:
            product_name = st.text_input("상품명 *")
        with col3:
            customer_name = st.text_input("고객명 *")
        with col4:
            contact = st.text_input("연락처")

        col5, col6, col7, col8, col9 = st.columns(5)
        with col5:
            reason = st.selectbox("사유 *", REASON_OPTIONS)
        with col6:
            vendors = get_all_vendors()
            if vendors:
                vendor = st.selectbox("거래처 *", options=vendors, index=None, placeholder="검색 또는 선택...")
            else:
                vendor = st.text_input("거래처 *", placeholder="거래처 탭에서 먼저 등록하세요")
        with col7:
            tracking_number = st.text_input("송장번호")
        with col8:
            delivery_fee = st.radio("택배비", DELIVERY_FEE_OPTIONS, horizontal=True)
        with col9:
            notes = st.text_input("비고")

        submitted = st.form_submit_button("등록하기", type="primary", use_container_width=True)

    if submitted:
        if not product_name or not customer_name or not vendor:
            st.error("상품명, 고객명, 거래처는 필수 입력값입니다.")
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
        st.success(f"✅ [{vendor}] {customer_name} / {product_name} 등록 완료")
