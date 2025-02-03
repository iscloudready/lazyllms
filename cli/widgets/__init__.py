# cli/widgets/__init__.py
"""LazyLLMs widgets package."""

from cli.widgets.models_panel import ModelsPanel
from cli.widgets.system_panel import SystemPanel
from cli.widgets.performance_panel import PerformancePanel
from cli.widgets.log_panel import LogPanel
from cli.widgets.details_panel import ModelDetailsPanel
from cli.widgets.time_panel import TimePanel
from cli.widgets.stats_panel import ModelStatsPanel
from cli.widgets.system_banner import SystemConfigBanner

__all__ = [
    'ModelsPanel',
    'SystemPanel',
    'PerformancePanel',
    'LogPanel',
    'ModelDetailsPanel',
    'TimePanel',
    'ModelStatsPanel',
    'SystemConfigBanner',
]