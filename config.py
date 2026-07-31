# =============================================================================
# NUM-OSINT - config.py
# Developed by Lucky
# Telegram: https://t.me/+vSQiUVbXYc5hYjBl | Website: luckyverse.tech
# =============================================================================

import os

def _load_env():
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

API_URL = os.getenv("API_URL", "")


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
TELEGRAM     = "https://t.me/+vSQiUVbXYc5hYjBl"
WEBSITE      = "luckyverse.tech"
