from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Log
from textual.binding import Binding
from core.ollama_api import get_running_models

from cli.widgets.models_panel import ModelsPanel
from cli.widgets.system_banner import SystemConfigBanner
from cli.widgets.system_panel import SystemPanel
from cli.widgets.performance_panel import PerformancePanel
from cli.widgets.log_panel import LogPanel
from cli.widgets.details_panel import ModelDetailsPanel
from cli.widgets.time_panel import TimePanel
from cli.widgets.stats_panel import ModelStatsPanel  # Add this import

import yaml
import time

class LazyLLMsApp(App):
    """LazyLLMs TUI Application"""
    TITLE = "🧧 LazyLLMs - AI Model Manager"
    SUB_TITLE = "Monitor and manage your AI models"

    CSS = """
    Screen {
        layout: vertical;
    }

    Header1 {
        dock: top;
        background: $boost;
        color: $text;
        height: 1;
    }

    Header {
        background: $boost;
        color: $text;
        text-align: center;
        height: 1;
    }

    Footer {
        dock: bottom;
        background: $boost;
        color: $text;
        height: 1;
    }

    .models-row {
        height: 35%;
        layout: horizontal;
        margin: 1;
    }

    ModelsPanel {
        width: 70%;
        height: 100%;
        margin-right: 1;
        border: round $primary;
    }

    ModelStatsPanel {
        width: 30%;
        height: 100%;
        border: round $primary;
    }

    .system-row {
        height: 30%;
        layout: horizontal;
        margin: 0 1;
    }

    SystemPanel {
        width: 1fr;
        height: 100%;
        margin-right: 1;
        border: round $primary;
    }

    PerformancePanel {
        width: 1fr;
        height: 100%;
        margin-right: 1;
        border: round $primary;
    }

    TimePanel {
        width: 1fr;
        height: 100%;
        border: round $primary;
    }

    .bottom-row {
        height: 35%;
        layout: horizontal;
        margin: 0 1 1 1;
    }

    ModelDetailsPanel {
        width: 1fr;
        height: 100%;
        margin-right: 1;
        border: round $primary;
    }

    LogPanel {
        width: 1fr;
        height: 100%;
        border: round $primary;
    }

    .panel-title {
        background: $panel;
        padding: 1;
        text-align: center;
        border-bottom: heavy $primary;
        width: 100%;
    }

    DataTable {
        width: 100%;
        height: 85%;
        margin: 0 1;
    }

    Log {
        margin: 0 1;
        height: 85%;
        background: $surface;
        color: $text;
    }

    .focusable:focus {
        border: double $accent;
    }

    SystemConfigBanner {
        background: $surface;
        color: $text;
        height: 1;
        padding: 0 1;
        border-bottom: heavy $primary;
    }

    SystemConfigBanner1 {
        background: $boost;
        color: $text;
        height: 1;
        dock: top;
        padding: 0 1;
        border-bottom: heavy $primary;
    }
    """

    def __init__(self):
        super().__init__()
        # Initialize cache and update intervals
        self._cache = {
            'models': {},
            'system': {},
            'performance': {},
            'selected_model': None,
            'last_update': 0
        }
        self._update_intervals = {
            'system': 2.0,
            'models': 5.0,
            'performance': 3.0,
            'details': 1.0
        }

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("tab", "focus_next", "Focus Next"),
        Binding("shift+tab", "focus_previous", "Focus Previous"),
        Binding("c", "clear_logs", "Clear Logs"),
        Binding("enter", "select_model", "Select Model"),
        Binding("?", "show_help", "Show Help"),
    ]

    # Add to tui.py
    def safe_refresh(self) -> None:
        """Safe refresh with recovery."""
        for panel in self.query("Panel"):
            try:
                if hasattr(panel, 'update'):
                    panel.update()
            except Exception as e:
                self.notify(f"Panel refresh error: {str(e)}", severity="error")
                try:
                    panel.mount()  # Try remounting
                except:
                    pass

    # Update in models_panel.py
    def on_data_table_selection_changed(self) -> None:
        """Handle table selection with caching."""
        if not hasattr(self, '_last_selection_time'):
            self._last_selection_time = 0

        current_time = time.time()
        if current_time - self._last_selection_time < 0.1:  # Debounce
            return

        table = self.query_one(DataTable)
        if table and table.cursor_row is not None:
            try:
                model_cell = table.get_row_at(table.cursor_row)[0]
                if model_cell:
                    model_name = str(model_cell).strip()
                    if model_name != self._last_selected:
                        self._last_selected = model_name
                        self._last_selection_time = current_time
                        if self.app:
                            self.app.action_select_model()
            except Exception:
                pass

    # Add this method to LazyLLMsApp class in tui.py
    def get_system_info(self) -> str:
        """Get formatted system configuration information."""
        try:
            import platform
            import psutil
            from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetName, nvmlDeviceGetMemoryInfo

            # CPU Info
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_info = f"CPU: {cpu_count} cores @ {cpu_freq.max/1000:.1f}GHz"
            else:
                cpu_info = f"CPU: {cpu_count} cores"

            # RAM Info
            ram = psutil.virtual_memory()
            ram_info = f"RAM: {ram.total / (1024**3):.1f}GB"

            # GPU Info
            try:
                nvmlInit()
                handle = nvmlDeviceGetHandleByIndex(0)
                gpu_name = nvmlDeviceGetName(handle)
                gpu_memory = nvmlDeviceGetMemoryInfo(handle)
                gpu_info = f"GPU: {gpu_name} ({gpu_memory.total / (1024**3):.1f}GB)"
            except Exception:
                gpu_info = "GPU: None"

            # OS Info
            os_info = f"OS: {platform.system()} {platform.release()}"

            # Python Info
            python_info = f"Python: {platform.python_version()}"

            return f"🖥️ {cpu_info} | 💾 {ram_info} | 🎮 {gpu_info} | 💻 {os_info} | 🐍 {python_info}"

        except Exception as e:
            return f"Error getting system info: {str(e)}"

    def compose(self) -> ComposeResult:
            """Create app layout."""
            yield Header(show_clock=True)

            # Adding SystemConfigBanner with proper styling
            with SystemConfigBanner():
                yield Static(self.get_system_info(), id="system-info")

            # Top row - Models and Stats
            with Container(classes="models-row"):
                yield ModelsPanel()
                yield ModelStatsPanel()

            # Middle row - System Resources, Performance, Time
            with Container(classes="system-row"):
                yield SystemPanel()
                yield PerformancePanel()
                yield TimePanel()

            # Bottom row - Model Details and Logs
            with Container(classes="bottom-row"):
                yield ModelDetailsPanel()
                yield LogPanel()

            yield Footer()

    def on_mount(self) -> None:
        """Initialize app and start refresh timer."""
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
                refresh_interval = float(config.get("monitoring", {}).get("refresh_interval", 2.0))
        except Exception as e:
            self.notify("⚠️ Using default refresh interval (2s)", severity="warning")
            refresh_interval = 2.0

        # Initial data load
        self.refresh_data()

        # Start refresh timer
        self.set_interval(refresh_interval, self.refresh_data)

    def refresh_data(self) -> None:
        """Optimized refresh with caching."""
        current_time = time.time()

        try:
            # Only update system metrics every interval
            if current_time - self._cache['last_update'] > self._update_intervals['system']:
                self.query_one(SystemPanel).update_metrics()
                self.query_one(TimePanel).update_time()
                self._cache['last_update'] = current_time

            # Update models only if needed
            if current_time - self._cache.get('models_last_update', 0) > self._update_intervals['models']:
                models_panel = self.query_one(ModelsPanel)
                new_models = get_running_models()
                if new_models != self._cache.get('models_data'):
                    self._cache['models_data'] = new_models
                    models_panel.update_models()
                    self.query_one(ModelStatsPanel).update_stats()
                self._cache['models_last_update'] = current_time

            # Update performance metrics
            if current_time - self._cache.get('performance_last_update', 0) > self._update_intervals['performance']:
                self.query_one(PerformancePanel).update_metrics()
                self._cache['performance_last_update'] = current_time

        except Exception as e:
            self.notify(f"Refresh error: {str(e)}", severity="error")

    def action_refresh(self) -> None:
        """Manual refresh action."""
        self.refresh_data()
        self.notify("✨ Refreshed", severity="information")

    def action_clear_logs(self) -> None:
        """Clear the logs panel."""
        self.query_one(LogPanel).clear_logs()
        self.notify("🧹 Logs cleared", severity="information")

    def action_focus_next(self) -> None:
        """Cycle focus through panels."""
        panels = [
            self.query_one(ModelsPanel),
            self.query_one(SystemPanel),
            self.query_one(PerformancePanel),
            self.query_one(ModelStatsPanel),  # New panel
            self.query_one(TimePanel),
            self.query_one(ModelDetailsPanel),
            self.query_one(LogPanel)
        ]

        current = self.focused
        if current in panels:
            idx = panels.index(current)
            next_idx = (idx + 1) % len(panels)
            panels[next_idx].focus()
        else:
            panels[0].focus()

    def action_focus_previous(self) -> None:
        """Cycle focus through panels in reverse."""
        panels = [
            self.query_one(ModelsPanel),
            self.query_one(SystemPanel),
            self.query_one(PerformancePanel),
            self.query_one(ModelStatsPanel),  # New panel
            self.query_one(TimePanel),
            self.query_one(ModelDetailsPanel),
            self.query_one(LogPanel)
        ]

        current = self.focused
        if current in panels:
            idx = panels.index(current)
            prev_idx = (idx - 1) % len(panels)
            panels[prev_idx].focus()
        else:
            panels[-1].focus()

    def action_clear_logs(self) -> None:
        """Clear the logs panel."""
        log_panel = self.query_one(LogPanel)
        if log_panel:
            log_panel.clear_logs()
            self.notify("🧹 Logs cleared", severity="information")

    def action_show_help(self) -> None:
        """Show help overlay."""
        help_text = """
        Keyboard Shortcuts:
        q       - Quit application
        r       - Refresh all panels
        tab     - Focus next panel
        shift+tab - Focus previous panel
        c       - Clear logs
        enter   - Select model
        ?       - Show this help
        """
        self.notify(help_text, severity="information", timeout=10)

    def action_select_model(self) -> None:
            """Handle model selection with error handling."""
            try:
                models_table = self.query_one(ModelsPanel).query_one(DataTable)
                if not models_table or models_table.row_count == 0:
                    return

                cursor_row = models_table.cursor_row
                if cursor_row is None:
                    return

                # Get the content from the rendered row
                row_key = cursor_row
                try:
                    # Get model name safely from the first column
                    model_cell = models_table.get_row_at(row_key)[0]
                    if not model_cell:
                        return

                    model_name = str(model_cell).strip()
                    if model_name and model_name != "No models":
                        # Update model details
                        details_panel = self.query_one(ModelDetailsPanel)
                        if details_panel:
                            details_panel.selected_model = model_name
                            details_panel.update_details(model_name)

                        # Update logs
                        log_panel = self.query_one(LogPanel)
                        if log_panel:
                            log_panel.selected_model = model_name
                            log_panel.clear_logs()
                            log_panel.update_logs()

                        self.notify(f"✨ Selected: {model_name}")

                except Exception as e:
                    self.notify(f"❌ Error accessing table data: {str(e)}", severity="error")

            except Exception as e:
                self.notify(f"❌ Selection error: {str(e)}", severity="error")

    def on_data_table_row_selected(self) -> None:
        """Handle row selection in any DataTable."""
        self.action_select_model()

    def on_data_table_row_highlighted(self) -> None:
        """Handle row highlight in any DataTable."""
        self.action_select_model()

def show_tui():
    """Launch the TUI application"""
    app = LazyLLMsApp()
    app.run()