import uuid
from datetime import datetime

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

from config.settings import (
    CREDENTIALS_FILE,
    RETURNS_SHEET,
    SETTLEMENTS_SHEET,
    VENDORS_SHEET,
    SPREADSHEET_NAME,
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

RETURNS_COLUMNS = [
    "id", "date", "product_name", "customer_name", "contact",
    "reason", "vendor", "tracking_number", "delivery_fee",
    "notes", "logistics_status", "created_at", "updated_at",
]

SETTLEMENTS_COLUMNS = [
    "id", "vendor", "amount", "settlement_status",
    "return_id", "notes", "created_at", "updated_at",
]

VENDORS_COLUMNS = ["id", "name", "created_at"]


@st.cache_resource
def get_client() -> gspread.Client:
    import os
    if not os.path.exists(CREDENTIALS_FILE):
        st.error(
            f"**`{CREDENTIALS_FILE}` 파일을 찾을 수 없습니다.**\n\n"
            "Google Cloud Console에서 서비스 계정 JSON 키를 다운로드한 후 "
            f"`{os.path.abspath(CREDENTIALS_FILE)}` 경로에 저장하세요.\n\n"
            "자세한 설정 방법은 README 또는 PRD의 Google Sheets 셋업 순서를 참고하세요."
        )
        st.stop()
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return gspread.authorize(creds)


def _get_spreadsheet():
    return get_client().open(SPREADSHEET_NAME)


@st.cache_data(ttl=30)
def get_all_returns() -> pd.DataFrame:
    sheet = _get_spreadsheet().worksheet(RETURNS_SHEET)
    records = sheet.get_all_records()
    if not records:
        return pd.DataFrame(columns=RETURNS_COLUMNS)
    return pd.DataFrame(records)


@st.cache_data(ttl=30)
def get_all_settlements() -> pd.DataFrame:
    sheet = _get_spreadsheet().worksheet(SETTLEMENTS_SHEET)
    records = sheet.get_all_records()
    if not records:
        return pd.DataFrame(columns=SETTLEMENTS_COLUMNS)
    return pd.DataFrame(records)


def append_return(row_dict: dict) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    row = {
        "id": str(uuid.uuid4()),
        "logistics_status": "신청",
        "created_at": now,
        "updated_at": now,
        **row_dict,
    }
    sheet = _get_spreadsheet().worksheet(RETURNS_SHEET)
    sheet.append_row([row.get(col, "") for col in RETURNS_COLUMNS])
    st.cache_data.clear()


def update_return_status(row_id: str, new_status: str) -> None:
    sheet = _get_spreadsheet().worksheet(RETURNS_SHEET)
    row_num = _find_row_by_id(sheet, row_id)
    now = datetime.now().isoformat(timespec="seconds")
    status_col = RETURNS_COLUMNS.index("logistics_status") + 1
    updated_col = RETURNS_COLUMNS.index("updated_at") + 1
    sheet.update_cell(row_num, status_col, new_status)
    sheet.update_cell(row_num, updated_col, now)
    st.cache_data.clear()


def append_settlement(row_dict: dict) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    row = {
        "id": str(uuid.uuid4()),
        "settlement_status": "확인전",
        "created_at": now,
        "updated_at": now,
        **row_dict,
    }
    sheet = _get_spreadsheet().worksheet(SETTLEMENTS_SHEET)
    sheet.append_row([row.get(col, "") for col in SETTLEMENTS_COLUMNS])
    st.cache_data.clear()


def update_settlement_status(row_id: str, new_status: str) -> None:
    sheet = _get_spreadsheet().worksheet(SETTLEMENTS_SHEET)
    row_num = _find_row_by_id(sheet, row_id)
    now = datetime.now().isoformat(timespec="seconds")
    status_col = SETTLEMENTS_COLUMNS.index("settlement_status") + 1
    updated_col = SETTLEMENTS_COLUMNS.index("updated_at") + 1
    sheet.update_cell(row_num, status_col, new_status)
    sheet.update_cell(row_num, updated_col, now)
    st.cache_data.clear()


@st.cache_data(ttl=30)
def get_all_vendors() -> list[str]:
    sheet = _get_spreadsheet().worksheet(VENDORS_SHEET)
    records = sheet.get_all_records()
    if not records:
        return []
    return sorted([r["name"] for r in records if r.get("name")])


def append_vendor(name: str) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    sheet = _get_spreadsheet().worksheet(VENDORS_SHEET)
    sheet.append_row([str(uuid.uuid4()), name, now])
    st.cache_data.clear()


def delete_vendor(name: str) -> None:
    sheet = _get_spreadsheet().worksheet(VENDORS_SHEET)
    names = sheet.col_values(2)  # Column B = name
    try:
        idx = names.index(name)
        sheet.delete_rows(idx + 1)  # 1-based
        st.cache_data.clear()
    except ValueError:
        raise ValueError(f"거래처 '{name}'을(를) 찾을 수 없습니다.")


def _find_row_by_id(sheet: gspread.Worksheet, row_id: str) -> int:
    ids = sheet.col_values(1)  # Column A (1-indexed)
    try:
        # ids[0] is header "id", data starts at index 1 → row 2
        idx = ids.index(row_id)
        return idx + 1  # 1-based row number
    except ValueError:
        raise ValueError(f"ID '{row_id}' not found in sheet '{sheet.title}'")
