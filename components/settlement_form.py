import streamlit as st

from services.sheets_client import append_settlement, get_all_vendors


def render():
    st.subheader("정산 등록")
    with st.form("settlement_form", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            vendors = get_all_vendors()
            if vendors:
                vendor = st.selectbox("거래처 *", options=vendors, index=None, placeholder="검색 또는 선택...")
            else:
                vendor = st.text_input("거래처 *", placeholder="거래처 탭에서 먼저 등록하세요")
        with col2:
            amount = st.number_input("정산금액 (원) *", min_value=0, step=1000, value=0)
        with col3:
            return_id = st.text_input("연계 반품ID (선택)")
        with col4:
            notes = st.text_input("비고")

        submitted = st.form_submit_button("등록하기", type="primary", use_container_width=True)

    if submitted:
        if not vendor:
            st.error("거래처는 필수 입력값입니다.")
            return
        if amount <= 0:
            st.error("정산금액을 입력해주세요.")
            return
        append_settlement({
            "vendor": vendor,
            "amount": int(amount),
            "return_id": return_id,
            "notes": notes,
        })
        st.success(f"✅ [{vendor}] {amount:,}원 정산 등록 완료")
