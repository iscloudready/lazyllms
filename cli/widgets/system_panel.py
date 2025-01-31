from textual.widgets import Static, DataTable
from textual.app import ComposeResult
from rich.text import Text
from core.monitor import get_system_usage

class SystemPanel(Static):
    """Panel showing system resources"""

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