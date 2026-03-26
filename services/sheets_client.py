import uuid
from datetime import datetime

import pandas as pd
import streamlit as st
from supabase import create_client

RETURNS_COLUMNS = [
    "id", "date", "order_date", "product_name", "customer_name", "contact",
    "reason", "vendor", "tracking_number", "delivery_fee",
    "notes", "logistics_status", "created_at", "updated_at",
]

SETTLEMENTS_COLUMNS = [
    "id", "vendor", "amount", "settlement_status",
    "return_id", "notes", "created_at", "updated_at",
]


@st.cache_resource
def _get_client():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


# ── 반품/교환 ───────────────────────────────────────────

@st.cache_data(ttl=30)
def get_all_returns() -> pd.DataFrame:
    result = _get_client().table("returns").select("*").order("created_at", desc=True).execute()
    if not result.data:
        return pd.DataFrame(columns=RETURNS_COLUMNS)
    return pd.DataFrame(result.data)


def append_return(row_dict: dict) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    row = {
        "id": str(uuid.uuid4()),
        "logistics_status": "신청",
        "created_at": now,
        "updated_at": now,
        "order_date": row_dict.get("order_date", ""), # 주문날짜 옵셔널 매핑 처리
        **row_dict,
    }
    _get_client().table("returns").insert(row).execute()
    st.cache_data.clear()


def update_return_status(row_id: str, new_status: str) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    _get_client().table("returns").update({
        "logistics_status": new_status,
        "updated_at": now,
    }).eq("id", row_id).execute()
    st.cache_data.clear()

def update_return_full(row_id: str, new_data: dict) -> None:
    """반품 데이터 전체를 업데이트합니다."""
    now = datetime.now().isoformat(timespec="seconds")
    update_payload = dict(new_data)
    update_payload["updated_at"] = now
    
    # ID는 변경 불가하므로 payload에 있다면 제거
    if "id" in update_payload:
        del update_payload["id"]
        
    _get_client().table("returns").update(update_payload).eq("id", row_id).execute()
    st.cache_data.clear()

def delete_return(row_id: str) -> None:
    """특정 반품 데이터를 영구 삭제합니다."""
    _get_client().table("returns").delete().eq("id", row_id).execute()
    st.cache_data.clear()


# ── 정산 ────────────────────────────────────────────────

@st.cache_data(ttl=30)
def get_all_settlements() -> pd.DataFrame:
    result = _get_client().table("settlements").select("*").order("created_at", desc=True).execute()
    if not result.data:
        return pd.DataFrame(columns=SETTLEMENTS_COLUMNS)
    return pd.DataFrame(result.data)


def append_settlement(row_dict: dict) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    row = {
        "id": str(uuid.uuid4()),
        "settlement_status": "확인전",
        "created_at": now,
        "updated_at": now,
        **row_dict,
    }
    _get_client().table("settlements").insert(row).execute()
    st.cache_data.clear()


def update_settlement_status(row_id: str, new_status: str) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    _get_client().table("settlements").update({
        "settlement_status": new_status,
        "updated_at": now,
    }).eq("id", row_id).execute()
    st.cache_data.clear()

def update_settlement_full(row_id: str, new_data: dict) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    update_payload = dict(new_data)
    update_payload["updated_at"] = now
    if "id" in update_payload:
        del update_payload["id"]
    _get_client().table("settlements").update(update_payload).eq("id", row_id).execute()
    st.cache_data.clear()

def delete_settlement(row_id: str) -> None:
    _get_client().table("settlements").delete().eq("id", row_id).execute()
    st.cache_data.clear()


# ── 거래처 ───────────────────────────────────────────────

def get_all_vendors() -> list[str]:
    if "vendors" not in st.session_state:
        result = _get_client().table("vendors").select("name").order("name").execute()
        st.session_state.vendors = [r["name"] for r in result.data] if result.data else []
    return st.session_state.vendors


def append_vendor(name: str) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    _get_client().table("vendors").insert({
        "id": str(uuid.uuid4()),
        "name": name,
        "created_at": now,
    }).execute()
    vendors = list(st.session_state.get("vendors", []))
    vendors.append(name)
    st.session_state.vendors = sorted(vendors)


def update_vendor(old_name: str, new_name: str) -> None:
    _get_client().table("vendors").update({"name": new_name}).eq("name", old_name).execute()
    vendors = [new_name if v == old_name else v for v in st.session_state.get("vendors", [])]
    st.session_state.vendors = sorted(vendors)


def delete_vendor(name: str) -> None:
    _get_client().table("vendors").delete().eq("name", name).execute()
    st.session_state.vendors = [v for v in st.session_state.get("vendors", []) if v != name]
