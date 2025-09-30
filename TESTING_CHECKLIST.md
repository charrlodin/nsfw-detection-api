# 🧪 Testing Checklist - MUST DO Before Launch

## ⚠️ CRITICAL: This Must Be Done

You cannot launch without testing. The code is ready, but unvalidated.

---

## Step 1: Setup Local Environment (10 minutes)

```bash
cd /Users/arronchild/Projects/nsfw-detection-api

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Expected: All packages install successfully
```

**Checklist:**
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] No error messages

---

## Step 2: Start API Locally (15 minutes)

```bash
# Run API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**First run expectations:**
- Model will auto-download (~400MB)
- Takes 2-3 minutes
- Watch for "Application startup complete"

**Checklist:**
- [ ] Model downloads successfully
- [ ] Model loads without errors
- [ ] API starts on http://localhost:8000
- [ ] No error messages in logs

---

## Step 3: Test Health Endpoints (5 minutes)

```bash
# In another terminal

# Test root
curl http://localhost:8000/

# Test ping  
curl http://localhost:8000/ping

# Test status
curl http://localhost:8000/status

# Test metrics
curl http://localhost:8000/metrics
```

**Expected:**
- All return 200 OK
- JSON responses
- No errors

**Checklist:**
- [ ] `/` returns status ok
- [ ] `/ping` returns timestamp
- [ ] `/status` shows model info
- [ ] `/metrics` shows performance data

---

## Step 4: Test with Safe Images (30 minutes)

**Get test images:**
```bash
# Download safe test images from Unsplash
curl -o test_beach.jpg "https://source.unsplash.com/800x600/?beach"
curl -o test_landscape.jpg "https://source.unsplash.com/800x600/?landscape"
curl -o test_food.jpg "https://source.unsplash.com/800x600/?food"
curl -o test_nature.jpg "https://source.unsplash.com/800x600/?nature"
curl -o test_city.jpg "https://source.unsplash.com/800x600/?city"
```

**Test each image:**
```bash
# Test with balanced threshold
curl -X POST http://localhost:8000/moderate \
  -F "image=@test_beach.jpg" \
  -F "threshold=balanced"

# Expected: is_nsfw: false, confidence > 0.7
```

**Checklist for EACH image:**
- [ ] Response is JSON
- [ ] `is_nsfw` is false (for safe images)
- [ ] `confidence` is > 0.6
- [ ] `processing_time_ms` < 1000ms
- [ ] `request_id` is present

**Test ALL thresholds:**
- [ ] Strict (0.3) - should still be safe
- [ ] Balanced (0.5) - should be safe
- [ ] Permissive (0.7) - should be safe

**Record Results:**
```
Image: test_beach.jpg
Threshold: balanced
is_nsfw: false
confidence: 0.XX
time: XXXms
```

---

## Step 5: Test with NSFW Images (30 minutes)

**⚠️ You need NSFW test images for this**

**Option 1:** Use public academic datasets
**Option 2:** Use known NSFW sample images (be careful)

**Test each image:**
```bash
curl -X POST http://localhost:8000/moderate \
  -F "image=@nsfw_test.jpg" \
  -F "threshold=balanced"

# Expected: is_nsfw: true, confidence > 0.7
```

**Checklist:**
- [ ] `is_nsfw` is true (for NSFW images)
- [ ] `confidence` is > 0.6
- [ ] `processing_time_ms` < 1000ms
- [ ] Results consistent across thresholds

**Test threshold differences:**
- [ ] Strict (0.3) - should flag more
- [ ] Balanced (0.5) - should flag obvious ones
- [ ] Permissive (0.7) - should flag only very obvious

---

## Step 6: Test Edge Cases (20 minutes)

**Test these scenarios:**

**1. Medical images:**
- [ ] Medical imagery (anatomy, surgery)
- [ ] Expected: May flag as NSFW (document this)

**2. Art/paintings:**
- [ ] Classical art with nudity
- [ ] Expected: May flag depending on threshold

**3. Beach photos:**
- [ ] People in swimwear
- [ ] Expected: Permissive threshold should pass

**4. Large images:**
```bash
# Test with 4096x4096 image
curl -X POST http://localhost:8000/moderate \
  -F "image=@large_image.jpg"

# Expected: Works fine
```

**5. Oversized image:**
```bash
# Try >10MB image
# Expected: 413 error "File too large"
```

**6. Invalid image:**
```bash
# Try non-image file
curl -X POST http://localhost:8000/moderate \
  -F "image=@test.txt"

