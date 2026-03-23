import pyperclip

from config.settings import KAKAO_FORMAT


def build_kakao_message(row: dict) -> str:
    return KAKAO_FORMAT.format(
        vendor=row.get("vendor", ""),
        customer_name=row.get("customer_name", ""),
        product_name=row.get("product_name", ""),
        reason=row.get("reason", ""),
        tracking_number=row.get("tracking_number", ""),
    )


def copy_to_clipboard(text: str) -> bool:
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False
