"""Validate guide provenance URLs without trusting arbitrary prefix matches."""
from urllib.parse import urlsplit

APPROVED_HOSTS = frozenset({
    "powerpyx.com", "www.powerpyx.com",
    "insider-gaming.com", "www.insider-gaming.com",
})


def validate_guide_source(value: object) -> bool:
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    if any(ord(char) < 33 or ord(char) == 127 for char in value) or "\\" in value:
        return False
    try:
        parsed = urlsplit(value)
        return (
            parsed.scheme == "https"
            and parsed.hostname in APPROVED_HOSTS
            and parsed.username is None
            and parsed.password is None
            and parsed.port in (None, 443)
            and parsed.path.startswith("/")
            and len(parsed.path) > 1
            and not parsed.fragment
        )
    except (ValueError, TypeError):
        return False
