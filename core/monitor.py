import psutil
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates, nvmlDeviceGetMemoryInfo

nvmlInit()

def get_system_usage():
    """Fetch system usage stats: CPU, RAM, GPU"""
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent

    gpu_usage = 0
    gpu_memory = 0
    try:
        handle = nvmlDeviceGetHandleByIndex(0)
        gpu_usage = nvmlDeviceGetUtilizationRates(handle).gpu
        gpu_memory = nvmlDeviceGetMemoryInfo(handle).used / (1024 * 1024)
    except Exception:
        pass  # No GPU detected

    return {
        "CPU": f"{cpu_usage}%",
        "RAM": f"{ram_usage}%",
        "GPU": f"{gpu_usage}%",
        "VRAM": f"{gpu_memory}MB"
    }
