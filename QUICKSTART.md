# Quick Start Guide

Get up and running with the NSFW Detection API in 2 minutes.

---

## Step 1: Test the Live API

### Health Check

```bash
curl https://your-api.onrender.com/
```

**Response:**
```json
{
  "status": "ok",
  "service": "NSFW Detection API",
  "version": "1.0.0",
  "privacy": "Images are processed in-memory only. No data is stored."
}
```

---

## Step 2: Moderate Your First Image

### Option A: From URL

```bash
curl -X POST https://your-api.onrender.com/moderate-url \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "threshold": "balanced"
  }'
```

###Option B: Upload File

```bash
curl -X POST https://your-api.onrender.com/moderate \
  -F "image=@/path/to/image.jpg" \
  -F "threshold=balanced"
```

---

## Step 3: Understand the Response

```json
{
  "nsfw": 0.87,              // Probability of NSFW content (0-1)
  "normal": 0.13,            // Probability of safe content (0-1)
  "is_nsfw": true,           // Boolean classification result
  "confidence": 0.87,        // How confident the model is (0-1)
  "threshold_used": 0.5,     // Threshold value used
  "threshold_preset": "balanced",  // Which preset was used
  "processing_time_ms": 245.3,     // How long it took
  "request_id": "550e8400..."      // Unique ID for this request
}
```

### Interpreting Results

| Field | Meaning |
|-------|---------|
| `nsfw` > 0.5 | Likely NSFW content |
| `nsfw` < 0.3 | Likely safe content |
| `confidence` > 0.8 | High confidence |
| `confidence` < 0.6 | Lower confidence, review manually |

---

## Step 4: Choose Your Threshold

### Strict (0.3) - Flag More

**Best for:** Children's platforms, highly moderated communities

```bash
curl -X POST https://your-api.onrender.com/moderate-url \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "threshold": "strict"
  }'
```

**Result:** More false positives, fewer false negatives

---

### Balanced (0.5) - Recommended ⭐

**Best for:** Most applications, dating apps, social media

```bash
curl -X POST https://your-api.onrender.com/moderate-url \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "threshold": "balanced"
  }'
```

**Result:** Good balance

---

### Permissive (0.7) - Flag Less

**Best for:** Art platforms, mature audiences

```bash
curl -X POST https://your-api.onrender.com/moderate-url \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "threshold": "permissive"
  }'
```

**Result:** Fewer false positives, more false negatives

---

## Step 5: Check API Status

```bash
curl https://your-api.onrender.com/status
```

**Response:**
```json
{
  "status": "ok",
  "model": {
    "name": "Falconsai/nsfw_image_detection",
    "type": "binary_classification",
    "classes": ["normal", "nsfw"]
  },
  "thresholds": {
    "available": ["strict", "balanced", "permissive"],
    "values": {
      "strict": 0.3,
      "balanced": 0.5,
      "permissive": 0.7
    }
  }
}
```

---

## Python Example

```python
import requests

API_URL = "https://your-api.onrender.com"

def moderate_image(image_url, threshold="balanced"):
    response = requests.post(
        f"{API_URL}/moderate-url",
        json={
            "image_url": image_url,
            "threshold": threshold
        }
    )
    return response.json()

# Test
result = moderate_image("https://example.com/image.jpg")

print(f"NSFW: {result['is_nsfw']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Request ID: {result['request_id']}")

# Make decision
if result['is_nsfw'] and result['confidence'] > 0.8:
    print("⛔ Block this image")
elif result['is_nsfw']:
    print("⚠️  Flag for manual review")
else:
    print("✅ Image is safe")
```

---

## JavaScript Example

```javascript
const API_URL = "https://your-api.onrender.com";

async function moderateImage(imageUrl, threshold = "balanced") {
  const response = await fetch(`${API_URL}/moderate-url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image_url: imageUrl,
      threshold: threshold
    })
  });
  return await response.json();
}

