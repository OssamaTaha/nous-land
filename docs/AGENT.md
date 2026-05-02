# 🤖 AI Agent Guide

Hermes is your native OS assistant, living inside Nous Land as an integrated desktop agent.

## Invocation

Press **`Super+A`** to summon the floating AI chat interface.

> The agent daemon runs on `localhost:18789` and starts automatically via systemd user service.

## What Hermes Can Do

### 🎨 Theme Control
```
You: Switch to Cyberpunk theme
Hermes: [Executes: nous-theme cyberpunk]
Hermes: Theme switched to Cyberpunk! Neon lights activated. ✨
```

### 🔊 System Diagnostics
```
You: Why is my audio not working?
Hermes: Let me check... [Executes: pamixer get-volume]
Hermes: Your volume is at 0%. Try: pamixer -i 50
```

### 📦 System Updates
```
You: Update my system
Hermes: [Executes: pacman -Syu --noconfirm]
Hermes: System updated successfully! 42 packages upgraded.
```

### 💻 System Info
```
You: What's my system info?
Hermes: [Executes: neofetch]
Hermes: You're running Arch Linux (CachyOS) with Hyprland.
      CPU: AMD Ryzen 7, GPU: NVIDIA RTX 3080, RAM: 32GB
```

### 🎵 Media Control
```
You: Pause the music
Hermes: [Executes: playerctl play-pause]
Hermes: Music paused.
```

## How It Works

```
┌─────────────────────────────────────────┐
│  Super+A → ui.py (floating chat)       │
│            ↓                            │
│  localhost:18789 → daemon.py          │
│            ↓                            │
│  LLM API (OpenRouter) + System Tools  │
└─────────────────────────────────────────┘
```

### Components

| Component | File | Description |
|-----------|------|-------------|
| **Daemon** | `daemon.py` | Listens on port 18789, manages LLM, executes commands |
| **UI** | `ui.py` | Terminal-based chat interface (launchable as floating window) |
| **Tools** | `system_tools.py` | Whitelist of safe system commands |
| **Memory** | `memory.json` | Conversation history (last 100 messages) |

## Configuration

### API Key

Set your OpenRouter API key:

```bash
# Add to ~/.bashrc or ~/.zshrc
export OPENROUTER_API_KEY="sk-or-v1-..."

# Or set it for the agent service
systemctl --user edit nous-agent.service
# Add: Environment=OPENROUTER_API_KEY=sk-or-v1-...
```

### Changing the Model

```bash
export NOUS_AGENT_MODEL="anthropic/claude-3-haiku"
```

Default: `google/gemini-2.0-flash-lite`

## Security

Hermes uses a **command whitelist** for security. Only pre-approved commands can be executed:

- ✅ `nous-theme` (theme switching)
- ✅ `pamixer` (volume control)
- ✅ `brightnessctl` (brightness control)
- ✅ `playerctl` (media control)
- ✅ `pacman -Syu` (system update)
- ✅ `neofetch`, `free`, `df` (system info)
- ❌ `rm -rf /` (never allowed)
- ❌ `sudo` commands (not in whitelist)

To add custom commands, edit `system_tools.py`:

```python
# Add to ALLOWED_PATTERNS
r'^my-custom-command\s+\w+$',
```

## Memory

Hermes remembers the last 100 messages across sessions. Memory is stored in:

```
~/.config/nous-agent/memory.json
```

Clear memory:
```bash
rm ~/.config/nous-agent/memory.json
```

## Logs

Check agent logs:
```bash
cat ~/.config/nous-agent/agent.log
```

Check daemon status:
```bash
systemctl --user status nous-agent.service
```

## Extending Hermes

### Adding New Tools

1. Edit `system_tools.py`:
```python
def my_custom_tool(self, args: str) -> dict:
    # Your logic here
    return {"success": True, "output": "Done!"}
```

2. Update the LLM system message in `daemon.py` to mention the new tool.

3. Restart the agent:
```bash
systemctl --user restart nous-agent.service
```

## Troubleshooting

### Agent Not Responding

```bash
# Check if daemon is running
ps aux | grep agent

# Start manually
python3 ~/.config/nous-agent/daemon.py &

# Check logs
tail -f ~/.config/nous-agent/agent.log
```

### LLM Errors

```bash
# Verify API key
echo $OPENROUTER_API_KEY

# Test the API
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"google/gemini-2.0-flash-lite","messages":[{"role":"user","content":"Hello"}]}'
```

### UI Not Opening

```bash
# Check if Super+A keybind is set
grep "Super+A" ~/.config/hypr/keybinds.conf

# Try launching manually
python3 ~/.config/nous-agent/ui.py
```
