#!/usr/bin/env python3
"""
setup_wizard.py — Nous Land Interactive Setup Wizard
A Textual TUI for configuring API keys and LLM model selection.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Static, Input, Button, RadioSet, RadioButton
from textual.screen import Screen
from textual import on
from textual.reactive import reactive
import os
import sys
from pathlib import Path
import requests

# ── Configuration ──────────────────────────────────
REPO_DIR = Path(__file__).parent
ENV_FILE = REPO_DIR / ".env"

# Nous Research aesthetic colors
NOUS_BG = "#0a0a0a"
NOUS_SURFACE = "#1a1a1a"
NOUS_ACCENT = "#d4a017"  # Amber/gold
NOUS_ACCENT_DIM = "#8b6b10"
NOUS_TEXT = "#ffffff"
NOUS_TEXT_DIM = "#888888"


class APIKeyScreen(Screen):
    """Step 1: API Key input."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(classes="screen-container"):
            yield Static("⛩ NOUS LAND — SETUP WIZARD", classes="title")
            yield Static("Step 1 of 3: API Key Configuration", classes="subtitle")

            yield Static("", classes="spacer")

            # Check if key already exists
            existing_key = ""
            if ENV_FILE.exists():
                with open(ENV_FILE) as f:
                    for line in f:
                        if line.strip().startswith("OPENROUTER_API_KEY="):
                            existing_key = line.strip().split("=", 1)[1]
                            break

            if existing_key and existing_key != "***":
                yield Static(f"✓ API key found: {existing_key[:10]}...{existing_key[-4:]}", classes="status-ok")
                yield Static("", classes="spacer")
                yield Static("Enter new key to replace (or leave blank to keep current):", classes="label")
            else:
                yield Static("No API key found. Enter your OpenRouter API key:", classes="label")
                yield Static("Get one at: https://openrouter.ai/keys", classes="hint")

            yield Input(
                placeholder="sk-... (leave blank to skip LLM features)",
                password=True,  # Mask the key
                id="api-key-input"
            )

            yield Static("", classes="spacer")

            with Horizontal(classes="button-row"):
                yield Button("Skip (No AI)", id="skip-btn", classes="btn-secondary")
                yield Button("Continue →", id="continue-btn", classes="btn-primary")

        yield Footer()

    @on(Button.Pressed, "#continue-btn")
    def on_continue(self):
        api_input = self.query_one("#api-key-input", Input)
        key = api_input.value.strip()

        # If key provided, validate it
        if key:
            self.app.notify("Validating API key...", title="Please wait")
            try:
                headers = {"Authorization": f"Bearer {key}"}
                resp = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
                if resp.status_code == 200:
                    self.app.api_key = key
                    self.app.notify("✓ API key validated!", title="Success")
                    self.app.push_screen(ModelSelectScreen())
                else:
                    self.app.notify(f"✗ Invalid API key (HTTP {resp.status_code})", title="Error", severity="error")
            except Exception as e:
                self.app.notify(f"✗ Could not validate key: {e}", title="Error", severity="error")
        else:
            # Keep existing key or skip
            existing = ""
            if ENV_FILE.exists():
                with open(ENV_FILE) as f:
                    for line in f:
                        if line.strip().startswith("OPENROUTER_API_KEY="):
                            existing = line.strip().split("=", 1)[1]
                            break
            self.app.api_key = existing if existing and existing != "***" else ""
            self.app.push_screen(ModelSelectScreen())

    @on(Button.Pressed, "#skip-btn")
    def on_skip(self):
        self.app.api_key = ""
        self.app.notify("Skipping LLM setup", title="Info")
        self.app.push_screen(ModelSelectScreen())

    @on(Input.Submitted, "#api-key-input")
    def on_input_submit(self):
        self.on_continue()


