#!/usr/bin/env bash
# ───────────────────────────────────────────────────────
# NOUS LAND — Backup Current Dotfiles
# Backs up existing dotfiles before installing Nous Land
# ───────────────────────────────────────────────────────

set -euo pipefail

BACKUP_DIR="$HOME/.config/nous-land-backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

log() { echo -e "\033[0;36m[nous]\033[0m $*"; }

log "Backing up existing dotfiles to $BACKUP_DIR..."

CONFIGS=(
    "$HOME/.config/hypr"
    "$HOME/.config/niri"
    "$HOME/.config/kitty"
    "$HOME/.config/waybar"
    "$HOME/.config/wofi"
    "$HOME/.config/swaync"
    "$HOME/.config/rofi"
    "$HOME/.config/mako"
)

for cfg in "${CONFIGS[@]}"; do
    if [ -d "$cfg" ]; then
        name=$(basename "$cfg")
        cp -r "$cfg" "$BACKUP_DIR/$name"
        log "Backed up $cfg"
    fi
done

log "Backup complete."
