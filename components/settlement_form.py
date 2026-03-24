import streamlit as st

from services.sheets_client import append_settlement, get_all_vendors

def render():
    st.markdown("### 💳 정산 정보 등록")
    st.caption("거래처에 송금하거나 받을 정산 내역을 기입합니다.")
    
    with st.form("settlement_form", clear_on_submit=True, border=True):
        col_date, col_vendor, col_amt = st.columns([1, 1.5, 1.5])
        with col_date:
            settlement_dt = st.date_input("정산일 *")
        with col_vendor:
            vendors = get_all_vendors()
            if vendors:
                vendor = st.selectbox("거래처 *", options=vendors, index=None, placeholder="거래처 선택...")
            else:
                vendor = st.text_input("거래처 *", placeholder="거래처 탭에서 먼저 등록하세요")
        with col_amt:
            # 콤마 단위를 보기 편하게 step과 format 지정 (원화 느낌의 integer)
            amount = st.number_input("정산금액 (원) *", min_value=0, step=1000, value=0, format="%d")
            
        col_ret, col_note = st.columns([1.5, 2.5])
        with col_ret:
            return_id = st.text_input("연계 반품ID (선택)", placeholder="관련 반품 건의 아이디 기입")
        with col_note:
            notes = st.text_input("비고", placeholder="이체 메모 등 추가 정보")

        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 정산 내역 처리하기", type="primary", use_container_width=True)

    if submitted:
        if not vendor:
            st.error("⚠️ 거래처는 필수 정보입니다.")
            return
        if amount <= 0:
            st.error("⚠️ 0원 초과의 실제 정산금액을 입력해주세요.")
            return

        append_settlement({
            "settlement_date": settlement_dt.strftime("%Y-%m-%d"),
            "vendor": vendor,
            "amount": int(amount),
            "return_id": return_id,
            "notes": notes,
        })
        st.success(f"✅ [{vendor}] 거래처와 {amount:,}원의 정산 내역이 날짜({settlement_dt})에 성공적으로 입력되었습니다.")
