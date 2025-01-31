from textual.widgets import Static, DataTable, ProgressBar, Log
from textual.app import ComposeResult
from textual.containers import Vertical
from core.monitor import get_system_usage
import psutil

class ResourceAllocationWidget(Static):
    """Widget to display detailed resource allocation metrics"""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield DataTable()
            yield ProgressBar()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(
            "Resource",
            "Total",
            "Used",
            "Available",
            "Processes"
        )
        self.update_resources()

    def update_resources(self) -> None:
        """Update detailed resource allocation information"""
        table = self.query_one(DataTable)
        progress = self.query_one(ProgressBar)
        table.clear()

        # CPU Details
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        table.add_row(
            "CPU Cores",
            f"{cpu_count} cores",
            f"{cpu_percent}%",
            f"{100-cpu_percent}%",
            f"{len(psutil.Process().threads())} threads"
        )

        # Memory Details
        mem = psutil.virtual_memory()
        table.add_row(
            "Memory",
            f"{mem.total/1024/1024/1024:.1f}GB",
            f"{mem.used/1024/1024/1024:.1f}GB",
            f"{mem.available/1024/1024/1024:.1f}GB",
            f"{len(psutil.Process().memory_maps())} maps"
        )

        # Disk Details
        disk = psutil.disk_usage('/')
        table.add_row(
            "Disk",
            f"{disk.total/1024/1024/1024:.1f}GB",
            f"{disk.used/1024/1024/1024:.1f}GB",
            f"{disk.free/1024/1024/1024:.1f}GB",
            f"{len(psutil.disk_partitions())} parts"
        )

        # Update progress bar
        progress.progress = cpu_percent