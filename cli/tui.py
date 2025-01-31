from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import Header, Footer, Static
from textual.binding import Binding
from textual.events import Key

from cli.widgets.models_panel import ModelsPanel
from cli.widgets.system_panel import SystemPanel
from cli.widgets.performance_panel import PerformancePanel
from cli.widgets.log_panel import LogPanel
from cli.widgets.details_panel import ModelDetailsPanel
from cli.widgets.time_panel import TimePanel

import yaml
import time

class LazyLLMsApp(App):
    """LazyLLMs TUI Application"""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 1;
        padding: 1;
    }

    .top-section {
        layout: grid;
        grid-size: 2;  /* Two columns */
        height: 40%;
        margin: 1;
    }

    .middle-section {
        layout: grid;
        grid-size: 3;  /* Three columns */
        height: 30%;
        margin: 1;
    }

    .bottom-section {
        layout: grid;
        grid-size: 1;  /* One column */
        height: 30%;
        margin: 1;
    }

    ModelsPanel {
        column-span: 2;
        height: 100%;
        border: round $primary;
    }

    SystemPanel, PerformancePanel, TimePanel {
        height: 100%;
        border: round $primary;
        margin-right: 1;
    }

    ModelDetailsPanel {
        height: 100%;
        border: round $primary;
    }

    LogPanel {
        height: 100%;
        border: round $primary;
    }

    .title {
        background: $panel;
        padding: 1;
        text-align: center;
        border-bottom: heavy $primary;
    }

    DataTable {
        width: 100%;
        height: 100%;
    }

    Log {
        background: $surface;
        color: $text;
        border: none;
        padding: 0 1;
        width: 100%;
        height: 85%;
    }

    TimeDisplay {
        content-align: center middle;
        text-style: bold;
        width: 100%;
        height: 3;
        margin: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("f", "focus_next", "Focus Next"),
        Binding("c", "clear_logs", "Clear Logs"),
        Binding("enter", "select_model", "Select Model"),
        Binding("?", "toggle_help", "Help"),
    ]

    def __init__(self):
        super().__init__()
        self.refresh_timer = None
        self.last_refresh = 0
        self._loading = False

    def compose(self) -> ComposeResult:
        """Create main layout."""
        yield Header()

        # Top section: Models
        with Container(classes="top-section"):
            yield ModelsPanel()

        # Middle section: System, Performance, Time
        with Container(classes="middle-section"):
            yield SystemPanel()
            yield PerformancePanel()
            yield TimePanel()

        # Bottom section: Model Details and Logs
        with Container(classes="bottom-section"):
            with Horizontal():
                yield ModelDetailsPanel()
                yield LogPanel()

        yield Footer()

    def on_mount(self) -> None:
        """Initialize app and start refresh timer."""
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
                refresh_interval = float(config.get("monitoring", {}).get("refresh_interval", 2.0))
        except Exception as e:
            self.notify(f"Config error: {str(e)}", severity="warning")
            refresh_interval = 2.0

        # Initial data load
        self.refresh_data()

        # Start refresh timer
        self.refresh_timer = self.set_interval(refresh_interval, self.refresh_data)

    def refresh_data(self) -> None:
        """Refresh all panels with rate limiting and error handling."""
        if self._loading:
            return

        try:
            self._loading = True
            current_time = time.time()

            # Update panels
            self.query_one(ModelsPanel).update_models()
            self.query_one(SystemPanel).update_metrics()
            self.query_one(PerformancePanel).update_metrics()
            self.query_one(TimePanel).update_time()

            # Update model-specific panels
            details_panel = self.query_one(ModelDetailsPanel)
            log_panel = self.query_one(LogPanel)

            if details_panel.selected_model:
                details_panel.update_details()
            if log_panel.selected_model:
                log_panel.update_logs()

        except Exception as e:
            self.notify(f"Refresh error: {str(e)}", severity="error")
        finally:
            self._loading = False

    def action_refresh(self) -> None:
        """Manual refresh action."""
        self.refresh_data()
        self.notify("Refreshed!", severity="information")

    def action_toggle_help(self) -> None:
        """Toggle help screen."""
        # Implement help screen
        self.notify("Help screen coming soon!", severity="information")

    def action_select_model(self) -> None:
        """Handle model selection with error handling."""
        try:
            models_table = self.query_one(ModelsPanel).query_one("DataTable")
            if models_table.cursor_row is not None:
                model_name = str(models_table.get_cell_at(models_table.cursor_row, 0))
                model_name = model_name.strip()

                if model_name and model_name != "No models":
                    # Update model details
                    details_panel = self.query_one(ModelDetailsPanel)
                    details_panel.selected_model = model_name
                    details_panel.update_details()

                    # Update logs
                    log_panel = self.query_one(LogPanel)
                    log_panel.selected_model = model_name
                    log_panel.clear_logs()
                    log_panel.update_logs()

                    self.notify(f"Selected model: {model_name}")
        except Exception as e:
            self.notify(f"Error selecting model: {str(e)}", severity="error")

def show_tui():
    """Launch the TUI application"""
    app = LazyLLMsApp()
    app.run()