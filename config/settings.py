SPREADSHEET_NAME = "SettleFlow"
RETURNS_SHEET = "returns"
SETTLEMENTS_SHEET = "settlements"
VENDORS_SHEET = "vendors"
CREDENTIALS_FILE = "credentials.json"

LOGISTICS_STATUSES = ["신청", "수거신청", "입고완료", "환불완료"]
SETTLEMENT_STATUSES = ["확인전", "확인완료", "세금계산서 발행 완료", "입금완료"]
REASON_OPTIONS = ["단순변심", "불량", "오배송", "기타"]
DELIVERY_FEE_OPTIONS = ["없음", "부담"]

STATUS_COLORS = {
    "신청":                    "#6B7280",  # Gray  - 대기
    "수거신청":                "#3B82F6",  # Blue  - 진행중
    "입고완료":                "#F97316",  # Orange - 확인필요
    "환불완료":                "#EF4444",  # Red   - 완료
    "확인전":                  "#6B7280",
    "확인완료":                "#3B82F6",
    "세금계산서 발행 완료":    "#F97316",
    "입금완료":                "#EF4444",
}

ITEMS_PER_PAGE = 15

KAKAO_FORMAT = "[{vendor}] 반품요청: {customer_name}/{product_name}/{reason}/송장:{tracking_number}"
