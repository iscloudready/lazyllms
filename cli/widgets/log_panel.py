from textual.widgets import Static, Log
from textual.app import ComposeResult
from textual.containers import Vertical
from core.ollama_api import get_model_logs
import time

class LogPanel(Static):
    """Panel showing model logs"""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("📝 Live Model Logs", classes="panel-title")
            yield Static("Press Enter to view selected model logs", classes="log-help")
            yield Log(highlight=True, wrap=True)  # Add wrap=True for better text wrapping

    def on_mount(self) -> None:
        self._selected_model = None
        self._last_update = 0
        self._log_history = set()  # Use set for faster duplicate checking

    @property
    def selected_model(self) -> str:
        """Get selected model."""
        return self._selected_model

    @selected_model.setter
    def selected_model(self, value: str) -> None:
        """Set selected model and trigger update."""
        if value != self._selected_model:
            self._selected_model = value
            self.clear_logs()
            self.update_logs()

    def clear_logs(self) -> None:
        """Clear logs and history."""
        try:
            log_widget = self.query_one(Log)
            if log_widget:
                log_widget.clear()
            self._log_history.clear()
            self._last_update = 0
        except Exception as e:
            if hasattr(self, 'app'):
                self.app.notify(f"Error clearing logs: {str(e)}", severity="error")

    def update_logs(self) -> None:
        """Update logs with rate limiting and error handling."""
        try:
            # Rate limit updates
            current_time = time.time()
            if current_time - self._last_update < 1:
                return

            log_widget = self.query_one(Log)
            if not log_widget:
                return

            if not self._selected_model:
                if log_widget.line_count == 0:
                    log_widget.write("[dim]Select a model to view logs...[/]")
                return

            try:
                logs = get_model_logs(self._selected_model)
                timestamp = time.strftime("%H:%M:%S")

                for entry in logs:
                    # Skip if we've already shown this log
                    if entry in self._log_history:
                        continue

                    # Determine log level and style
                    if "ERROR" in entry:
                        style = "red"
                        prefix = "❌"
                    elif "WARNING" in entry:
                        style = "yellow"
                        prefix = "⚠️"
                    else:
                        style = "green"
                        prefix = "ℹ️"

                    # Format and write log entry
                    log_line = f"[{timestamp}] {prefix} [{style}]{entry}[/]"
                    log_widget.write(log_line)

                    # Add to history
                    self._log_history.add(entry)

                # Auto-scroll to latest logs
                log_widget.scroll_end(animate=False)
                self._last_update = current_time

            except Exception as e:
                log_widget.write(f"[red bold][{timestamp}] ❌ Error fetching logs: {str(e)}[/]")
                if hasattr(self, 'app'):
                    self.app.notify(f"Error fetching logs: {str(e)}", severity="error")

        except Exception as e:
            if hasattr(self, 'app'):
                self.app.notify(f"Error updating logs: {str(e)}", severity="error")

    def on_mount(self) -> None:
        """Initialize log panel."""
        self._selected_model = None
        self._last_update = 0
        self._log_history = set()
        self.update_logs()  # Show initial message