#!/usr/bin/env bash
# ───────────────────────────────────────────────────────
# NOUS LAND — Theme Switcher GUI (Wofi)
# Presents a Wofi menu to pick a theme
# ───────────────────────────────────────────────────────

NOUS_DIR="$HOME/.config/nous-land"
THEMES_DIR="$NOUS_DIR/themes"
TMP_DIR="/tmp/nous-current-theme"

# Get current theme
if [ -f "$TMP_DIR/current_theme.txt" ]; then
    CURRENT=$(cat "$TMP_DIR/current_theme.txt")
else
    CURRENT=""
fi

# Build theme list for wofi
THEME_LIST=""
for d in "$THEMES_DIR"/*/; do
    if [ -f "$d/theme.json" ]; then
        name=$(basename "$d")
        if [ "$name" = "$CURRENT" ]; then
            THEME_LIST="$THEME_LIST$name (active)\n"
        else
            THEME_LIST="$THEME_LIST$name\n"
        fi
    fi
done

# Show wofi menu
SELECTED=$(echo -e "$THEME_LIST" | wofi --show dmenu --prompt "Select Theme:")

if [ -n "$SELECTED" ]; then
    # Strip (active) suffix if present
    THEME_NAME=$(echo "$SELECTED" | sed 's/ (active)//')
    bash "$HOME/.local/bin/nous-theme" "$THEME_NAME"
fi
