from textual.widgets import Static, DataTable
from textual.app import ComposeResult
from rich.text import Text
from core.ollama_api import get_running_models

class PerformancePanel(Static):
    """Panel showing model performance metrics"""

    def compose(self) -> ComposeResult:
        yield Static("⚡ Performance Stats", classes="panel-title")
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.zebra_stripes = True
        table.add_columns(
            "Model",
            "Throughput",
            "Latency",
            "Memory Usage",
            "Load"
        )
        self._metrics = {}  # Store metrics history
        self.update_metrics()

    def update_metrics(self) -> None:
        models = get_running_models()
        table = self.query_one(DataTable)
        table.clear()

        if models:
            for model in models:
                size_gb = model['size'] / 1024 / 1024 / 1024
                # Simulate performance metrics (replace with real metrics from your API)
                throughput = "10 tokens/s"
                latency = "150ms"
                memory = f"{size_gb:.1f}GB"
                load = "Active"

                table.add_row(
                    Text(model['name'], style="bright_green"),
                    Text(throughput, style="yellow"),
                    Text(latency, style="cyan"),
                    Text(memory, style="magenta"),
                    Text(load, style="green")
                )