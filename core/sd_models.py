import os
import json
from pathlib import Path
import time

def get_sd_models(base_path: str) -> list:
    """Detect Stable Diffusion models in the given path."""
    models = []

    # Common SD model extensions and patterns
    sd_patterns = ['.ckpt', '.safetensors', '.pt', '.pth']
    sd_folders = ['models', 'stable-diffusion', 'checkpoints']

    def get_model_size(path):
        """Get model size in GB."""
        try:
            size_bytes = os.path.getsize(path)
            return f"{size_bytes / (1024**3):.1f}GB"
        except:
            return "N/A"

    def is_sd_model(path):
        """Check if file is likely a SD model."""
        return any(path.endswith(ext) for ext in sd_patterns)

    try:
        base = Path(base_path)

        # Recursively search for model files
        for folder in sd_folders:
            model_path = base / folder
            if model_path.exists():
                for file in model_path.rglob("*"):
                    if file.is_file() and is_sd_model(str(file)):
                        modified_time = time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.localtime(os.path.getmtime(file))
                        )

                        models.append({
                            'name': file.name,
                            'path': str(file),
                            'size': get_model_size(file),
                            'modified': modified_time,
                            'parameters': 'SD',  # Could parse from filename
                            'status': 'Available',
                            'type': 'Stable Diffusion'
                        })

        # Also check for config files that might indicate models
        config_files = [
            'config.json',
            'sd_models.json',
            'models.yaml'
        ]

        for config in config_files:
            config_path = base / config
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config_data = json.load(f)
                        if isinstance(config_data, dict) and 'models' in config_data:
                            for model in config_data['models']:
                                if isinstance(model, dict):
                                    models.append({
                                        'name': model.get('name', 'Unknown'),
                                        'path': model.get('path', ''),
                                        'size': get_model_size(model.get('path', '')),
                                        'parameters': model.get('type', 'SD'),
                                        'status': 'Available',
                                        'type': 'Stable Diffusion'
                                    })
                except:
                    pass

        return models

    except Exception as e:
        print(f"Error scanning for SD models: {e}")
        return []