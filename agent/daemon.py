#!/usr/bin/env python3
"""
NOUS LAND — AI Desktop Agent Daemon
Hermes living natively within the OS as an integrated system assistant.

Listens on localhost:18789 for UI connections.
Holds API key, manages conversation memory, executes safe system commands.
"""

import os
import sys
import json
import subprocess
import threading
import signal
import logging
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import re

# ── Configuration ────────────────────────────────
AGENT_DIR = Path.home() / ".config" / "nous-agent"
MEMORY_FILE = AGENT_DIR / "memory.json"
LOG_FILE = AGENT_DIR / "agent.log"
SOCKET_HOST = "localhost"
SOCKET_PORT = 18789

# LLM Configuration
LLM_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
LLM_API_BASE = os.environ.get("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
LLM_MODEL = os.environ.get("NOUS_AGENT_MODEL", "google/gemini-2.0-flash-lite")

# ── Logging ──────────────────────────────────────
AGENT_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("nous-agent")

# ── System Tools (Whitelist) ────────────────────
class SystemTools:
    """Safe system commands that the agent is allowed to execute."""
    
    # Whitelist of allowed commands (regex patterns)
    ALLOWED_PATTERS = [
        r'^nous-theme\s+\w+$',           # Theme switching
        r'^bash\s+~/.local/bin/nous-theme',    # Theme scripts
        r'^hyprctl\s+\w+',                   # Hyprland control
        r'^niri\s+\w+',                       # Niri control
        r'^pamixer\s+[\w\s\-]+$',           # Volume control
        r'^brightnessctl\s+set\s+[\w%]+$',   # Brightness control
        r'^playerctl\s+\w+',                  # Media control
        r'^systemctl\s+--user\s+\w+\s+\w+', # Systemd user services
        r'^killall\s+-SIG\w+\s+\w+$',       # Signal processes
        r'^pacman\s+-Syu\s*',                # System update
        r'^yay\s+-Syu\s*',                    # AUR update
        r'^neofetch$',                          # System info
        r'^fastfetch$',                         # System info
        r'^uname\s+-a$',                       # Kernel info
        r'^cat\s+/proc/\w+',                  # Read proc info
        r'^ps\s+aux\s*',                      # List processes
        r'^free\s*-h$',                        # Memory info
        r'^df\s*-h$',                          # Disk info
    ]
    
    def __init__(self):
        self.patterns = [re.compile(p) for p in self.ALLOWED_PATTERS]
    
    def is_allowed(self, command: str) -> bool:
        """Check if a command is in the whitelist."""
        command = command.strip()
        return any(p.match(command) for p in self.patterns)
    
    def execute(self, command: str) -> dict:
        """Execute a whitelisted system command."""
        if not self.is_allowed(command):
            return {
                "success": False,
                "output": f"Command not allowed: {command}",
                "error": "Permission denied by security policy."
            }
        
        log.info(f"Executing: {command}")
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
            return {"success": False, "output": "", "error": "Command timed out (30s)."}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}


# ── Memory Manager ───────────────────────────────
class MemoryManager:
    """Manages conversation memory storage."""
    
    def __init__(self, path: Path):
        self.path = path
        self.memories = self._load()
    
    def _load(self) -> list:
        """Load memories from file."""
        if self.path.exists():
            try:
                with open(self.path) as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except Exception:
                pass
        return []
    
    def save(self):
        """Save memories to file."""
        with open(self.path, 'w') as f:
            json.dump(self.memories, f, indent=2)
    
    def add(self, role: str, content: str):
        """Add a memory entry."""
        self.memories.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        # Keep only last 100 messages
        if len(self.memories) > 100:
            self.memories = self.memories[-100:]
        self.save()
    
    def get_context(self, limit: int = 10) -> list:
        """Get recent conversation context."""
        return self.memories[-limit:] if self.memories else []


