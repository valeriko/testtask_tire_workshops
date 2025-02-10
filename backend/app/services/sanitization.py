import html
from typing import Dict, Any


def sanitize_input(input):
    """
    Sanitize input strings to prevent XSS and injection attacks.
    """
    if not isinstance(input, str):
        return input

    sanitized = html.escape(input).replace("&amp;", "&")
    return sanitized


def sanitize_data(data: dict):
    """
    Sanitize all relevant fields in data.
    """
    return {
        key: sanitize_input(value) if key != 'booking_body' and value is not None and isinstance(value, str) else value
        for key, value in data.items()
    }
