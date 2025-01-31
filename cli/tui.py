from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import Header, Footer, Static, DataTable, Log
from textual.binding import Binding
from textual.timer import Timer
from rich.text import Text
import yaml
import time

from core.ollama_api import get_running_models, get_model_logs
from core.monitor import get_system_usage

class ModelsPanel(Static):
    def compose(self) -> ComposeResult:
        yield Static("📦 Available Models", classes="panel-title")
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("Model", "Parameters", "Size", "Type", "Status")
        self.update_models()

    def update_models(self) -> None:
        models = get_running_models()
        table = self.query_one(DataTable)
        table.clear()

        if models:
            for model in models:
                size_gb = model['size'] / 1024 / 1024 / 1024
                details = model.get('details', {})
                param_size = details.get('parameter_size', 'N/A')
                quant = details.get('quantization_level', 'N/A')
                family = details.get('family', 'unknown')

                table.add_row(
                    Text(model['name'], style="bright_green"),
                    Text(param_size, style="bright_yellow"),
                    Text(f"{size_gb:.1f}GB", style="cyan"),
                    Text(f"{family} ({quant})", style="magenta"),
                    Text("✓ Running", style="green")
                )
        else:
            table.add_row(
                Text("No models", style="red"),
                Text("-", style="red"),
                Text("-", style="red"),
                Text("-", style="red"),
                Text("❌ Not running", style="red")
            )

class PerformancePanel(Static):
    def compose(self) -> ComposeResult:
        yield Static("⚡ Performance Stats", classes="panel-title")
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.zebra_stripes = True
        table.add_columns("Model", "Req/s", "Latency", "Memory")
        self.update_metrics()

    def update_metrics(self) -> None:
        models = get_running_models()
        table = self.query_one(DataTable)
        table.clear()

        if models:
            for model in models:
                table.add_row(
                    Text(model['name'], style="bright_green"),
                    Text("10/s", style="yellow"),  # Example metrics
                    Text("150ms", style="cyan"),
                    Text("2.1GB", style="magenta")
                )

class SystemPanel(Static):
    def compose(self) -> ComposeResult:
        yield Static("🖥️ System Resources", classes="panel-title")
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.zebra_stripes = True
        table.add_columns("Resource", "Usage", "Peak", "Status")
        self._peak_values = {"CPU": 0, "RAM": 0, "GPU": 0}
        self.update_metrics()

    def update_metrics(self) -> None:
        usage = get_system_usage()
        table = self.query_one(DataTable)
        table.clear()

        def get_status_style(value: float) -> tuple[str, str]:
            if value < 50:
                return "✓", "green"
            elif value < 80:
                return "⚠", "yellow"
            return "⛔", "red"

        for resource in ["CPU", "RAM", "GPU"]:
            value = float(usage[resource].strip("%"))
            self._peak_values[resource] = max(self._peak_values[resource], value)
            icon, style = get_status_style(value)

            table.add_row(
                Text(resource, style="blue"),
                Text(f"{value:.1f}%", style=style),
                Text(f"{self._peak_values[resource]:.1f}%", style="bright_magenta"),
                Text(icon, style=style)
            )

        table.add_row(
            Text("VRAM", style="blue"),
            Text(usage["VRAM"], style="cyan"),
            Text("-", style="bright_magenta"),
            Text("ℹ️", style="cyan")
        )

class LogPanel(Static):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("📝 Live Model Logs", classes="panel-title")
            yield Static("Press Enter to view selected model logs", classes="log-help")
            yield Log()

    def on_mount(self) -> None:
        self.selected_model = None
        self.update_logs()

    def clear_logs(self) -> None:
        log_widget = self.query_one(Log)
        log_widget.clear()

    def update_logs(self) -> None:
        log_widget = self.query_one(Log)

        if self.selected_model:
            timestamp = time.strftime("%H:%M:%S")
            logs = get_model_logs(self.selected_model)

            for entry in logs:
                if "ERROR" in entry:
                    log_widget.write(f"[{timestamp}] [red bold]{entry}[/]")
                elif "WARNING" in entry:
                    log_widget.write(f"[{timestamp}] [yellow]{entry}[/]")
                else:
                    log_widget.write(f"[{timestamp}] [green]{entry}[/]")
        else:
            if log_widget.line_count == 0:
                log_widget.write("[dim]Select a model to view logs...[/]")

class LazyLLMsApp(App):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 3;
        grid-gutter: 1 1;
        padding: 1;
    }

    .panel-title {
        dock: top;
        padding: 1;
        background: $panel;
        border-bottom: heavy $primary;
        color: $text;
        text-align: center;
        text-style: bold;
    }

    .log-help {
        dock: top;
        padding: 1;
        color: $text-disabled;
        text-align: center;
    }

    ModelsPanel {
        column-span: 2;
        height: 100%;
        border: round $primary;
    }

    SystemPanel {
        height: 100%;
        border: round $primary;
    }

    PerformancePanel {
        height: 100%;
        border: round $primary;
    }

    LogPanel {
        column-span: 2;
        height: 100%;
        border: round $primary;
    }

    DataTable {
        height: 100%;
        align: center top;
    }

    Log {
        height: 100%;
        border: none;
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

    def __init__(self):
        super().__init__()
        self.refresh_timer = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield ModelsPanel()
        yield SystemPanel()
        yield PerformancePanel()
        yield LogPanel()
        yield Footer()

    def on_mount(self) -> None:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            refresh_interval = config["monitoring"]["refresh_interval"]

        self.refresh_timer = self.set_interval(refresh_interval, self.refresh_data)

    def refresh_data(self) -> None:
        self.query_one(ModelsPanel).update_models()
        self.query_one(SystemPanel).update_metrics()
        self.query_one(PerformancePanel).update_metrics()
        if self.query_one(LogPanel).selected_model:
            self.query_one(LogPanel).update_logs()

    def action_refresh(self) -> None:
        self.refresh_data()

    def action_clear_logs(self) -> None:
        self.query_one(LogPanel).clear_logs()

    def action_select_model(self) -> None:
        models_table = self.query_one(ModelsPanel).query_one(DataTable)
        if models_table.cursor_row is not None:
            model_name = models_table.get_cell_at(models_table.cursor_row, 0)
            log_panel = self.query_one(LogPanel)
            log_panel.selected_model = str(model_name)
            log_panel.clear_logs()
            log_panel.update_logs()

def show_tui():
    app = LazyLLMsApp()
    app.run()

if __name__ == "__main__":
    show_tui()