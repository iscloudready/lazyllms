from textual.widgets import Static, DataTable
from textual.app import ComposeResult
from rich.text import Text
from core.ollama_api import get_running_models

class ModelStatsPanel(Static):
    """Panel showing model statistics and summaries"""

    def compose(self) -> ComposeResult:
        yield Static("📊 Model Statistics", classes="panel-title")
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.zebra_stripes = True
        table.add_columns("Metric", "Value")
        self.update_stats()

    def update_stats(self) -> None:
        """Update model statistics."""
        table = self.query_one(DataTable)
        table.clear()

        try:
            models = get_running_models()
            if not models:
                return

            # Calculate statistics
            total_models = len(models)
            total_size = sum(m.get('size', 0) for m in models) / (1024**3)  # GB
            families = set(m.get('details', {}).get('family', '') for m in models)
            largest_model = max(models, key=lambda m: m.get('size', 0))
            total_params = sum(float(m.get('details', {}).get('parameter_size', '0').rstrip('B')) for m in models)

            # Add statistics rows
            stats = [
                ("Total Models", f"{total_models}", "bright_green"),
                ("Total Size", f"{total_size:.1f}GB", "cyan"),
                ("Model Families", f"{len(families)}", "yellow"),
                ("Largest Model", f"{largest_model.get('name')} ({largest_model.get('size')/(1024**3):.1f}GB)", "magenta"),
                ("Total Parameters", f"{total_params:.1f}B", "bright_blue"),
                ("Average Size", f"{total_size/total_models:.1f}GB", "green"),
                ("Average Parameters", f"{total_params/total_models:.1f}B", "blue"),
                ("Quantization Types", str(len(set(m.get('details', {}).get('quantization_level', '') for m in models))), "bright_magenta")
            ]

            for label, value, style in stats:
                table.add_row(
                    Text(label, style="blue"),
                    Text(value, style=style)
                )

        except Exception as e:
            if hasattr(self, 'app'):
                self.app.notify(f"Error updating stats: {str(e)}", severity="error")