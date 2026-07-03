#!/usr/bin/env python3
# =============================================================================
#  NUM-OSINT  |  v1.0
#  Developed by Lucky
#  Telegram  : @universeluckyy
#  Website   : luckyverse.tech
# =============================================================================
#
#  DISCLAIMER:
#  This tool is intended for EDUCATIONAL PURPOSES ONLY.
#  The developer does NOT own, collect, or store any of the data retrieved
#  by this tool.  The data queried through this tool has reportedly been
#  leaked and is already circulating on the dark-web.  The developer is
#  NOT responsible for any misuse, damage, or legal consequences arising
#  from the use of this tool.  USE AT YOUR OWN RISK.
#
# =============================================================================

import requests
import json
import os
import re
import sys
import shutil
import time
import random
import hashlib
from colorama import init, Fore, Style

from config import (
    _rc1,
    _rc2,
    _rh,
    _zx,
    _za,
    TOOL_VERSION,
    TOOL_NAME,
    AUTHOR,
    TELEGRAM,
    WEBSITE,
)


# Initialise colorama (auto-reset after each print)
init(autoreset=True)

# ─────────────────────────────────────────────────────────────────────────────
#  ANSI 256-COLOUR HELPERS
# ─────────────────────────────────────────────────────────────────────────────

_ANSI_ESCAPE = re.compile(r'\033\[[0-9;]*m')

def _c(n: int) -> str:
    """ANSI 256-colour foreground escape."""
    return f"\033[38;5;{n}m"

def _b() -> str:
    """ANSI bold on."""
    return "\033[1m"

def _r() -> str:
    """ANSI full reset."""
    return "\033[0m"

def _tw() -> int:
    """Usable terminal width (capped 60–108)."""
    try:
        return max(60, min(shutil.get_terminal_size((82, 24)).columns - 4, 108))
    except Exception:
        return 76

# 256-colour gradient palettes
_G_GREEN  = [22, 28, 34, 40, 46, 82, 118]
_G_CYAN   = [23, 30, 37, 44, 51, 87, 123]
_G_BLUE   = [17, 19, 21, 27, 33, 39, 75]
_G_RED    = [52, 88, 124, 160, 196, 203]
_G_YELLOW = [136, 142, 148, 154, 184, 220, 226]
_G_MAGENTA= [53, 90, 127, 164, 201, 207]


# ─────────────────────────────────────────────────────────────────────────────
#  ANIMATION HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def type_effect(text: str, delay: float = 0.016) -> None:
    """Typewriter effect: reveal text character by character."""
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()


def swipe_effect(text: str, delay: float = 0.005) -> None:
    """Swipe-in reveal: each line streams in character by character."""
    for line in text.splitlines():
        for ch in line:
            print(ch, end='', flush=True)
            time.sleep(delay)
        print()


def draw_separator(char: str = "─", width: int = 0, color: str = "") -> None:
    """Horizontal separator. Defaults to terminal width and cyan colour."""
    w = width or _tw()
    c = color or _c(37)
    print(f"  {c}{char * w}{_r()}")


