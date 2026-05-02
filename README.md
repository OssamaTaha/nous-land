# 🏛️ NOUS LAND

**A complete, production-ready dotfiles ecosystem for Hyprland & Niri on Arch Linux.**

> Inspired by ML4W but with a revolutionary LLM-powered installer, dynamic multi-theme architecture, and a deeply integrated AI desktop agent.

![Nous Land](https://img.shields.io/badge/Arch%20Linux-1793D1?style=for-the-badge&logo=archlinux)
![Hyprland](https://img.shields.io/badge/Hyprland-ff6f00?style=for-the-badge)
![Niri](https://img.shields.io/badge/Niri-8B5CF6?style=for-the-badge)
![AI Agent](https://img.shields.io/badge/AI%20Agent-00C853?style=for-the-badge)

## ✨ Features

- 🎨 **4 Distinct Themes** — Pharaoh (Egyptian/CRT), Obsidian (Nous minimal), Cyberpunk (neon), Solace (warm/productive)
- 🔄 **Hot-Reloading** — Switch themes and watch all apps update instantly (Waybar, Kitty, Wofi, SwayNC, Rofi, Mako)
- 🤖 **AI Desktop Agent** — Hermes lives natively in your OS. Press `Super+A` to chat, control themes, debug audio, update system
- 🧠 **LLM-Powered Installer** — Self-heals when packages fail. Sends errors to LLM, gets fix commands, retries
- 🪟 **Dual Compositor** — Full support for Hyprland (master/stack) and Niri (scrollable tiling)
- 🚀 **Smart Install** — Interactive installer with 2-step method (explained below)

## 🎨 Themes

| Theme | Description | Accent |
|-------|-------------|--------|
| **Pharaoh** | Ancient Egyptian / CRT retro | 🟡 Gold |
| **Obsidian** | Dark minimal / Nous Research vibe | 🔵 Cool Blue |
| **Cyberpunk** | Neon / synthwave | 🟣 Hot Pink |
| **Solace** | Warm / muted / productivity | 🟠 Amber |

Switch themes instantly:
```bash
nous-theme pharaoh      # CLI
Super+T                  # GUI menu
```

## 🤖 AI Agent (Hermes)

Your native OS assistant, available at `Super+A`:

- "Switch to Cyberpunk theme"
- "Why is my audio not working?"
- "Update my system"
- "What's my current theme?"
- "Make the font bigger"

The agent uses LLM (OpenRouter) and can safely execute whitelisted system commands.

## 📦 Installation

### ⚠️ Important: Interactive Setup Required

The installer needs to prompt you for an **OpenRouter API key** (for the AI self-healing feature). Because of this, the old `curl | bash` method **will not work** — pipes don't provide an interactive terminal.

### ✅ Correct Installation (2-Step Method)

```bash
# Step 1: Download the installer
curl -fsSL https://raw.githubusercontent.com/OssamaTaha/nous-land/main/install.sh -o /tmp/nous-install.sh

# Step 2: Run it interactively (gives you a real terminal for the API key prompt)
bash /tmp/nous-install.sh
```

### 🚀 What Happens During Install

1. **Pre-flight checks** — Verifies Arch Linux, installs missing dependencies
2. **Clones repository** to `~/.config/nous-land/`
3. **Bootstraps Python** — Creates venv, installs dependencies
4. **LLM Smart Install** — Installs all packages (Hyprland, Niri, Kitty, Waybar, etc.)
   - If a package fails → LLM analyzes the error → suggests fix → retries automatically
5. **Deploys configs** — Copies all dotfiles to `~/.config/`
6. **Sets up AI Agent** — Hermes daemon + keybind integration

### Requirements

- **Arch Linux** (tested on CachyOS)
- **pacman** and **yay**/`paru` (AUR helper)
- **Python 3.10+**
- **OpenRouter API Key** (get one free at [openrouter.ai](https://openrouter.ai))

### For LLM Self-Healing

You'll be prompted for your **OpenRouter API key** during installation. This enables the smart installer to:
- Auto-fix PGP key errors
- Resolve package conflicts
- Handle missing dependencies
- Retry failed installations

*The key is saved to `~/.config/nous-land/.env` and never committed to Git.*

## 📂 Directory Structure

```
~/.config/nous-land/
├── themes/          # Theme definitions (Pharaoh, Obsidian, Cyberpunk, Solace)
│   ├── pharaoh/
│   ├── obsidian/
│   ├── cyberpunk/
│   └── solace/
├── configs/         # All config files (Hyprland, Niri, Kitty, Waybar, etc.)
│   ├── hyprland/
│   ├── niri/
│   ├── kitty/
│   ├── waybar/
│   ├── wofi/
│   ├── swaync/
│   ├── rofi/
│   └── mako/
├── scripts/         # Theme switcher, hot-reload, backup
├── agent/           # AI desktop agent (daemon, UI, tools)
├── systemd/         # Systemd user units
├── smart_installer.py
└── install.sh
```

## ⌨️ Keybinds (Shared Philosophy)

### Global

| Keybind | Action |
|---------|--------|
| `Super+Q` | Open Kitty terminal |
| `Super+Space` | Open Wofi launcher |
| `Super+A` | Open AI Agent (Hermes) |
| `Super+T` | Theme switcher GUI |
| `Super+C` | Close active window |
| `Super+V` | Toggle floating |
| `Super+F` | Toggle fullscreen |

### Workspaces

| Keybind | Action |
|---------|--------|
| `Super+1-0` | Switch to workspace 1-10 |
| `Super+Shift+1-0` | Move window to workspace 1-10 |

### Layout

| Keybind | Action |
|---------|--------|
| `Super+Arrows` | Move focus |
| `Super+Shift+Arrows` | Swap windows |
| `Super+Ctrl+Arrows` | Resize windows |
| `Super+T` | Toggle split |
| `Super+G` | Toggle gaps |

## 🛠️ Configuration

### Customizing Themes

Edit any theme in `~/.config/nous-land/themes/<theme>/theme.json`:

```json
{
  "colors": {
    "bg": "#0a0a0a",
    "accent": "#d4a017"
  }
}
```

Then apply: `nous-theme <theme>`

### Adding New Themes

1. Create `~/.config/nous-land/themes/my-theme/theme.json`
2. Follow the schema in `themes/_schema.json`
3. Add `wallpaper.png` in the same directory
4. Run `nous-theme my-theme`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [ML4W Dotfiles](https://github.com/mylinuxforwork/dotfiles) for inspiration
- [Hyprland](https://hyprland.org/) — The smoothest Wayland compositor
- [Niri](https://github.com/YaLTeR/niri) — Scrollable tiling WM
- [Nous Research](https://nousresearch.com/) — The vibe

---

**Made with ❤️ by [Ossama Taha (Vlad)](https://github.com/OssamaTaha)**
