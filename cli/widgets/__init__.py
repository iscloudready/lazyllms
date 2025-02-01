"""LazyLLMs widgets package."""

# Import all widgets to make them available from cli.widgets
from cli.widgets.models_panel import ModelsPanel
from cli.widgets.system_panel import SystemPanel
from cli.widgets.performance_panel import PerformancePanel
from cli.widgets.log_panel import LogPanel
from cli.widgets.details_panel import ModelDetailsPanel
from cli.widgets.time_panel import TimePanel

__all__ = [
    'ModelsPanel',
    'SystemPanel',
    'PerformancePanel',
    'LogPanel',
    'ModelDetailsPanel',
    'TimePanel',
]