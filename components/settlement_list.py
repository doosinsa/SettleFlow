import math
import streamlit as st

from config.settings import ITEMS_PER_PAGE, SETTLEMENT_STATUSES, STATUS_COLORS
from services.sheets_client import get_all_settlements, update_settlement_status

def _status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#6B7280")
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
    st.markdown("### 📋 정산 현황")
    
    df = get_all_settlements()
    if df.empty:
        st.info("💳 등록된 정산 내역이 없습니다.")
        return

    # --- 필터 영역 (컨테이너 처리) ---
    with st.container(border=True):
        vendors = ["전체"] + sorted(df["vendor"].dropna().unique().tolist())
        statuses = ["전체"] + SETTLEMENT_STATUSES

        col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
        with col_f1:
            selected_vendor = st.selectbox("🏢 거래처 필터", vendors, key="set_vendor_filter")
        with col_f2:
            selected_status = st.selectbox("📌 상태 필터", statuses, key="set_status_filter")

    filtered = df.copy()
    if selected_vendor != "전체":
        filtered = filtered[filtered["vendor"] == selected_vendor]
    if selected_status != "전체":
        filtered = filtered[filtered["settlement_status"] == selected_status]

    if "created_at" in filtered.columns:
        filtered = filtered.sort_values("created_at", ascending=False)
        
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # --- 미정산 합계 요약 (Metric 스타일 활용) ---
    unpaid = filtered[filtered["settlement_status"] != "입금완료"]
    total_unpaid = 0
    if not unpaid.empty and "amount" in unpaid.columns:
        total_unpaid = unpaid["amount"].astype(float).sum()
        
    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        st.metric(label="📊 조회된 미정산 합계액", value=f"{total_unpaid:,.0f} 원", delta="결제 대기중", delta_color="inverse")

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    total = len(filtered)
    if total == 0:
        st.info("🔍 조건에 맞는 내역이 없습니다.")
        return

    # 페이지네이션
    col_p1, col_p2 = st.columns([4, 1])
    with col_p2:
        total_pages = max(1, math.ceil(total / ITEMS_PER_PAGE))
        page = st.selectbox(
            f"페이지 (총 {total}건)",
            range(1, total_pages + 1),
            key="set_page",
            label_visibility="collapsed",
        )

    start = (page - 1) * ITEMS_PER_PAGE
    page_df = filtered.iloc[start : start + ITEMS_PER_PAGE]

    st.markdown("---")

    # --- 카드 컨테이너 레이아웃 (반응형 최적화) ---
    for _, row in page_df.iterrows():
        row_id = row["id"]
        
        with st.container(border=True):
            info_col, action_col = st.columns([4, 1])
            
            with info_col:
                st.markdown(f"{_status_badge(row.get('settlement_status', ''))} &nbsp;&nbsp; `<{str(row.get('created_at', ''))[:10]}>`", unsafe_allow_html=True)
                
                try:
                    amt = float(row.get("amount", 0))
                    amt_str = f"{amt:,.0f}원"
                except (ValueError, TypeError):
                    amt_str = str(row.get("amount", ""))
                    
                st.markdown(f"#### 🏢 {row.get('vendor', '알수없음')} <span style='color: #4CAF50;'>({amt_str})</span>", unsafe_allow_html=True)
                
                if row.get("return_id"):
                    st.caption(f"🔗 연계 반품ID: {row['return_id']}")
                if row.get("notes"):
                    st.caption(f"📝 메모: {row['notes']}")

            with action_col:
                st.write("") # 버튼 세로정렬용
                with st.popover("🔄 변경", use_container_width=True):
                    current = row.get("settlement_status", SETTLEMENT_STATUSES[0])
                    current_idx = SETTLEMENT_STATUSES.index(current) if current in SETTLEMENT_STATUSES else 0
                    new_status = st.selectbox(
                        "새 상태 지정",
                        SETTLEMENT_STATUSES,
                        index=current_idx,
                        key=f"set_sel_{row_id}",
                    )
                    if st.button("확인", key=f"set_confirm_{row_id}", type="primary", use_container_width=True):
                        if new_status != current:
                            update_settlement_status(row_id, new_status)
                            st.rerun()
