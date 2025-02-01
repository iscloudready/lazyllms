from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Log
from textual.binding import Binding

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
        layout: vertical;
    }

    Header {
        dock: top;
        background: $boost;
        color: $text;
        height: 1;
    }

    Footer {
        dock: bottom;
        background: $boost;
        color: $text;
        height: 1;
    }

    ModelsPanel {
        height: 35%;
        margin: 1;
        border: round $primary;
    }

    .system-row {
        height: 30%;
        layout: horizontal;
        margin: 0 1;
    }

    SystemPanel {
        width: 1fr;
        height: 100%;
        margin-right: 1;
        border: round $primary;
    }

    PerformancePanel {
        width: 1fr;
        height: 100%;
        margin-right: 1;
        border: round $primary;
    }

    TimePanel {
        width: 1fr;
        height: 100%;
        border: round $primary;
    }

    .bottom-row {
        height: 35%;
        layout: horizontal;
        margin: 0 1 1 1;
    }

    ModelDetailsPanel {
        width: 1fr;
        height: 100%;
        margin-right: 1;
        border: round $primary;
    }

    LogPanel {
        width: 1fr;
        height: 100%;
        border: round $primary;
    }

    .panel-title {
        background: $panel;
        padding: 1;
        text-align: center;
        border-bottom: heavy $primary;
        width: 100%;
    }

    DataTable {
        width: 100%;
        height: 85%;
        margin: 0 1;
    }

    Log {
        margin: 0 1;
        height: 85%;
        background: $surface;
        color: $text;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("f", "focus_next", "Focus Next"),
        Binding("c", "clear_logs", "Clear Logs"),
        Binding("enter", "select_model", "Select Model"),
    ]

    def compose(self) -> ComposeResult:
        """Create app layout."""
        yield Header()

        # Top section - Models
        yield ModelsPanel()

        # Middle section - System Resources, Performance, Time
        with Container(classes="system-row"):
            yield SystemPanel()
            yield PerformancePanel()
            yield TimePanel()

        # Bottom section - Model Details and Logs
        with Container(classes="bottom-row"):
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
            self.notify("⚠️ Using default refresh interval (2s)", severity="warning")
            refresh_interval = 2.0

        # Initial data load
        self.refresh_data()

        # Start refresh timer
        self.set_interval(refresh_interval, self.refresh_data)

    def refresh_data(self) -> None:
            """Refresh all panels with error handling."""
            try:
                # Get currently selected model before refresh
                details_panel = self.query_one(ModelDetailsPanel)
                log_panel = self.query_one(LogPanel)
                current_model = details_panel.selected_model if details_panel else None

                # Update main panels
                self.query_one(ModelsPanel).update_models()
                self.query_one(SystemPanel).update_metrics()
                self.query_one(PerformancePanel).update_metrics()
                self.query_one(TimePanel).update_time()

                # Update model-specific panels if we have a selection
                if current_model:
                    if details_panel:
                        details_panel.update_details(current_model)
                    if log_panel:
                        log_panel.update_logs()

            except Exception as e:
                self.notify(f"Refresh error: {str(e)}", severity="error")

    def action_refresh(self) -> None:
        """Manual refresh action."""
        self.refresh_data()
        self.notify("✨ Refreshed", severity="information")

    def action_clear_logs(self) -> None:
        """Clear the logs panel."""
        self.query_one(LogPanel).clear_logs()
        self.notify("🧹 Logs cleared", severity="information")

    def action_focus_next(self) -> None:
        """Cycle focus through panels."""
        current = self.screen.focused
        if current:
            panels = list(self.query(ModelsPanel, SystemPanel,
                                   PerformancePanel, TimePanel,
                                   ModelDetailsPanel, LogPanel))
            try:
                current_idx = panels.index(current)
                next_idx = (current_idx + 1) % len(panels)
                panels[next_idx].focus()
            except ValueError:
                panels[0].focus()

    def action_select_model(self) -> None:
            """Handle model selection with error handling."""
            try:
                models_table = self.query_one(ModelsPanel).query_one(DataTable)
                if not models_table or models_table.row_count == 0:
                    return

                cursor_row = models_table.cursor_row
                if cursor_row is None:
                    return

                # Get the content from the rendered row
                row_key = cursor_row
                try:
                    # Get model name safely from the first column
                    model_cell = models_table.get_row_at(row_key)[0]
                    if not model_cell:
                        return

                    model_name = str(model_cell).strip()
                    if model_name and model_name != "No models":
                        # Update model details
                        details_panel = self.query_one(ModelDetailsPanel)
                        if details_panel:
                            details_panel.selected_model = model_name
                            details_panel.update_details(model_name)

                        # Update logs
                        log_panel = self.query_one(LogPanel)
                        if log_panel:
                            log_panel.selected_model = model_name
                            log_panel.clear_logs()
                            log_panel.update_logs()

                        self.notify(f"✨ Selected: {model_name}")

                except Exception as e:
                    self.notify(f"❌ Error accessing table data: {str(e)}", severity="error")

            except Exception as e:
                self.notify(f"❌ Selection error: {str(e)}", severity="error")

    def on_data_table_row_selected(self) -> None:
        """Handle row selection in any DataTable."""
        self.action_select_model()

    def on_data_table_row_highlighted(self) -> None:
        """Handle row highlight in any DataTable."""
        self.action_select_model()

def show_tui():
    """Launch the TUI application"""
    app = LazyLLMsApp()
    app.run()