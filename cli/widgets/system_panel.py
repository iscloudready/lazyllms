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
        self._peak_values = {"CPU": 0, "RAM": 0, "GPU": 0, "VRAM": 0}
        self._last_update = 0
        self.update_metrics()

    def get_status_style(self, value: float) -> tuple[str, str, str]:
        """Get status icon, color and message based on usage level."""
        if value < 50:
            return "✓", "green", "Normal"
        elif value < 80:
            return "⚠", "yellow", "High"
        return "⛔", "red", "Critical"

    def format_size(self, size_mb: float) -> str:
        """Format size in MB to appropriate unit."""
        if size_mb > 1024:
            return f"{size_mb/1024:.1f}GB"
        return f"{size_mb:.0f}MB"

    def update_metrics(self) -> None:
        """Update system metrics with error handling."""
        table = self.query_one(DataTable)
        table.clear()

        try:
            usage = get_system_usage()

            # Update CPU, RAM, GPU metrics
            for resource in ["CPU", "RAM", "GPU"]:
                try:
                    value = float(usage[resource].strip("%"))
                    self._peak_values[resource] = max(self._peak_values[resource], value)
                    icon, style, status = self.get_status_style(value)

                    table.add_row(
                        Text(resource, style="blue"),
                        Text(f"{value:.1f}%", style=style),
                        Text(f"{self._peak_values[resource]:.1f}%", style="bright_magenta"),
                        Text(f"{icon} {status}", style=style)
                    )
                except (ValueError, KeyError) as e:
                    table.add_row(
                        Text(resource, style="blue"),
                        Text("N/A", style="red"),
                        Text("N/A", style="red"),
                        Text("⚠ Error", style="red")
                    )

            # Handle VRAM separately
            try:
                vram = usage.get("VRAM", "0MB")
                vram_mb = float(vram.strip("MB"))
                self._peak_values["VRAM"] = max(self._peak_values["VRAM"], vram_mb)

                table.add_row(
                    Text("VRAM", style="blue"),
                    Text(self.format_size(vram_mb), style="cyan"),
                    Text(self.format_size(self._peak_values["VRAM"]), style="bright_magenta"),
                    Text("ℹ️ Available", style="cyan")
                )
            except (ValueError, KeyError):
                table.add_row(
                    Text("VRAM", style="blue"),
                    Text("N/A", style="red"),
                    Text("N/A", style="red"),
                    Text("⚠ Error", style="red")
                )

        except Exception as e:
            # Handle complete failure
            table.add_row(
                Text("Error", style="red"),
                Text("Failed to get metrics", style="red"),
                Text("-", style="red"),
                Text(f"⚠ {str(e)}", style="red")
            )
            if hasattr(self, 'app'):
                self.app.notify(f"Error updating system metrics: {str(e)}", severity="error")