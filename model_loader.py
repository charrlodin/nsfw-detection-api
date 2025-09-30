"""
Model loader and inference for NSFW detection
"""

import logging
import torch
from PIL import Image
from transformers import AutoModelForImageClassification, AutoFeatureExtractor
from pathlib import Path
import io
from typing import Dict, Union

import config

logger = logging.getLogger(__name__)


class NSFWDetector:
    """NSFW content detector using Hugging Face transformers"""
    
    def __init__(self):
        self.model = None
        self.feature_extractor = None
        self.device = None
        self.labels = None
        
    def load_model(self):
        """Load the NSFW detection model"""
        logger.info(f"Loading model: {config.MODEL_NAME}")
        
        try:
            # Detect device (GPU if available, else CPU)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Using device: {self.device}")
            
            # Load model and feature extractor
            self.model = AutoModelForImageClassification.from_pretrained(
                config.MODEL_NAME,
                cache_dir=str(config.MODEL_DIR)
            )
            self.feature_extractor = AutoFeatureExtractor.from_pretrained(
                config.MODEL_NAME,
                cache_dir=str(config.MODEL_DIR)
            )
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            # Get label mappings
            self.labels = self.model.config.id2label
            logger.info(f"Model loaded successfully. Labels: {self.labels}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def predict(self, image_bytes: bytes, threshold_preset: str = "balanced") -> Dict[str, float]:
        """
        Predict NSFW content from image bytes
        
        Args:
            image_bytes: Image data as bytes
            threshold_preset: Threshold preset (strict/balanced/permissive)
            
        Returns:
            Dictionary with predictions and metadata
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed (handle RGBA, grayscale, etc.)
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            # Preprocess image
            inputs = self.feature_extractor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
            
            # Convert to dict - Binary classification
            probs = probabilities[0].cpu().numpy()
            results = {}
            
            # Map to binary classes (normal/nsfw)
            for idx, prob in enumerate(probs):
                label = self.labels.get(idx, f"class_{idx}")
                label = label.lower().replace(" ", "_")
                results[label] = float(prob)
            
            # Ensure we have both classes
            if "normal" not in results:
                results["normal"] = 1.0 - results.get("nsfw", 0.0)
            if "nsfw" not in results:
                results["nsfw"] = 1.0 - results.get("normal", 0.0)
            
            return results
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise
    
    def is_nsfw(self, predictions: Dict[str, float], threshold_preset: str = "balanced") -> bool:
        """
        Check if content is NSFW based on configurable threshold
        
        Args:
            predictions: Dictionary with normal/nsfw probabilities
            threshold_preset: Threshold preset (strict/balanced/permissive)
            
        Returns:
            True if NSFW probability exceeds threshold
        """
        threshold = config.THRESHOLDS.get(threshold_preset, config.THRESHOLDS["balanced"])
        return predictions.get("nsfw", 0.0) >= threshold
    
    def get_confidence(self, predictions: Dict[str, float]) -> float:
        """
        Get confidence score (how sure we are of the prediction)
        
        Returns:
            Confidence score (0-1), higher = more confident
        """
        # Confidence is the maximum probability
        return max(predictions.values())


# Global instance
detector = NSFWDetector()


def load_model():
    """Load the model (called at startup)"""
    detector.load_model()


def predict_nsfw(image_bytes: bytes, threshold_preset: str = "balanced") -> Dict[str, float]:
    """
    Predict NSFW content from image bytes
    
    Args:
        image_bytes: Image data as bytes
        threshold_preset: Threshold preset (strict/balanced/permissive)
        
    Returns:
        Dictionary with predictions, classification, and confidence
    """
    predictions = detector.predict(image_bytes, threshold_preset)
    
    is_nsfw = detector.is_nsfw(predictions, threshold_preset)
    confidence = detector.get_confidence(predictions)
    
    return {
        "nsfw": predictions.get("nsfw", 0.0),
        "normal": predictions.get("normal", 0.0),
        "is_nsfw": is_nsfw,
        "confidence": confidence,
        "threshold_used": config.THRESHOLDS.get(threshold_preset, config.THRESHOLDS["balanced"]),
        "threshold_preset": threshold_preset
    }
