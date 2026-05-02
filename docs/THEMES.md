# 🎨 Themes Guide

Nous Land uses a **dynamic multi-theme architecture**. Each theme is a self-contained directory with a `theme.json` that defines colors, typography, wallpapers, and app-specific settings.

## Available Themes

### 🏛️ Pharaoh (Default)
**Ancient Egyptian / CRT retro aesthetic**

- Warm golds (`#d4a017`), deep blacks (`#0a0a0a`), sandstone accents
- Monospace: JetBrains Mono Nerd Font
- Perfect for that Identity-as-a-Moat branding

### 🔮 Obsidian
**Dark minimal / Nous Research vibe**

- Deep blacks (`#0d1117`), cool blue accent (`#58a6ff`)
- Clean, professional, distraction-free
- Inspired by GitHub's dark theme and Nous Research

### 🌆 Cyberpunk
**Neon / synthwave aesthetic**

- Hot pink (`#ff2e97`), electric blue (`#00cfff`), deep purple (`#0a0014`)
- High contrast, vibrant
- Maximum futuristic energy

### 🍂 Solace
**Warm / muted / productivity**

- Warm earth tones, soft contrasts
- Easy on the eyes for long coding sessions
- Gruvbox-inspired but softer

## Theme Structure

Each theme directory contains:

```
themes/<theme-name>/
├── theme.json          # Central theme definition
├── wallpaper.png      # Wallpaper image
├── kitty.conf         # Kitty-specific overrides (optional)
├── waybar.css         # Waybar-specific overrides (optional)
└── wofi.css          # Wofi-specific overrides (optional)
```

### theme.json Schema

```json
{
  "name": "theme-name",
  "author": "Nous Land",
  "version": "1.0.0",
  "colors": {
    "bg": "#0a0a0a",           // Background
    "bg_alt": "#141414",        // Alternative background
    "bg_highlight": "#1e1e1e",  // Highlight background
    "fg": "#d4c5a9",           // Foreground text
    "fg_alt": "#b8a88a",        // Alternative foreground
    "fg_dim": "#8a7e6a",        // Dimmed foreground
    "accent": "#d4a017",        // Primary accent
    "accent_alt": "#f0c75e",    // Secondary accent
    "urgent": "#c0392b",        // Urgent/error color
    "success": "#27ae60",        // Success color
    "warning": "#e67e22",        // Warning color
    "border": "#2c2c2c",        // Border color
    "shadow": "#000000"          // Shadow color
  },
  "surface": {
    "panel_bg": "#0a0a0a",      // Panel/taskbar background
    "panel_fg": "#d4c5a9",      // Panel text color
    "panel_border": "#2c2c2c",   // Panel border
    "launcher_bg": "#0a0a0a",   // App launcher background
    "launcher_fg": "#d4c5a9",   // Launcher text
    "launcher_sel_bg": "#d4a017", // Selected item background
    "launcher_sel_fg": "#0a0a0a", // Selected item text
    "notification_bg": "#141414",  // Notification background
    "notification_fg": "#d4c5a9", // Notification text
    "notification_border": "#d4a017" // Notification border
  },
  "typography": {
    "font_mono": "JetBrainsMono Nerd Font",
    "font_ui": "JetBrainsMono Nerd Font",
    "font_size": 11,
    "font_size_ui": 9
  },
  "wallpaper": {
    "path": "wallpaper.png",
    "mode": "fill"
  },
  "hyprland": {
    "border_width": 2,
    "active_border": "d4a017",
    "inactive_border": "2c2c2c",
    "gaps_inner": 6,
    "gaps_outer": 8,
    "rounding": 8,
    "dim_strength": 0.3,
    "shadow_range": 20,
    "shadow_render_power": 3
  },
  "kitty": {
    "foreground": "#d4c5a9",
    "background": "#0a0a0a",
    // ... (all 16 terminal colors)
  }
}
```

## Switching Themes

### CLI
```bash
nous-theme              # Show current theme
nous-theme --list      # List all themes
nous-theme cyberpunk   # Switch to Cyberpunk
```

### GUI
Press `Super+T` for a graphical theme picker (uses Wofi).

### Hot-Reloading
When you switch a theme, the following apps automatically reload:
- ✅ Hyprland (config + colors)
- ✅ Niri (if running)
- ✅ Waybar (SIGUSR2)
- ✅ Kitty (SIGUSR1)
- ✅ SwayNC (CSS reload)
- ✅ Wofi (next launch)
- ✅ Rofi (next launch)
- ✅ Mako (reload)
- ✅ Wallpaper (hyprpaper)

## Creating a Custom Theme

1. Create a new directory:
   ```bash
   mkdir -p ~/.config/nous-land/themes/my-theme
   ```

2. Copy an existing theme.json:
   ```bash
   cp ~/.config/nous-land/themes/pharaoh/theme.json ~/.config/nous-land/themes/my-theme/
   ```

3. Edit the theme.json with your colors:
   ```bash
   nano ~/.config/nous-land/themes/my-theme/theme.json
   ```

4. Add a wallpaper (optional):
   ```bash
   cp /path/to/wallpaper.png ~/.config/nous-land/themes/my-theme/wallpaper.png
   ```

5. Apply your theme:
   ```bash
   nous-theme my-theme
   ```

## Theme Variables in Configs

Config files use `{{variable}}` placeholders that get replaced when switching themes:

```
# Example from kitty.conf.template
foreground    {{foreground}}
background    {{background}}
color1         {{color1}}
```

This allows all apps to stay in sync with the active theme.
