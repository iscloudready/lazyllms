# cli/widgets/system_banner.py
from textual.widgets import Static
from textual.app import ComposeResult
import platform
import psutil
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetName, nvmlDeviceGetMemoryInfo

class SystemConfigBanner(Static):
    """Banner showing system configuration"""

    def compose(self) -> ComposeResult:
        yield Static("", id="system-config")

    def on_mount(self) -> None:
        self.update_config()

    def get_gpu_info(self) -> str:
        """Get GPU information using pynvml"""
        try:
            nvmlInit()
            handle = nvmlDeviceGetHandleByIndex(0)
            name = nvmlDeviceGetName(handle)
            memory = nvmlDeviceGetMemoryInfo(handle)
            return f"GPU: {name} ({memory.total / (1024**3):.1f}GB)"
        except Exception:
            return "GPU: None"

    def update_config(self) -> None:
        try:
            # CPU info
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_info = f"CPU: {cpu_count} cores @ {cpu_freq.max/1000:.1f}GHz"
            else:
                cpu_info = f"CPU: {cpu_count} cores"

            # RAM info
            ram = psutil.virtual_memory()
            ram_info = f"RAM: {ram.total / (1024**3):.1f}GB"

            # GPU info
            gpu_info = self.get_gpu_info()

            # OS info
            os_info = f"OS: {platform.system()} {platform.release()}"

            # Python info
            python_info = f"Python: {platform.python_version()}"

            config_text = f"🖥️ {cpu_info} | 💾 {ram_info} | 🎮 {gpu_info} | 💻 {os_info} | 🐍 {python_info}"

            self.query_one("#system-config").update(config_text)

        except Exception as e:
            self.app.notify(f"Error updating system config: {str(e)}", severity="error")