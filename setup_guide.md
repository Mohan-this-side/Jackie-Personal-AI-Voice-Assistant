# 🚀 Mohan Voice Assistant - Complete Setup Guide

This guide will walk you through setting up Jackie, Mohan's AI Voice Assistant, from scratch to production deployment.

## 🎯 What We've Built

A **Speech-to-Speech Personal AI Assistant** using the **latest FREE AI technologies**:

- **🧠 LLM**: Groq Llama 3.3 (ultra-fast inference)
- **🎤 STT**: Distil-Whisper v3.5 + Local Whisper (completely free)
- **🔊 TTS**: Microsoft Edge TTS + Coqui TTS (free, high-quality)
- **🌐 Deployment**: Modal.com (serverless, auto-scaling)

## 🆕 Latest Technologies Used

### **Speech-to-Text (STT) - Multiple FREE Options:**
1. **Groq Distil-Whisper** (fastest, $0.02/hour)
2. **Local Whisper** (completely free, runs locally)
3. **OpenAI Whisper** (fallback if you have API key)

### **Text-to-Speech (TTS) - Latest FREE Options:**
1. **Microsoft Edge TTS** (free, excellent quality)
2. **Coqui TTS** (local, completely free)
3. **OpenAI TTS** (fallback if you have API key)

### **Why These Are Better:**
- **Edge TTS**: Beats many paid services in quality, completely free
- **Local Whisper**: No API costs, runs on your hardware
- **Groq**: 10-100x faster than traditional inference
- **Multiple Fallbacks**: Extremely reliable

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **Modal.com account** (free tier available)
- **Groq API key** (free tier available)
- **OpenAI API key** (optional, for enhanced features)

## 🛠️ Step-by-Step Setup

### Step 1: Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd mohan-groq-assistant

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Modal CLI
pip install modal
```

### Step 2: Get API Keys

#### 🔑 Groq API Key (Required)

1. **Visit Groq Console**: [console.groq.com](https://console.groq.com)
2. **Sign Up/Login**: Create an account or log in
3. **Create API Key**: 
   - Navigate to "API Keys" section
   - Click "Create API Key"
   - Copy the key (starts with `gsk_`)
   - Store it securely

**Why Groq?**
- ⚡ Ultra-fast inference (10-100x faster than traditional LLMs)
- 💰 Cost-effective pricing
- 🎯 High-quality responses
- 🔄 Multiple model options

#### 🔑 OpenAI API Key (Optional)

1. **Visit OpenAI Platform**: [platform.openai.com](https://platform.openai.com)
2. **Sign Up/Login**: Create an account or log in
3. **Create API Key**:
   - Navigate to "API Keys" section
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)
   - Store it securely

**OpenAI Usage:**
- 🎤 Fallback for speech-to-text
- 🔊 Fallback for text-to-speech
- ⚡ Only used when primary services fail

### Step 3: Configure Modal

#### Setup Modal Account

```bash
# Login to Modal (opens browser)
modal setup

# Verify setup
modal --version
```

#### Configure Secrets

```bash
# Required: Set Groq API key
modal secret create groq-api-key GROQ_API_KEY=your_groq_key_here

# Optional: Set OpenAI API key
modal secret create openai-api-key OPENAI_API_KEY=your_openai_key_here

# Verify secrets
modal secret list
```

### Step 4: Test Your Setup

#### Test Groq Connection

```bash
# Set environment variable for local testing
export GROQ_API_KEY="your_groq_key_here"

