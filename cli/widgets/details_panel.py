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
        self.update_details()

    def update_details(self, model_name: str = None) -> None:
        table = self.query_one(DataTable)
        table.clear()

        if model_name:
            self.selected_model = model_name
            models = get_running_models()
            model = next((m for m in models if m['name'] == model_name), None)

            if model:
                details = model.get('details', {})
                modified_at = model.get('modified_at', '')

                # Parse timestamp and convert to local time
                try:
                    timestamp = time.strptime(modified_at.split("+")[0], "%Y-%m-%dT%H:%M:%S")
                    local_time = time.strftime("%Y-%m-%d %H:%M:%S", timestamp)
                except:
                    local_time = modified_at

                # Model details
                table.add_row(
                    Text("Model Name", style="blue"),
                    Text(model['name'], style="bright_green")
                )
                table.add_row(
                    Text("Family", style="blue"),
                    Text(details.get('family', 'Unknown'), style="yellow")
                )
                table.add_row(
                    Text("Parameters", style="blue"),
                    Text(details.get('parameter_size', 'Unknown'), style="magenta")
                )
                table.add_row(
                    Text("Format", style="blue"),
                    Text(details.get('format', 'Unknown'), style="cyan")
                )
                table.add_row(
                    Text("Quantization", style="blue"),
                    Text(details.get('quantization_level', 'Unknown'), style="green")
                )
                table.add_row(
                    Text("Last Modified", style="blue"),
                    Text(local_time, style="yellow")
                )
                table.add_row(
                    Text("Size", style="blue"),
                    Text(f"{model['size'] / 1024 / 1024 / 1024:.1f}GB", style="magenta")
                )

                # Additional details if available
                if 'license' in details:
                    table.add_row(
                        Text("License", style="blue"),
                        Text(details['license'], style="cyan")
                    )
                if 'languages' in details:
                    table.add_row(
                        Text("Languages", style="blue"),
                        Text(", ".join(details['languages']), style="green")
                    )
        else:
            table.add_row(
                Text("No model selected", style="dim"),
                Text("-", style="dim")
            )