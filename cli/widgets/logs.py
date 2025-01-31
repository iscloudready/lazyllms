from textual.widgets import Static, Log, DataTable
from textual.app import ComposeResult
from core.ollama_api import get_model_logs
import time

class ModelLogsWidget(Static):
    """Widget to display real-time model logs"""

    def compose(self) -> ComposeResult:
        """Create a Log widget for displaying logs."""
        yield Log()

    def on_mount(self) -> None:
        """Called when widget is mounted in the app."""
        self.update_logs()

    def update_logs(self, model_name: str = None) -> None:
        """Update logs for the selected model"""
        log_widget = self.query_one(Log)

        if model_name:
            logs = get_model_logs(model_name)
            for log in logs:
                timestamp = time.strftime("%H:%M:%S")
                if "ERROR" in log:
                    log_widget.write(f"[red]{timestamp} {log}[/red]")
                elif "WARNING" in log:
                    log_widget.write(f"[yellow]{timestamp} {log}[/yellow]")
                else:
                    log_widget.write(f"[green]{timestamp} {log}[/green]")
        else:
            log_widget.write("[yellow]Select a model to view logs...[/yellow]")