# ⌨️ Keybinds Reference

All keybinds are shared between **Hyprland** and **Niri** with the same keybind philosophy.

## Notation

- `Super` = Windows/Command key
- `Shift`, `Ctrl`, `Alt` = Modifier keys
- `Arrows` = Left, Right, Up, Down

## Launching Apps

| Keybind | Action |
|---------|--------|
| `Super+Q` | Open Kitty terminal |
| `Super+Space` | Open Wofi launcher (drun mode) |
| `Super+Shift+Space` | Open Wofi launcher (run mode) |
| `Super+A` | Open Hermes AI Agent |

## Window Management

| Keybind | Action |
|---------|--------|
| `Super+C` | Close active window |
| `Super+Shift+C` | Force kill active window |
| `Super+V` | Toggle floating mode |
| `Super+Shift+V` | Force float window |
| `Super+F` | Toggle fullscreen |
| `Super+Shift+F` | Toggle fullscreen (alt) |
| `Super+T` | Toggle split (dwindle) |
| `Super+Shift+T` | Toggle pseudotile |
| `Super+G` | Toggle gaps on/off |
| `Super+Shift+G` | Reset gaps to 0 |

## Navigation (Focus)

| Keybind | Action |
|---------|--------|
| `Super+Left` | Move focus left |
| `Super+Right` | Move focus right |
| `Super+Up` | Move focus up |
| `Super+Down` | Move focus down |

## Moving Windows (Swap)

| Keybind | Action |
|---------|--------|
| `Super+Alt+Left` | Swap window left |
| `Super+Alt+Right` | Swap window right |
| `Super+Alt+Up` | Swap window up |
| `Super+Alt+Down` | Swap window down |

## Resizing

| Keybind | Action |
|---------|--------|
| `Super+Ctrl+Left` | Shrink width |
| `Super+Ctrl+Right` | Expand width |
| `Super+Ctrl+Up` | Shrink height |
| `Super+Ctrl+Down` | Expand height |

## Workspaces

| Keybind | Action |
|---------|--------|
| `Super+1` to `Super+0` | Switch to workspace 1-10 |
| `Super+Shift+1` to `Super+Shift+0` | Move window to workspace 1-10 |
| `Super+S` | Toggle special workspace (scratchpad) |
| `Super+Shift+S` | Move window to special workspace |

## System Controls

| Keybind | Action |
|---------|--------|
| `Super+Shift+R` | Reload config (Hyprland: `hyprctl reload`, Niri: `reload-config`) |
| `Super+Shift+Q` | Exit compositor |
| `Super+Shift+L` | Lock screen (hyprlock) |
| `Super+T` | Theme switcher GUI |
| `Super+Shift+T` | Hot-reload theme |

## Media & Hardware

| Keybind | Action |
|---------|--------|
| `Print` | Screenshot (area selection with slurp) |
| `Shift+Print` | Full screenshot |
| `XF86AudioRaiseVolume` | Volume up (+5%) |
| `XF86AudioLowerVolume` | Volume down (-5%) |
| `XF86AudioMute` | Toggle mute |
| `XF86MonBrightnessUp` | Brightness up (+5%) |
| `XF86MonBrightnessDown` | Brightness down (-5%) |
| `XF86AudioPlay` | Play/Pause media |
| `XF86AudioNext` | Next track |
| `XF86AudioPrev` | Previous track |
| `Super+X` | Color picker (hyprpicker) |

## Hyprland-Specific

| Keybind | Action |
|---------|--------|
| `Super+P` | Toggle pseudotile |
| `Super+Shift+P` | Toggle pseudotile (alt) |

## Niri-Specific

Niri uses scrollable tiling. Windows in a workspace form a scrollable strip.

| Keybind | Action |
|---------|--------|
| `Super+Scroll` | Scroll through windows |
| `Super+H` | Toggle horizontal layout |
| `Super+Shift+H` | Reset layout |

## Customizing Keybinds

### Hyprland
Edit `~/.config/hypr/keybinds.conf`:

```bash
# Example: Change terminal keybind
bind = $mainMod, T, exec, alacritty
```

Then reload: `Super+Shift+R`

### Niri
Edit `~/.config/niri/binds.kdl`:

```kdl
// Example: Change terminal keybind
bind "Super+T" { spawn "alacritty"; }
```

Then reload: `Super+Shift+R`