# Run Groq test
python test_groq.py
```

**Expected Output:**
```
🧪 Testing Groq connection...
🔗 Using model: llama-3.3-70b-versatile
✅ SUCCESS! Groq is working!
🤖 Response: [Mohan's background response]
⚡ Model: Ultra-fast inference with Groq!
💰 Cost-effective: Groq offers competitive pricing
```

#### Comprehensive Setup Validation

```bash
# Run full setup validation
python setup_validator.py
```

This will test:
- ✅ Python dependencies
- ✅ Modal authentication
- ✅ API key configuration
- ✅ Project file structure
- ✅ API connections

### Step 5: Development & Testing

#### Local Development

```bash
# Start development server
modal serve main.py

# Your app will be available at:
# https://your-username--mohan-voice-assistant-dev.modal.run
```

#### Test Features

1. **Open the provided URL** in your browser
2. **Allow microphone access** when prompted
3. **Test voice interaction**:
   - Click "🎤 Start Recording"
   - Ask: "Tell me about Mohan's experience"
   - Wait for response

4. **Test keyboard shortcuts**:
   - **Spacebar**: Start/stop recording
   - **Escape**: Stop audio playback

### Step 6: Production Deployment

```bash
# Deploy to production
modal deploy main.py

# Your production URL:
# https://your-username--mohan-voice-assistant.modal.run
```

## 🎯 Testing & Validation

### Basic Functionality Tests

#### Professional Questions
```
✅ "Tell me about Mohan's current role"
✅ "What are his technical skills?"
✅ "What achievements has he accomplished?"
✅ "How much data science experience does he have?"
```

#### Current Information Tests
```
✅ "What are the latest AI trends?"
✅ "Tell me about recent tech developments"
✅ "What's happening in machine learning today?"
```

#### Voice Interaction Tests
```
✅ Clear speech recognition
✅ Natural voice responses
✅ Proper error handling for unclear audio
✅ Keyboard shortcuts functionality
```

### Performance Validation

| Component | Expected Performance |
|-----------|---------------------|
| **STT Processing** | < 3 seconds |
| **LLM Response** | < 2 seconds |
| **TTS Generation** | < 2 seconds |
| **Total Response** | < 7 seconds |
| **Accuracy** | 95%+ speech recognition |

## 🔧 Configuration Options

### Environment Variables

```bash
# Required
export GROQ_API_KEY="gsk_your_key_here"

# Optional
export OPENAI_API_KEY="sk_your_key_here"
```

### Modal Configuration

Edit `main.py` for custom settings:

```python
@app.function(
    image=image,
    secrets=[...],
    keep_warm=2,     # Number of warm instances
    timeout=600,     # Timeout in seconds
    cpu=2,           # CPU cores
    memory=1024      # Memory in MB
)
```

### Voice Settings

Customize TTS voices in `main.py`:

```python
# Edge TTS voices
"en-US-AriaNeural"    # Default female voice
"en-US-GuyNeural"     # Male voice
"en-GB-SoniaNeural"   # British accent
"en-AU-NatashaNeural" # Australian accent
```

## 🐛 Troubleshooting

### Common Issues

#### 1. "Groq API Error"
```bash
# Check API key format
echo $GROQ_API_KEY  # Should start with gsk_

# Verify Modal secret
modal secret list | grep groq

# Re-create secret if needed
modal secret create groq-api-key GROQ_API_KEY=new_key
```

#### 2. "Microphone Access Denied"
- **Enable microphone** in browser settings
- **Use HTTPS** (Modal provides automatically)
- **Try different browser** (Chrome recommended)
- **Check firewall settings**

#### 3. "Model Loading Slow"
- **First run downloads models** (one-time, 2-5 minutes)
- **Subsequent runs are faster** (< 30 seconds)
- **Consider smaller models** for faster startup

#### 4. "Audio Not Playing"
- **Check browser audio settings**
- **Verify audio output device**
- **Try different browser**
- **Check internet connection** (Edge TTS requires internet)

### Debug Mode

Enable verbose logging:

```python
# In main.py, add debug prints
print(f"🔍 Debug: {variable_name}")

# Check Modal logs
modal logs mohan-voice-assistant
```

### Performance Issues

#### Optimize Response Time
```python
# Use smaller Whisper model
self.local_whisper = whisper.load_model("tiny")  # Faster

# Reduce max tokens
max_tokens=400  # Instead of 800

# Use faster Groq model
model="llama3-8b-8192"  # Instead of 70B
```

#### Reduce Costs
```python
# Disable OpenAI fallbacks
self.openai_client = None

# Use only free services
# - Local Whisper for STT
# - Edge TTS for speech
# - DuckDuckGo for search
```

## 📊 Monitoring & Analytics

### Modal Dashboard

Access at [modal.com/apps](https://modal.com/apps):

- **📈 Usage metrics**: Requests, response times
- **💰 Cost tracking**: API usage and billing
- **📝 Real-time logs**: Debug information
- **⚙️ Configuration**: Update secrets and settings

### Browser Analytics

Monitor in browser console (F12):

- **🎤 STT performance**: Processing times
- **🧠 LLM responses**: Response quality
- **🔊 TTS generation**: Audio quality
- **🌐 WebSocket status**: Connection health

### Custom Analytics

Add to `main.py`:

```python
# Track usage
usage_stats = {
    "requests": 0,
    "response_times": [],
    "error_count": 0
}

# Log performance
print(f"📊 Response time: {response_time:.2f}s")
```

## 🚀 Production Checklist

### Before Deployment

- [ ] **API keys configured** in Modal secrets
- [ ] **All tests passing** (setup_validator.py)
- [ ] **Performance validated** (< 7s total response time)
- [ ] **Error handling tested** (unclear audio, API failures)
- [ ] **Security reviewed** (no hardcoded keys)

### Production Settings

```python
# Recommended production config
keep_warm=2,      # For reliability
timeout=300,      # 5 minute timeout
cpu=2,            # Better performance
memory=1024       # Adequate memory
```

### Monitoring Setup

- [ ] **Modal alerts** configured for errors
- [ ] **Cost monitoring** enabled
- [ ] **Performance tracking** implemented
- [ ] **Backup systems** tested

## 🔄 Updates & Maintenance

### Regular Maintenance

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Update Modal
pip install --upgrade modal

# Redeploy with updates
modal deploy main.py
```

### Monitor Performance

- **Weekly**: Check response times and error rates
- **Monthly**: Review costs and usage patterns
- **Quarterly**: Update dependencies and test new features

### Version Control

```bash
# Tag releases
git tag -a v1.0.0 -m "Production release"
git push origin v1.0.0

# Track deployments
modal apps list --verbose
```

## 🤝 Support & Resources

### Documentation
- **Groq API**: [console.groq.com/docs](https://console.groq.com/docs)
- **Modal Docs**: [modal.com/docs](https://modal.com/docs)
- **FastAPI**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

### Community
- **Modal Discord**: [discord.gg/modal](https://discord.gg/modal)
- **Groq Community**: [community.groq.com](https://community.groq.com)

### Getting Help

1. **Check setup_validator.py** output
2. **Review Modal logs** for errors
3. **Test individual components** (test_groq.py)
4. **Check browser console** for client-side issues

---

## 🎉 Congratulations!

You now have a **production-ready AI voice assistant** using cutting-edge technologies! 

**Next Steps:**
1. **Share your assistant** with potential employers
2. **Customize responses** for your background
3. **Monitor usage** and optimize performance
4. **Add new features** as needed

**Your assistant is live at:**
`https://your-username--mohan-voice-assistant.modal.run` 