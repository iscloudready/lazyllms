import os
import json
import yaml
from pathlib import Path
import time
from typing import Dict, List, Optional

class ModelScanner:
    """Scan and manage different types of AI models."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self._cache = {}
        self._last_scan = 0

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from yaml file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def _should_rescan(self) -> bool:
        """Check if we should rescan based on cache duration."""
        cache_duration = self.config.get('models', {}).get('cache_duration', 300)
        return time.time() - self._last_scan > cache_duration

    def _get_model_family(self, filename: str) -> Optional[Dict]:
        """Determine model family from filename."""
        families = self.config.get('models', {}).get('model_families', {})

        for family, details in families.items():
            extensions = details.get('extensions', [])
            if any(filename.endswith(ext) for ext in extensions):
                return {'family': family, **details}
        return None

    def _get_model_size(self, path: str) -> str:
        """Get formatted model size."""
        try:
            size_bytes = os.path.getsize(path)
            return f"{size_bytes / (1024**3):.1f}GB"
        except:
            return "N/A"

    def scan_models(self, force: bool = False) -> List[Dict]:
        """Scan for all model types in configured paths."""
        if not force and not self._should_rescan() and self._cache:
            return self._cache.get('models', [])

        models = []
        paths = self.config.get('models', {}).get('paths', [])
        scan_subdirs = self.config.get('models', {}).get('scan_subdirectories', True)

        for base_path in paths:
            try:
                base = Path(base_path)
                if not base.exists():
                    continue

                # Scan for model files
                if scan_subdirs:
                    files = base.rglob("*")
                else:
                    files = base.glob("*")

                for file in files:
                    if not file.is_file():
                        continue

                    model_info = self._get_model_family(str(file))
                    if model_info:
                        modified_time = time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.localtime(os.path.getmtime(file))
                        )

                        models.append({
                            'name': file.name,
                            'path': str(file),
                            'size': self._get_model_size(file),
                            'modified': modified_time,
                            'type': model_info['type'],
                            'family': model_info['family'],
                            'color': model_info['color'],
                            'priority': model_info.get('priority', 99),
                            'status': 'Available'
                        })

            except Exception as e:
                print(f"Error scanning path {base_path}: {e}")

        # Sort models by priority and name
        models.sort(key=lambda x: (x['priority'], x['name'].lower()))

        # Update cache
        self._cache['models'] = models
        self._last_scan = time.time()

        return models

    def get_model_stats(self) -> Dict:
        """Get statistics about available models."""
        models = self.scan_models()

        stats = {
            'total_count': len(models),
            'total_size': sum(float(m['size'].rstrip('GB')) for m in models if m['size'] != 'N/A'),
            'by_type': {},
            'by_family': {},
            'largest_model': None,
            'newest_model': None
        }

        # Gather statistics
        for model in models:
            # Count by type
            model_type = model['type']
            stats['by_type'][model_type] = stats['by_type'].get(model_type, 0) + 1

            # Count by family
            family = model['family']
            stats['by_family'][family] = stats['by_family'].get(family, 0) + 1

            # Track largest model
            if not stats['largest_model'] or float(model['size'].rstrip('GB')) > float(stats['largest_model']['size'].rstrip('GB')):
                stats['largest_model'] = model

            # Track newest model
            if not stats['newest_model'] or model['modified'] > stats['newest_model']['modified']:
                stats['newest_model'] = model

        return stats