class ModelSelectScreen(Screen):
    """Step 2: Model selection from OpenRouter."""

    models = reactive([])

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(classes="screen-container"):
            yield Static("⛩ NOUS LAND — SETUP WIZARD", classes="title")
            yield Static("Step 2 of 3: LLM Model Selection", classes="subtitle")

            yield Static("", classes="spacer")

            if self.app.api_key:
                yield Static("✓ API key configured — fetching available models...", classes="status-ok")
                self.fetch_models()
            else:
                yield Static("No API key — using default model", classes="status-warn")

            yield Static("Select an LLM model:", classes="label")

            with RadioSet(id="model-radio"):
                # Default free models as fallback
                defaults = [
                    ("openrouter/free", "OpenRouter Free (Auto)"),
                    ("google/gemini-flash-1.5:free", "Google Gemini Flash 1.5 (Free)"),
                    ("meta-llama/llama-3.1-8b-instruct:free", "Meta Llama 3.1 8B (Free)"),
                    ("microsoft/phi-3-medium-128k-instruct:free", "Microsoft Phi-3 Medium (Free)"),
                    ("nousresearch/hermes-3-llama-3.1-8b:free", "Nous Hermes 3 8B (Free)"),
                ]
                for model_id, label in defaults:
                    yield RadioButton(label, id=f"model-{model_id}")

            yield Static("", classes="spacer")
            yield Static("Or enter a custom model ID:", classes="label")
            yield Input(placeholder="e.g., anthropic/claude-3.5-sonnet", id="custom-model-input")

            yield Static("", classes="spacer")

            with Horizontal(classes="button-row"):
                yield Button("← Back", id="back-btn", classes="btn-secondary")
                yield Button("Continue →", id="continue-btn", classes="btn-primary")

        yield Footer()

    def fetch_models(self):
        """Fetch free models from OpenRouter API."""
        try:
            headers = {"Authorization": f"Bearer {self.app.api_key}"}
            resp = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
            if resp.status_code == 200:
                all_models = resp.json().get("data", [])
                free_models = [m for m in all_models if ":free" in m.get("id", "").lower()][:10]
                if free_models:
                    radio_set = self.query_one("#model-radio", RadioSet)
                    radio_set.remove_children()
                    for m in free_models:
                        radio_set.mount(RadioButton(m["id"], id=f"model-{m['id']}"))
        except Exception:
            pass  # Use defaults

    @on(Button.Pressed, "#continue-btn")
    def on_continue(self):
        radio_set = self.query_one("#model-radio", RadioSet)
        custom_input = self.query_one("#custom-model-input", Input)

        selected = radio_set.pressed_button
        custom = custom_input.value.strip()

        if custom:
            self.app.model = custom
        elif selected:
            # Extract model ID from button id (remove "model-" prefix)
            btn_id = selected.id
            self.app.model = btn_id[6:] if btn_id and btn_id.startswith("model-") else (btn_id or "openrouter/free")
        else:
            self.app.model = "openrouter/free"  # Default

        self.app.notify(f"Selected model: {self.app.model}", title="Model")
        self.app.push_screen(SaveScreen())

    @on(Button.Pressed, "#back-btn")
    def on_back(self):
        self.app.pop_screen()

    @on(Input.Submitted, "#custom-model-input")
    def on_input_submit(self):
        self.on_continue()


