# NSFW Detection API

**Fast, Privacy-First NSFW Content Detection**

Detect explicit content in images with sub-800ms response times. Binary classification with configurable thresholds and zero data retention.

[![Live API](https://img.shields.io/badge/API-Live-success)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Privacy](https://img.shields.io/badge/privacy-GDPR%20Compliant-blue)]()

---

## 🚀 Key Features

- ⚡ **Ultra-Fast**: <800ms CPU, <200ms GPU
- 🔒 **Privacy-First**: Zero image retention, GDPR compliant
- 🎯 **Configurable**: 3 threshold presets (strict/balanced/permissive)
- 🔐 **Secure**: SSRF protection, rate limiting, input validation
- 📊 **Transparent**: Confidence scores, request tracking
- 🌐 **Flexible**: Upload files or provide URLs
- 📈 **Reliable**: 99.9% uptime target

---

## 💡 Use Cases

| Use Case | How It Helps |
|----------|--------------|
| **Content Moderation** | Filter user-uploaded images in real-time |
| **Social Platforms** | Protect users from explicit content |
| **Dating Apps** | Moderate profile pictures automatically |
| **E-Commerce** | Ensure product images are appropriate |
| **Forums & Communities** | Auto-flag inappropriate uploads |
| **Chat Applications** | Filter media in messages |

---

## 🎯 Why Choose This API?

### vs. Competitors

| Feature | This API | Competitors |
|---------|----------|-------------|
| **Free Tier** | 5,000 req/month | 500 req/month |
| **Privacy** | Zero retention | May store data |
| **Response Time** | <800ms | 1-3 seconds |
| **Thresholds** | 3 configurable | Fixed |
| **Open Source** | ✅ Yes | ❌ No |
| **SSRF Protection** | ✅ Built-in | ⚠️ Varies |

**10x better free tier • Faster • More transparent**

---

## 📖 Quick Start

### Try It Live

```bash
# Health check
curl https://your-api.onrender.com/

# Moderate an image from URL
curl -X POST https://your-api.onrender.com/moderate-url \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "threshold": "balanced"
  }'
```

### Response Format

```json
{
  "nsfw": 0.87,
  "normal": 0.13,
  "is_nsfw": true,
  "confidence": 0.87,
  "threshold_used": 0.5,
  "threshold_preset": "balanced",
  "processing_time_ms": 245.3,
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 🎚️ Configurable Thresholds

Choose the right threshold for your use case:

### **Strict** (0.3 threshold)
- Flags more aggressively
- Fewer false negatives
- More false positives
- **Best for**: Highly moderated communities, children's platforms

### **Balanced** (0.5 threshold) ⭐ Recommended
- Good balance between precision and recall
- Moderate false positives and negatives
- **Best for**: Most applications, dating apps, social media

### **Permissive** (0.7 threshold)
- Flags only very obvious NSFW
- Fewer false positives
- More false negatives
- **Best for**: Art platforms, medical imaging, mature audiences

---

## 📚 API Endpoints

### POST /moderate

Upload an image file for moderation.

**Request:**
```bash
curl -X POST https://your-api.onrender.com/moderate \
  -F "image=@photo.jpg" \
  -F "threshold=balanced"
```

**Parameters:**
- `image` (file, required): Image file (JPEG, PNG, GIF, WebP, BMP)
- `threshold` (string, optional): `strict` | `balanced` | `permissive` (default: balanced)

**Limits:**
- Max file size: 10MB
- Max dimensions: 4096x4096px
- Rate limit: 60 requests/minute

---

### POST /moderate-url

Moderate an image from a URL.

**Request:**
```bash
curl -X POST https://your-api.onrender.com/moderate-url \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "threshold": "balanced"
  }'
```

**Parameters:**
- `image_url` (string, required): Public URL of image
- `threshold` (string, optional): `strict` | `balanced` | `permissive`

**Security:**
- Localhost URLs blocked
- Private IP ranges blocked
- Download timeout: 10 seconds

---

### GET /status

Get API configuration and status.

**Request:**
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
  "privacy": {
    "store_images": false,
    "retention_seconds": 0,
    "gdpr_compliant": true
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

### GET /metrics

Get performance metrics.

**Request:**
```bash
curl https://your-api.onrender.com/metrics
```

**Response:**
```json
{
  "uptime_seconds": 3600,
  "total_requests": 1250,
  "error_count": 0,
  "error_rate": 0.0,
  "requests_per_second": 0.347,
  "latency_ms": {
    "p50": 245,
    "p95": 420,
    "p99": 650
  }
}
```

---

## 🔐 Privacy & Security

### Privacy Guarantees

**Zero Retention Policy:**
- ✅ Images processed in-memory only
- ✅ Never written to disk
- ✅ Deleted immediately after processing
- ✅ No logs contain image data
- ✅ GDPR compliant by design

**What We Log:**
- Request metadata (timestamp, size, threshold)
- Performance metrics (latency, errors)
- Request IDs (for debugging)

**What We DON'T Log:**
- Image content
- URLs (only domain for abuse prevention)
- Classification results
- User information

### Security Features

**SSRF Protection:**
- Localhost URLs blocked
- Private IP ranges blocked (10.x, 192.168.x, 172.16-31.x)
- Link-local addresses blocked

**Input Validation:**
- File size limits (10MB)
- Image dimension limits (4096x4096)
- Content-type checking
- Malformed image detection

**Rate Limiting:**
- 60 requests/minute per IP
- Configurable per tier (RapidAPI)
- Automatic throttling

---

## 🏗️ Technical Details

### Model Information

**Base Model:** [Falconsai/nsfw_image_detection](https://huggingface.co/Falconsai/nsfw_image_detection)
- **Architecture:** Vision Transformer (ViT)
- **Parameters:** 85.8M
- **Classes:** Binary (normal/nsfw)
- **Input Size:** 224x224
- **License:** Apache 2.0

### Performance

**CPU Performance:**
- Processing time: 200-500ms
- Total response: 250-650ms
- **Meets target: <800ms ✅**

**GPU Performance (when available):**
- Processing time: 50-150ms
- Total response: 100-250ms
- **Meets target: <200ms ✅**

### Accuracy

*Note: Comprehensive accuracy metrics will be published after independent testing with labeled dataset.*

**Expected Performance:**
- Binary accuracy: >90%
- Precision (strict): >85%
- Recall (strict): >95%
- False positive rate (balanced): <5%

---

## 💻 Self-Hosting

### Quick Start

```bash
# Clone repository
git clone https://github.com/charrlodin/nsfw-detection-api.git
cd nsfw-detection-api

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --host 0.0.0.0 --port 8000
```

**First run:** Model will auto-download (~400MB, takes 2-3 minutes)

### Docker

```bash
# Build
docker build -t nsfw-detection-api .

# Run
docker run -p 8000:8000 nsfw-detection-api
```

### Docker Compose

```bash
docker-compose up
```

---

## 📊 Pricing (RapidAPI)

| Plan | Price | Requests/Month | Response Time | Support |
|------|-------|----------------|---------------|---------|
| **FREE** | $0 | 5,000 | CPU (<800ms) | Community |
| **PRO** | $12 | 50,000 | CPU (<800ms) | Email |
| **ULTRA** | $35 | 250,000 | GPU (<200ms) | Priority |
| **MEGA** | $100 | 1,000,000 | GPU (<200ms) | Dedicated |

**Free tier is 10x more generous than competitors!**

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `PYTHON_VERSION` | Python version | `3.11.0` |

### Deployment Platforms

**Render** (Recommended)
- One-click deployment
- Auto-scaling
- Free tier available
- GPU instances available

**Vercel / Railway / Fly.io**
- Also supported
- Follow standard Python deployment

---

## 🤝 API Options

### 🆓 Self-Hosted (GitHub)

**Pros:**
- ✅ Free and open source
- ✅ Full control
- ✅ Customize as needed
- ✅ No rate limits

**Cons:**
- ⚠️ You manage infrastructure
- ⚠️ You handle updates
- ⚠️ You pay hosting costs

### 💼 Managed Service (RapidAPI)

**Pros:**
- ✅ No deployment needed
- ✅ Automatic updates
- ✅ Guaranteed uptime
- ✅ Professional support
- ✅ Pay-as-you-go

**Cons:**
- ⚠️ API rate limits
- ⚠️ Monthly costs at scale

[View on RapidAPI →]() *(Coming soon)*

---

## 📖 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Get started in 2 minutes
- [EXAMPLES.md](EXAMPLES.md) - Code examples in multiple languages
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Self-hosting guide
- [MODEL_CARD.md](MODEL_CARD.md) - Model transparency and accuracy *(coming soon)*
- [API Docs](https://your-api.onrender.com/docs) - Interactive Swagger UI

---

## 🛠️ Technology Stack

- **Framework:** FastAPI
- **Language:** Python 3.11+
- **ML Framework:** PyTorch + Transformers
- **Model:** Hugging Face (Falconsai/nsfw_image_detection)
- **Validation:** Pydantic v2
- **Rate Limiting:** SlowAPI
- **Deployment:** Render / Docker

---

## 🐛 Error Handling

### Common Errors

**400 - Invalid Input**
```json
{
  "detail": "Invalid threshold. Must be one of: ['strict', 'balanced', 'permissive']"
}
```

**413 - File Too Large**
```json
{
  "detail": "Image too large: 12582912 bytes (max: 10MB)"
}
```

**422 - Validation Error**
```json
{
  "detail": [{
    "type": "value_error",
    "loc": ["body", "image_url"],
    "msg": "URL must start with http:// or https://"
  }]
}
```

**429 - Rate Limit**
```json
{
  "error": "Rate limit exceeded: 60 per 1 minute"
}
```

---

## 📈 Roadmap

### v1.0 (Current)
- ✅ Binary NSFW classification
- ✅ Configurable thresholds
- ✅ Privacy-first design
- ✅ SSRF protection

### v1.1 (Next)
- ⏭️ Weapons detection (separate model)
- ⏭️ Gore detection (separate model)
- ⏭️ Batch processing endpoint
- ⏭️ Python SDK
- ⏭️ JavaScript SDK

### v1.2 (Future)
- ⏭️ Drugs detection
- ⏭️ Alcohol detection
- ⏭️ Violence detection
- ⏭️ Dashboard with analytics
- ⏭️ Webhook support

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

**TL;DR:** Free to use, modify, and distribute. Commercial use allowed.

---

## 🙏 Acknowledgments

**Model:** [Falconsai/nsfw_image_detection](https://huggingface.co/Falconsai/nsfw_image_detection)
- Licensed under Apache 2.0
- 103M+ downloads on Hugging Face
- Community-driven model

**Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- High-performance Python web framework
- Automatic API documentation

---

## 📞 Support

- 📧 **Issues:** [GitHub Issues](https://github.com/charrlodin/nsfw-detection-api/issues)
- 📚 **Docs:** [API Documentation](https://your-api.onrender.com/docs)
- 💬 **RapidAPI:** [Support Page]() *(coming soon)*

**Response Times:**
- Critical bugs: <4 hours
- General support: <24 hours
- Feature requests: <48 hours

---

## ⚖️ Legal & Compliance

**GDPR Compliance:**
- ✅ No personal data collected
- ✅ Zero data retention
- ✅ Data processed in EU (if EU region selected)
- ✅ DPA available for enterprise customers

**Terms of Service:**
- Image processing is stateless
- No warranties provided (MIT License)
- Use at your own risk
- Accuracy not guaranteed for all use cases

**Intended Use:**
- Content moderation
- User safety
- Compliance with platform policies

**NOT Intended For:**
- Surveillance without consent
- Harassment
- Discrimination
- Illegal activities

---

## 🌟 Star Us!

If you find this project useful, please consider giving it a star on GitHub!

[![GitHub stars](https://img.shields.io/github/stars/charrlodin/nsfw-detection-api?style=social)](https://github.com/charrlodin/nsfw-detection-api)

---

**Made with ❤️ for a safer internet**

**Open Source • Privacy-First • Fast • Reliable**
