"""Telegram Mini App initData verification helpers."""
from __future__ import annotations

import hashlib
import hmac
import urllib.parse
from typing import Dict, List, Tuple


def _secret_key(bot_token: str) -> bytes:
    """Derive secret key for initData verification."""
    return hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()


def _parse_init_data(init_data: str) -> List[Tuple[str, str]]:
    """Parse query-string style initData keeping blank values."""
    return urllib.parse.parse_qsl(init_data, keep_blank_values=True)


def check_init_data(init_data: str, bot_token: str) -> bool:
    """Validate initData signature according to Telegram spec."""
    parsed = _parse_init_data(init_data)
    data = sorted((k, v) for k, v in parsed if k != "hash")
    check_string = "\n".join(f"{k}={v}" for k, v in data)
    secret = _secret_key(bot_token)
    calculated = hmac.new(secret, check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    supplied = dict(parsed).get("hash", "")
    return hmac.compare_digest(calculated, supplied)


def extract_user(init_data: str) -> Dict[str, str]:
    """Return raw initData fields as a simple dictionary."""
    parsed = dict(_parse_init_data(init_data))
    return parsed
