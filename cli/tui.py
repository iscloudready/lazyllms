from rich.console import Console
from rich.table import Table
from core.ollama_api import get_running_models
from core.monitor import get_system_usage

console = Console()

def show_tui():
    """Display interactive terminal UI"""
    models = get_running_models()
    usage = get_system_usage()

    table = Table(title="LazyLLMs - Model Manager")
    table.add_column("Model Name", justify="left", style="cyan")
    table.add_column("Version", justify="center", style="yellow")
    table.add_column("Status", justify="right", style="green")

    if models:
        for model in models:
            table.add_row(model['name'], model['digest'], "✅ Running")
    else:
        table.add_row("No models", "-", "❌ Not running")

    console.print(table)

    console.print("\n[bold]📊 System Usage:[/bold]")
    for key, value in usage.items():
        console.print(f"[blue]{key}[/blue]: {value}")

if __name__ == "__main__":
    show_tui()
