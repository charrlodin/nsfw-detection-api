"""
Configuration for NSFW Detection API
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# Model configuration
MODEL_NAME = "Falconsai/nsfw_image_detection"  # Hugging Face model
MODEL_PATH = MODEL_DIR / "nsfw_model"
DEVICE = "cpu"  # Will auto-detect GPU if available

# API configuration
API_TITLE = "NSFW Detection API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Fast, privacy-first NSFW content detection API"

# Image processing
MAX_IMAGE_SIZE_MB = 10
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp", "image/bmp"}
MAX_IMAGE_DIMENSION = 4096  # Max width or height in pixels

# Classification thresholds
# Binary classification: normal vs nsfw
NSFW_CLASSES = ["normal", "nsfw"]

# Configurable threshold presets
THRESHOLDS = {
    "strict": 0.3,      # Flag more aggressively (fewer false negatives, more false positives)
    "balanced": 0.5,    # Recommended default
    "permissive": 0.7   # Only very obvious NSFW (fewer false positives, more false negatives)
}

# Default threshold
DEFAULT_THRESHOLD = "balanced"
FLAG_THRESHOLD = THRESHOLDS[DEFAULT_THRESHOLD]

# Rate limiting
RATE_LIMIT_MODERATE = "60/minute"  # 60 requests per minute for /moderate
RATE_LIMIT_HEALTH = "300/minute"   # Higher limit for health checks

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Privacy settings
STORE_IMAGES = False  # Never store images
LOG_IMAGE_DATA = False  # Never log image content
RETAIN_PREDICTIONS = False  # Don't store prediction results

# Performance
INFERENCE_TIMEOUT_SECONDS = 30
IMAGE_DOWNLOAD_TIMEOUT_SECONDS = 10
