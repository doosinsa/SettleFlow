import streamlit as st

from services.sheets_client import append_vendor, delete_vendor, get_all_vendors


def render():
    st.markdown("### 🏢 거래처 관리")
    st.caption("새로운 거래처를 추가하거나 기존 목록을 관리합니다.")
    
    with st.form("vendor_form", clear_on_submit=True, border=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            name = st.text_input("새 거래처명", placeholder="등록할 거래처의 이름을 입력하세요 (예: 동대문 창고)", label_visibility="collapsed")
        with col2:
            submitted = st.form_submit_button("➕ 추가", type="primary", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("⚠️ 거래처명을 입력해주세요.")
        else:
            vendors = get_all_vendors()
            if name.strip() in vendors:
                st.warning(f"⚠️ '{name}' 거래처가 이미 등록되어 있습니다.")
            else:
                append_vendor(name.strip())
                st.success(f"✅ '{name}' 거래처가 성공적으로 등록 되었습니다.")
                st.rerun()

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    
    st.subheader("등록된 거래처 목록")
    vendors = get_all_vendors()

    if not vendors:
        st.info("등록된 거래처가 없습니다.")
        return

    # 검색 필터
    search = st.text_input("🔍 거래처 검색", placeholder="이름으로 빠르게 검색...", key="vendor_search")
    filtered = [v for v in vendors if search.lower() in v.lower()] if search else vendors

    st.caption(f"총 **{len(vendors)}**개 중 **{len(filtered)}**개 표시")

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    for vendor in filtered:
        # 세련된 인라인 리스트 아이템 UI 
        cont = st.container(border=True)
        with cont:
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"**{vendor}**")
            with col2:
                with st.popover("🗑️ 삭제", use_container_width=True):
                    st.warning(f"**'{vendor}'** 거래처를 삭제하시겠습니까?\n\n이 작업은 복구할 수 없습니다.")
                    if st.button("영구 삭제", key=f"del_{vendor}", type="primary"):
                        delete_vendor(vendor)
                        st.rerun()
