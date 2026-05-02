#!/usr/bin/env python3
"""
NOUS LAND — AI Agent UI
Floating drop-down chat interface.
Invoked via Super+A.
"""

import os
import sys
import json
import urllib.request
import threading
import time
from pathlib import Path

# ── Configuration ────────────────────────────────
AGENT_URL = "http://localhost:18789"
HISTORY_FILE = Path.home() / ".config" / "nous-agent" / "ui_history.txt"

# ── Terminal UI (simple) ─────────────────────────
def terminal_ui():
    """Simple terminal-based chat UI."""
    print("\033[1;36m" + "=" * 50 + "\033[0m")
    print("\033[1;36m  NOUS LAND — Hermes AI Agent\033[0m")
    print("\033[1;36m" + "=" * 50 + "\033[0m")
    print("Type 'quit' or 'exit' to close. Type 'clear' to clear history.\n")
    
    # Show current theme
    try:
        with urllib.request.urlopen(f"{AGENT_URL}/theme") as resp:
            data = json.loads(resp.read())
            print(f"\033[0;33mCurrent theme: {data.get('theme', 'none')}\033[0m\n")
    except:
        print("\033[0;31m[!] Agent daemon not running. Start it first.\033[0m\n")
        sys.exit(1)
    
    while True:
        try:
            user_input = input("\033[1;34mYou:\033[0m ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        
        if user_input.lower() == "clear":
            if HISTORY_FILE.exists():
                HISTORY_FILE.unlink()
            print("History cleared.\n")
            continue
        
        if not user_input.strip():
            continue
        
        # Send to agent
        try:
            payload = json.dumps({"message": user_input}).encode()
            req = urllib.request.Request(
                f"{AGENT_URL}/chat",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                response = data.get("response", "No response.")
                cmd_output = data.get("command_output")
                
                print(f"\033[1;32mHermes:\033[0m {response}")
                
                if cmd_output and cmd_output.get("success"):
                    print(f"\033[0;90m[Executed: {cmd_output.get('output', '')[:100]}]\033[0m")
                elif cmd_output and not cmd_output.get("success"):
                    print(f"\033[0;31m[Error: {cmd_output.get('error', '')}]\033[0m")
                print()
        except Exception as e:
            print(f"\033[0;31mError: {e}\033[0m\n")


# ── Entry Point ──────────────────────────────────
if __name__ == "__main__":
    terminal_ui()
