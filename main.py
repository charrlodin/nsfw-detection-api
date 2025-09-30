"""
NSFW Detection API - Main Application

Fast, privacy-first API for detecting nudity and NSFW content in images.
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
import time
import io
import uuid
import ipaddress
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import requests
from PIL import Image

import config
from model_loader import load_model, predict_nsfw

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


class Metrics:
    """Track API performance metrics"""
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.latencies = []
        self.start_time = datetime.utcnow()
        
    def record_request(self, latency_ms: float, is_error: bool = False):
        self.request_count += 1
        if is_error:
            self.error_count += 1
        self.latencies.append(latency_ms)
        # Keep last 1000 latencies
        if len(self.latencies) > 1000:
            self.latencies = self.latencies[-1000:]
    
    def get_stats(self):
        if not self.latencies:
            return {}
        sorted_latencies = sorted(self.latencies)
        return {
            'p50': sorted_latencies[len(sorted_latencies) // 2],
            'p95': sorted_latencies[int(len(sorted_latencies) * 0.95)],
            'p99': sorted_latencies[int(len(sorted_latencies) * 0.99)],
        }


metrics = Metrics()


# Request/Response Models
class ImageURLRequest(BaseModel):
    """Request model for image URL"""
    image_url: str = Field(..., description="URL of image to moderate")
    threshold: Optional[str] = Field("balanced", description="Threshold preset: strict/balanced/permissive")
    
    @validator('image_url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        
        # Security: Prevent SSRF attacks
        try:
            parsed = urlparse(v)
            if parsed.hostname:
                # Block localhost
                if parsed.hostname.lower() in ['localhost', '127.0.0.1', '::1', '0.0.0.0']:
                    raise ValueError('Localhost URLs not allowed')
                
                # Block private IP ranges
                try:
                    ip = ipaddress.ip_address(parsed.hostname)
                    if ip.is_private or ip.is_loopback or ip.is_link_local:
                        raise ValueError('Private IP addresses not allowed')
                except ValueError:
                    # Not an IP, probably a domain - that's OK
                    pass
        except Exception as e:
            if 'not allowed' in str(e):
                raise
            # Other parsing errors - let requests handle it
        
        return v
    
    @validator('threshold')
    def validate_threshold(cls, v):
        if v not in config.THRESHOLDS:
            raise ValueError(f'Threshold must be one of: {list(config.THRESHOLDS.keys())}')
        return v


class ModerationResponse(BaseModel):
    """Response model for NSFW detection results"""
    # Binary classification probabilities
    nsfw: float = Field(..., ge=0.0, le=1.0, description="NSFW probability (0-1)")
    normal: float = Field(..., ge=0.0, le=1.0, description="Normal/safe content probability (0-1)")
    
    # Classification result
    is_nsfw: bool = Field(..., description="True if content is classified as NSFW")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    
    # Threshold information
    threshold_used: float = Field(..., description="Threshold value used for classification")
    threshold_preset: str = Field(..., description="Threshold preset used (strict/balanced/permissive)")
    
    # Metadata
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    request_id: str = Field(..., description="Unique request ID for tracking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nsfw": 0.87,
                "normal": 0.13,
                "is_nsfw": True,
                "confidence": 0.87,
                "threshold_used": 0.5,
                "threshold_preset": "balanced",
                "processing_time_ms": 245.3,
                "request_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup"""
    logger.info("Starting up NSFW Detection API...")
    
    # Load model at startup
    try:
        load_model()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise
    
    yield
    
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version=config.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Helper functions
async def download_image(url: str) -> bytes:
    """Download image from URL"""
    try:
        response = requests.get(
            url,
            timeout=config.IMAGE_DOWNLOAD_TIMEOUT_SECONDS,
            headers={'User-Agent': 'NSFWDetectionAPI/1.0'}
        )
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if not any(ct in content_type for ct in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']):
            raise ValueError(f"Invalid content type: {content_type}")
        
        # Check size
        if len(response.content) > config.MAX_IMAGE_SIZE_BYTES:
            raise ValueError(f"Image too large: {len(response.content)} bytes (max: {config.MAX_IMAGE_SIZE_BYTES})")
        
        return response.content
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="Image download timeout")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def validate_image(image_bytes: bytes) -> None:
    """Validate image data"""
    # Check size
    if len(image_bytes) > config.MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Image too large: {len(image_bytes)} bytes (max: {config.MAX_IMAGE_SIZE_MB}MB)"
        )
    
    # Check if valid image
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Check dimensions
        width, height = img.size
        if width > config.MAX_IMAGE_DIMENSION or height > config.MAX_IMAGE_DIMENSION:
            raise HTTPException(
                status_code=413,
                detail=f"Image dimensions too large: {width}x{height} (max: {config.MAX_IMAGE_DIMENSION}x{config.MAX_IMAGE_DIMENSION})"
            )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