# Expected: 400 error "Invalid image file"
```

---

## Step 7: Test URL Endpoint (15 minutes)

**Test with safe URL:**
```bash
curl -X POST http://localhost:8000/moderate-url \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://source.unsplash.com/800x600/?nature",
    "threshold": "balanced"
  }'
```

**Checklist:**
- [ ] Works with HTTPS URLs
- [ ] Processes correctly
- [ ] Similar latency to file upload

**Test security:**
```bash
# Test localhost (should be blocked)
curl -X POST http://localhost:8000/moderate-url \
  -H "Content-Type: application/json" \
  -d '{"image_url": "http://localhost:8000/test.jpg"}'

# Expected: 422 error "Localhost URLs not allowed"

# Test private IP (should be blocked)
curl -X POST http://localhost:8000/moderate-url \
  -H "Content-Type: application/json" \
  -d '{"image_url": "http://192.168.1.1/test.jpg"}'

# Expected: 422 error "Private IP addresses not allowed"
```

**Security checklist:**
- [ ] Localhost blocked ✅
- [ ] 127.0.0.1 blocked ✅
- [ ] Private IPs blocked ✅
- [ ] Public URLs work ✅

---

## Step 8: Performance Testing (20 minutes)

**Test response times:**

```bash
# Run 10 tests and average
for i in {1..10}; do
  curl -X POST http://localhost:8000/moderate \
    -F "image=@test_beach.jpg" \
    -w "\nTime: %{time_total}s\n"
done
```

**Measure:**
- [ ] Average response time
- [ ] p50 latency
- [ ] p95 latency
- [ ] p99 latency

**Target: <800ms average on CPU**

**Record results:**
```
Test 1: XXXms
Test 2: XXXms
...
Average: XXXms
p95: XXXms
p99: XXXms

PASS/FAIL: <800ms target
```

---

## Step 9: Rate Limiting Test (10 minutes)

**Test rate limit:**
```bash
# Send 65 requests quickly
for i in {1..65}; do
  curl -X POST http://localhost:8000/moderate \
    -F "image=@test_beach.jpg" &
done
wait
```

**Expected:**
- First 60 succeed
- Next 5 get 429 error

**Checklist:**
- [ ] Rate limit triggers at 60 req/min
- [ ] Returns 429 status code
- [ ] Error message is clear

---

## Step 10: Document Results (30 minutes)

**Create MODEL_CARD.md with:**

1. **Model Information**
   - Name: Falconsai/nsfw_image_detection
   - Architecture: ViT
   - Parameters: 85.8M

2. **Test Results**
   - Safe images tested: XX
   - NSFW images tested: XX
   - Accuracy: XX%
   - False positive rate: XX%
   - False negative rate: XX%

3. **Performance**
   - Average latency: XXXms
   - p95 latency: XXXms
   - p99 latency: XXXms
   - Target: <800ms ✅/❌

4. **Threshold Recommendations**
   - Strict: Use for [scenarios]
   - Balanced: Use for [scenarios]
   - Permissive: Use for [scenarios]

5. **Known Limitations**
   - Medical images may be flagged
   - Art with nudity may be flagged
   - Context not understood (just visual)

6. **Edge Cases**
   - List examples with outcomes

---

## ✅ Final Checklist Before Deploy

- [ ] All health endpoints work
- [ ] Tested with 25+ safe images
- [ ] Tested with 25+ NSFW images (if available)
- [ ] Edge cases tested
- [ ] Security tests pass (SSRF protection)
- [ ] Performance meets target (<800ms)
- [ ] Rate limiting works
- [ ] MODEL_CARD.md created
- [ ] No critical bugs found
- [ ] All issues documented

---

## 🚀 If All Tests Pass

**You're ready to deploy!**

Next steps:
1. Push MODEL_CARD.md to GitHub
2. Deploy to Render
3. Test production endpoints
4. Create RapidAPI listing
5. Launch!

---

## 🚨 If Tests Fail

**Don't deploy yet!**

1. Document all failures
2. Fix issues one by one
3. Re-test
4. Only deploy when all tests pass

Common issues and fixes:
- Model download fails → Check internet, retry
- Inference errors → Check model compatibility
- Performance issues → Check CPU/RAM
- Security bypasses → Tighten validation

---

## 📊 Expected Time

- Setup: 10 min
- Start API: 15 min
- Health tests: 5 min
- Safe images: 30 min
- NSFW images: 30 min (if available)
- Edge cases: 20 min
- URL endpoint: 15 min
- Performance: 20 min
- Rate limiting: 10 min
- Documentation: 30 min

**Total: 3-4 hours**

---

**This testing is MANDATORY. Do not skip it.** ✋

**The code is good, but untested code is untrustworthy code.**

**TEST, TEST, TEST.** 🧪
