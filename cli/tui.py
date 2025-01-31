from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Log
from textual.binding import Binding
from textual.timer import Timer
from rich.text import Text
import yaml
import time

from core.ollama_api import get_running_models, get_model_logs
from core.monitor import get_system_usage

class ModelsPanel(Static):
    """Left panel showing model list"""

    def compose(self) -> ComposeResult:
        yield Static("📦 Models", classes="panel-title")
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("Model Name", "Size", "Status")
        self.update_models()

    def update_models(self) -> None:
        models = get_running_models()
        table = self.query_one(DataTable)
        table.clear()

        if models:
            for model in models:
                # Convert size to GB
                size_gb = model['size'] / 1024 / 1024 / 1024
                details = model.get('details', {})
                param_size = details.get('parameter_size', 'N/A')
                quant = details.get('quantization_level', 'N/A')

                name = Text(model['name'], style="bright_green")
                size = Text(f"{size_gb:.1f}GB", style="bright_yellow")
                status = Text("✓ Running", style="green")

                table.add_row(name, size, status)
        else:
            table.add_row(
                Text("No models", style="red"),
                Text("-", style="red"),
                Text("❌ Not running", style="red")
            )

class SystemPanel(Static):
    """Right panel showing system metrics"""

    def compose(self) -> ComposeResult:
        yield Static("🖥️ System Resources", classes="panel-title")
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.zebra_stripes = True
        table.add_columns("Resource", "Usage", "Status")
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

        # CPU Usage
        cpu_value = float(usage["CPU"].strip("%"))
        cpu_icon, cpu_style = get_status_style(cpu_value)
        table.add_row(
            Text("CPU", style="blue"),
            Text(usage["CPU"], style=cpu_style),
            Text(cpu_icon, style=cpu_style)
        )

        # RAM Usage
        ram_value = float(usage["RAM"].strip("%"))
        ram_icon, ram_style = get_status_style(ram_value)
        table.add_row(
            Text("RAM", style="blue"),
            Text(usage["RAM"], style=ram_style),
            Text(ram_icon, style=ram_style)
        )

        # GPU Usage
        gpu_value = float(usage["GPU"].strip("%"))
        gpu_icon, gpu_style = get_status_style(gpu_value)
        table.add_row(
            Text("GPU", style="blue"),
            Text(usage["GPU"], style=gpu_style),
            Text(gpu_icon, style=gpu_style)
        )

        # VRAM Usage
        table.add_row(
            Text("VRAM", style="blue"),
            Text(usage["VRAM"], style="cyan"),
            Text("ℹ️", style="cyan")
        )

class LogPanel(Static):
    """Bottom panel showing logs"""

    def compose(self) -> ComposeResult:
        yield Static("📝 Model Logs", classes="panel-title")
        yield Log()

    def on_mount(self) -> None:
        self.selected_model = None
        self.update_logs()

    def update_logs(self) -> None:
        log = self.query_one(Log)

        if self.selected_model:
            logs = get_model_logs(self.selected_model)
            timestamp = time.strftime("%H:%M:%S")

            for entry in logs:
                if "ERROR" in entry:
                    log.write(f"[{timestamp}] [red]{entry}[/]")
                elif "WARNING" in entry:
                    log.write(f"[{timestamp}] [yellow]{entry}[/]")
                else:
                    log.write(f"[{timestamp}] [green]{entry}[/]")
        else:
            if log.line_count == 0:  # Only write if log is empty
                log.write("[dim]Select a model to view logs...[/]")

class LazyLLMsApp(App):
    """LazyLLMs TUI Application"""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 2;
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

    ModelsPanel {
        row-span: 2;
        height: 100%;
        border: round $primary;
    }

    SystemPanel {
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
        Binding("enter", "select_model", "Select Model"),
    ]

    def __init__(self):
        super().__init__()
        self.refresh_timer = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield ModelsPanel()
        yield SystemPanel()
        yield LogPanel()
        yield Footer()

    def on_mount(self) -> None:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            refresh_interval = config["monitoring"]["refresh_interval"]

        self.refresh_timer = self.set_interval(refresh_interval, self.refresh_data)

    def refresh_data(self) -> None:
        """Refresh all panels"""
        self.query_one(ModelsPanel).update_models()
        self.query_one(SystemPanel).update_metrics()
        self.query_one(LogPanel).update_logs()

    def action_refresh(self) -> None:
        self.refresh_data()

    def action_select_model(self) -> None:
        """Select model for logs"""
        models_table = self.query_one(ModelsPanel).query_one(DataTable)
        if models_table.cursor_row is not None:
            model_name = models_table.get_cell_at(models_table.cursor_row, 0)
            log_panel = self.query_one(LogPanel)
            log_panel.selected_model = str(model_name)
            log_panel.update_logs()

def show_tui():
    """Launch the TUI application"""
    app = LazyLLMsApp()
    app.run()

if __name__ == "__main__":
    show_tui()