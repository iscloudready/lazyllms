from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, TabbedContent, TabPane, Static, DataTable, Log
from textual.binding import Binding
from textual.timer import Timer
import yaml

from core.ollama_api import get_running_models
from core.monitor import get_system_usage

class ModelsWidget(Static):
    """Widget to display running models"""

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Model Name", "Version", "Status")
        self.update_models()

    def update_models(self) -> None:
        """Update running models data"""
        models = get_running_models()
        table = self.query_one(DataTable)
        table.clear()

        if models:
            for model in models:
                table.add_row(
                    f"[green]{model['name']}[/]",
                    f"[yellow]{model['digest'][:12]}...[/]",
                    f"[green]✅ Running[/]"
                )
        else:
            table.add_row(
                "[red]No models[/]",
                "[red]-[/]",
                "[red]❌ Not running[/]"
            )

class SystemUsageWidget(Static):
    """Widget to display system resource usage with color coding"""

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Resource", "Usage", "Status")
        self.update_usage()

    def get_usage_style(self, value: float) -> str:
        """Return style based on usage thresholds"""
        if value < 50:
            return "green"
        elif value < 80:
            return "yellow"
        return "red"

    def update_usage(self) -> None:
        """Update system usage data with color coding"""
        usage = get_system_usage()
        table = self.query_one(DataTable)
        table.clear()

        # Convert percentage strings to floats for comparison
        cpu_value = float(usage["CPU"].strip("%"))
        ram_value = float(usage["RAM"].strip("%"))
        gpu_value = float(usage["GPU"].strip("%"))

        def get_color_tag(value: float) -> str:
            return "[green]" if value < 50 else "[yellow]" if value < 80 else "[red]"

        def get_status_icon(value: float) -> str:
            return "🟢" if value < 50 else "🟡" if value < 80 else "🔴"

        table.add_row(
            "CPU",
            f"{get_color_tag(cpu_value)}{usage['CPU']}[/]",
            f"{get_color_tag(cpu_value)}{get_status_icon(cpu_value)}[/]"
        )
        table.add_row(
            "RAM",
            f"{get_color_tag(ram_value)}{usage['RAM']}[/]",
            f"{get_color_tag(ram_value)}{get_status_icon(ram_value)}[/]"
        )
        table.add_row(
            "GPU",
            f"{get_color_tag(gpu_value)}{usage['GPU']}[/]",
            f"{get_color_tag(gpu_value)}{get_status_icon(gpu_value)}[/]"
        )
        table.add_row(
            "VRAM",
            f"[blue]{usage['VRAM']}[/]",
            "[blue]ℹ️[/]"
        )

class LazyLLMsApp(App):
    """Main LazyLLMs TUI Application"""

    TITLE = "LazyLLMs - Model Manager"
    CSS = """
    Screen {
        align: center middle;
    }

    #models-container {
        width: 100%;
        height: auto;
    }

    DataTable {
        width: 100%;
        height: auto;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("l", "toggle_logs", "Toggle Logs"),
        Binding("tab", "next_tab", "Next Tab"),
        Binding("shift+tab", "prev_tab", "Previous Tab"),
    ]

    def __init__(self):
        super().__init__()
        self.refresh_timer = None

    def compose(self) -> ComposeResult:
        """Create app layout"""
        yield Header(show_clock=True)

        with TabbedContent():
            with TabPane("Overview", id="overview"):
                with Container(id="models-container"):
                    yield ModelsWidget()
                    yield SystemUsageWidget()

            with TabPane("System", id="system"):
                from cli.widgets.metrics import SystemMetricsWidget
                from cli.widgets.resources import ResourceAllocationWidget

                with Horizontal():
                    yield SystemMetricsWidget()
                    yield ResourceAllocationWidget()

            with TabPane("Queue", id="queue"):
                from cli.widgets.queue import QueueStatusWidget
                yield QueueStatusWidget()

            with TabPane("Logs", id="logs"):
                from cli.widgets.logs import ModelLogsWidget
                yield ModelLogsWidget()

        yield Footer()

    def on_mount(self) -> None:
        """Set up auto-refresh timer"""
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            refresh_interval = config["monitoring"]["refresh_interval"]

        self.refresh_timer = self.set_interval(refresh_interval, self.refresh_data)

    def refresh_data(self) -> None:
        """Refresh all data in the UI"""
        self.query_one(ModelsWidget).update_models()
        self.query_one(SystemUsageWidget).update_usage()

        # Refresh other widgets if they're visible
        current_tab = self.query_one(TabbedContent).active
        if current_tab == "system":
            self.query_one("#system SystemMetricsWidget").update_metrics()
            self.query_one("#system ResourceAllocationWidget").update_resources()
        elif current_tab == "queue":
            self.query_one("#queue QueueStatusWidget").update_queue()
        elif current_tab == "logs":
            self.query_one("#logs ModelLogsWidget").update_logs()

    def action_refresh(self) -> None:
        """Manual refresh action"""
        self.refresh_data()

def show_tui():
    """Launch the TUI application"""
    app = LazyLLMsApp()
    app.run()

if __name__ == "__main__":
    show_tui()