import math
import streamlit as st

from config.settings import ITEMS_PER_PAGE, LOGISTICS_STATUSES, STATUS_COLORS
from services.clipboard import build_kakao_message
from services.sheets_client import get_all_returns, update_return_status

def _status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#6B7280")
    # 약간 더 부드럽고 모던한 느낌의 뱃지로 렌더링
    return f"""
    <span style="
        background-color: {color}15;
        color: {color};
        padding: 4px 12px;
        border: 1px solid {color}40;
        border-radius: 16px;
        font-size: 0.85em;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 0.5rem;
    ">{status}</span>
    """

def render():
    st.markdown("### 📋 반품/교환 현황")
    
    df = get_all_returns()
    if df.empty:
        st.info("📦 아직 접수된 반품/교환 내역이 없습니다.")
        return

    # --- 필터 영역 ---
    with st.container(border=True):
        vendors = ["전체"] + sorted(df["vendor"].dropna().unique().tolist())
        statuses = ["전체"] + LOGISTICS_STATUSES

        col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
        with col_f1:
            selected_vendor = st.selectbox("🏢 거래처 필터", vendors, key="ret_vendor_filter")
        with col_f2:
            selected_status = st.selectbox("📌 상태 필터", statuses, key="ret_status_filter")
            
    filtered = df.copy()
    if selected_vendor != "전체":
        filtered = filtered[filtered["vendor"] == selected_vendor]
    if selected_status != "전체":
        filtered = filtered[filtered["logistics_status"] == selected_status]

    if "created_at" in filtered.columns:
        filtered = filtered.sort_values("created_at", ascending=False)

    total = len(filtered)
    if total == 0:
        st.info("🔍 조건에 맞는 내역이 없습니다.")
        return

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 페이지네이션
    col_p1, col_p2 = st.columns([4, 1])
    with col_p2:
        total_pages = max(1, math.ceil(total / ITEMS_PER_PAGE))
        page = st.selectbox(
            f"페이지 (총 {total}건)",
            range(1, total_pages + 1),
            key="ret_page",
            label_visibility="collapsed"
        )
    
    start = (page - 1) * ITEMS_PER_PAGE
    page_df = filtered.iloc[start : start + ITEMS_PER_PAGE]

    st.markdown("---")

    # --- 반응형 카드(Card) 레이아웃 리스트 ---
    for _, row in page_df.iterrows():
        row_id = row["id"]
        # 건별로 분리된 컨테이너
        with st.container(border=True):
            info_col, action_col = st.columns([4, 1])
            
            with info_col:
                # 상태 뱃지 및 날짜 (html 렌더링)
                st.markdown(f"{_status_badge(row.get('logistics_status', ''))} &nbsp;&nbsp; `<{row.get('date', '')}>`", unsafe_allow_html=True)
                
                # 메인 타이틀(상품 + 고객명)
                st.markdown(
                    f"#### {row.get('product_name', '상품명 없음')} "
                    f"<span style='font-size: 0.9em; font-weight: 400; color: gray;'>/ {row.get('customer_name', '고객')}</span>", 
                    unsafe_allow_html=True
                )
                
                # 주요 부가 정보
                st.caption(
                    f"**🏢 {row.get('vendor', '')}** | 🚚 {row.get('tracking_number', '송장 미입력')} "
                    f"| 💰 택비: {row.get('delivery_fee', '')} | 🏷️ 사유: {row.get('reason', '')}"
                )
                if row.get("notes"):
                    st.caption(f"📝 {row['notes']}")

            with action_col:
                # 버튼들의 수직 여백/정렬 조정
                st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
                
                # 카톡복사 기능을 popover로 감춤 (UI 간소화)
                with st.popover("💬 카톡 양식", use_container_width=True):
                    msg = build_kakao_message(row.to_dict())
                    st.code(msg, language="text")
                    
                # 상태변경 액션
                with st.popover("🔄 변경", use_container_width=True):
                    current = row.get("logistics_status", LOGISTICS_STATUSES[0])
                    current_idx = LOGISTICS_STATUSES.index(current) if current in LOGISTICS_STATUSES else 0
                    new_status = st.selectbox(
                        "새 상태 지정",
                        LOGISTICS_STATUSES,
                        index=current_idx,
                        key=f"ret_sel_{row_id}",
                    )
                    if st.button("확인", key=f"ret_confirm_{row_id}", type="primary", use_container_width=True):
                        if new_status != current:
                            update_return_status(row_id, new_status)
                            st.rerun()
