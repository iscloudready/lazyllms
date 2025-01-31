from textual.widgets import Static, Log, DataTable
from textual.app import ComposeResult
from core.monitor import get_system_usage

class SystemMetricsWidget(Static):
    """Widget to display detailed system metrics"""

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(
            "Metric", "Current", "Peak", "Status"
        )
        self.update_metrics()

    def get_status_icon(self, value: float) -> str:
        """Return status icon based on usage level"""
        if value < 50:
            return "🟢"
        elif value < 80:
            return "🟡"
        return "🔴"

    def update_metrics(self) -> None:
        """Update detailed system metrics"""
        usage = get_system_usage()
        table = self.query_one(DataTable)
        table.clear()

        # CPU Metrics
        cpu_value = float(usage["CPU"].strip("%"))
        table.add_row(
            "CPU Usage",
            usage["CPU"],
            "95%",  # Example peak value
            self.get_status_icon(cpu_value)
        )

        # RAM Metrics
        ram_value = float(usage["RAM"].strip("%"))
        table.add_row(
            "RAM Usage",
            usage["RAM"],
            "92%",  # Example peak value
            self.get_status_icon(ram_value)
        )

        # GPU Metrics
        gpu_value = float(usage["GPU"].strip("%"))
        table.add_row(
            "GPU Usage",
            usage["GPU"],
            "88%",  # Example peak value
            self.get_status_icon(gpu_value)
        )

        # VRAM Metrics
        table.add_row(
            "VRAM Usage",
            usage["VRAM"],
            "16GB",  # Example peak value
            "ℹ️"
        )