class SaveScreen(Screen):
    """Step 3: Save configuration and start installation."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(classes="screen-container"):
            yield Static("⛩ NOUS LAND — SETUP WIZARD", classes="title")
            yield Static("Step 3 of 3: Save & Start Installation", classes="subtitle")

            yield Static("", classes="spacer")

            # Show summary
            yield Static("Configuration Summary:", classes="label")
            yield Static(f"  API Key: {'✓ Configured' if self.app.api_key else '✗ Not set (LLM disabled)'}", classes="summary")
            yield Static(f"  Model: {self.app.model}", classes="summary")

            yield Static("", classes="spacer")

            yield Static("Settings will be saved to: .env", classes="hint")
            yield Static("The smart installer will start automatically.", classes="hint")

            yield Static("", classes="spacer")

            with Horizontal(classes="button-row"):
                yield Button("← Back", id="back-btn", classes="btn-secondary")
                yield Button("START INSTALLATION", id="start-btn", classes="btn-primary")

        yield Footer()

    def on_mount(self):
        # Auto-save config when screen loads
        self.save_config()

    def save_config(self):
        """Save API key and model to .env file."""
        try:
            lines = []
            if ENV_FILE.exists():
                with open(ENV_FILE) as f:
                    lines = f.readlines()

            # Update or add OPENROUTER_API_KEY
            key_line = f"OPENROUTER_API_KEY={self.app.api_key}\n" if self.app.api_key else None
            model_line = f"NOUS_INSTALLER_MODEL={self.app.model}\n" if self.app.model else None

            # Remove existing lines
            lines = [l for l in lines if not l.startswith("OPENROUTER_API_KEY=") and not l.startswith("NOUS_INSTALLER_MODEL=")]

            if key_line:
                lines.append(key_line)
            if model_line:
                lines.append(model_line)

            with open(ENV_FILE, "w") as f:
                f.writelines(lines)

            # Update environ
            if self.app.api_key:
                os.environ["OPENROUTER_API_KEY"] = self.app.api_key
            if self.app.model:
                os.environ["NOUS_INSTALLER_MODEL"] = self.app.model

            self.app.notify("✓ Configuration saved!", title="Success")
        except Exception as e:
            self.app.notify(f"✗ Failed to save config: {e}", title="Error", severity="error")

    @on(Button.Pressed, "#start-btn")
    def on_start(self):
        self.app.exit(0)  # Exit with success code

    @on(Button.Pressed, "#back-btn")
    def on_back(self):
        self.app.pop_screen()


class SetupWizard(App):
    """Main Textual application for Nous Land setup."""

    CSS = """
    Screen {
        background: #0a0a0a;
        color: #ffffff;
    }

    Header {
        background: #1a1a1a;
        color: #d4a017;
        text-style: bold;
        padding: 1;
    }

    Footer {
        background: #1a1a1a;
        color: #888888;
    }

    .screen-container {
        width: 80%;
        height: 80%;
        background: #1a1a1a;
        border: thick #d4a017;
        padding: 2;
        align: center top;
    }

    .title {
        text-align: center;
        color: #d4a017;
        text-style: bold;
        margin-bottom: 1;
    }

    .subtitle {
        text-align: center;
        color: #888888;
        margin-bottom: 2;
    }

    .label {
        color: #ffffff;
        margin-bottom: 1;
    }

    .hint {
        color: #888888;
        text-style: italic;
        margin-bottom: 1;
    }

    .status-ok {
        color: $success;
        text-style: bold;
        margin-bottom: 1;
    }

    .status-warn {
        color: $warning;
        text-style: bold;
        margin-bottom: 1;
    }

    .summary {
        color: #ffffff;
        margin-bottom: 1;
    }

    .spacer {
        height: 1;
    }

    Input {
        width: 100%;
        margin-bottom: 1;
    }

    RadioSet {
        width: 100%;
        margin-bottom: 1;
    }

    RadioButton {
        margin-bottom: 1;
    }

    .button-row {
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 2;
        min-width: 20;
    }

    .btn-primary {
        background: #d4a017;
        color: #0a0a0a;
        text-style: bold;
    }

    .btn-secondary {
        background: #1a1a1a;
        color: #ffffff;
        border: round #888888;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.api_key = ""
        self.model = "openrouter/free"

    def on_mount(self):
        self.push_screen(APIKeyScreen())

    def action_quit(self):
        self.exit(1)  # Exit with error code (user cancelled)


def main():
    """Entry point for the setup wizard."""
    app = SetupWizard()
    try:
        exit_code = app.run()
        return exit_code
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
