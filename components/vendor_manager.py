import streamlit as st

from services.sheets_client import append_vendor, delete_vendor, get_all_vendors


def render():
    st.subheader("거래처 등록")
    with st.form("vendor_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            name = st.text_input("거래처명 *", placeholder="예: 한국물산")
        with col2:
            submitted = st.form_submit_button("등록", type="primary", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("거래처명을 입력해주세요.")
        else:
            vendors = get_all_vendors()
            if name.strip() in vendors:
                st.warning(f"'{name}' 거래처가 이미 등록되어 있습니다.")
            else:
                append_vendor(name.strip())
                st.success(f"✅ '{name}' 등록 완료")

    st.divider()
    st.subheader("등록된 거래처 목록")

    vendors = get_all_vendors()

    if not vendors:
        st.info("등록된 거래처가 없습니다.")
        return

    # 검색 필터
    search = st.text_input("거래처 검색", placeholder="이름 입력...", key="vendor_search")
    filtered = [v for v in vendors if search.lower() in v.lower()] if search else vendors

    st.caption(f"총 {len(vendors)}개 중 {len(filtered)}개 표시")

    for vendor in filtered:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.write(vendor)
        with col2:
            with st.popover("삭제", use_container_width=True):
                st.warning(f"**'{vendor}'** 거래처를 삭제하시겠습니까?")
                if st.button("확인 삭제", key=f"del_{vendor}", type="primary"):
                    delete_vendor(vendor)
                    st.rerun()
