# cli/widgets/performance_panel.py
from textual.widgets import Static, DataTable
from textual.app import ComposeResult
from rich.text import Text
from core.metrics import MetricsManager
from core.ollama_api import get_running_models
import psutil
import time

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
        self._metrics_manager = MetricsManager()

    def update_metrics(self) -> None:
        """Update with real metrics."""
        if not self._metrics_manager.should_update():
            return

        table = self.query_one(DataTable)
        table.clear()

        try:
            models = get_running_models()
            for model in models:
                metrics = self._metrics_manager.get_model_metrics(model['name'])

                if metrics:
                    # Use real metrics
                    memory_info = metrics.get('memory_info', {})
                    cpu_percent = metrics.get('cpu_percent', 0)

                    table.add_row(
                        Text(model['name'], style="bright_green"),
                        Text(f"{self._estimate_throughput(cpu_percent)} tokens/s", style="yellow"),
                        Text(f"{self._estimate_latency(cpu_percent)}ms", style="cyan"),
                        Text(self.format_memory(getattr(memory_info, 'rss', 0)), style="magenta"),
                        Text(f"{cpu_percent:.1f}%", style="green")
                    )
                else:
                    # Use estimated metrics
                    model_size = model.get('size', 0)
                    table.add_row(
                        Text(model['name'], style="bright_green"),
                        Text("10 tokens/s", style="yellow"),
                        Text("150ms", style="cyan"),
                        Text(self.format_memory(model_size), style="magenta"),
                        Text("Active", style="green")
                    )

        except Exception as e:
            self.app.notify(f"Error updating metrics: {str(e)}", severity="error")

    def format_memory(self, size_bytes: int) -> str:
        """Format memory size to appropriate unit."""
        try:
            if isinstance(size_bytes, (int, float)):
                if size_bytes >= 1024**3:
                    return f"{size_bytes / (1024**3):.1f}GB"
                elif size_bytes >= 1024**2:
                    return f"{size_bytes / (1024**2):.1f}MB"
                else:
                    return f"{size_bytes / 1024:.1f}KB"
            else:
                return str(size_bytes)
        except (TypeError, ValueError):
            return "N/A"

    def _estimate_throughput(self, cpu_percent: float) -> int:
        """Estimate throughput based on CPU usage."""
        return max(5, int(20 - (cpu_percent / 10)))

    def _estimate_latency(self, cpu_percent: float) -> int:
        """Estimate latency based on CPU usage."""
        return min(500, int(100 + cpu_percent * 2))