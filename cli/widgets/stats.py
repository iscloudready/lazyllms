from textual.widgets import Static, DataTable, ProgressBar, Log
from textual.app import ComposeResult
from core.ollama_api import get_running_models

class ModelStatsWidget(Static):
    """Widget to display model statistics and performance metrics"""

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(
            "Model",
            "Requests/sec",
            "Avg Latency",
            "Memory Usage"
        )
        self.update_stats()

    def update_stats(self) -> None:
        """Update model performance statistics"""
        models = get_running_models()
        table = self.query_one(DataTable)
        table.clear()

        if models:
            for model in models:
                # Example performance metrics (replace with real metrics)
                table.add_row(
                    model['name'],
                    "12.5",
                    "156ms",
                    "2.3GB"
                )
        else:
            table.add_row(
                "No models",
                "-",
                "-",
                "-"
            )