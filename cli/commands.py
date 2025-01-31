from core.ollama_api import get_running_models
from core.monitor import get_system_usage

def list_models():
    """List all running models with system usage"""
    models = get_running_models()
    usage = get_system_usage()

    print("\n📌 Running Models:")
    if not models:
        print("❌ No models running")
        return

    for model in models:
        print(f"✅ {model['name']} - Version: {model['digest']}")

    print("\n📊 System Usage:")
    for key, value in usage.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    list_models()
