# =============================================================================
# NUM-OSINT - config.py
# Developed by Lucky
# Telegram: @universeluckyy | Website: luckyverse.tech
# =============================================================================

import base64

_P = b"aHR0cHM6Ly9leHBsb2l0c2luZGlhLnNpdGUvb3NpbnQvYXBpLnBocD9rZXk9b2JpdG8mdHlwZT1udW1iZXImbnVtPQ=="
_S = b"aHR0cHM6Ly9icm9ueC13ZWItYXBpLm9ucmVuZGVyLmNvbS9hcGkva2V5LWJyb254L251bWJlcj9rZXk9ZGVtby0zMC1kYXlzJm51bT0="

def _rc1() -> str:
    return base64.b64decode(_P).decode("utf-8")

def _rc2() -> str:
    return base64.b64decode(_S).decode("utf-8")

_rh = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Termux) Gecko/117.0 Firefox/117.0",
    "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://luckyverse.tech/",
    "Connection": "keep-alive"
}

_zx = "b988b5837c24ad1987f31266e0246b0fdaaf7948714cfa2a9f7757c52977ff14"
_za = "37b10217c5e7b58a0d017d144edf2a40d31d28965669e5caaa9cd664b8b60c5a"

TOOL_VERSION = "v1.0"
TOOL_NAME    = "NUM-OSINT"
AUTHOR       = "Lucky"
TELEGRAM     = "@universeluckyy"
WEBSITE      = "luckyverse.tech"
