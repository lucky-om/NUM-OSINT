# =============================================================================
# NUM-OSINT v3.0 - config.py
# Developed by Lucky
# Telegram: https://t.me/+vSQiUVbXYc5hYjBl | Website: num-osint.luckyverse.tech
# =============================================================================

import os
import base64
import hashlib
import sys

def _load_env():
    """Load .env file if present (optional on Termux/Linux)."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip("'\""))

_load_env()

# SHA-256 Salted & Encrypted Payload (Cannot be decoded via simple base64)
_ENC_PAYLOAD = "vwzpy3mhkFuF4l9tSz9Vqn6rQpe3M73zmDoLxIFAkqlY+U2yxEu3pD9RKpi5V+9QxA3rO87NQpUly/ftJrDsGKpWKBYoPg0Szi+CfA=="
_SALT = b"NUM_OSINT_LUCKY_V2_SALT_2026"

def _decode_api():
    """
    Resolve API URL:
    1. Encrypted payload (primary — always available)
    2. .env / environment variable override (optional, for dev only)
    """
    # Try encrypted payload first (primary source — always secure)
    try:
        key = hashlib.sha256(_SALT).digest()
        raw_bytes = base64.b64decode(_ENC_PAYLOAD)
        dec_bytes = bytearray()
        for i, b in enumerate(raw_bytes):
            k_byte = key[i % len(key)]
            dec_bytes.append(b ^ k_byte ^ ((i * 37 + 13) & 0xFF))
        decoded = dec_bytes.decode("utf-8")
        # Validate that it looks like a real URL
        if decoded.startswith("http://") or decoded.startswith("https://"):
            # Allow .env override only if explicitly set (for development)
            env_url = os.getenv("API_URL", "").strip()
            if env_url and (env_url.startswith("http://") or env_url.startswith("https://")):
                return env_url
            return decoded
    except Exception as e:
        print(f"\033[31m  ⚠  API decryption failed: {e}\033[0m", file=sys.stderr)

    # Fallback: check environment variable
    env_url = os.getenv("API_URL", "").strip()
    if env_url:
        return env_url

    return ""

API_URL = _decode_api()

_rh = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Termux) Gecko/117.0 Firefox/117.0",
    "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://num-osint.luckyverse.tech/",
    "Connection": "keep-alive"
}

TOOL_VERSION = "v3.0"
TOOL_NAME    = "NUM-OSINT"
AUTHOR       = "Lucky"
TELEGRAM     = "https://t.me/+vSQiUVbXYc5hYjBl"
WEBSITE      = "num-osint.luckyverse.tech"