# Health check endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": config.API_TITLE,
        "version": config.API_VERSION,
        "privacy": "Images are processed in-memory only. No data is stored."
    }


@app.get("/ping")
async def ping():
    """Simple ping endpoint for health monitoring"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "service": config.API_TITLE
    }


@app.get("/status")
async def status():
    """
    Get API status and configuration.
    
    Returns information about the model, classification type, privacy settings,
    and available threshold presets.
    """
    return {
        "status": "ok",
        "model": {
            "name": config.MODEL_NAME,
            "type": "binary_classification",
            "classes": config.NSFW_CLASSES,
            "device": config.DEVICE
        },
        "version": config.API_VERSION,
        "privacy": {
            "store_images": config.STORE_IMAGES,
            "log_image_data": config.LOG_IMAGE_DATA,
            "retain_predictions": config.RETAIN_PREDICTIONS,
            "retention_seconds": 0,
            "gdpr_compliant": True
        },
        "thresholds": {
            "available": list(config.THRESHOLDS.keys()),
            "values": config.THRESHOLDS,
            "default": config.DEFAULT_THRESHOLD,
            "description": {
                "strict": "Flag more aggressively (0.3 threshold)",
                "balanced": "Recommended default (0.5 threshold)",
                "permissive": "Only very obvious NSFW (0.7 threshold)"
            }
        },
        "limits": {
            "max_image_size_mb": config.MAX_IMAGE_SIZE_MB,
            "max_dimensions": config.MAX_IMAGE_DIMENSION,
            "rate_limit_moderate": config.RATE_LIMIT_MODERATE
        }
    }


@app.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    uptime = (datetime.utcnow() - metrics.start_time).total_seconds()
    latency_stats = metrics.get_stats()
    
    return {
        "uptime_seconds": uptime,
        "total_requests": metrics.request_count,
        "error_count": metrics.error_count,
        "error_rate": metrics.error_count / metrics.request_count if metrics.request_count > 0 else 0,
        "requests_per_second": metrics.request_count / uptime if uptime > 0 else 0,
        "latency_ms": latency_stats
    }


# Main moderation endpoint - File upload
@app.post("/moderate", response_model=ModerationResponse)
@limiter.limit(config.RATE_LIMIT_MODERATE)
async def moderate_image_file(
    request: Request,
    image: UploadFile = File(..., description="Image file to moderate"),
    threshold: str = "balanced"
):
    """
    Moderate an uploaded image for NSFW content.
    
    Upload an image file (JPEG, PNG, GIF, WebP, BMP) and receive binary classification
    results indicating whether the image contains NSFW (Not Safe For Work) content.
    
    **Privacy Guarantee**: Images are processed in-memory only and NEVER stored.
    No image data is logged or retained after processing.
    
    **Configurable Thresholds**:
    - `strict` (0.3): Flag more aggressively, fewer false negatives
    - `balanced` (0.5): Recommended default, good balance
    - `permissive` (0.7): Only very obvious NSFW, fewer false positives
    
    **Rate limit**: 60 requests per minute per IP
    **Max file size**: 10MB
    **Max dimensions**: 4096x4096 pixels
    
    **Returns**: Binary classification with confidence scores and unique request ID
    """
    start_time = time.time()
    is_error = False
    request_id = str(uuid.uuid4())
    
    try:
        # Validate threshold
        if threshold not in config.THRESHOLDS:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid threshold. Must be one of: {list(config.THRESHOLDS.keys())}"
            )
        
        # Read image
        image_bytes = await image.read()
        
        # Validate
        validate_image(image_bytes)
        
        # Run inference
        logger.info(f"[{request_id}] Processing image: {image.filename} ({len(image_bytes)} bytes), threshold: {threshold}")
        results = predict_nsfw(image_bytes, threshold_preset=threshold)
        
        # Record metrics
        elapsed_ms = (time.time() - start_time) * 1000
        metrics.record_request(elapsed_ms, is_error)
        
        # Add metadata
        results['processing_time_ms'] = elapsed_ms
        results['request_id'] = request_id
        
        logger.info(f"[{request_id}] Inference completed in {elapsed_ms:.2f}ms. NSFW: {results['is_nsfw']}, Confidence: {results['confidence']:.3f}")
        
        return results
        
    except HTTPException:
        is_error = True
        elapsed_ms = (time.time() - start_time) * 1000
        metrics.record_request(elapsed_ms, is_error)
        raise
    except Exception as e:
        is_error = True
        elapsed_ms = (time.time() - start_time) * 1000
        metrics.record_request(elapsed_ms, is_error)
        logger.error(f"[{request_id}] Moderation error: {e}")
        raise HTTPException(status_code=500, detail=f"Moderation error: {str(e)}")


# Main moderation endpoint - URL
@app.post("/moderate-url", response_model=ModerationResponse)
@limiter.limit(config.RATE_LIMIT_MODERATE)
async def moderate_image_url(
    request: Request,
    image_request: ImageURLRequest
):
    """
    Moderate an image from URL for NSFW content.
    
    Provide an image URL and receive binary classification results indicating 
    whether the image contains NSFW (Not Safe For Work) content.
    
    **Privacy Guarantee**: Images are downloaded to memory only and NEVER stored.
    No image data is logged or retained after processing.
    
    **Security**: URLs are validated to prevent SSRF attacks. Localhost and 
    private IP addresses are blocked.
    
    **Configurable Thresholds**:
    - `strict` (0.3): Flag more aggressively, fewer false negatives
    - `balanced` (0.5): Recommended default, good balance
    - `permissive` (0.7): Only very obvious NSFW, fewer false positives
    
    **Rate limit**: 60 requests per minute per IP
    **Max file size**: 10MB
    **Download timeout**: 10 seconds
    
    **Returns**: Binary classification with confidence scores and unique request ID
    """
    start_time = time.time()
    is_error = False
    request_id = str(uuid.uuid4())
    
    try:
        threshold = image_request.threshold
        
        # Download image
        logger.info(f"[{request_id}] Downloading image from: {image_request.image_url}")
        image_bytes = await download_image(image_request.image_url)
        
        # Validate
        validate_image(image_bytes)
        
        # Run inference
        logger.info(f"[{request_id}] Processing downloaded image ({len(image_bytes)} bytes), threshold: {threshold}")
        results = predict_nsfw(image_bytes, threshold_preset=threshold)
        
        # Record metrics
        elapsed_ms = (time.time() - start_time) * 1000
        metrics.record_request(elapsed_ms, is_error)
        
        # Add metadata
        results['processing_time_ms'] = elapsed_ms
        results['request_id'] = request_id
        
        logger.info(f"[{request_id}] Inference completed in {elapsed_ms:.2f}ms. NSFW: {results['is_nsfw']}, Confidence: {results['confidence']:.3f}")
        
        return results
        
    except HTTPException:
        is_error = True
        elapsed_ms = (time.time() - start_time) * 1000
        metrics.record_request(elapsed_ms, is_error)
        raise
    except Exception as e:
        is_error = True
        elapsed_ms = (time.time() - start_time) * 1000
        metrics.record_request(elapsed_ms, is_error)
        logger.error(f"[{request_id}] Moderation error: {e}")
        raise HTTPException(status_code=500, detail=f"Moderation error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
