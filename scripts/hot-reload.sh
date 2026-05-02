#!/usr/bin/env bash
# ───────────────────────────────────────────────────────
# NOUS LAND — Hot-Reload Orchestrator
# Signals all running apps to reload their configs
# ───────────────────────────────────────────────────────

set -euo pipefail

THEME_NAME="${1:-}"
TMP_DIR="/tmp/nous-current-theme"

log() { echo -e "\033[0;36m[nous]\033[0m $*"; }
ok()  { echo -e "\033[0;32m[ok]\033[0m $*"; }

log "Hot-reloading all applications..."

# Hyprland reload
if pgrep -x Hyprland > /dev/null; then
    hyprctl reload 2>/dev/null && log "Hyprland reloaded." || true
fi

# Waybar reload (SIGUSR2)
if pgrep -x waybar > /dev/null; then
    killall -SIGUSR2 waybar 2>/dev/null && log "Waybar reloaded." || true
fi

# Kitty reload (SIGUSR1) - all kitty instances
if pgrep -x kitty > /dev/null; then
    killall -SIGUSR1 kitty 2>/dev/null && log "Kitty reloaded." || true
fi

# SwayNC reload CSS
if pgrep -x swaync > /dev/null; then
    swaync-client --reload-css 2>/dev/null && log "SwayNC reloaded." || true
fi

# Rofi (no live reload - reads config on next launch)

# Mako reload
if pgrep -x mako > /dev/null; then
    makoctl reload 2>/dev/null && log "Mako reloaded." || true
fi

# GTK theme (if using nwg-look)
if command -v nwg-look &>/dev/null; then
    nwg-look -a 2>/dev/null && log "GTK theme applied." || true
fi

ok "Hot-reload complete for theme: $THEME_NAME"
