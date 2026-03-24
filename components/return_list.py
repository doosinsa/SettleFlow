import math
import streamlit as st

from config.settings import ITEMS_PER_PAGE, LOGISTICS_STATUSES, STATUS_COLORS, REASON_OPTIONS
from services.clipboard import build_kakao_message
from services.sheets_client import get_all_returns, update_return_status, update_return_full, delete_return

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

@st.dialog("🖊️ 반품/교환 정보 수정")
def edit_dialog(row_dict: dict):
    with st.form(f"edit_form_{row_dict['id']}", border=False):
        st.caption("고객 정보 및 주문 정보를 수정합니다.")
        c1, c2 = st.columns(2)
        with c1:
            prod = st.text_input("상품명", value=row_dict.get("product_name", ""))
            cust = st.text_input("고객명", value=row_dict.get("customer_name", ""))
            order_dt = st.text_input("주문날짜", value=row_dict.get("order_date", ""))
            cont = st.text_input("연락처", value=row_dict.get("contact", ""))
        with c2:
            ven = st.text_input("거래처", value=row_dict.get("vendor", ""))
            
            # 사유 콤보박스 기본 인덱스 처리
            reason_val = row_dict.get("reason", "")
            r_idx = REASON_OPTIONS.index(reason_val) if reason_val in REASON_OPTIONS else 0
            res = st.selectbox("사유", REASON_OPTIONS, index=r_idx)
            
            trk = st.text_input("송장번호", value=row_dict.get("tracking_number", ""))
            nt = st.text_input("비고", value=row_dict.get("notes", ""))
            
        btn = st.form_submit_button("✅ 변경하기", type="primary", use_container_width=True)
        if btn:
            new_data = dict(row_dict)
            new_data.update({
                "product_name": prod, "customer_name": cust, "order_date": order_dt,
                "contact": cont, "vendor": ven, "reason": res,
                "tracking_number": trk, "notes": nt
            })
            update_return_full(row_dict["id"], new_data)
            st.rerun()

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

    # --- 카드(Card) 레이아웃 리스트 ---
    for _, row in page_df.iterrows():
        row_id = row["id"]
        with st.container(border=True):
            info_col, action_col = st.columns([4, 1])
            
            with info_col:
                # 상태 배지 + 접수/주문 날짜 표출
                st.markdown(f"{_status_badge(row.get('logistics_status', ''))} &nbsp;&nbsp; `<접수: {row.get('date', '')} | 주문: {row.get('order_date', '미입력')}>`", unsafe_allow_html=True)
                
                st.markdown(f"#### {row.get('product_name', '상품명 없음')} <span style='font-size: 0.9em; font-weight: 400; color: gray;'>/ {row.get('customer_name', '고객')} ({row.get('contact', '연락처없음')})</span>", unsafe_allow_html=True)
                
                st.caption(f"**🏢 {row.get('vendor', '')}** | 🚚 {row.get('tracking_number', '미입력')} | 💰 택비: {row.get('delivery_fee', '')} | 🏷️ {row.get('reason', '')}")
                if row.get("notes"):
                    st.caption(f"📝 {row['notes']}")

            with action_col:
                st.write("") 
                # 카톡 복사
                with st.popover("💬 카톡양식", use_container_width=True):
                    msg = build_kakao_message(row.to_dict())
                    st.code(msg, language="text")
                    
                # 관리 메뉴 (상태변경 & 추가 액션)
                with st.popover("⚙️ 관리", use_container_width=True):
                    st.caption("상태 변경")
                    current = row.get("logistics_status", LOGISTICS_STATUSES[0])
                    current_idx = LOGISTICS_STATUSES.index(current) if current in LOGISTICS_STATUSES else 0
                    new_status = st.selectbox(
                        "상태지정",
                        LOGISTICS_STATUSES,
                        index=current_idx,
                        key=f"sel_{row_id}",
                        label_visibility="collapsed"
                    )
                    if st.button("상태 저장", key=f"confirm_{row_id}", type="primary", use_container_width=True):
                        if new_status != current:
                            update_return_status(row_id, new_status)
                            st.rerun()
                            
                    st.divider()
                    
                    st.caption("데이터 권한")
                    if st.button("🖊️ 세부내용 수정", key=f"edit_{row_id}", use_container_width=True):
                        edit_dialog(row.to_dict())
                        
                    if st.button("🗑️ 영구 삭제", key=f"del_{row_id}", use_container_width=True):
                        delete_return(row_id)
                        st.rerun()

