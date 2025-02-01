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
            yield Log(highlight=True)  # Remove wrap parameter

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

    def _update_logs(self) -> None:
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

                    # Format log entry with word wrapping
                    entry_lines = self._wrap_text(entry, 80)  # Wrap at 80 characters
                    for i, line in enumerate(entry_lines):
                        if i == 0:
                            # First line has timestamp and prefix
                            log_line = f"[{timestamp}] {prefix} [{style}]{line}[/]"
                        else:
                            # Continuation lines are indented
                            log_line = f"[{style}]{'   ' * 3}{line}[/]"
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

    def update_logs(self) -> None:
        """Update logs with better performance."""
        try:
            current_time = time.time()
            if current_time - self._last_update < 0.5:  # Reduced from 1s to 0.5s
                return

            log_widget = self.query_one(Log)
            if not log_widget:
                return

            if not self._selected_model:
                if log_widget.line_count == 0:
                    log_widget.write("[dim]Select a model to view logs...[/]")
                return

            logs = get_model_logs(self._selected_model)
            timestamp = time.strftime("%H:%M:%S")

            # Buffer logs to reduce writes
            new_logs = []
            for entry in logs:
                if entry in self._log_history:
                    continue

                if "ERROR" in entry:
                    style = "red"
                    prefix = "❌"
                elif "WARNING" in entry:
                    style = "yellow"
                    prefix = "⚠️"
                else:
                    style = "green"
                    prefix = "ℹ️"

                new_logs.append(f"[{timestamp}] {prefix} [{style}]{entry}[/]")
                self._log_history.add(entry)

            if new_logs:
                log_widget.write("\n".join(new_logs))
                log_widget.scroll_end(animate=False)

            self._last_update = current_time

        except Exception as e:
            if hasattr(self, 'app'):
                self.app.notify(f"Error updating logs: {str(e)}", severity="error")

    def _wrap_text(self, text: str, width: int) -> list[str]:
        """Wrap text to specified width."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word)
            if current_length + word_length + 1 <= width:
                current_line.append(word)
                current_length += word_length + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_length + 1

        if current_line:
            lines.append(" ".join(current_line))

        return lines or [text]  # Return original text if wrapping fails