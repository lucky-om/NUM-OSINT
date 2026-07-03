#!/usr/bin/env bash
# =============================================================================
#  NUM-OSINT  |  run.sh
#  Premium Shell Wrapper & Launcher
#  Developed by Lucky  |  Telegram: @universeluckyy  |  luckyverse.tech
# =============================================================================

# Reset and clear
clear

# Colour codes
RED='\033[38;5;196m'
GREEN='\033[38;5;46m'
YELLOW='\033[38;5;220m'
CYAN='\033[38;5;51m'
MAGENTA='\033[38;5;201m'
BLUE='\033[38;5;33m'
WHITE='\033[38;5;255m'
RESET='\033[0m'
BOLD='\033[1m'

# Animated cyber loading spinner
cyber_spinner() {
    local label="$1"
    local delay=0.08
    local spin='-\|/'
    echo -ne "  ${BLUE}[*]${RESET} ${label} "
    for i in {1..8}; do
        echo -ne "${spin:i%4:1}\b"
        sleep $delay
    done
    echo -e "${GREEN}[✔]${RESET}"
}

# Micro progress bar
mini_progress() {
    local label="$1"
    local total=20
    printf "  ${CYAN}%-22s${RESET} [" "$label"
    for ((i=0; i<total; i++)); do
        printf "${GREEN}█${RESET}"
        sleep 0.015
    done
    echo -e "] ${GREEN}OK${RESET}"
}

# Print shell header
echo -e "${GREEN}${BOLD}"
echo '  ██╗     ██╗   ██╗  ██████╗ ██╗  ██╗██╗   ██╗'
echo '  ██║     ██║   ██║ ██╔════╝ ██║ ██╔╝╚██╗ ██╔╝'
echo '  ██║     ██║   ██║ ██║      █████╔╝  ╚████╔╝ '
echo '  ██║     ██║   ██║ ██║      ██╔═██╗   ╚██╔╝  '
echo '  ███████╗╚██████╔╝ ╚██████╗ ██║  ██╗   ██║   '
echo '  ╚══════╝ ╚═════╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝   '
echo -e "${RESET}"
echo -e "${YELLOW}  ══════════════════════════════════════════════════════════════════════${RESET}"
echo -e "  ${BOLD}${CYAN}NUM-OSINT Launcher${RESET}  |  ${MAGENTA}Developed by Lucky${RESET}  |  ${CYAN}@universeluckyy${RESET}"
echo -e "${YELLOW}  ══════════════════════════════════════════════════════════════════════${RESET}"
echo ""

# Dependency validation
cyber_spinner "Checking Shell Environment"
cyber_spinner "Locating Python 3 Engine"

if ! command -v python3 &>/dev/null; then
    echo -e "  ${RED}[✘] Error: Python3 is not installed or not in PATH.${RESET}"
    echo -e "  ${YELLOW}[i] Please run: ./install.sh to fix all dependencies.${RESET}"
    exit 1
fi

# Check Python packages
python3 -c "import colorama, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "  ${YELLOW}[*] Missing required packages. Launching installer...${RESET}"
    chmod +x install.sh 2>/dev/null
    ./install.sh
fi

mini_progress "Checking Security"
mini_progress "Loading Core Packages"
mini_progress "Connecting API Routes"

echo -e "\n  ${GREEN}⚡ Launching NUM-OSINT Core Engine...${RESET}"
sleep 0.4

# Run the python script
python3 num-osint.py "$@"
