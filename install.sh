#!/usr/bin/env bash
# ──────────────────────────────────────────────────────
# NOUS LAND — Smart Installer Entry Point
# Usage: curl -fsSL https://raw.githubusercontent.com/OssamaTaha/nous-land/main/install.sh | bash
# Better: curl -o /tmp/nous-install.sh https://... && bash /tmp/nous-install.sh
# ──────────────────────────────────────────────────────

# Note: we do NOT use 'set -u' because we check unbound vars with -n/-z
set -eo pipefail

# ── Colors ───────────────────────────────────────────
RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[1;33m'
CYN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log()  { echo -e "${CYN}[nous]${NC} $*"; }
warn() { echo -e "${YLW}[warn]${NC} $*"; }
err()  { echo -e "${RED}[error]${NC} $*"; }
ok()   { echo -e "${GRN}[ok]${NC} $*"; }
info() { echo -e "${BOLD}[info]${NC} $*"; }

# ── Banner ────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║    NOUS LAND — Smart Dotfiles Installer  ║${NC}"
echo -e "${BOLD}║    Hyprland + Niri + AI Agent           ║${NC}"
echo -e "${BOLD}╚════════════════════════════════════════╝${NC}"
echo ""

# ── PIPE DETECTION (MUST be first thing after banner) ──
# Check if stdin is a pipe/redirect (curl | bash scenario)
if [ ! -t 0 ]; then
    echo ""
    echo -e "${BOLD}╔════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}║   INTERACTIVE SETUP REQUIRED            ║${NC}"
    echo -e "${BOLD}╚════════════════════════════════════════╝${NC}"
    echo ""
    err "Running via 'curl | bash' does NOT support interactive prompts."
    echo ""
    info "The installer needs to ask you for an API key (for the AI features)."
    info "Please run these TWO commands instead:"
    echo ""
    echo -e "  ${CYN}curl -fsSL https://raw.githubusercontent.com/OssamaTaha/nous-land/main/install.sh -o /tmp/nous-install.sh${NC}"
    echo -e "  ${CYN}bash /tmp/nous-install.sh${NC}"
    echo ""
    info "This gives the script a real terminal for interactive prompts."
    echo ""
    exit 1
fi

# ── Pre-flight Checks ─────────────────────────────────
info "Running pre-flight checks..."

# Check if running as root
if [ "$(id -u)" -eq 0 ]; then
    err "This script should NOT be run as root."
    err "It will use sudo when needed."
    exit 1
fi

# Check for Arch Linux
if ! command -v pacman &>/dev/null; then
    err "pacman not found. This installer is for Arch Linux only."
    exit 1
fi

if [ ! -f /etc/arch-release ]; then
    warn "This doesn't appear to be Arch Linux. Continue anyway? (y/N)"
    read -r answer
    if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
        exit 1
    fi
fi

# Check for git
if ! command -v git &>/dev/null; then
    log "Installing git..."
    sudo pacman -S --noconfirm git
fi

# ── Clone or Update Repository ────────────────────────
NOUS_DIR="$HOME/.config/nous-land"
REPO_URL="https://github.com/OssamaTaha/nous-land.git"

if [ -d "$NOUS_DIR/.git" ]; then
    log "Existing installation found. Pulling latest changes..."
    git -C "$NOUS_DIR" pull --rebase 2>/dev/null || true
else
    log "Cloning Nous Land repository..."
    if git clone "$REPO_URL" "$NOUS_DIR" 2>/dev/null; then
        ok "Repository cloned successfully."
    else
        err "GitHub clone failed. Check your internet connection."
        exit 1
    fi
fi

# Ensure we're in the right directory
cd "$NOUS_DIR" || {
    err "Failed to enter $NOUS_DIR"
    exit 1
}

# ── Bootstrap Python Environment ─────────────────────
log "Bootstrapping Python environment..."

# Find or install Python
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON=$(command -v "$cmd")
        break
    fi
done

if [ -z "$PYTHON" ]; then
    log "Installing Python..."
    sudo pacman -S --noconfirm python
    PYTHON=$(command -v python3)
fi

# Create venv if needed
VENV_DIR="$NOUS_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    log "Creating Python virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
fi

# Activate venv
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# Install Python dependencies
log "Installing Python dependencies..."
pip install -q --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
else
    # Install defaults if requirements.txt missing
    pip install -q requests textual
fi

# ── Hand Off to Smart Installer ─────────────────────
log "Starting LLM-powered smart installer..."
echo ""

if [ -f "smart_installer.py" ]; then
    python3 smart_installer.py "$@"
    EXIT_CODE=$?
else
    warn "smart_installer.py not found. Skipping LLM installer."
    warn "Deploying configs manually..."
    CONFIGS_DIR="$NOUS_DIR/configs"
    for dir in hyprland niri kitty waybar wofi swaync rofi mako; do
        if [ -d "$CONFIGS_DIR/$dir" ]; then
            cp -r "$CONFIGS_DIR/$dir" "$HOME/.config/" 2>/dev/null || true
            log "Deployed $dir config"
        fi
    done
    EXIT_CODE=0
fi

# ── Post-Installation ────────────────────────────────
echo ""

if [ "$EXIT_CODE" -eq 0 ]; then
    ok "Installation complete!"
    echo ""
    info "Next steps:"
    echo "  1. Log out and log back in (or reboot)"
    echo "  2. Select 'Nous Land (Hyprland)' or 'Nous Land (Niri)' at login"
    echo "  3. Run 'nous-theme' to see available themes"
    echo "  4. Press Super+A to chat with Hermes (AI agent)"
    echo "  5. Press Super+T to switch themes via GUI"
    echo ""
    ok "Welcome to Nous Land! 🚀"
else
    err "Installation exited with code $EXIT_CODE"
    err "Check the log at: $NOUS_DIR/install.log"
fi

# Cleanup
rm -rf /tmp/nous-install.sh 2>/dev/null || true
exit $EXIT_CODE