def gradient_separator(width: int = 0, palette: list = None) -> None:
    """A separator bar that transitions through a 256-colour gradient."""
    w   = width or _tw()
    pal = palette or _G_GREEN
    seg = max(1, w // len(pal))
    line = ""
    _hbar = "\u2501"
    for i, col in enumerate(pal):
        n = seg if i < len(pal) - 1 else max(1, w - seg * i)
        line += f"{_c(col)}{_hbar * n}"
    print(f"  {line}{_r()}")


def loading_bar(label: str = "Loading", width: int = 36, delay: float = 0.032) -> None:
    """Gradient loading bar: fills with colour-shifting blocks."""
    pal = _G_GREEN + list(reversed(_G_GREEN))
    print(f"\n  {_c(51)}{_b()}{label}{_r()}  ", end="", flush=True)
    for i in range(width):
        col = pal[i % len(pal)]
        print(f"{_c(col)}\u2588{_r()}", end="", flush=True)
        time.sleep(delay)
    print(f"  {_c(46)}{_b()}\u2714{_r()}\n")


def spinner(label: str = "Fetching", duration: float = 1.8) -> None:
    """Smooth orbital spinner with 256-colour cycling."""
    dot_frames = ["\u280b","\u2819","\u2839","\u2838","\u283c","\u2834","\u2826","\u2827","\u2807","\u280f"]
    orb_frames = ["\u25dc","\u25dd","\u25de","\u25df"]
    pal      = _G_CYAN
    end_time = time.time() + duration
    idx      = 0
    while time.time() < end_time:
        col = pal[idx % len(pal)]
        df  = dot_frames[idx % len(dot_frames)]
        of  = orb_frames[idx % len(orb_frames)]
        print(
            f"\r  {_c(col)}{_b()}{of} {df}  {_r()}{_c(226)}{label}{_c(col)}...{_r()}",
            end="", flush=True
        )
        time.sleep(0.09)
        idx += 1
    print("\r" + " " * 60 + "\r", end="", flush=True)


def glitch_effect(text: str, iterations: int = 6) -> None:
    """Corrupt-then-reveal glitch animation."""
    gc = "!@#$%^&*<>?/|\\~\u2591\u2592\u2593"
    for i in range(iterations):
        ratio  = 0.45 - (i / iterations) * 0.35   # less glitch each pass
        noise  = "".join(
            random.choice(gc) if random.random() < ratio else ch
            for ch in text
        )
        col = random.choice(_G_RED[-3:])
        print(f"\r{_c(col)}{noise}{_r()}", end="", flush=True)
        time.sleep(0.04)
    print(f"\r{_c(46)}{_b()}{text}{_r()}" + " " * 6)


def print_colored(text: str, delay: float = 0.004) -> None:
    """Print each line cycling through a 256-colour gradient."""
    pal = _G_CYAN + _G_GREEN + _G_MAGENTA
    for i, line in enumerate(text.splitlines()):
        col = pal[i % len(pal)]
        for ch in line:
            print(f"{_c(col)}{ch}", end="", flush=True)
            time.sleep(delay)
        print(_r())


def matrix_rain(duration: float = 0.75) -> None:
    """Column-based matrix rain: bright head drops with dim trailing tails."""
    w       = _tw()
    cols    = w // 2
    # each column tracks how deep into its tail sequence it is
    depths  = [random.randint(0, 10) for _ in range(cols)]
    speeds  = [random.choice([1, 1, 2]) for  _ in range(cols)]
    chars   = "01\uff86\uff83\uff66\uff71\uff73\uff74\uff75\uff76\uff77@#$%&ABCXYZ"
    end_t   = time.time() + duration
    while time.time() < end_t:
        line = ""
        for i in range(cols):
            d = depths[i]
            if d == 0:
                line += f"{_c(255)}{_b()}{random.choice(chars)} {_r()}"   # bright head
            elif d < 3:
                line += f"{_c(46)}{random.choice(chars)} {_r()}"           # bright tail
            elif d < 6:
                line += f"{_c(34)}{random.choice(chars)} {_r()}"           # mid tail
            elif d < 9:
                line += f"{_c(22)}{random.choice(chars)} {_r()}"           # dim tail
            else:
                line += "  "                                                 # empty
            depths[i] = (depths[i] + speeds[i]) % 13
        print(f"  {line}")
        time.sleep(0.055)
    print(_r(), end="")


def boot_sequence(role: str = "user") -> None:
    """Staggered 256-colour boot log after successful key verification."""
    def tag(label: str, col: int) -> str:
        return f"{_c(col)}{_b()}[ {label:<4} ]{_r()}"

    steps = [
        (tag("SYS",  39),   "Initialising NUM-OSINT core engine..."),
        (tag("OK",   46),   "Cryptographic security layer  \u2714  LOADED"),
        (tag("OK",   46),   "Primary + fallback API routing \u2714  READY"),
        (tag("INFO", 226),  "Null-value filter              \u2714  ACTIVE"),
        (tag("INFO", 226),  "Record deduplication engine    \u2714  ONLINE"),
    ]
    if role == "admin":
        steps += [
            (tag("ADM", 201), "Rate limiter    *** DISABLED (admin mode) ***"),
            (tag("ADM", 201), "Full privilege access         \u2714  GRANTED"),
        ]
    else:
        steps.append((tag("INFO", 226), "Rate limiter: 15s cooldown between lookups"))
    steps.append((tag("BOOT", 46), "System READY  \u2500  Welcome to NUM-OSINT!"))

    print()
    gradient_separator(palette=_G_CYAN)
    for t, msg in steps:
        time.sleep(random.uniform(0.07, 0.15))
        print(f"  {t}  {_c(255)}{msg}{_r()}")
    gradient_separator(palette=_G_GREEN)
    print()


def scan_line(number: str) -> None:
    """Double-sweep gradient scanner bar before each lookup."""
    w     = _tw()
    label = f" \u25c8 SCANNING TARGET: {number} \u25c8 "
    pad   = max(0, (w - len(label)) // 2)

    print()
    char_filled = '\u2593'
    char_trail = '\u2591'
    for sweep in range(2):          # two passes: L→R then R→L
        for pos in range(0, w + 1, 2):
            p = pos if sweep == 0 else w - pos
            p = max(0, min(p, w - 2))
            filled = f"{_c(28)}{char_filled * p}"
            head   = f"{_c(46)}{_b()}\u2588\u2588{_r()}"
            trail  = f"{_c(22)}{char_trail * (w - p - 2)}{_r()}"
            print(f"\r  [{filled}{head}{trail}]", end="", flush=True)
            time.sleep(0.010)

    char_double_dash = '\u2550'
    top_bar = f"{_c(46)}{char_double_dash * (w + 2)}{_r()}"
    hdr     = f"{' ' * pad}{_c(51)}{_b()}{label}{_r()}"
    bot_bar = f"{_c(34)}{char_double_dash * (w + 2)}{_r()}"
    print(f"\r  {top_bar}")
    print(f"  {hdr}")
    print(f"  {bot_bar}")
    print()


def neon_box(lines: list, palette: list = None, width: int = 0) -> None:
    """Double-line neon box rendered with 256-colour borders."""
    pal = palette or _G_CYAN
    w   = width or min(_tw(), 66)
    bc  = _c(pal[-1]) + _b()   # border colour
    char_double_dash = '\u2550'
    print(f"  {bc}\u2554{char_double_dash * w}\u2557{_r()}")
    for line in lines:
        visible = _ANSI_ESCAPE.sub('', line)
        pad     = max(0, w - len(visible) - 2)
        print(f"  {bc}\u2551{_r()} {line}{' ' * pad} {bc}\u2551{_r()}")
    print(f"  {bc}\u255a{char_double_dash * w}\u255d{_r()}")


def success_flash(count: int) -> None:
    """Flashing success banner when results are found."""
    msg = f"  \u2726  {count} RESULT(S) FOUND  \u2726"
    bar = "\u2588" * (len(msg) + 4)
    for _ in range(3):
        print(f"\r  {_c(46)}{_b()}{bar}  {msg}  {bar}{_r()}", end="", flush=True)
        time.sleep(0.11)
        print(f"\r{' ' * (len(msg) + len(bar) * 2 + 8)}", end="", flush=True)
        time.sleep(0.07)
    print(f"\r  {_c(46)}{_b()}{bar}  {msg}  {bar}{_r()}")
    print()


def pulse_text(text: str, palette: list = None, pulses: int = 3) -> None:
    """Colour-cycling pulse: text flickers through gradient shades."""
    pal = palette or _G_CYAN
    for i in range(pulses * len(pal)):
        col = pal[i % len(pal)]
        print(f"\r{_c(col)}{_b()}{text}{_r()}", end="", flush=True)
        time.sleep(0.06)
    print(f"\r{_c(pal[-1])}{_b()}{text}{_r()}")



# ─────────────────────────────────────────────────────────────────────────────
#  BANNER
# ─────────────────────────────────────────────────────────────────────────────

def show_banner() -> None:
    """Display animated banner: matrix rain \u2192 gradient ASCII art \u2192 info bar."""
    os.system("cls" if os.name == "nt" else "clear")
    matrix_rain(duration=0.6)
    os.system("cls" if os.name == "nt" else "clear")

    # Banner rows — each printed with a 256-colour gradient (dark\u2192bright green)
    rows = [
        "  \u2588\u2588\u2557  \u2588\u2588\u2557\u2588\u2588\u2557   \u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2557        \u2588\u2588\u2588\u2588\u2588\u2588\u2557  \u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2551\u2588\u2588\u2588\u2557  \u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557",
        "  \u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2550\u2550\u255d       \u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2554\u2550\u2550\u2550\u2550\u255d\u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2550\u2550\u255d",
        "  \u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2557         \u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2557  \u2588\u2588\u2551\u2588\u2588\u2554\u2588\u2588\u2557\u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2557  ",
        "  \u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2551   \u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u255d         \u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u255d  \u2588\u2588\u2551\u2588\u2588\u2551\u255a\u2588\u2588\u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u255d  ",
        "  \u255a\u2588\u2588\u2588\u2588\u2554\u255d\u255a\u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557       \u255a\u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2551\u2588\u2588\u2551 \u255a\u2588\u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557",
        "   \u255a\u2550\u2550\u2550\u255d  \u255a\u2550\u2550\u2550\u2550\u2550\u255d \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d        \u255a\u2550\u2550\u2550\u2550\u2550\u255d \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d\u255a\u2550\u255d\u255a\u2550\u255d  \u255a\u2550\u2550\u255d\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d",
    ]
    grad = [22, 28, 34, 40, 46, 82]   # dark \u2192 bright green
    for i, row in enumerate(rows):
        col = grad[min(i, len(grad) - 1)]
        print(f"{_c(col)}{_b()}{row}{_r()}")
        time.sleep(0.04)

    w = _tw()
    print()
    gradient_separator(w, _G_YELLOW)
    print(
        f"  {_c(51)}{_b()}  {TOOL_NAME} {_c(255)}{TOOL_VERSION}   "
        f"{_c(201)}{_b()}Developed by {_c(255)}{AUTHOR}  "
        f"{_c(226)}@{_c(255)}{TELEGRAM}  "
        f"{_c(226)}\u25ba {_c(255)}{WEBSITE}{_r()}"
    )
    gradient_separator(w, _G_YELLOW)
    print()
    neon_box(
        [
            f"{_c(196)}{_b()}\u26a0  DISCLAIMER: Educational purposes ONLY. Use at your own risk.",
            f"{_c(203)}   Data is from publicly leaked sources. Developer is NOT responsible.",
        ],
        palette=_G_RED, width=min(w, 64)
    )
    print()


# ─────────────────────────────────────────────────────────────────────────────
#  SECURITY  (SHA-256 key verification)
# ─────────────────────────────────────────────────────────────────────────────

def _hash_key(raw: str) -> str:
    """SHA-256 of raw string — preserves original case."""
    return hashlib.sha256(raw.strip().encode()).hexdigest()


def _hash_key_lower(raw: str) -> str:
    """SHA-256 of lowercased string (for case-insensitive keys)."""
    return hashlib.sha256(raw.strip().lower().encode()).hexdigest()


def verify_security_key() -> str:
    """
    Prompt the user for the security key.
    Returns 'admin' for the admin key, 'user' for the standard key.
    Exits after 3 failed attempts.
    """
    draw_separator()
    type_effect(Fore.YELLOW + "\n  \U0001f510  Security Verification Required", delay=0.02)
    type_effect(Fore.WHITE  + "  Enter the security key to access NUM-OSINT:\n", delay=0.015)

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            key_input = input(f"  {Fore.CYAN}Key [{attempt}/{max_attempts}] \u27a4 {Fore.WHITE}")
        except KeyboardInterrupt:
            print(Fore.RED + "\n\n  \u26d4  Interrupted. Exiting...")
            sys.exit(0)

        # Check admin key first (case-sensitive)
        if _hash_key(key_input) == _za:
            print(Fore.YELLOW + Style.BRIGHT + "\n  \U0001f451  Admin Access Granted — No Rate Limit.\n")
            loading_bar("Initialising Admin Mode", width=30, delay=0.025)
            return "admin"

        # Check standard user key (case-insensitive)
        if _hash_key_lower(key_input) == _zx:
            print(Fore.GREEN + "\n  \u2705  Access Granted!\n")
            loading_bar("Initialising", width=30, delay=0.03)
            return "user"

        remaining = max_attempts - attempt
        if remaining:
            print(Fore.RED + f"  \u274c  Wrong key. {remaining} attempt(s) remaining.\n")
        else:
            print(Fore.RED + "  \U0001f6ab  Too many failed attempts. Exiting.\n")
            sys.exit(1)

    return "user"  # unreachable but satisfies type checker


# ─────────────────────────────────────────────────────────────────────────────
#  API / DATA LAYER
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_from_url(url: str, label: str) -> dict | list | None:
    """
    Make a GET request and return parsed JSON, or None on failure.
    `label` is used only for user-facing status messages.
    """
    try:
        spinner(f"Querying {label}", duration=1.5)
        resp = requests.get(url, headers=_rh, timeout=20)
        raw = resp.text.strip()

        # Direct JSON parse
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract the outermost {...} block
            s, e = raw.find("{"), raw.rfind("}")
            if s != -1 and e > s:
                return json.loads(raw[s : e + 1])
            return None
    except requests.exceptions.ReadTimeout:
        print(Fore.RED + f"  ⏱  {label} timed out.")
        return None
    except requests.exceptions.RequestException:
        print(Fore.RED + f"  📡  {label} unreachable.")
        return None
    except Exception as exc:
        print(Fore.RED + f"  ⚠  {label} error: {exc}")
        return None


def fetch_number_data(number: str) -> dict | list | None:
    """
    Fetch data for `number` using primary API; falls back to secondary if
    the primary fails or returns empty/null results.
    """
    primary_url   = _rc1() + number
    secondary_url = _rc2() + number

    data = _fetch_from_url(primary_url, "Primary API")
    if data:
        return data

    print(Fore.YELLOW + "  ↩  Primary API unavailable. Switching to fallback API...\n")
    data = _fetch_from_url(secondary_url, "Fallback API")
    return data





def _record_fingerprint(record: dict) -> str:
    """Create a dedup key from the most stable fields of a record."""
    parts = [
        str(record.get("num",     record.get("mobile",  ""))).strip(),
        str(record.get("name",    record.get("title",   ""))).strip().upper(),
        str(record.get("aadhar",  "")).strip(),
        str(record.get("address", "")).strip()[:60],
    ]
    return "|".join(parts)


def normalize_response(data) -> list[dict]:
    """
    Handle the real API shapes:
      { "results": [...], "result": [...], "success": true, ... }
    Merges every list found under common result keys, then deduplicates.
    """
    # Keys the APIs use for result arrays (priority order)
    RESULT_KEYS = ("results", "result", "data", "records")

    collected: list[dict] = []

    if isinstance(data, dict):
        for key in RESULT_KEYS:
            val = data.get(key)
            if isinstance(val, list):
                collected.extend(r for r in val if isinstance(r, dict))
            elif isinstance(val, dict) and val:
                collected.append(val)

        # Flat dict with user fields — treat whole response as one record
        if not collected:
            user_keys = {"name", "mobile", "num", "circle", "address", "aadhar"}
            if user_keys.intersection(data.keys()):
                collected.append(data)

    elif isinstance(data, list):
        collected = [r for r in data if isinstance(r, dict)]

    # Deduplicate by fingerprint
    seen: set[str] = set()
    unique: list[dict] = []
    for rec in collected:
        fp = _record_fingerprint(rec)
        if fp not in seen:
            seen.add(fp)
            unique.append(rec)

    return unique


# Fields that are API metadata, not user data — always hidden
_META_KEYS = {
    "success", "status", "total", "page", "count", "message", "error",
}


def clean_address(value: str) -> str:
    """Replace ! separators used by some API responses with readable commas."""
    if isinstance(value, str) and "!" in value:
        parts = [p.strip() for p in value.split("!") if p.strip()]
        value = ", ".join(parts)
    return value.strip()


def filter_nulls(record: dict) -> dict:
    """
    Remove null/empty/junk values and hidden metadata keys.
    Clean address separators.
    """
    skip_values = {None, "", "null", "NULL", "N/A", "n/a", "none", "None", "-", "--"}
    out = {}
    for k, v in record.items():
        if k.lower() in _META_KEYS:
            continue
        val = v.strip() if isinstance(v, str) else v
        if val in skip_values:
            continue
        if k.lower() == "address" and isinstance(val, str):
            val = clean_address(val)
            if not val:
                continue
        out[k] = val
    return out


# ─────────────────────────────────────────────────────────────────────────────
#  OUTPUT / DISPLAY
# ─────────────────────────────────────────────────────────────────────────────

# Friendly display names for common API field keys
FIELD_LABELS = {
    # Name variants
    "name":             "👤  Name",
    "title":            "👤  Name",
    # Mobile / number variants
    "mobile":           "📱  Mobile",
    "num":              "📱  Mobile",
    "number":           "📱  Number",
    # Alternate number
    "alt":              "📞  Alt Number",
    "alternate":        "📞  Alt Number",
    # Father / relative
    "fname":            "👨  Father Name",
    "father":           "👨  Father Name",
    "mother":           "👩  Mother Name",
    "spouse":           "💍  Spouse",
    # Address / location
    "address":          "🏠  Address",
    "city":             "🏙️   City",
    "state":            "🗺️   State",
    "circle":           "🗺️   Circle",
    "pincode":          "📮  Pincode",
    # Identity documents
    "aadhar":           "🆔  Aadhaar",
    "aadhaar":          "🆔  Aadhaar",
    "pan":              "🪪   PAN",
    "voter_id":         "🗳️   Voter ID",
    "dl":               "🚗  DL Number",
    # Contact / social
    "email":            "📧  Email",
    "truecaller_name":  "📲  Truecaller",
    # Network
    "operator":         "📡  Operator",
    "sim":              "📡  SIM Type",
    # Misc
    "dob":              "🎂  Date of Birth",
    "gender":           "⚧   Gender",
    "occupation":       "💼  Occupation",
    "income":           "💰  Income",
    "company":          "🏢  Company",
    "source":           "🔗  Source",
    "leakdb":           "💾  Leak DB",
}


def display_record(idx: int, record: dict) -> None:
    """Pretty-print a single OSINT result record, skipping null values."""
    clean = filter_nulls(record)
    if not clean:
        print(Fore.YELLOW + f"  ⚠  Result {idx}: All fields are empty/null — skipped.\n")
        return

    draw_separator("═", 60, Fore.MAGENTA)
    type_effect(
        Fore.LIGHTRED_EX + Style.BRIGHT + f"  📋  RESULT {idx}",
        delay=0.015,
    )
    draw_separator("─", 60, Fore.CYAN)

    for key, value in clean.items():
        label = FIELD_LABELS.get(key.lower())
        if not label:
            words = key.replace("_", " ").split()
            label = "ℹ️   " + " ".join(word.capitalize() for word in words)
        value_str = (
            json.dumps(value, ensure_ascii=False)
            if isinstance(value, (dict, list))
            else str(value)
        )
        color = random.choice([Fore.LIGHTCYAN_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTGREEN_EX])
        print(f"  {Fore.WHITE}{label:<22} {color}{value_str}")
        time.sleep(0.015)

    draw_separator("─", 60, Fore.CYAN)


def display_branding() -> None:
    """Print the closing branding / credit block."""
    print()
    draw_separator("═", 60, Fore.YELLOW)
    print(
        f"  {Fore.MAGENTA + Style.BRIGHT}⚡  Developed by {Fore.WHITE}{AUTHOR}\n"
        f"  {Fore.CYAN}📲  Telegram  : {Fore.LIGHTCYAN_EX}{TELEGRAM}\n"
        f"  {Fore.CYAN}🌐  Website   : {Fore.LIGHTCYAN_EX}{WEBSITE}\n"
        f"  {Fore.RED}⚠   This data is from leaked sources — for research only."
    )
    draw_separator("═", 60, Fore.YELLOW)
    print()


# ─────────────────────────────────────────────────────────────────────────────
#  SEARCH ORCHESTRATOR
# ─────────────────────────────────────────────────────────────────────────────

def search_number(number: str) -> None:
    """Main search pipeline: fetch → normalise → filter nulls → display."""
    print()
    glitch_effect(f"  🔍 Initiating lookup for {number}...")
    print()

    # ── OSINT APIs ─────────────────────────────────────────────────────────
    raw_data = fetch_number_data(number)

    if raw_data is None:
        print(Fore.RED + "\n  ❌  Both OSINT APIs failed. Check your internet connection.\n")
    else:
        records = normalize_response(raw_data)
        if not records:
            print(Fore.YELLOW + "\n  ⚠  No OSINT data found for this number.\n")
        else:
            swipe_effect(
                f"\n{Fore.CYAN + Style.BRIGHT}  📊  Search Results for {Fore.WHITE}{number}\n",
                delay=0.006,
            )
            for idx, record in enumerate(records, start=1):
                display_record(idx, record)

    display_branding()


# ─────────────────────────────────────────────────────────────────────────────
#  DISCLAIMER  (shown once per session at start)
# ─────────────────────────────────────────────────────────────────────────────

def show_disclaimer() -> None:
    """Print the full legal disclaimer."""
    draw_separator("═", 64, Fore.RED)
    disclaimer = f"""
{Fore.RED + Style.BRIGHT}  ╔══════════════════════  DISCLAIMER  ══════════════════════╗

{Fore.WHITE}  This tool (NUM-OSINT) is created strictly for
  EDUCATIONAL PURPOSES ONLY.

  • The developer (Lucky) does NOT own, store, or distribute
    any personal data retrieved by this tool.

  • The data accessed through this tool has reportedly been
    leaked and is already publicly available on the dark-web.

  • The developer is NOT responsible for any misuse, illegal
    activity, privacy violations, or damages caused by use of
    this tool.

  • By continuing, you confirm that you accept FULL LEGAL
    RESPONSIBILITY for your actions.

  • USE AT YOUR OWN RISK.

{Fore.RED + Style.BRIGHT}  ╚══════════════════════════════════════════════════════════╝
"""
    print(disclaimer)
    draw_separator("═", 64, Fore.RED)
    print()
    time.sleep(0.5)


# ─────────────────────────────────────────────────────────────────────────────
#  HELP SCREEN
# ─────────────────────────────────────────────────────────────────────────────

def show_help() -> None:
    """Display the help / usage screen."""
    draw_separator("═", 64, Fore.CYAN)
    print(Fore.CYAN + Style.BRIGHT + """
  ██╗  ██╗███████╗██╗     ██████╗
  ██║  ██║██╔════╝██║     ██╔══██╗
  ███████║█████╗  ██║     ██████╔╝
  ██╔══██║██╔══╝  ██║     ██╔═══╝
  ██║  ██║███████╗███████╗██║
  ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝
""")
    draw_separator("─", 64, Fore.YELLOW)

    sections = [
        ("USAGE", [
            ("<10-digit number>",  "Look up info on a mobile number"),
            ("help",               "Show this guide screen"),
            ("clear",              "Clear the terminal screen"),
            ("exit",               "Exit NUM-OSINT"),
        ]),
        ("NOTES", [
            ("Dual API",       "Primary API queried first; auto-fallback on failure"),
            ("Null filtering", "Empty / null fields are hidden automatically"),
            ("Security",       "Tool requires a security key at startup"),
            ("Input format",   "Number must be exactly 10 digits (no spaces/dashes)"),
        ]),
        ("CONTACT ME", [
            ("Telegram",       f"{TELEGRAM}"),
            ("Website",        f"{WEBSITE}"),
        ]),
    ]

    for section, rows in sections:
        print(Fore.YELLOW + Style.BRIGHT + f"\n  ┌─ {section} " + "─" * (54 - len(section)) + "┐")
        for cmd, desc in rows:
            print(
                f"  │  {Fore.LIGHTCYAN_EX}{cmd:<28}{Fore.WHITE}{desc}"
            )
            time.sleep(0.015)
        print(Fore.YELLOW + Style.BRIGHT + "  └" + "─" * 62 + "┘")

    draw_separator("─", 64, Fore.YELLOW)
    print(
        f"\n  {Fore.MAGENTA}⚡ NUM-OSINT {TOOL_VERSION}   "
        f"{Fore.WHITE}Developed by {Fore.CYAN}{AUTHOR}   "
        f"{Fore.YELLOW}Telegram: {Fore.LIGHTCYAN_EX}{TELEGRAM}\n"
    )
    draw_separator("═", 64, Fore.CYAN)


# ─────────────────────────────────────────────────────────────────────────────
#  RATE LIMITER
# ─────────────────────────────────────────────────────────────────────────────

_RATE_LIMIT_SECS = 15


def rate_limit_countdown(seconds: int = _RATE_LIMIT_SECS) -> None:
    """
    Animated countdown bar shown between lookups for standard users.
    Counts down second by second with a colour-shifting progress bar.
    """
    draw_separator("─", 60, Fore.RED)
    print(Fore.RED + Style.BRIGHT +
          f"  \u23f3  Rate limit active — next lookup in {seconds}s")

    bar_width = 40
    for remaining in range(seconds, 0, -1):
        filled  = int((seconds - remaining) / seconds * bar_width)
        empty   = bar_width - filled

        # Colour shifts green → yellow → red as time passes
        if remaining > seconds * 0.6:
            bar_color = Fore.RED
        elif remaining > seconds * 0.3:
            bar_color = Fore.YELLOW
        else:
            bar_color = Fore.GREEN

        bar = bar_color + "\u2588" * filled + Fore.WHITE + "\u2591" * empty
        print(
            f"\r  {Fore.WHITE}[{bar}{Fore.WHITE}]  "
            f"{bar_color}{remaining:>2}s remaining ",
            end='', flush=True
        )
        time.sleep(1)

    full_bar = "\u2588" * bar_width
    print(f"\r  {Fore.GREEN}[{full_bar}]  {Fore.GREEN}Ready!          ")
    draw_separator("─", 60, Fore.GREEN)
    print()


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN CLI LOOP
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point — orchestrates banner → disclaimer → auth → search loop."""
    show_banner()
    show_disclaimer()

    role = verify_security_key()   # 'admin' or 'user'
    is_admin = (role == "admin")

    last_lookup: float = 0.0       # timestamp of most recent successful lookup

    while True:
        draw_separator("─", 60, Fore.BLUE)
        try:
            type_effect(
                Fore.BLUE + "  \U0001f4de  Enter Number / Command  "
                + Fore.CYAN + "[ type 'help' for guide ]",
                delay=0.012,
            )
            raw = input(Fore.LIGHTGREEN_EX + "  Target \u27a4 " + Fore.WHITE).strip()
        except KeyboardInterrupt:
            print(Fore.RED + "\n\n  \u26d4  Exiting NUM-OSINT. Stay safe!\n")
            break

        cmd = raw.lower()

        if cmd in ("exit", "quit", "q"):
            print(Fore.YELLOW + "\n  \U0001f44b  Goodbye! Stay safe.\n")
            display_branding()
            break

        if cmd in ("help", "?"):
            show_help()
            continue

        if cmd in ("clear", "cls"):
            os.system("clear || cls")
            show_banner()
            continue

        if raw.isdigit() and len(raw) == 10:
            # ── Rate limit check (standard users only) ──────────────────────
            if not is_admin:
                elapsed = time.time() - last_lookup
                if elapsed < _RATE_LIMIT_SECS and last_lookup != 0.0:
                    wait = int(_RATE_LIMIT_SECS - elapsed) + 1
                    rate_limit_countdown(wait)

            search_number(raw)
            last_lookup = time.time()
        else:
            print(
                Fore.RED + "  \u274c  Unknown command or invalid number.  "
                + Fore.YELLOW + "Type 'help' for usage.\n"
            )


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()