import math
import streamlit as st

from config.settings import ITEMS_PER_PAGE, SETTLEMENT_STATUSES, STATUS_COLORS
from services.sheets_client import get_all_settlements, update_settlement_status, update_settlement_full, delete_settlement, batch_update_settlement_status

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

@st.dialog("🖊️ 정산 정보 세부 수정")
def edit_settlement_dialog(row_dict: dict):
    with st.form(f"edit_set_form_{row_dict['id']}", border=False):
        c1, c2 = st.columns(2)
        with c1:
            ven = st.text_input("거래처", value=row_dict.get("vendor", ""))
            amt = st.number_input("정산금액(원)", value=int(row_dict.get("amount", 0)), step=1000)
            settle_dt = st.text_input("정산일", value=row_dict.get("settlement_date", ""))
        with c2:
            ret_id = st.text_input("반품ID", value=row_dict.get("return_id", ""))
            nt = st.text_input("비고", value=row_dict.get("notes", ""))
            
        btn = st.form_submit_button("✅ 저장하기", type="primary", use_container_width=True)
        if btn:
            new_data = dict(row_dict)
            new_data.update({
                "vendor": ven, "amount": amt, "settlement_date": settle_dt,
                "return_id": ret_id, "notes": nt
            })
            update_settlement_full(row_dict["id"], new_data)
            st.rerun()

def render():
    st.markdown("### 📋 정산 현황")
    
    df = get_all_settlements()
    if df.empty:
        st.info("💳 등록된 정산 내역이 없습니다.")
        return

    # --- 복합 검색 필터 ---
    with st.container(border=True):
        vendors = ["전체"] + sorted(df["vendor"].dropna().unique().tolist())
        statuses = ["전체"] + SETTLEMENT_STATUSES

        col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
        with col_f1:
            selected_vendor = st.selectbox("🏢 거래처", vendors, key="set_vendor_filter")
        with col_f2:
            selected_status = st.selectbox("📌 상태", statuses, key="set_status_filter")
        with col_f3:
            date_range = st.date_input("📅 기간 검색 (시작~종료)", value=[], key="set_date_filter")

    filtered = df.copy()
    if selected_vendor != "전체":
        filtered = filtered[filtered["vendor"] == selected_vendor]
    if selected_status != "전체":
        filtered = filtered[filtered["settlement_status"] == selected_status]

    # 날짜 범위 조건 활성화 (시작일과 종료일이 모두 들어온 경우)
    if date_range and len(date_range) == 2 and "settlement_date" in filtered.columns:
        start_date, end_date = date_range
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        mask = filtered["settlement_date"].notna()
        # string 비교 필터링 수행
        filtered = filtered[mask & (filtered["settlement_date"] >= start_str) & (filtered["settlement_date"] <= end_str)]

    if "created_at" in filtered.columns:
        filtered = filtered.sort_values("created_at", ascending=False)
        
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # --- 미정산 금액 요약 렌더링 ---
    unpaid = filtered[filtered["settlement_status"] != "입금완료"]
    total_unpaid = 0
    if not unpaid.empty and "amount" in unpaid.columns:
        total_unpaid = unpaid["amount"].astype(float).sum()
        
    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        st.metric(label="📊 조회된 미정산 합계액", value=f"{total_unpaid:,.0f} 원", delta="결제 대기중", delta_color="inverse")

    # --- 선택 항목 일괄 상태 변경 바 ---
    selected_ids = [k.replace("set_chk_", "") for k, v in st.session_state.items() if k.startswith("set_chk_") and v]
    if selected_ids:
        with st.container(border=True):
            sc1, sc2, sc3 = st.columns([1.5, 1.5, 1])
            with sc1:
                st.info(f"☑️ {len(selected_ids)}건 선택됨")
            with sc2:
                batch_to_sel = st.selectbox("변경할 상태", SETTLEMENT_STATUSES, key="batch_to_sel")
            with sc3:
                st.write("")
                if st.button("선택 항목 일괄 변경", type="primary", use_container_width=True):
                    batch_update_settlement_status(selected_ids, batch_to_sel)
                    for k in list(st.session_state.keys()):
                        if k.startswith("set_chk_"):
                            del st.session_state[k]
                    st.rerun()

    # --- 전체 일괄 변경 (현재 필터 기준) ---
    with st.expander("⚡ 조회 결과 전체 일괄 변경"):
        bc1, bc2 = st.columns([2, 1])
        with bc1:
            batch_to = st.selectbox("변경할 상태", SETTLEMENT_STATUSES, key="batch_to")
        with bc2:
            st.write("")
            if st.button("전체 일괄 변경", type="primary", use_container_width=True):
                ids = filtered["id"].tolist()
                if not ids:
                    st.warning("변경할 항목이 없습니다.")
                else:
                    batch_update_settlement_status(ids, batch_to)
                    st.success(f"✅ 조회된 {len(ids)}건을 '{batch_to}'(으)로 변경했습니다.")
                    st.rerun()

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    total = len(filtered)
    if total == 0:
        st.info("🔍 조건에 맞는 정산 내역이 없습니다.")
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

    # --- 데이터 뷰 카드 레이아웃 ---
    for _, row in page_df.iterrows():
        row_id = row["id"]

        with st.container(border=True):
            chk_col, info_col, action_col = st.columns([0.3, 3.7, 1])
            with chk_col:
                st.checkbox("선택", key=f"set_chk_{row_id}", label_visibility="collapsed")
            
            with info_col:
                st.markdown(f"{_status_badge(row.get('settlement_status', ''))} &nbsp;&nbsp; `<정산일:{row.get('settlement_date', '미입력')}>`", unsafe_allow_html=True)
                
                try:
                    amt = float(row.get("amount", 0))
                    amt_str = f"{amt:,.0f}원"  # 콤마 렌더링 확정
                except (ValueError, TypeError):
                    amt_str = str(row.get("amount", ""))
                    
                st.markdown(f"#### 🏢 {row.get('vendor', '알수없음')} <span style='color: #4CAF50;'>({amt_str})</span>", unsafe_allow_html=True)
                
                add_infos = []
                ps = row.get("period_start", "")
                pe = row.get("period_end", "")
                if ps and pe:
                    add_infos.append(f"📆 매출기간: {ps} ~ {pe}")
                if row.get("return_id"):
                    add_infos.append(f"🔗 연계 반품ID: {row['return_id']}")
                if row.get("notes"):
                    add_infos.append(f"📝 메모: {row['notes']}")
                if add_infos:
                    st.caption(" | ".join(add_infos))

            with action_col:
                st.write("")
                current = row.get("settlement_status", SETTLEMENT_STATUSES[0])
                current_idx = SETTLEMENT_STATUSES.index(current) if current in SETTLEMENT_STATUSES else 0
                new_status = st.selectbox(
                    "상태",
                    SETTLEMENT_STATUSES,
                    index=current_idx,
                    key=f"set_sel_{row_id}",
                    label_visibility="collapsed"
                )
                if new_status != current:
                    update_settlement_status(row_id, new_status)
                    st.rerun()

                with st.popover("⚙️ 관리", use_container_width=True):
                    st.caption("데이터 컨트롤")
                    if st.button("🖊️ 세부내용 수정", key=f"set_edit_{row_id}", use_container_width=True):
                        edit_settlement_dialog(row.to_dict())

                    if st.button("🗑️ 영구 삭제", key=f"set_del_{row_id}", use_container_width=True):
                        delete_settlement(row_id)
                        st.rerun()
