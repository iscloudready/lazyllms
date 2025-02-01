from textual.widgets import Static, DataTable
from textual.app import ComposeResult
from rich.text import Text
from core.ollama_api import get_running_models
import time

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
        self.update_details()

    def format_timestamp(self, timestamp_str: str) -> str:
        """Format timestamp with error handling."""
        try:
            # Parse the timestamp and handle timezone
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
        """Update model details with comprehensive error handling."""
        table = self.query_one(DataTable)
        table.clear()

        if not model_name:
            table.add_row(
                Text("No model selected", style="dim"),
                Text("-", style="dim")
            )
            return

        try:
            # Rate limit updates
            current_time = time.time()
            if current_time - self._last_update < 1:
                return

            self.selected_model = model_name
            models = get_running_models()
            model = next((m for m in models if m['name'] == model_name), None)

            if not model:
                table.add_row(
                    Text("Error", style="red"),
                    Text(f"Model '{model_name}' not found", style="red")
                )
                return

            # Extract model details safely
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

            # Add base attributes
            for attr, value, style in attributes:
                table.add_row(
                    Text(attr, style="blue"),
                    Text(str(value), style=style)
                )

            # Add extended attributes if available
            if 'license' in details:
                table.add_row(
                    Text("License", style="blue"),
                    Text(str(details['license']), style="bright_blue")
                )

            if 'languages' in details:
                table.add_row(
                    Text("Languages", style="blue"),
                    Text(", ".join(details['languages']), style="bright_cyan")
                )

            # Add any additional details present in the model
            extra_details = {k: v for k, v in details.items()
                           if k not in ['family', 'parameter_size', 'format',
                                      'quantization_level', 'license', 'languages']}

            for key, value in extra_details.items():
                if value:  # Only add if value exists
                    table.add_row(
                        Text(key.replace('_', ' ').title(), style="blue"),
                        Text(str(value), style="white")
                    )

            self._last_update = current_time

        except Exception as e:
            table.add_row(
                Text("Error", style="red"),
                Text(f"Failed to load details: {str(e)}", style="red")
            )
            if hasattr(self, 'app'):
                self.app.notify(f"Error updating model details: {str(e)}", severity="error")