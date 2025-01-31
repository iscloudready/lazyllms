import requests
import random

OLLAMA_API_URL = "http://localhost:11434/api"

def get_model_logs(model_name):
    """Simulated function to fetch logs for a specific AI model"""
    sample_logs = [
        f"[INFO] {model_name} Model Initialized...",
        f"[INFO] {model_name} Processing Requests...",
        f"[WARNING] {model_name} High Memory Usage Detected!",
        f"[ERROR] {model_name} Model Timeout!",
        f"[DEBUG] {model_name} Debugging Information..."
    ]
    return random.sample(sample_logs, 3)  # Return 3 random logs

def get_running_models():
    """Fetch list of running Ollama models"""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags")
        response.raise_for_status()
        models = response.json().get("models", [])
        return models
    except requests.RequestException as e:
        print(f"❌ Error fetching models: {e}")
        return []

def start_model(model_name):
    """Start an Ollama model"""
    try:
        response = requests.post(f"{OLLAMA_API_URL}/run", json={"model": model_name})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Failed to start {model_name}: {e}")
        return None
