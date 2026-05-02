#!/usr/bin/env python3
"""
NOUS LAND — System Tools
Safe system command whitelist for the AI agent.
"""

import re
import subprocess
from typing import Dict, Any

class SystemTools:
    """Safe system commands that the agent is allowed to execute."""
    
    # Whitelist of allowed commands (regex patterns)
    ALLOWED_PATTERNS = [
        r'^nous-theme\s+\w+$',
        r'^bash\s+~/.local/bin/nous-theme',
        r'^hyprctl\s+\w+',
        r'^niri\s+\w+',
        r'^pamixer\s+[\w\s\-]+$',
        r'^brightnessctl\s+set\s+[\w%]+$',
        r'^playerctl\s+\w+',
        r'^systemctl\s+--user\s+\w+\s+\w+',
        r'^killall\s+-SIG\w+\s+\w+$',
        r'^pacman\s+-Syu\s*',
        r'^yay\s+-Syu\s*',
        r'^neofetch$',
        r'^fastfetch$',
        r'^uname\s+-a$',
        r'^cat\s+/proc/\w+',
        r'^ps\s+aux\s*',
        r'^free\s*-h$',
        r'^df\s*-h$',
    ]
    
    def __init__(self):
        self.patterns = [re.compile(p) for p in self.ALLOWED_PATTERNS]
    
    def is_allowed(self, command: str) -> bool:
        """Check if a command is in the whitelist."""
        command = command.strip()
        return any(p.match(command) for p in self.patterns)
    
    def execute(self, command: str) -> Dict[str, Any]:
        """Execute a whitelisted system command."""
        if not self.is_allowed(command):
            return {
                "success": False,
                "output": "",
                "error": f"Command not allowed: {command}"
            }
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip(),
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}


if __name__ == "__main__":
    tools = SystemTools()
    print("System Tools loaded.")
    print(f"Allowed patterns: {len(tools.patterns)}")
