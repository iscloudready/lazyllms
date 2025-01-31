from textual.widgets import Static, DataTable
from textual.app import ComposeResult
from rich.text import Text
import time
from datetime import datetime
import pytz

class TimePanel(Static):
    """Panel showing time-related information"""

    def compose(self) -> ComposeResult:
        yield Static("🕒 Time Info", classes="panel-title")
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.zebra_stripes = True
        table.add_columns("Info", "Value")
        self.update_time()

    def update_time(self) -> None:
        table = self.query_one(DataTable)
        table.clear()

        # Get current time in different formats
        now = datetime.now()
        utc_now = datetime.now(pytz.UTC)
        local_tz = datetime.now().astimezone().tzinfo

        table.add_row(
            Text("Local Time", style="blue"),
            Text(now.strftime("%Y-%m-%d %H:%M:%S"), style="green")
        )
        table.add_row(
            Text("UTC Time", style="blue"),
            Text(utc_now.strftime("%Y-%m-%d %H:%M:%S"), style="yellow")
        )
        table.add_row(
            Text("Timezone", style="blue"),
            Text(str(local_tz), style="magenta")
        )
        table.add_row(
            Text("Week", style="blue"),
            Text(f"Week {now.isocalendar()[1]}", style="cyan")
        )
        table.add_row(
            Text("Uptime", style="blue"),
            Text(self._get_uptime(), style="bright_green")
        )

    def _get_uptime(self) -> str:
        """Get system uptime."""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"
        except:
            return "N/A"