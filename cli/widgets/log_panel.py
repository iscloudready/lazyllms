# cli/widgets/log_panel.py
from textual.widgets import Static, Log
from textual.app import ComposeResult
from textual.containers import Vertical
from rich.text import Text
from core.ollama_api import get_model_logs
import time

class LogPanel(Static):
    """Panel showing model logs"""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("📝 Live Model Logs", classes="panel-title")
            yield Static("Press Enter to view selected model logs", classes="log-help")
            yield Log(highlight=True)  # Removed markup=True as it's not supported

    def on_mount(self) -> None:
        self.selected_model = None
        self._last_update = 0
        self.auto_scroll = True
        self.update_logs()

    def clear_logs(self) -> None:
        log_widget = self.query_one(Log)
        log_widget.clear()

    def update_logs(self) -> None:
        now = time.time()
        # Rate limit updates to once per second
        if now - self._last_update < 1:
            return

        log_widget = self.query_one(Log)

        if self.selected_model:
            try:
                logs = get_model_logs(self.selected_model)
                timestamp = time.strftime("%H:%M:%S")

                for entry in logs:
                    if "ERROR" in entry:
                        style = "bold red"
                        prefix = "❌"
                    elif "WARNING" in entry:
                        style = "yellow"
                        prefix = "⚠️"
                    else:
                        style = "green"
                        prefix = "ℹ️"

                    log_widget.write(
                        f"[{timestamp}] {prefix} [{style}]{entry}[/]"
                    )

                if self.auto_scroll:
                    log_widget.scroll_end()

            except Exception as e:
                log_widget.write(f"[red]Error getting logs: {str(e)}[/]")

            self._last_update = now
        elif log_widget.line_count == 0:
            log_widget.write("[dim]Select a model to view logs...[/]")