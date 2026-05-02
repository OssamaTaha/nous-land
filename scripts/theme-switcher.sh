#!/usr/bin/env bash
# ───────────────────────────────────────────────────────
# NOUS LAND — Theme Switcher (CLI)
# Usage: nous-theme [theme_name]
#        nous-theme           # Show current theme
# ───────────────────────────────────────────────────────

set -euo pipefail

NOUS_DIR="$HOME/.config/nous-land"
THEMES_DIR="$NOUS_DIR/themes"
CONFIGS_DIR="$NOUS_DIR/configs"
TMP_DIR="/tmp/nous-current-theme"
BIN_DIR="$HOME/.local/bin"

# Colors for output
RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[1;33m'
CYN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${CYN}[nous]${NC} $*"; }
warn() { echo -e "${YLW}[warn]${NC} $*"; }
err()  { echo -e "${RED}[error]${NC} $*"; }
ok()   { echo -e "${GRN}[ok]${NC} $*"; }

# ── Show usage ────────────────────────────────────────
usage() {
    echo "Usage: nous-theme [theme_name]"
    echo ""
    echo "Available themes:"
    for d in "$THEMES_DIR"/*/; do
        if [ -f "$d/theme.json" ]; then
            basename "$d"
        fi
    done
    echo ""
    echo "If no theme_name is provided, shows current theme."
    exit 0
}

# ── List themes ───────────────────────────────────────
list_themes() {
    echo -e "${CYN}Available themes:${NC}"
    for d in "$THEMES_DIR"/*/; do
        if [ -f "$d/theme.json" ]; then
            name=$(basename "$d")
            if [ -f "$TMP_DIR/theme.json" ]; then
                current=$(jq -r '.name' "$TMP_DIR/theme.json" 2>/dev/null)
                if [ "$name" = "$current" ]; then
                    echo -e "  ${GRN}● $name${NC} (active)"
                else
                    echo "  ○ $name"
                fi
            else
                echo "  ○ $name"
            fi
        fi
    done
}

# ── Show current theme ────────────────────────────────
show_current() {
    if [ -f "$TMP_DIR/theme.json" ]; then
        current=$(jq -r '.name' "$TMP_DIR/theme.json" 2>/dev/null)
        echo -e "${CYN}Current theme:${NC} $current"
    else
        echo -e "${YLW}No theme active. Run: nous-theme <theme_name>${NC}"
        list_themes
    fi
}

# ── Render template ───────────────────────────────────
render_template() {
    local template_file="$1"
    local output_file="$2"
    local theme_json="$3"
    
    # Read template
    local content=$(cat "$template_file")
    
    # Replace all {{key}} with values from theme.json
    # This uses jq to extract values and sed to replace
    while IFS= read -r line; do
        key=$(echo "$line" | sed -n 's/.*\{\{{\([a-z_]*\)\}\}.*/\1/p')
        if [ -n "$key" ]; then
            value=$(jq -r ".$key // .colors.\$key // .surface.\$key // .typography.\$key // .hyprland.\$key // .kitty.\$key // empty" "$theme_json" 2>/dev/null)
            if [ -n "$value" ] && [ "$value" != "null" ]; then
                content=$(echo "$content" | sed "s/{{\$key}}/$value/g")
            fi
        fi
    done < "$template_file"
    
    # Actually, let's do it properly with jq and a more robust approach
    # Extract all keys from theme.json
    python3 - <<PYEOF
import json, re, os, sys

template_path = "$template_file"
output_path = "$output_file"
theme_path = "$theme_json"

with open(theme_path) as f:
    theme = json.load(f)

# Flatten theme into a single dict for easy lookup
flat = {}
flat.update(theme.get('colors', {}))
flat.update(theme.get('surface', {}))
flat.update(theme.get('typography', {}))
flat.update(theme.get('hyprland', {}))
flat.update(theme.get('kitty', {}))

with open(template_path) as f:
    content = f.read()

# Replace {{key}} patterns
def replace(match):
    key = match.group(1)
    return str(flat.get(key, match.group(0)))

content = re.sub(r'\{\{(\w+)\}\}', replace, content)

with open(output_path, 'w') as f:
    f.write(content)

print(f"Rendered: {os.path.basename(template_path)} -> {os.path.basename(output_path)}")
PYEOF
}

# ── Switch theme ───────────────────────────────────────
switch_theme() {
    local theme_name="$1"
    local theme_dir="$THEMES_DIR/$theme_name"
    local theme_json="$theme_dir/theme.json"
    
    if [ ! -d "$theme_dir" ]; then
        err "Theme '$theme_name' not found."
        list_themes
        exit 1
    fi
    
    if [ ! -f "$theme_json" ]; then
        err "theme.json not found in $theme_dir"
        exit 1
    fi
    
    log "Switching to theme: $theme_name"
    
    # Create tmp dir
    mkdir -p "$TMP_DIR"
    
    # Copy theme.json to tmp
    cp "$theme_json" "$TMP_DIR/theme.json"
    
    # ── Render Hyprland colors ────────────────────────
    log "Rendering Hyprland colors..."
    python3 - <<PYEOF
import json

with open("$theme_json") as f:
    theme = json.load(f)

h = theme.get('hyprland', {})
c = theme.get('colors', {})

lines = []
lines.append(f"\$active_border = {h.get('active_border', 'ffffff')}")
lines.append(f"\$inactive_border = {h.get('inactive_border', '555555')}")
lines.append(f"\$gaps_inner = {h.get('gaps_inner', 6)}")
lines.append(f"\$gaps_outer = {h.get('gaps_outer', 8)}")
lines.append(f"\$rounding = {h.get('rounding', 8)}")
lines.append(f"\$dim_strength = {h.get('dim_strength', 0.3)}")
lines.append(f"\$shadow_range = {h.get('shadow_range', 20)}")
lines.append(f"\$shadow_render_power = {h.get('shadow_render_power', 3)}")
lines.append(f"\$shadow = {c.get('shadow', '000000')}")

with open("$TMP_DIR/hyprland-colors.conf", 'w') as f:
    f.write('\n'.join(lines))
    
print("Hyprland colors written.")
PYEOF
    
    # ── Render Kitty config ───────────────────────────
    log "Rendering Kitty config..."
    if [ -f "$CONFIGS_DIR/kitty/kitty.conf.template" ]; then
        render_template "$CONFIGS_DIR/kitty/kitty.conf.template" "$HOME/.config/kitty/kitty.conf" "$theme_json"
    fi
    
    # ── Render Waybar CSS ─────────────────────────────
    log "Rendering Waybar style..."
    if [ -f "$CONFIGS_DIR/waybar/style.css.template" ]; then
        render_template "$CONFIGS_DIR/waybar/style.css.template" "$HOME/.config/waybar/style.css" "$theme_json"
    fi
    
    # ── Render Wofi CSS ───────────────────────────────
    log "Rendering Wofi style..."
    if [ -f "$CONFIGS_DIR/wofi/style.css.template" ]; then
        render_template "$CONFIGS_DIR/wofi/style.css.template" "$HOME/.config/wofi/style.css" "$theme_json"
    fi
    
    # ── Render SwayNC CSS ─────────────────────────────
    log "Rendering SwayNC style..."
    if [ -f "$CONFIGS_DIR/swaync/style.css.template" ]; then
        render_template "$CONFIGS_DIR/swaync/style.css.template" "$HOME/.config/swaync/style.css" "$theme_json"
    fi
    
    # ── Render Rofi theme ─────────────────────────────
    log "Rendering Rofi theme..."
    if [ -f "$CONFIGS_DIR/rofi/theme.rasi.template" ]; then
        render_template "$CONFIGS_DIR/rofi/theme.rasi.template" "$HOME/.config/rofi/theme.rasi" "$theme_json"
    fi
    
    # ── Render Mako config ────────────────────────────
    log "Rendering Mako config..."
    if [ -f "$CONFIGS_DIR/mako/config.template" ]; then
        render_template "$CONFIGS_DIR/mako/config.template" "$HOME/.config/mako/config" "$theme_json"
    fi
    
    # ── Copy wallpaper ────────────────────────────────
    log "Setting wallpaper..."
    wallpaper_path=$(jq -r '.wallpaper.path' "$theme_json")
    wallpaper_mode=$(jq -r '.wallpaper.mode' "$theme_json")
    if [ -f "$theme_dir/$wallpaper_path" ]; then
        cp "$theme_dir/$wallpaper_path" "$TMP_DIR/wallpaper"
        # Set wallpaper with hyprpaper if running
        if pgrep -x hyprpaper > /dev/null; then
            hyprctl hyprpaper wallpaper "$TMP_DIR/wallpaper,$wallpaper_mode" 2>/dev/null || true
        fi
    fi
    
    # ── Export theme name ─────────────────────────────
    export NOUS_THEME="$theme_name"
    echo "$theme_name" > "$TMP_DIR/current_theme.txt"
    
    ok "Theme switched to: $theme_name"
    
    # ── Hot-reload ─────────────────────────────────────
    log "Hot-reloading applications..."
    bash "$BIN_DIR/hot-reload.sh" "$theme_name"
}

# ── Main ───────────────────────────────────────────────
if [ $# -eq 0 ]; then
    show_current
    exit 0
fi

case "$1" in
    -h|--help|help)
        usage
        ;;
    -l|--list|list)
        list_themes
        ;;
    *)
        switch_theme "$1"
        ;;
esac
