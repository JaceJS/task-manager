from app.core.exceptions import ValidationFailed

MAX_NAME_LENGTH = 255


def clean_required_text(value: str | None, field: str) -> str:
    text = (value or "").strip()
    if not text:
        raise ValidationFailed(f"{field} must not be empty")
    if len(text) > MAX_NAME_LENGTH:
        raise ValidationFailed(f"{field} must be at most {MAX_NAME_LENGTH} characters")
    return text


def clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None
