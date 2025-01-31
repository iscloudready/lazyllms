"""LazyLLMs TUI widgets."""

from cli.widgets.models_panel import ModelsPanel
from cli.widgets.system_panel import SystemPanel
from cli.widgets.performance_panel import PerformancePanel
from cli.widgets.log_panel import LogPanel
from cli.widgets.details_panel import ModelDetailsPanel

__all__ = [
    'ModelsPanel',
    'SystemPanel',
    'PerformancePanel',
    'LogPanel',
    'ModelDetailsPanel',
]