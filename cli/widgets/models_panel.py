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
        self._last_selected = None  # Store last selected model
        self.update_models()

    def update_models(self) -> None:
        """Update the models list with error handling."""
        table = self.query_one(DataTable)
        current_cursor = table.cursor_row  # Store current cursor position
        table.clear()

        try:
            models = get_running_models()

            if not models:
                table.add_row(
                    Text("No models", style="red"),
                    Text("-", style="red"),
                    Text("-", style="red"),
                    Text("-", style="red"),
                    Text("❌ Not running", style="red")
                )
                return

            # Sort models by name for consistent display
            models = sorted(models, key=lambda x: x.get('name', ''))

            # Track where to restore cursor
            restore_index = None

            for idx, model in enumerate(models):
                try:
                    # Extract model details safely
                    size_gb = model.get('size', 0) / 1024 / 1024 / 1024
                    details = model.get('details', {})
                    param_size = details.get('parameter_size', 'N/A')
                    quant = details.get('quantization_level', 'N/A')
                    family = details.get('family', 'unknown')
                    name = model.get('name', 'Unknown')

                    # If this is our previously selected model, note the index
                    if name == self._last_selected:
                        restore_index = idx

                    # Color-code model families
                    family_colors = {
                        'llama': 'red',
                        'gemma2': 'bright_blue',
                        'qwen2': 'green',
                        'mistral': 'magenta',
                        'phi': 'yellow',
                        'granite': 'cyan'
                    }
                    family_color = family_colors.get(family.lower(), 'white')

                    table.add_row(
                        Text(name, style="bright_green"),
                        Text(str(param_size), style="yellow"),
                        Text(f"{size_gb:.1f}GB", style="cyan"),
                        Text(f"{family} ({quant})", style=family_color),
                        Text("✓ Running", style="green")
                    )
                except Exception as e:
                    table.add_row(
                        Text(str(model.get('name', 'Error')), style="red"),
                        Text("Error", style="red"),
                        Text("Error", style="red"),
                        Text("Error", style="red"),
                        Text("⚠ Error", style="red")
                    )

            # Restore cursor position
            if restore_index is not None:
                table.move_cursor(row=restore_index)
            elif current_cursor is not None and current_cursor < len(models):
                table.move_cursor(row=current_cursor)

        except Exception as e:
            table.add_row(
                Text("Error loading models", style="red"),
                Text("-", style="red"),
                Text("-", style="red"),
                Text("-", style="red"),
                Text(f"⚠ {str(e)}", style="red")
            )
            if hasattr(self, 'app'):
                self.app.notify(f"Error loading models: {str(e)}", severity="error")

    def on_data_table_selection_changed(self) -> None:
        """Handle table selection change."""
        table = self.query_one(DataTable)
        if table and table.cursor_row is not None:
            # Store the selected model name
            model_cell = table.get_row_at(table.cursor_row)[0]
            if model_cell:
                self._last_selected = str(model_cell).strip()

        if self.app and hasattr(self.app, "action_select_model"):
            self.app.action_select_model()

    def on_data_table_highlight_changed(self) -> None:
        """Handle table highlight change."""
        if self.app and hasattr(self.app, "action_select_model"):
            self.app.action_select_model()