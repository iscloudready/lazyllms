from textual.widgets import Static, DataTable
from textual.app import ComposeResult
from rich.text import Text
from core.ollama_api import get_running_models

class ModelsPanel(Static):
    """Panel showing available models"""

    def compose(self) -> ComposeResult:
        yield Static("📦 Available Models", classes="panel-title")
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("Model", "Parameters", "Size", "Type", "Status")
        self.update_models()

    def update_models(self) -> None:
        models = get_running_models()
        table = self.query_one(DataTable)
        table.clear()

        if models:
            for model in models:
                size_gb = model['size'] / 1024 / 1024 / 1024
                details = model.get('details', {})
                param_size = details.get('parameter_size', 'N/A')
                quant = details.get('quantization_level', 'N/A')
                family = details.get('family', 'unknown')

                # Color-code model families
                family_colors = {
                    'llama': 'red',
                    'gemma2': 'bright_blue',
                    'qwen2': 'green',
                    'mistral': 'magenta'
                }
                family_color = family_colors.get(family, 'white')

                table.add_row(
                    Text(model['name'], style="bright_green"),
                    Text(param_size, style="yellow"),
                    Text(f"{size_gb:.1f}GB", style="cyan"),
                    Text(f"{family} ({quant})", style=family_color),
                    Text("✓ Running", style="green")
                )
        else:
            table.add_row(
                Text("No models", style="red"),
                Text("-", style="red"),
                Text("-", style="red"),
                Text("-", style="red"),
                Text("❌ Not running", style="red")
            )