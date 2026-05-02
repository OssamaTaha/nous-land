# 📦 Installation Guide

## Prerequisites

- **Arch Linux** (or Arch-based like CachyOS)
- **pacman** (with sudo access)
- **yay** or **paru** (AUR helper — will be installed if missing)
- **Python 3.10+**
- **Git**

## Quick Install

The one-liner that does everything:

```bash
curl -fsSL https://raw.githubusercontent.com/OssamaTaha/nous-land/main/install.sh | bash
```

This will:
1. ✅ Clone the repository to `~/.config/nous-land/`
2. ✅ Bootstrap a Python virtual environment
3. ✅ Install all required packages via `pacman` and `yay`
4. ✅ Deploy configuration files to `~/.config/`
5. ✅ Apply the default (Pharaoh) theme
6. ✅ Set up the AI agent

## Manual Install

If you prefer to review before executing:

```bash
git clone https://github.com/OssamaTaha/nous-land.git ~/.config/nous-land
cd ~/.config/nous-land
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 smart_installer.py
```

## LLM-Powered Self-Healing

The installer uses an LLM (via OpenRouter) to fix package installation errors automatically.

### Enable LLM Self-Healing

```bash
# Get an API key from https://openrouter.ai/
export OPENROUTER_API_KEY="sk-or-v1-..."

# Then run the installer
curl -fsSL https://raw.githubusercontent.com/OssamaTaha/nous-land/main/install.sh | bash
```

### How it works

1. Installer tries to install a package
2. If it fails, stderr is captured
3. LLM is asked: "How do I fix this?"
4. LLM returns a fix command (e.g., `pacman-key --refresh-keys`)
5. Fix is executed, then installer retries
6. Maximum 3 retries per package

### Without LLM

If no API key is set, the installer falls back to common fixes:
- Refreshing PGP keys
- Using `--overwrite '*'` for conflicting files
- Updating the system before retrying

## Post-Installation

### 1. Log out and log back in
Or reboot for clean state.

### 2. Select Your Session
At the login screen (GDM/SDDM), select:
- **Nous Land (Hyprland)** — For Hyprland session
- **Nous Land (Niri)** — For Niri session

### 3. Try the AI Agent
Press `Super+A` to open Hermes, your AI desktop assistant.

### 4. Switch Themes
```bash
nous-theme          # See current theme
nous-theme --list   # List all themes
nous-theme cyberpunk  # Switch to Cyberpunk theme
```

Or press `Super+T` for a GUI menu.

## Troubleshooting

### Package Installation Fails

```bash
# Check the install log
cat ~/.config/nous-land/install.log

# Try installing the failed package manually
sudo pacman -S <package-name>
```

### Theme Not Applying

```bash
# Check current theme
cat /tmp/nous-current-theme/current_theme.txt

# Re-apply theme
nous-theme <theme-name>
```

### AI Agent Not Responding

```bash
# Check if agent is running
ps aux | grep agent

# Start manually
python3 ~/.config/nous-agent/daemon.py &

# Check agent logs
cat ~/.config/nous-agent/agent.log
```

## Uninstall

```bash
# Remove configs
rm -rf ~/.config/hypr ~/.config/niri ~/.config/kitty
rm -rf ~/.config/waybar ~/.config/wofi ~/.config/swaync

# Remove nous-land
rm -rf ~/.config/nous-land

# Restore backups (if any)
ls ~/.config/nous-land-backup/
```
