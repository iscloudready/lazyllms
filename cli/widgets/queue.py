from textual.widgets import Static, DataTable, ProgressBar
from textual.app import ComposeResult
from textual.containers import Vertical
from core.ollama_api import get_running_models
import random  # For demo data, replace with actual queue metrics

class QueueStatusWidget(Static):
    """Widget to display model request queue status"""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield DataTable()
            yield Static("Queue Load:", id="queue-header")
            yield ProgressBar(show_eta=False)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(
            "Model",
            "Queue Length",
            "Processing",
            "Avg Wait Time",
            "Status"
        )
        self.update_queue()

    def get_queue_status(self, queue_length: int) -> str:
        """Return status text with color markup based on length"""
        if queue_length < 5:
            return "[green]✓ Normal[/]"
        elif queue_length < 10:
            return "[yellow]⚠ Busy[/]"
        return "[red]⛔ Overloaded[/]"

    def get_color_markup(self, queue_length: int) -> str:
        """Return color markup based on queue length"""
        if queue_length < 5:
            return "green"
        elif queue_length < 10:
            return "yellow"
        return "red"

    def update_queue(self) -> None:
        """Update queue status information"""
        table = self.query_one(DataTable)
        progress = self.query_one(ProgressBar)
        table.clear()

        models = get_running_models()
        total_load = 0
        max_queue = 0

        if models:
            for model in models:
                # Simulate queue metrics (replace with actual metrics)
                queue_length = random.randint(0, 15)
                processing = random.randint(1, 5)
                wait_time = random.randint(100, 2000)

                color = self.get_color_markup(queue_length)
                status = self.get_queue_status(queue_length)

                table.add_row(
                    f"[{color}]{model['name']}[/]",
                    f"[{color}]{queue_length}[/]",
                    f"[{color}]{processing}[/]",
                    f"[{color}]{wait_time}ms[/]",
                    status
                )

                total_load += queue_length
                max_queue = max(max_queue, queue_length)
        else:
            table.add_row(
                "[dim]No models[/]",
                "[dim]-[/]",
                "[dim]-[/]",
                "[dim]-[/]",
                "[dim]N/A[/]"
            )

        # Update progress bar to show overall queue load
        if max_queue > 0:
            progress.update(total=(max_queue * len(models)))
            progress.advance(total_load)