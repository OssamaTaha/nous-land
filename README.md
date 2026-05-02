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
- 🚀 **Smart Install** — Clones repo, bootstraps Python, runs LLM installer automatically

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
Super+T                  # GUI menu (Wofi)
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

### Option 1: One-Liner (With AI Features)

Set your OpenRouter API key, then pipe the installer:

```bash
export OPENROUTER_API_KEY="sk-..."
curl -fsSL https://raw.githubusercontent.com/OssamaTaha/nous-land/main/install.sh | bash
```

**What happens:**
1. Script detects pipe mode ✅
2. Clones repo to `~/.nous-land` ✅
3. Bootstraps Python venv ✅
4. Runs LLM smart installer with your API key ✅

---

### Option 2: Two-Step (Interactive, Recommended)

If you don't have your API key yet, or prefer interactive prompts:

```bash
# Step 1: Download
curl -fsSL https://raw.githubusercontent.com/OssamaTaha/nous-land/main/install.sh -o /tmp/nous-install.sh

# Step 2: Run interactively (prompts for API key)
bash /tmp/nous-install.sh
```

**Benefits:**
- Proper terminal for interactive `input()` prompts
- Can skip API key (installs without AI features, add key later)
- Better error visibility

---

### Option 3: No API Key (Basic Install)

Just want the dotfiles without AI features?

```bash
curl -fsSL https://raw.githubusercontent.com/OssamaTaha/nous-land/main/install.sh | bash
```

The installer will:
- ✅ Clone the repository
- ✅ Install all packages (Hyprland, Niri, Kitty, Waybar, etc.)
- ✅ Deploy configs
- ⚠️ Skip AI features (add key later to `~/.nous-land/.env`)

---

### 🔧 What Happens During Install

| Step | Action | Details |
|------|--------|---------|
| 1️⃣ | **Pre-flight checks** | Verifies Arch Linux, checks for `git` |
| 2️⃣ | **Clone repository** | Clones to `~/.nous-land` (or pulls latest) |
| 3️⃣ | **Bootstrap Python** | Creates venv, installs dependencies |
| 4️⃣ | **LLM Smart Install** | Installs packages via `pacman`/`yay` |
| 5️⃣ | **Auto-heal errors** | LLM analyzes failures, suggests fixes, retries |
| 6️⃣ | **Deploy configs** | Copies dotfiles to `~/.config/` |
| 7️⃣ | **Setup AI Agent** | Hermes daemon + keybind integration |

---

### 📋 Requirements

- **Arch Linux** (tested on CachyOS)
- **pacman** and **yay**/`paru` (AUR helper)
- **Python 3.10+**
- **OpenRouter API Key** (get one free at [openrouter.ai](https://openrouter.ai)) — *optional for basic install*

---

### 🔑 Adding API Key Later

If you installed without an API key:

```bash
# Edit the .env file
nano ~/.nous-land/.env

# Add your key:
OPENROUTER_API_KEY=sk-...

# Restart the agent daemon
systemctl --user restart nous-agent
```

---

## 📂 Directory Structure

```
~/.nous-land/
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
│   ├── theme-switcher.sh
│   ├── hot-reload.sh
│   └── backup-current.sh
├── agent/           # AI desktop agent (daemon, UI, tools)
│   ├── daemon.py
│   ├── ui.py
│   └── system_tools.py
├── systemd/         # Systemd user units
│   └── nous-agent.service
├── smart_installer.py
├── install.sh
└── .env            # Your API keys (NOT committed to Git)
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

Edit any theme in `~/.nous-land/themes/<theme>/theme.json`:

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

1. Create `~/.nous-land/themes/my-theme/theme.json`
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
