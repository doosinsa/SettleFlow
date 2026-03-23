import math

import streamlit as st

from config.settings import (
    ITEMS_PER_PAGE,
    LOGISTICS_STATUSES,
    STATUS_COLORS,
)
from services.clipboard import build_kakao_message
from services.sheets_client import get_all_returns, update_return_status


def _status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#6B7280")
    return (
        f'<span style="background:{color};color:white;padding:2px 10px;'
        f'border-radius:12px;font-size:0.8em;font-weight:600;">{status}</span>'
    )


def render():
    st.subheader("반품/교환 현황")

    df = get_all_returns()

    if df.empty:
        st.info("등록된 반품/교환 내역이 없습니다.")
        return

    # --- 필터 ---
    vendors = ["전체"] + sorted(df["vendor"].dropna().unique().tolist())
    statuses = ["전체"] + LOGISTICS_STATUSES

    col_f1, col_f2, col_f3 = st.columns([2, 2, 4])
    with col_f1:
        selected_vendor = st.selectbox("거래처 필터", vendors, key="ret_vendor_filter")
    with col_f2:
        selected_status = st.selectbox("상태 필터", statuses, key="ret_status_filter")

    filtered = df.copy()
    if selected_vendor != "전체":
        filtered = filtered[filtered["vendor"] == selected_vendor]
    if selected_status != "전체":
        filtered = filtered[filtered["logistics_status"] == selected_status]

    # 최신순 정렬
    if "created_at" in filtered.columns:
        filtered = filtered.sort_values("created_at", ascending=False)

    total = len(filtered)
    if total == 0:
        st.info("조건에 맞는 내역이 없습니다.")
        return

    total_pages = max(1, math.ceil(total / ITEMS_PER_PAGE))
    page = st.selectbox(
        f"페이지 (총 {total}건)",
        range(1, total_pages + 1),
        key="ret_page",
        label_visibility="visible",
    )

    start = (page - 1) * ITEMS_PER_PAGE
    page_df = filtered.iloc[start : start + ITEMS_PER_PAGE]

    # --- 헤더 ---
    h1, h2, h3, h4, h5, h6 = st.columns([1.5, 2, 2, 2, 1.5, 2])
    with h1:
        st.caption("날짜")
    with h2:
        st.caption("상품명 / 고객명")
    with h3:
        st.caption("거래처 / 송장번호")
    with h4:
        st.caption("사유 / 택배비")
    with h5:
        st.caption("상태")
    with h6:
        st.caption("액션")
    st.divider()

    for _, row in page_df.iterrows():
        row_id = row["id"]
        c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2, 2, 2, 1.5, 2])
        with c1:
            st.write(row.get("date", ""))
        with c2:
            st.write(f"**{row.get('product_name', '')}**")
            st.caption(row.get("customer_name", ""))
        with c3:
            st.write(row.get("vendor", ""))
            st.caption(row.get("tracking_number", "") or "-")
        with c4:
            st.write(row.get("reason", ""))
            st.caption(f"택배비: {row.get('delivery_fee', '')}")
        with c5:
            st.markdown(_status_badge(row.get("logistics_status", "")), unsafe_allow_html=True)
        with c6:
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                with st.popover("카톡복사", use_container_width=True):
                    msg = build_kakao_message(row.to_dict())
                    st.code(msg, language=None)
            with btn_col2:
                with st.popover("상태변경", use_container_width=True):
                    current = row.get("logistics_status", LOGISTICS_STATUSES[0])
                    current_idx = LOGISTICS_STATUSES.index(current) if current in LOGISTICS_STATUSES else 0
                    new_status = st.selectbox(
                        "새 상태",
                        LOGISTICS_STATUSES,
                        index=current_idx,
                        key=f"sel_{row_id}",
                    )
                    if st.button("확인", key=f"confirm_{row_id}", type="primary"):
                        if new_status != current:
                            update_return_status(row_id, new_status)
                            st.rerun()

        if row.get("notes"):
            st.caption(f"📝 {row['notes']}")
        st.divider()
