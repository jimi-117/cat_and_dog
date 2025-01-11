import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-replace-in-production')
    MODEL_PATH = os.path.join(BASE_DIR, "models", "model.keras")
    FEEDBACK_FOLDER = os.path.join(BASE_DIR, "data", "feedback")
    
    # Monitoring settings
    PROMETHEUS_PORT = 8000
    MLFLOW_TRACKING_URI = "http://localhost:5000"
    
    # Model settings
    IMAGE_SIZE = (128, 128)
    CLASS_NAMES = ["chien", "chat"]
    CONFIDENCE_THRESHOLD = 0.5