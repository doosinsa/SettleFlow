import math

import streamlit as st

from config.settings import (
    ITEMS_PER_PAGE,
    SETTLEMENT_STATUSES,
    STATUS_COLORS,
)
from services.sheets_client import get_all_settlements, update_settlement_status


def _status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#6B7280")
    return (
        f'<span style="background:{color};color:white;padding:2px 10px;'
        f'border-radius:12px;font-size:0.8em;font-weight:600;">{status}</span>'
    )


def render():
    st.subheader("정산 현황")

    df = get_all_settlements()

    if df.empty:
        st.info("등록된 정산 내역이 없습니다.")
        return

    # --- 필터 ---
    vendors = ["전체"] + sorted(df["vendor"].dropna().unique().tolist())
    statuses = ["전체"] + SETTLEMENT_STATUSES

    col_f1, col_f2, col_f3 = st.columns([2, 2, 4])
    with col_f1:
        selected_vendor = st.selectbox("거래처 필터", vendors, key="set_vendor_filter")
    with col_f2:
        selected_status = st.selectbox("상태 필터", statuses, key="set_status_filter")

    filtered = df.copy()
    if selected_vendor != "전체":
        filtered = filtered[filtered["vendor"] == selected_vendor]
    if selected_status != "전체":
        filtered = filtered[filtered["settlement_status"] == selected_status]

    if "created_at" in filtered.columns:
        filtered = filtered.sort_values("created_at", ascending=False)

    # --- 미정산 합계 요약 ---
    unpaid = filtered[filtered["settlement_status"] != "입금완료"]
    if not unpaid.empty and "amount" in unpaid.columns:
        total_unpaid = unpaid["amount"].astype(float).sum()
        st.info(f"💰 미정산 합계 (현재 필터 기준): **{total_unpaid:,.0f}원**")

    total = len(filtered)
    if total == 0:
        st.info("조건에 맞는 내역이 없습니다.")
        return

    total_pages = max(1, math.ceil(total / ITEMS_PER_PAGE))
    page = st.selectbox(
        f"페이지 (총 {total}건)",
        range(1, total_pages + 1),
        key="set_page",
        label_visibility="visible",
    )

    start = (page - 1) * ITEMS_PER_PAGE
    page_df = filtered.iloc[start : start + ITEMS_PER_PAGE]

    # --- 헤더 ---
    h1, h2, h3, h4, h5 = st.columns([2, 2.5, 1.5, 2, 2])
    with h1:
        st.caption("거래처")
    with h2:
        st.caption("정산금액")
    with h3:
        st.caption("등록일")
    with h4:
        st.caption("상태")
    with h5:
        st.caption("액션")
    st.divider()

    for _, row in page_df.iterrows():
        row_id = row["id"]
        c1, c2, c3, c4, c5 = st.columns([2, 2.5, 1.5, 2, 2])
        with c1:
            st.write(f"**{row.get('vendor', '')}**")
            if row.get("return_id"):
                st.caption(f"반품: {row['return_id'][:8]}…")
        with c2:
            try:
                amt = float(row.get("amount", 0))
                st.write(f"{amt:,.0f}원")
            except (ValueError, TypeError):
                st.write(row.get("amount", ""))
        with c3:
            created = str(row.get("created_at", ""))
            st.caption(created[:10] if created else "")
        with c4:
            st.markdown(_status_badge(row.get("settlement_status", "")), unsafe_allow_html=True)
        with c5:
            with st.popover("상태변경", use_container_width=True):
                current = row.get("settlement_status", SETTLEMENT_STATUSES[0])
                current_idx = SETTLEMENT_STATUSES.index(current) if current in SETTLEMENT_STATUSES else 0
                new_status = st.selectbox(
                    "새 상태",
                    SETTLEMENT_STATUSES,
                    index=current_idx,
                    key=f"set_sel_{row_id}",
                )
                if st.button("확인", key=f"set_confirm_{row_id}", type="primary"):
                    if new_status != current:
                        update_settlement_status(row_id, new_status)
                        st.rerun()

        if row.get("notes"):
            st.caption(f"📝 {row['notes']}")
        st.divider()
