# Model Card: NSFW Detection API

**Model:** Falconsai/nsfw_image_detection  
**Version:** 1.0.0  
**Last Updated:** 2025-09-30  
**License:** Apache 2.0

---

## Model Overview

### Description

Binary image classification model for detecting NSFW (Not Safe For Work) content in images. The model classifies images into two categories: `normal` (safe) or `nsfw` (explicit content).

### Architecture

- **Base Model:** Vision Transformer (ViT)
- **Parameters:** 85.8M
- **Input Size:** 224x224 pixels
- **Framework:** PyTorch + Transformers
- **Source:** [Hugging Face - Falconsai/nsfw_image_detection](https://huggingface.co/Falconsai/nsfw_image_detection)

---

## Intended Use

### Primary Use Cases

1. **Content Moderation**
   - Automatically flag user-uploaded images
   - Pre-screen content before publication
   - Protect users from explicit content

2. **Social Media Platforms**
   - Profile picture validation
   - Post moderation
   - Comment image filtering

3. **Dating Applications**
   - Profile photo screening
   - Chat media moderation
   - Safety enforcement

4. **E-Commerce**
   - Product image validation
   - User review photo screening
   - Marketplace safety

5. **Community Platforms**
   - Forum post moderation
   - User-generated content filtering
   - Compliance with platform policies

### Out-of-Scope Use Cases

**NOT intended for:**
- ❌ Surveillance without consent
- ❌ Harassment or discrimination
- ❌ Illegal activities
- ❌ Medical diagnosis
- ❌ Legal evidence (requires human review)

---

## Performance

### Test Results (2025-09-30)

**Test Environment:** Local CPU (macOS, Python 3.13)  
**Test Images:** 5 safe images from various sources  
**Test Duration:** 10 inference requests

#### Accuracy

| Category | Images Tested | Correct | Accuracy |
|----------|---------------|---------|----------|
| **Safe Images** | 5 | 5 | **100%** |
| **NSFW Images** | 0 | - | *Not tested* |

**Confidence Scores (Safe Images):**
- Test 1: 99.95% confident (normal)
- Test 2: 99.96% confident (normal)
- Test 3: 99.94% confident (normal)
- Test 4: 99.99% confident (normal)
- Test 5: 99.98% confident (normal)

**Average Confidence:** 99.96%

#### Latency

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Average (after warmup)** | 584.6ms | <800ms | ✅ PASS |
| **First Request** | 2197.7ms | N/A | Expected (model loading) |
| **Minimum** | 304.8ms | N/A | Best case |
| **Maximum** | 905.5ms | N/A | Worst case (after warmup) |
| **p50 (Median)** | 602.2ms | N/A | Typical |

**Device:** CPU (M-series Apple Silicon)  
**GPU Performance:** Not yet tested (estimated <200ms)

---

## Threshold Configuration

### Available Presets

The API provides three configurable thresholds to balance false positives vs false negatives:

#### 1. Strict (0.3)
**Use when:** Maximum safety is required

- **Behavior:** Flags content more aggressively
- **False Positives:** Higher (may flag safe content)
- **False Negatives:** Lower (rarely misses NSFW)
- **Best For:** Children's platforms, highly moderated communities, zero-tolerance policies

**Example:** Medical images, art with partial nudity, beach photos with swimwear may be flagged.

---

#### 2. Balanced (0.5) ⭐ **Recommended**
**Use when:** Standard moderation is needed

- **Behavior:** Good balance between precision and recall
- **False Positives:** Moderate
- **False Negatives:** Moderate
- **Best For:** Most applications, dating apps, social media, forums

**Example:** Clear NSFW content flagged, edge cases require human review.

---

#### 3. Permissive (0.7)
**Use when:** Allowing more content is acceptable

- **Behavior:** Only flags very obvious NSFW content
- **False Positives:** Lower (less safe content flagged)
- **False Negatives:** Higher (may miss borderline NSFW)
- **Best For:** Art platforms, mature audiences, medical contexts

**Example:** Only explicit pornography flagged, suggestive content passes.

---

## Known Limitations

### 1. **Binary Classification Only**

The model provides only two categories: normal or NSFW.

- **No subcategories:** Cannot distinguish between nudity, violence, gore, etc.
- **No context awareness:** Doesn't understand artistic, medical, or educational context
- **Workaround:** Use separate specialized models for violence, gore, weapons if needed

---

### 2. **Context Limitations**

The model analyzes visual content only, without understanding context:

- **Medical images:** May be flagged as NSFW (showing anatomy)
- **Classical art:** Paintings/sculptures with nudity may be flagged
- **Educational content:** Anatomy textbooks, health education may be flagged
- **Breastfeeding:** May be incorrectly flagged
- **Cultural clothing:** Traditional attire showing skin may be flagged

**Mitigation:** Use threshold configuration and human review for edge cases.

---

### 3. **Cultural Bias**

The model was trained on Western-centric datasets:

- May not align with all cultural norms
- What's considered "NSFW" varies globally
- Some traditional clothing or cultural practices may be misclassified

**Recommendation:** Adjust thresholds based on your audience's cultural context.

---

### 4. **Image Quality Dependence**

Performance may vary with image quality:

- **Low resolution:** May reduce accuracy
- **Extreme lighting:** Very dark/bright images may confuse model
- **Obstructed views:** Partial images, cropped content may be harder to classify
- **Filters/effects:** Heavy editing may affect classification

**Best results:** Clear, well-lit, unobstructed images at reasonable resolution.

---

### 5. **Adversarial Attacks**

Like all ML models, vulnerable to adversarial examples:

- Intentionally crafted images designed to fool the model
- Subtle pixel changes imperceptible to humans but affect classification
- Not robust against determined attackers

**Mitigation:** Combine with other safety measures (user reports, pattern detection).

---

### 6. **Test Coverage Limitations**

**Current testing:**
- ✅ Tested with 5+ safe images (100% accuracy)
- ❌ Not tested with NSFW images (no test dataset available)
- ❌ Not tested with edge cases (medical, art, cultural)

**Confidence:** High for safe image detection, unknown for NSFW detection.

**Recommendation:** Gather real-world accuracy data post-launch.

---

## Training Data

### Source Model

This API uses the pre-trained `Falconsai/nsfw_image_detection` model from Hugging Face.

**Original Training:**
- **Dataset:** Not publicly disclosed by model author
- **Size:** Unknown
- **Composition:** Likely mix of safe and NSFW images
- **Bias:** Assumed Western-centric content

**We did NOT retrain this model.** This API provides inference only.

For detailed training information, see: [Falconsai/nsfw_image_detection on Hugging Face](https://huggingface.co/Falconsai/nsfw_image_detection)

---

## Ethical Considerations

### Privacy

**This API prioritizes privacy:**

- ✅ **Zero retention:** Images deleted immediately after processing
- ✅ **In-memory only:** Never written to disk
- ✅ **No logging:** Image content not logged
- ✅ **GDPR compliant:** By design
- ✅ **No tracking:** Request IDs for debugging only, not tied to users

**What we log:**
- Request metadata (timestamp, size, threshold)
- Performance metrics (latency, errors)
- Request IDs (debugging)

**What we DON'T log:**
- Image content
- Classification results
- URLs (only domain for abuse prevention)
- User information

---

### Fairness

**Potential biases:**

1. **Gender bias:** Model may disproportionately flag images of women
2. **Skin tone bias:** May perform differently across skin tones
3. **Cultural bias:** Western-centric training data
4. **Body type bias:** May have different thresholds for different body types

**We have NOT audited this model for bias.** Users should monitor for unfair outcomes.

**Recommendation:**
- Monitor classification decisions by demographic
- Provide appeals process for false positives
- Use human review for edge cases
- Be transparent with users about automated moderation

---

### Transparency

**This API is transparent:**

- ✅ Open source code on GitHub
- ✅ Public model (Hugging Face)
- ✅ Documented limitations
- ✅ Clear threshold configuration
- ✅ Confidence scores provided
- ✅ Honest about untested areas

**Users know:**
- What model is being used
- How decisions are made
- What limitations exist
- What data is collected (none)

---

## Updates and Versioning

### Current Version: 1.0.0

**Released:** 2025-09-30

**Features:**
- Binary NSFW classification
- Configurable thresholds
- SSRF protection
- Zero data retention
- Comprehensive API

### Future Updates

**v1.1 (Planned):**
- Violence detection (separate model)
- Gore detection (separate model)
- Weapons detection (separate model)
- Batch processing
- Python/JavaScript SDKs

**v1.2 (Future):**
- Multi-category classification
- Improved accuracy metrics
- Fine-tuning on custom datasets
- Dashboard with analytics

---

## Model Maintenance

### Monitoring

**In Production:**
- Track classification distribution (% NSFW vs safe)
- Monitor latency percentiles (p50, p95, p99)
- Detect anomalies (sudden changes in classification rate)
- User feedback (false positive reports)

**Alerts:**
- Latency > 1000ms
- Error rate > 5%
- Classification rate anomalies

---

### Updates

**When to update model:**
- Significant accuracy improvement available
- New vulnerabilities discovered
- Community feedback indicates bias
- New NSFW categories need coverage

**Update process:**
- Test new model thoroughly
- A/B test in production
- Monitor metrics closely
- Provide rollback capability

---

## References

### Model Source

- **Hugging Face:** [Falconsai/nsfw_image_detection](https://huggingface.co/Falconsai/nsfw_image_detection)
- **License:** Apache 2.0
- **Downloads:** 103M+ (as of 2025-09-30)
- **Community:** Active on Hugging Face

### Related Work

- Vision Transformers (ViT): [An Image is Worth 16x16 Words](https://arxiv.org/abs/2010.11929)
- Content Moderation: Industry best practices
- NSFW Detection: Comparative model studies

---

## Contact

**For model issues:**
- Original model: [Falconsai on Hugging Face](https://huggingface.co/Falconsai)
- API issues: [GitHub Issues](https://github.com/charrlodin/nsfw-detection-api/issues)

**For API support:**
- GitHub: https://github.com/charrlodin/nsfw-detection-api
- Email: [Via GitHub profile]

---

## Disclaimer

**This model is provided "as is" without warranties.**

- ✅ Use for content moderation
- ✅ Combine with human review
- ✅ Monitor for bias
- ❌ Don't rely solely on automation
- ❌ Don't use for surveillance without consent
- ❌ Don't use for illegal purposes

**Accuracy not guaranteed for all use cases.**

Users are responsible for:
- Testing model performance for their specific use case
- Monitoring for unfair outcomes
- Providing human review and appeals
- Complying with applicable laws

---

**Model Card Version:** 1.0  
**Last Updated:** 2025-09-30  
**Next Review:** After 1000+ production inferences
