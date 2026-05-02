#!/usr/bin/env python3
"""
nous-land smart_installer.py
An LLM-powered installer that self-heals when package installation fails.
"""

import subprocess
import sys
import os
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime

# ── Configuration ────────────────────────────────
REPA_DIR = Path(__file__).parent
LOG_FILE = REPA_DIR / "install.log"
THEMES_DIR = REPA_DIR / "themes"
CONFIGS_DIR = REPA_DIR / "configs"
SCRIPTS_DIR = REPA_DIR / "scripts"
BACKUP_DIR = Path.home() / ".config" / "nous-land-backup"
# Load .env file if it exists (for saved API key)
env_file = REPA_DIR / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    print(f"[env] Loaded API key from .env file")

# LLM Configuration (user can override via env vars)
LLM_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
LLM_API_BASE = os.environ.get("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
LLM_MODEL = os.environ.get("NOUS_INSTALLER_MODEL", "google/gemini-2.0-flash-lite")

# ── Logging ──────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("nous-installer")


# ── Package Definitions ──────────────────────────
PACMAN_PACKAGES = [
    "hyprland",
    "waybar",
    "kitty",
    "wofi",
    "swaync",
    "mako",
    "rofi",
    "hyprpaper",
    "hyprlock",
    "hypridle",
    "xdg-desktop-portal-hyprland",
    "xdg-desktop-portal-gtk",
    "polkit-gnome",
    "grim",
    "slurp",
    "wl-clipboard",
    "swappy",
    "brightnessctl",
    "pamixer",
    "playerctl",
    "network-manager-applet",
    "blueberry",
    "ttf-jetbrains-mono-nerd",
    "ttf-font-awesome",
    "noto-fonts-emoji",
    "python",
    "python-pip",
    "python-virtualenv",
    "git",
    "curl",
    "jq",
    "swww",
    "niri",
]

AUR_PACKAGES = [
    "swaylock-effects",
    "wlogout",
    "nwg-look",
    "bibata-cursor-theme",
]

PIP_PACKAGES = [
    "requests>=2.31.0",
    "textual>=0.62.0",
]


# ── LLM Client ───────────────────────────────────
class LLMClient:
    """Minimal LLM client for self-healing installation errors."""

    def __init__(self):
        self.api_key = LLM_API_KEY
        self.api_base = LLM_API_BASE
        self.model = LLM_MODEL
        self.available = bool(self.api_key)

    def ask(self, prompt: str, context: str = "") -> str:
        """Send a prompt to the LLM and return the response."""
        if not self.available:
            log.warning("No LLM API key configured. Self-healing disabled.")
            return ""

        try:
            import requests

            system_msg = (
                "You are an expert Linux systems architect specializing in Arch Linux (CachyOS) package management. "
                "Your job: given a pacman/yay error, respond with ONLY the exact terminal command(s) to fix it. "
                "Rules: "
                "1. Return ONLY executable bash commands, no explanations, no markdown. "
                "2. Chain multiple commands with && if needed. "
                "3. For 'invalid or corrupted package' or PGP errors: use 'sudo pacman-key --refresh-keys && sudo pacman -Sy archlinux-keyring --noconfirm'. "
                "4. For 'conflicting files' errors: use 'sudo pacman -S --noconfirm --needed --overwrite \"*\" <package>'. "
                "5. For 'target not found': suggest 'yay -S <package>' or check AUR. "
                "6. For 'could not satisfy dependencies': use 'sudo pacman -Syu --noconfirm' first. "
                "7. For database lock issues: use 'sudo rm /var/lib/pacman/db.lck'. "
                "8. Always prefer pacman/yay solutions. "
                "9. Never suggest destructive operations like 'rm -rf /' or 'mkfs'. "
                "10. Prepend 'sudo' to commands that need root privileges."
           )

            messages = [{"role": "system", "content": system_msg}]
            if context:
                messages.append({"role": "user", "content": f"Context:\n{context}"})
            messages.append({"role": "user", "content": prompt})

            resp = requests.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 512,
                    "temperature": 0.1,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

        except Exception as e:
            log.error(f"LLM request failed: {e}")
            return ""


# ── Command Runner ───────────────────────────────
def run_command(cmd: str, check: bool = True, sudo: bool = False, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    if sudo and os.geteuid() != 0:
        cmd = f"sudo {cmd}"

    log.info(f"Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=capture,
        text=True,
    )

    if result.returncode != 0 and check:
        log.warning(f"Command failed (exit {result.returncode})")
        if result.stderr:
            log.warning(f"stderr: {result.stderr.strip()}")

    return result


# ── Self-Healing Installer ───────────────────────
class SmartInstaller:
    """Installs packages with LLM-powered error recovery."""

    MAX_RETRIES = 3

    def __init__(self):
        self.llm = LLMClient()
        self.failed_packages = []
        self.installed_packages = []

    def install_pacman(self, packages: list):
        """Install packages via pacman with self-healing."""
        log.info(f"Installing {len(packages)} pacman packages...")

        # Batch install first attempt
        pkg_str = " ".join(packages)
        result = run_command(f"pacman -S --noconfirm --needed {pkg_str}", check=False, sudo=True)

        if result.returncode == 0:
            self.installed_packages.extend(packages)
            log.info("All pacman packages installed successfully.")
            return

        # If batch failed, try individually and self-heal
        log.warning("Batch install failed. Trying packages individually...")
        for pkg in packages:
            self._install_single_pacman(pkg)

    def _install_single_pacman(self, pkg: str):
        """Install a single pacman package with retry and LLM healing."""
        for attempt in range(1, self.MAX_RETRIES + 1):
            log.info(f"  Installing {pkg} (attempt {attempt}/{self.MAX_RETRIES})...")
            result = run_command(f"pacman -S --noconfirm --needed {pkg}", check=False, sudo=True)

            if result.returncode == 0:
                self.installed_packages.append(pkg)
                log.info(f"  ✓ {pkg} installed.")
                return

            log.warning(f"  ✗ {pkg} failed (attempt {attempt})")
            stderr = result.stderr.strip() if result.stderr else ""
            stdout = result.stdout.strip() if result.stdout else ""

            if self.llm.available and attempt < self.MAX_RETRIES:
                log.info(f"  Asking LLM for fix...")
                fix_cmd = self.llm.ask(
                    prompt=f"pacman failed to install '{pkg}'.\n\nstderr:\n{stderr}\n\nstdout:\n{stdout}\n\nWhat command fixes this?",
                    context=f"Arch Linux CachyOS. Package: {pkg}. Attempt {attempt}.",
                )
                if fix_cmd:
                    log.info(f"  LLM suggests: {fix_cmd}")
                    run_command(fix_cmd, check=False, sudo=True)
                else:
                    log.warning("  LLM returned no fix. Trying common remedies...")
                    self._try_common_fixes(pkg, stderr)
            else:
                self._try_common_fixes(pkg, stderr)

        self.failed_packages.append(pkg)
        log.error(f"  ✗ {pkg} could not be installed after {self.MAX_RETRIES} attempts.")

    def _try_common_fixes(self, pkg: str, stderr: str):
        """Try common Arch Linux fixes without LLM."""
        stderr_lower = stderr.lower()

        if "invalid or corrupted package" in stderr_lower or "pgp" in stderr_lower:
            log.info("  → Refreshing PGP keys...")
            run_command("pacman-key --refresh-keys", check=False, sudo=True)
            run_command("pacman -Sy archlinux-keyring --noconfirm", check=False, sudo=True)

        elif "conflicting files" in stderr_lower:
            log.info("  → Trying with --overwrite...")
            run_command(f"pacman -S --noconfirm --needed --overwrite '*' {pkg}", check=False, sudo=True)

        elif "target not found" in stderr_lower:
            log.info(f"  → Package '{pkg}' not in repos. Will try AUR.")
            self._install_single_aur(pkg)

        elif "could not satisfy dependencies" in stderr_lower:
            log.info("  → Updating system first...")
            run_command("pacman -Syu --noconfirm", check=False, sudo=True)

    def install_aur(self, packages: list):
        """Install AUR packages via yay or paru."""
        helper = self._detect_aur_helper()
        if not helper:
            log.info("No AUR helper found. Installing yay...")
            self._install_yay()
            helper = "yay"

        log.info(f"Installing {len(packages)} AUR packages via {helper}...")
        for pkg in packages:
            self._install_single_aur(pkg, helper)

    def _detect_aur_helper(self) -> str | None:
        for helper in ["yay", "paru"]:
            if shutil.which(helper):
                return helper
        return None

    def _install_yay(self):
        """Install yay AUR helper."""
        tmp = "/tmp/yay-install"
        run_command(f"rm -rf {tmp}", check=False)
        run_command(f"git clone https://aur.archlinux.org/yay.git {tmp}", check=False)
        run_command(f"cd {tmp} && makepkg -si --noconfirm", check=False)

    def _install_single_aur(self, pkg: str, helper: str = "yay"):
        """Install a single AUR package."""
        for attempt in range(1, self.MAX_RETRIES + 1):
            log.info(f"  Installing {pkg} from AUR (attempt {attempt})...")
            result = run_command(f"{helper} -S --noconfirm --needed {pkg}", check=False)

            if result.returncode == 0:
                self.installed_packages.append(pkg)
                log.info(f"  ✓ {pkg} installed from AUR.")
                return

            stderr = result.stderr.strip() if result.stderr else ""
            log.warning(f"  ✗ AUR install failed for {pkg}")

            if self.llm.available and attempt < self.MAX_RETRIES:
                fix_cmd = self.llm.ask(
                    prompt=f"AUR helper failed to install '{pkg}'.\n\nstderr:\n{stderr}\n\nFix command:",
                    context="Arch Linux CachyOS. AUR package installation.",
                )
                if fix_cmd:
                    log.info(f"  LLM suggests: {fix_cmd}")
                    run_command(fix_cmd, check=False)

        self.failed_packages.append(pkg)
        log.error(f"  ✗ {pkg} could not be installed from AUR.")

    def install_pip(self, packages: list):
        """Install Python packages in the venv."""
        venv_pip = REPO_DIR / ".venv" / "bin" / "pip"
        if not venv_pip.exists():
            log.error("Virtual environment not found. Run install.sh first.")
            return

        for pkg in packages:
            result = run_command(f"{venv_pip} install {pkg}", check=False)
            if result.returncode == 0:
                log.info(f"  ✓ pip package {pkg} installed.")
            else:
                log.error(f"  ✗ pip package {pkg} failed.")

    def backup_existing(self):
        """Backup existing dotfiles before overwriting."""
        if not BACKUP_DIR.exists():
            BACKUP_DIR.mkdir(parents=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / timestamp
        backup_path.mkdir()

        configs_to_backup = [
            Path.home() / ".config" / "hypr",
            Path.home() / ".config" / "niri",
            Path.home() / ".config" / "kitty",
            Path.home() / ".config" / "waybar",
            Path.home() / ".config" / "wofi",
            Path.home() / ".config" / "swaync",
            Path.home() / ".config" / "rofi",
            Path.home() / ".config" / "mako",
        ]

        backed_up = False
        for cfg in configs_to_backup:
            if cfg.exists():
                dest = backup_path / cfg.name
                shutil.copytree(cfg, dest, dirs_exist_ok=True)
                backed_up = True
                log.info(f"  Backed up {cfg} → {dest}")

        if backed_up:
            log.info(f"Backups saved to {backup_path}")
        else:
            log.info("No existing configs to backup.")

    def deploy_configs(self):
        """Deploy configuration files to ~/.config/."""
        log.info("Deploying configurations...")

        config_mappings = {
            "hyprland": ".config/hypr",
            "niri": ".config/niri",
            "kitty": ".config/kitty",
            "waybar": ".config/waybar",
            "wofi": ".config/wofi",
            "swaync": ".config/swaync",
            "rofi": ".config/rofi",
            "mako": ".config/mako",
        }

        for src_name, dest_path in config_mappings.items():
            src = CONFIGS_DIR / src_name
            dest = Path.home() / dest_path

            if src.exists():
                dest.mkdir(parents=True, exist_ok=True)
                # Copy contents
                for item in src.iterdir():
                    if item.is_file():
                        shutil.copy2(item, dest / item.name)
                    elif item.is_dir():
                        shutil.copytree(item, dest / item.name, dirs_exist_ok=True)
                log.info(f"  Deployed {src_name} → {dest}")

        # Deploy scripts
        bin_dir = Path.home() / ".local" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        for script in SCRIPTS_DIR.iterdir():
            if script.suffix == ".sh":
                dest = bin_dir / script.stem
                shutil.copy2(script, dest)
                dest.chmod(0o755)
                log.info(f"  Installed script: {script.stem}")

        # Deploy agent
        agent_dest = Path.home() / ".config" / "nous-agent"
        agent_src = REPO_DIR / "agent"
        if agent_src.exists():
            shutil.copytree(agent_src, agent_dest, dirs_exist_ok=True)
            # Make agent scripts executable
            for f in agent_dest.iterdir():
                if f.suffix == ".py":
                    f.chmod(0o755)
            log.info(f"  Deployed agent → {agent_dest}")

        # Install systemd units
        systemd_user = Path.home() / ".config" / "systemd" / "user"
        systemd_src = REPO_DIR / "systemd"
        if systemd_src.exists():
            systemd_user.mkdir(parents=True, exist_ok=True)
            for unit in systemd_src.iterdir():
                shutil.copy2(unit, systemd_user / unit.name)
            run_command("systemctl --user daemon-reload", check=False)
            log.info("  Installed systemd user units.")

    def apply_default_theme(self):
        """Apply the first available theme as default."""
        # Find first available theme
        default_theme = None
        if THEMES_DIR.exists():
            for d in sorted(THEMES_DIR.iterdir()):
                if d.is_dir() and (d / "theme.json").exists():
                    default_theme = d.name
                    break

        if not default_theme:
            log.warning("No themes found.")
            return

        log.info(f"Applying default theme: {default_theme}")
        switcher = SCRIPTS_DIR / "theme-switcher.sh"
        if switcher.exists():
            run_command(f"bash {switcher} {default_theme}", check=False)
        else:
            log.warning("theme-switcher.sh not found. Skipping theme application.")

    def print_summary(self):
        """Print installation summary."""
        print("\n" + "=" * 50)
        print("  NOUS LAND — Installation Summary")
        print("=" * 50)
        print(f"  Installed: {len(self.installed_packages)} packages")
        if self.failed_packages:
            print(f"  Failed:    {len(self.failed_packages)} packages")
            for pkg in self.failed_packages:
                print(f"    - {pkg}")
        else:
            print("  Failed:    None ✓")
        print(f"  Log file:  {LOG_FILE}")
        print("=" * 50)

        if self.failed_packages:
            print("\n  Some packages failed. You can:")
            print("  1. Check the log: cat ~/.config/nous-land/install.log")
            print("  2. Set OPENROUTER_API_KEY and re-run for LLM self-healing")
            print("  3. Install failed packages manually")


# ── Main ─────────────────────────────────────────
def main():
    # ── Interactive API Key Prompt ────────────────
    if not LLM_API_KEY:
        print("\n" + "="*50)
        print("  NOUS LAND — LLM Self-Healing Setup")
        print("="*50)
        print("\nNo OPENROUTER_API_KEY found. LLM self-healing is DISABLED.")
        print("To enable smart error recovery, enter your OpenRouter API key below.")
        print("Get one at: https://openrouter.ai/keys\n")
        
        try:
            user_key = input("Enter OPENROUTER_API_KEY (or press Enter to skip): ").strip()
            if user_key:
                LLM_API_KEY = user_key
                # Save to .env for future runs
                env_file = REPO_DIR / ".env"
                with open(env_file, "w") as f:
                    f.write(f"OPENROUTER_API_KEY={user_key}\n")
                os.environ["OPENROUTER_API_KEY"] = user_key
                print("✓ API key saved to .env file.\n")
        except (EOFError, KeyboardInterrupt):
            print("\nSkipping LLM setup. Self-healing disabled.\n")

    installer = SmartInstaller()

    log.info("=" * 50)
    log.info("NOUS LAND — Smart Installer Starting")
    log.info(f"LLM self-healing: {'ENABLED' if installer.llm.available else 'DISABLED (set OPENROUTER_API_KEY)'}")
    log.info("=" * 50)

    # Step 1: Backup
    log.info("\n── Step 1: Backing up existing configs ──")
    installer.backup_existing()

    # Step 2: Install pacman packages
    log.info("\n── Step 2: Installing pacman packages ──")
    installer.install_pacman(PACMAN_PACKAGES)

    # Step 3: Install AUR packages
    log.info("\n── Step 3: Installing AUR packages ──")
    installer.install_aur(AUR_PACKAGES)

    # Step 4: Install pip packages
    log.info("\n── Step 4: Installing Python packages ──")
    installer.install_pip(PIP_PACKAGES)

    # Step 5: Deploy configs
    log.info("\n── Step 5: Deploying configurations ──")
    installer.deploy_configs()

    # Step 6: Apply default theme
    log.info("\n── Step 6: Applying default theme ──")
    installer.apply_default_theme()

    # Summary
    installer.print_summary()

    sys.exit(0 if not installer.failed_packages else 1)


if __name__ == "__main__":
    main()
