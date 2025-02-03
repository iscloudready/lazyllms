from textual.widgets import Static, DataTable
from textual.app import ComposeResult
from rich.text import Text
from core.ollama_api import get_running_models
import time

# details_panel.py
class ModelDetailsPanel(Static):
    """Panel showing detailed model information"""

    def compose(self) -> ComposeResult:
        yield Static("🔍 Model Details", classes="panel-title")
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.zebra_stripes = True
        table.add_columns("Attribute", "Value")
        self.selected_model = None
        self._last_update = 0
        self._cache = {}

    def format_timestamp(self, timestamp_str: str) -> str:
        """Format timestamp with error handling."""
        try:
            ts = time.strptime(timestamp_str.split("+")[0], "%Y-%m-%dT%H:%M:%S")
            return time.strftime("%Y-%m-%d %H:%M:%S", ts)
        except (ValueError, AttributeError, IndexError):
            return timestamp_str

    def format_size(self, size_bytes: int) -> str:
        """Format size in bytes to appropriate unit."""
        try:
            gb_size = size_bytes / (1024 * 1024 * 1024)
            if gb_size >= 1:
                return f"{gb_size:.1f}GB"
            mb_size = size_bytes / (1024 * 1024)
            return f"{mb_size:.1f}MB"
        except (TypeError, ZeroDivisionError):
            return "Unknown"

    def update_details(self, model_name: str = None) -> None:
        """Update model details with caching and error handling."""
        table = self.query_one(DataTable)
        current_time = time.time()

        # Clear table if no model selected
        if not model_name:
            table.clear()
            table.add_row(
                Text("No model selected", style="dim"),
                Text("-", style="dim")
            )
            return

        try:
            # Check cache and update interval
            if (model_name in self._cache and
                current_time - self._last_update < 2.0 and
                self.selected_model == model_name):
                return

            self.selected_model = model_name
            table.clear()

            # Fetch model details
            models = get_running_models()
            model = next((m for m in models if m['name'] == model_name), None)

            if not model:
                table.add_row(
                    Text("Error", style="red"),
                    Text(f"Model '{model_name}' not found", style="red")
                )
                return

            # Extract and display model details
            details = model.get('details', {})
            modified_at = model.get('modified_at', '')

            # Define attributes with their styling
            attributes = [
                ("Model Name", model.get('name', 'Unknown'), "bright_green"),
                ("Model ID", model.get('digest', 'Unknown')[:12], "bright_yellow"),
                ("Family", details.get('family', 'Unknown'), "blue"),
                ("Parameters", details.get('parameter_size', 'Unknown'), "magenta"),
                ("Format", details.get('format', 'Unknown'), "cyan"),
                ("Quantization", details.get('quantization_level', 'Unknown'), "green"),
                ("Size", self.format_size(model.get('size', 0)), "bright_magenta"),
                ("Last Modified", self.format_timestamp(modified_at), "yellow"),
            ]

            # Add rows to table
            for attr, value, style in attributes:
                table.add_row(
                    Text(attr, style="blue"),
                    Text(str(value), style=style)
                )

            # Cache the results
            self._cache[model_name] = {
                'data': model,
                'timestamp': current_time
            }
            self._last_update = current_time

        except Exception as e:
            error_msg = f"Failed to load details: {str(e)}"
            table.clear()
            table.add_row(
                Text("Error", style="red"),
                Text(error_msg, style="red")
            )
            if hasattr(self, 'app'):
                self.app.notify(error_msg, severity="error")

    def clear_cache(self) -> None:
        """Clear the cache when needed."""
        self._cache.clear()
        self._last_update = 0