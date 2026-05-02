# NOUS LAND — Project Specification

## Vision
A complete, production-ready dotfiles ecosystem for Hyprland and Niri on Arch Linux (CachyOS),
featuring a revolutionary LLM-powered smart installer, dynamic multi-theme architecture with
hot-reloading, and a deeply integrated AI desktop agent.

## Architecture

### Repository Structure
```
nous-land/
├── install.sh                      # One-liner entry point (curl | bash)
├── smart_installer.py              # LLM-powered Python orchestrator
├── requirements.txt                # Python deps
├── themes/
│   ├── _schema.json                # Theme contract
│   ├── pharaoh/                    # Ancient Egyptian / CRT retro
│   ├── obsidian/                   # Dark minimal / Nous Research vibe
│   ├── cyberpunk/                  # Neon / synthwave
│   └── solace/                     # Warm / muted / productivity
├── configs/
│   ├── hyprland/                   # hyprland.conf + modules
│   ├── niri/                       # config.kdl + binds.kdl
│   ├── kitty/                      # kitty.conf.template
│   ├── waybar/                     # config.jsonc + style.css.template
│   ├── wofi/                       # style.css.template
│   ├── swaync/                     # style.css.template
│   ├── rofi/                       # theme.rasi.template
│   └── mako/                       # config.template
├── scripts/
│   ├── theme-switcher.sh           # CLI theme switcher
│   ├── theme-switcher-gui.sh       # Wofi/Rofi GUI picker
│   ├── hot-reload.sh               # Hot-reload orchestrator
│   └── backup-current.sh           # Backup existing dotfiles
├── agent/
│   ├── daemon.py                   # Python daemon (API key, memory, shell)
│   ├── ui.py                       # Floating drop-down chat UI
│   ├── system_tools.py             # Safe system command whitelist
│   ├── memory.json                 # Conversation memory store
│   └── hermes.desktop              # .desktop entry for autostart
├── systemd/
│   ├── nous-agent.service          # User systemd unit
│   └── nous-theme-watcher.path     # Optional theme watcher
├── docs/
│   ├── INSTALL.md
│   ├── THEMES.md
│   ├── KEYBINDS.md
│   └── AGENT.md
├── LICENSE
└── README.md
```

### Hot-Reloading Mechanism
1. User selects theme via CLI or GUI picker
2. `theme-switcher.sh` reads `themes/<name>/theme.json`
3. Validates against `_schema.json`
4. Renders all `.template` files → target configs using `{{placeholder}}` substitution
5. `hot-reload.sh` signals running apps:
   - `hyprctl reload` → Hyprland
   - `niri msg reload-config` → Niri
   - `killall -SIGUSR2 waybar` → Waybar
   - `killall -SIGUSR1 kitty` → Kitty
   - `swaync-client --reload-css` → SwayNC
   - `hyprctl hyprpaper wallpaper` → Wallpaper
   - Export `NOUS_THEME=<name>` → Agent/UI inherits

### AI Agent Architecture
- Invocation: `Super + A` → launches `agent/ui.py`
- UI connects to `daemon.py` via local Unix socket (localhost:18789)
- Daemon holds LLM API key, conversation memory, whitelisted system commands
- User requests → LLM API → daemon executes safe system calls
- Theme switching, system updates, audio debug, etc.

### Smart Installer Logic
1. `install.sh` bootstraps Python venv, installs deps, hands off to `smart_installer.py`
2. Python script installs packages via `pacman`/`yay` using `subprocess`
3. On failure: captures stderr → sends to LLM API → receives fix command → executes fix → retries
4. Falls back to common fixes (PGP refresh, --overwrite, system update) if LLM unavailable
5. Deploys configs, applies default theme, prints summary

## Themes

### 1. Pharaoh (Default)
- Ancient Egyptian / CRT retro aesthetic
- Warm golds, deep blacks, sandstone accents
- Inspired by Vlad's Identity-as-a-Moat branding

### 2. Obsidian
- Dark minimal / Nous Research vibe
- Deep blacks, subtle grays, single accent color
- Clean, professional, distraction-free

### 3. Cyberpunk
- Neon / synthwave aesthetic
- Hot pink, electric blue, deep purple
- High contrast, vibrant

### 4. Solace
- Warm / muted / productivity
- Soft earth tones, gentle contrasts
- Easy on the eyes for long sessions

## Constraints
- No Rust helpers — Bash + Python only
- Target: Arch Linux / CachyOS
- Package managers: pacman + yay/paru
- All configs read colors from central theme.json
- Shared keybind philosophy between Hyprland and Niri