// Test
moderateImage("https://example.com/image.jpg")
  .then(result => {
    console.log(`NSFW: ${result.is_nsfw}`);
    console.log(`Confidence: ${(result.confidence * 100).toFixed(1)}%`);
    console.log(`Request ID: ${result.request_id}`);
    
    // Make decision
    if (result.is_nsfw && result.confidence > 0.8) {
      console.log("⛔ Block this image");
    } else if (result.is_nsfw) {
      console.log("⚠️  Flag for manual review");
    } else {
      console.log("✅ Image is safe");
    }
  });
```

---

## Common Use Cases

### User Upload Validation

```python
def validate_user_upload(file_path):
    """Validate user upload before saving"""
    result = moderate_image_file(file_path)
    
    if result['is_nsfw']:
        return {
            'allowed': False,
            'reason': 'Image contains inappropriate content',
            'request_id': result['request_id']
        }
    
    return {'allowed': True}
```

### Profile Picture Moderation

```python
def moderate_profile_picture(image_url):
    """Moderate profile picture with strict threshold"""
    result = moderate_image(image_url, threshold="strict")
    
    # Strict threshold for profile pictures
    if result['is_nsfw']:
        return {
            'approved': False,
            'message': 'Profile picture not allowed',
            'confidence': result['confidence']
        }
    
    return {'approved': True}
```

### Bulk Moderation

```python
def moderate_batch(image_urls):
    """Moderate multiple images"""
    results = []
    
    for url in image_urls:
        try:
            result = moderate_image(url)
            results.append({
                'url': url,
                'is_nsfw': result['is_nsfw'],
                'confidence': result['confidence'],
                'request_id': result['request_id']
            })
        except Exception as e:
            results.append({
                'url': url,
                'error': str(e)
            })
    
    return results
```

---

## Error Handling

```python
import requests

def moderate_with_error_handling(image_url):
    try:
        response = requests.post(
            f"{API_URL}/moderate-url",
            json={"image_url": image_url},
            timeout=30  # 30 second timeout
        )
        
        # Check for HTTP errors
        if response.status_code == 429:
            return {'error': 'Rate limit exceeded. Please wait.'}
        
        if response.status_code == 413:
            return {'error': 'Image too large. Max 10MB.'}
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        return {'error': 'Request timed out'}
    
    except requests.exceptions.RequestException as e:
        return {'error': f'Request failed: {str(e)}'}
```

---

## Rate Limits

**Free Tier:**
- 60 requests/minute per IP
- 5,000 requests/month

**Paid Tiers:**
- Higher rate limits
- Priority processing
- GPU acceleration

### Handling Rate Limits

```python
import time

def moderate_with_retry(image_url, max_retries=3):
    """Retry on rate limit"""
    for attempt in range(max_retries):
        result = moderate_image(image_url)
        
        if 'error' in result and 'rate limit' in result['error'].lower():
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            continue
        
        return result
    
    return {'error': 'Max retries exceeded'}
```

---

## Self-Hosting

### Local Development

```bash
# Clone repository
git clone https://github.com/charrlodin/nsfw-detection-api.git
cd nsfw-detection-api

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload --port 8000
```

### Docker

```bash
# Build
docker build -t nsfw-api .

# Run
docker run -p 8000:8000 nsfw-api
```

---

## Next Steps

- 📚 [Full Documentation](README.md)
- 💻 [Code Examples](EXAMPLES.md)
- 🚀 [Deployment Guide](DEPLOYMENT_GUIDE.md)
- 📊 [Model Card](MODEL_CARD.md) *(coming soon)*
- 🌐 [Interactive API Docs](https://your-api.onrender.com/docs)

---

## Need Help?

- 📧 [GitHub Issues](https://github.com/charrlodin/nsfw-detection-api/issues)
- 📚 [API Documentation](https://your-api.onrender.com/docs)
- 💬 [RapidAPI Support]() *(coming soon)*

**Response Time:** <24 hours for support requests

---

**You're all set! Start moderating content in production.** 🚀
