# core/metrics.py
import psutil
import time
from typing import Dict, Optional

class MetricsManager:
    def __init__(self):
        self._metrics_cache = {}
        self._last_update = time.time()
        self._update_interval = 2.0

    def get_model_process_id(self, model_name: str) -> Optional[int]:
        """Get process ID for Ollama model."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'ollama' in proc.info['name'].lower() and \
                   model_name in ' '.join(proc.info['cmdline'] or []):
                    return proc.info['pid']
        except:
            return None

    def get_model_metrics(self, model_name: str) -> Dict:
        """Get actual metrics if available, otherwise estimate."""
        try:
            # Check cache first
            if model_name in self._metrics_cache and \
               time.time() - self._metrics_cache[model_name]['timestamp'] < self._update_interval:
                return self._metrics_cache[model_name]['data']

            # Try to get real metrics from Ollama process
            pid = self.get_model_process_id(model_name)
            if pid:
                process = psutil.Process(pid)
                metrics = {
                    'cpu_percent': process.cpu_percent(),
                    'memory_info': process.memory_info(),
                    'io_counters': process.io_counters(),
                    'timestamp': time.time()
                }

                # Update cache
                self._metrics_cache[model_name] = {
                    'data': metrics,
                    'timestamp': time.time()
                }
                return metrics

        except Exception as e:
            print(f"Error getting metrics for {model_name}: {e}")
        return {}

    def should_update(self) -> bool:
        """Check if metrics should be updated."""
        return time.time() - self._last_update > self._update_interval