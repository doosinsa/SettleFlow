from config.settings import KAKAO_FORMAT

def build_kakao_message(row: dict) -> str:
    """
    카카오톡 복사용 포맷 문자열을 조합하여 반환합니다.
    실제 클립보드 복사는 pyperclip을 쓰지 않고, 
    Streamlit 앱 프론트(st.code) 자체의 복사 위젯을 이용합니다.
    """
    return KAKAO_FORMAT.format(
        vendor=row.get("vendor", ""),
        order_date=row.get("order_date", "날짜없음"),
        contact=row.get("contact", "연락처없음"),
        customer_name=row.get("customer_name", ""),
        product_name=row.get("product_name", ""),
        reason=row.get("reason", ""),
        tracking_number=row.get("tracking_number", ""),
    )
