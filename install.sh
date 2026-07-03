#!/usr/bin/env bash
# =============================================================================
#  NUM-OSINT  |  install.sh
#  Developed by Lucky
#  Telegram  : @universeluckyy
#  Website   : luckyverse.tech
# =============================================================================
#  This script installs all dependencies required to run NUM-OSINT on
#  Linux / Termux / macOS.  Run it once before launching the tool.
#
#  Usage:
#    chmod +x install.sh
#    ./install.sh
# =============================================================================

set -e   # Exit immediately if any command fails

# ── Colour codes ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
RESET='\033[0m'

# ── Banner ────────────────────────────────────────────────────────────────────
clear
echo -e "${GREEN}"
echo '  ███╗   ██╗██╗   ██╗███╗   ███╗      ██████╗ ███████╗██╗███╗   ██╗████████╗'
echo '  ████╗  ██║██║   ██║████╗ ████║     ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝'
echo '  ██╔██╗ ██║██║   ██║██╔████╔██║     ██║   ██║███████╗██║██╔██╗ ██║   ██║   '
echo '  ██║╚██╗██║██║   ██║██║╚██╔╝██║     ██║   ██║╚════██║██║██║╚██╗██║   ██║   '
echo '  ██║ ╚████║╚██████╔╝██║ ╚═╝ ██║     ╚██████╔╝███████║██║██║ ╚████║   ██║   '
echo '  ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝      ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝  '
echo -e "${RESET}"
echo -e "${YELLOW}  ────────────────────────────────────────────────────────────────${RESET}"
echo -e "  ${CYAN}NUM-OSINT v1.0${RESET}  ${MAGENTA}Developed by Lucky${RESET}"
echo -e "  ${YELLOW}Telegram: ${CYAN}@universeluckyy   ${YELLOW}Website: ${CYAN}luckyverse.tech${RESET}"
echo -e "${YELLOW}  ────────────────────────────────────────────────────────────────${RESET}"
echo ""

# ── Progress bar helper ────────────────────────────────────────────────────────
progress_bar() {
    local label="$1"
    local total=30
    printf "  ${CYAN}%-25s${RESET} [" "$label"
    for ((i = 0; i < total; i++)); do
        printf "${GREEN}█${RESET}"
        sleep 0.03
    done
    echo -e "] ${GREEN}✔${RESET}"
}

# ── Detect environment ────────────────────────────────────────────────────────
echo -e "  ${YELLOW}[*]${RESET} Detecting environment..."
if command -v pkg &>/dev/null; then
    ENV="termux"
    PKG_CMD="pkg"
elif command -v apt &>/dev/null; then
    ENV="debian"
    PKG_CMD="apt"
elif command -v brew &>/dev/null; then
    ENV="macos"
    PKG_CMD="brew"
else
    ENV="unknown"
fi
echo -e "  ${GREEN}[✔]${RESET} Environment: ${CYAN}${ENV}${RESET}"
echo ""

# ── Install Python3 / pip if missing ─────────────────────────────────────────
echo -e "  ${YELLOW}[*]${RESET} Checking Python 3 installation..."
if ! command -v python3 &>/dev/null; then
    echo -e "  ${RED}[!]${RESET} Python3 not found. Installing..."
    case "$ENV" in
        termux)  pkg install -y python ;;
        debian)  sudo apt install -y python3 python3-pip ;;
        macos)   brew install python3 ;;
        *)       echo -e "  ${RED}[✘]${RESET} Cannot auto-install Python3. Please install it manually." ; exit 1 ;;
    esac
fi
echo -e "  ${GREEN}[✔]${RESET} Python3 found: $(python3 --version)"

# ── Upgrade pip ───────────────────────────────────────────────────────────────
echo ""
echo -e "  ${YELLOW}[*]${RESET} Upgrading pip..."
python3 -m pip install --upgrade pip --quiet
echo -e "  ${GREEN}[✔]${RESET} pip is up to date."

# ── Install Python dependencies ───────────────────────────────────────────────
echo ""
echo -e "  ${YELLOW}[*]${RESET} Installing Python dependencies..."
sleep 0.5
progress_bar "Installing colorama"
python3 -m pip install colorama>=0.4.6 --quiet

progress_bar "Installing requests"
python3 -m pip install requests>=2.31.0 --quiet

echo ""
echo -e "  ${GREEN}[✔]${RESET} All Python dependencies installed."

# ── Optional: install figlet / lolcat for extra effects ──────────────────────
echo ""
echo -e "  ${YELLOW}[*]${RESET} Installing optional shell tools (figlet, lolcat)..."
if [ "$ENV" = "termux" ]; then
    pkg install -y figlet 2>/dev/null && echo -e "  ${GREEN}[✔]${RESET} figlet installed." || true
    pkg install -y lolcat 2>/dev/null && echo -e "  ${GREEN}[✔]${RESET} lolcat installed." || true
elif [ "$ENV" = "debian" ]; then
    sudo apt install -y figlet lolcat 2>/dev/null && echo -e "  ${GREEN}[✔]${RESET} figlet + lolcat installed." || true
fi

# ── Make main script executable ───────────────────────────────────────────────
echo ""
echo -e "  ${YELLOW}[*]${RESET} Setting permissions..."
chmod +x num-osint.py run.sh 2>/dev/null || true
echo -e "  ${GREEN}[✔]${RESET} Launchers are now executable."

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${YELLOW}  ════════════════════════════════════════════════════════════════${RESET}"
echo -e "  ${GREEN}✅  Installation complete!  Run the tool with:${RESET}"
echo -e "  ${CYAN}      ./run.sh${RESET}"
echo -e "${YELLOW}  ════════════════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "  ${MAGENTA}⚡  Developed by Lucky  |  Telegram: @universeluckyy  |  luckyverse.tech${RESET}"
echo ""
