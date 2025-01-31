from rich.console import Console
from rich.table import Table
from core.ollama_api import get_running_models
from core.monitor import get_system_usage

console = Console()

def show_tui():
    """Display interactive terminal UI"""
    models = get_running_models()
    usage = get_system_usage()

    # Table for AI Models
    model_table = Table(title="LazyLLMs - Model Manager", show_header=True, header_style="bold cyan")
    model_table.add_column("Model Name", justify="left", style="cyan")
    model_table.add_column("Version", justify="center", style="yellow")
    model_table.add_column("Status", justify="right", style="green")

    if models:
        for model in models:
            model_table.add_row(model['name'], model['digest'], "✅ Running")
    else:
        model_table.add_row("No models", "-", "❌ Not running")

    # Table for System Usage
    system_table = Table(title="📊 System Resource Usage", show_header=True, header_style="bold magenta")
    system_table.add_column("Resource", style="bold white", justify="left")
    system_table.add_column("Usage", style="yellow", justify="right")

    system_table.add_row("CPU", f"{usage['CPU']}")
    system_table.add_row("RAM", f"{usage['RAM']}")
    system_table.add_row("GPU", f"{usage['GPU']}")
    system_table.add_row("VRAM", f"{usage['VRAM']}")

    # Print tables
    console.print(model_table)
    console.print(system_table)

if __name__ == "__main__":
    show_tui()