# ── LLM Client ───────────────────────────────────
class LLMClient:
    """Minimal LLM client for the agent."""
    
    def __init__(self):
        self.api_key = LLM_API_KEY
        self.api_base = LLM_API_BASE
        self.model = LLM_MODEL
        self.available = bool(self.api_key)
    
    def chat(self, messages: list) -> str:
        """Send chat messages and return response."""
        if not self.available:
            return "I'm sorry, but I don't have an LLM API key configured. Set OPENROUTER_API_KEY."
        
        try:
            import requests
            
            system_msg = (
                "You are Hermes, an AI desktop assistant living natively within the Nous Land "
                "Linux environment (Hyprland/Niri on Arch/CachyOS). "
                "You can control the system through safe commands."
                "Available actions: switch themes (nous-theme <name>), "
                "control volume (pamixer), brightness (brightnessctl), "
                "media (playerctl), system info (neofetch, free, df), "
                "and update the system (pacman -Syu). "
                "Be concise, helpful, and action-oriented. "
                "When asked to perform an action, respond with the command to run."
            )
            
            full_messages = [{"role": "system", "content": system_msg}] + messages
            
            resp = requests.post(
                f"{self.api_base}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "messages": full_messages, "max_tokens": 1024, "temperature": 0.7},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            log.error(f"LLM request failed: {e}")
            return f"I encountered an error: {str(e)}"


# ── HTTP Request Handler ─────────────────────────
class AgentHandler(BaseHTTPRequestHandler):
    """HTTP handler for agent API."""
    
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        
        if parsed.path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({"status": "ok", "model": LLM_MODEL}).encode())
        elif parsed.path == "/memory":
            limit = int(parse_qs(parsed.query).get("limit", [10])[0])
            context = agent.memory.get_context(limit)
            self._set_headers()
            self.wfile.write(json.dumps({"memories": context}).encode())
        elif parsed.path == "/theme":
            tmp_dir = Path("/tmp/nous-current-theme")
            if (tmp_dir / "current_theme.txt").exists():
                theme = (tmp_dir / "current_theme.txt").read_text().strip()
            else:
                theme = "none"
            self._set_headers()
            self.wfile.write(json.dumps({"theme": theme}).encode())
        else:
            self._set_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else ""
        
        if parsed.path == "/chat":
            try:
                data = json.loads(body)
                user_msg = data.get("message", "")
                
                # Add user message to memory
                agent.memory.add("user", user_msg)
                
                # Get context and call LLM
                context = agent.memory.get_context(10)
                response = agent.llm.chat(context)
                
                # Add assistant response to memory
                agent.memory.add("assistant", response)
                
                # Check if response contains a command to execute
                tools = SystemTools()
                lines = response.split("\n")
                command_output = None
                clean_response = response
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("$") or line.startswith("#") or line.startswith("`"):
                        cmd = line.lstrip("$").lstrip("#").strip("`")
                        if tools.is_allowed(cmd):
                            result = tools.execute(cmd)
                            command_output = result
                            break
                
                self._set_headers()
                self.wfile.write(json.dumps({
                    "response": clean_response,
                    "command_output": command_output,
                }).encode())
            except Exception as e:
                log.error(f"Chat error: {e}")
                self._set_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        elif parsed.path == "/execute":
            try:
                data = json.loads(body)
                command = data.get("command", "")
                result = agent.tools.execute(command)
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self._set_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        else:
            self._set_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def log_message(self, format, *args):
        """Silence default logging."""
        pass


# ── Main Agent ───────────────────────────────────
class Agent:
    """Main agent instance."""
    
    def __init__(self):
        self.memory = MemoryManager(MEMORY_FILE)
        self.llm = LLMClient()
        self.tools = SystemTools()
        self.server = None
    
    def start(self):
        """Start the HTTP server."""
        log.info(f"Starting Nous Land Agent on {SOCKET_HOST}:{SOCKET_PORT}...")
        log.info(f"LLM available: {self.llm.available} (model: {LLM_MODEL})")
        
        self.server = HTTPServer((SOCKET_HOST, SOCKET_PORT), AgentHandler)
        
        # Handle shutdown gracefully
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        log.info("Agent started. Listening for requests...")
        self.server.serve_forever()
    
    def _signal_handler(self, sig, frame):
        log.info("Shutting down agent...")
        if self.server:
            self.server.shutdown()
        sys.exit(0)


# ── Entry Point ──────────────────────────────────
if __name__ == "__main__":
    agent = Agent()
    agent.start()
