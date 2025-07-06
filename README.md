# 🤖 Jackie - AI Voice Assistant

> **Fast, intelligent voice conversations powered by Groq and Modal.com**

[![Powered by Groq](https://img.shields.io/badge/Powered%20by-Groq-orange)](https://groq.com/)
[![Built with Modal](https://img.shields.io/badge/Deployed%20on-Modal-blue)](https://modal.com/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-green)](https://fastapi.tiangolo.com/)
[![WebSocket](https://img.shields.io/badge/Real--time-WebSocket-red)](https://websockets.readthedocs.io/)

## 🎯 Who is Jackie?

Jackie is an AI voice assistant that can:
- 💬 **Answer questions** about professional experience and skills
- 🌐 **Search the web** for current information
- 🎤 **Voice conversations** with natural speech-to-speech interaction
- ⚡ **Ultra-fast responses** powered by Groq's optimized inference

## 🙋‍♀️ Talk with Jackie

The application is deployed using Modal's serverless platform. You can view the deployment status at:

**Jackie resides here:** https://mohan-this-side--mohan-voice-assistant-latest-fastapi-app.modal.run/


## 🏗️ System Architecture & Data Flow

```mermaid
%%{init: {
  'theme': 'forest',
  'themeVariables': {
    'primaryColor': '#e8f5e9',
    'primaryTextColor': '#1b5e20',
    'primaryBorderColor': '#2e7d32',
    'lineColor': '#388e3c',
    'secondaryColor': '#c8e6c9',
    'tertiaryColor': '#a5d6a7',
    'background': '#f1f8e9',
    'mainBkg': '#e8f5e9',
    'secondBkg': '#c8e6c9',
    'tertiaryBkg': '#a5d6a7'
  },
  'flowchart': {
    'nodeSpacing': 60,
    'rankSpacing': 80,
    'curve': 'basis'
  }
}}%%
flowchart TD
    %% User Input Layer
    A["🌐 USER<br/><b>Web Browser</b>"] --> B["🎤 VOICE INPUT<br/><b>Microphone Recording</b>"]
    
    %% Network & Infrastructure Layer  
    B --> C["📡 WEBSOCKET<br/><b>Real-time Connection</b>"]
    C --> D["☁️ MODAL.COM<br/><b>FastAPI Server</b>"]
    
    %% Core Engine Layer
    D --> E["🧠 JACKIE ENGINE<br/><b>Voice Assistant Core</b>"]
    
    %% Speech-to-Text Processing
    E --> F["🎤 SPEECH-TO-TEXT<br/><b>Audio → Text Conversion</b>"]
    F --> F1["⚡ GROQ WHISPER<br/><b>Primary STT (Fast)</b>"]
    F --> F2["🏠 LOCAL WHISPER<br/><b>Fallback STT</b>"]
    F --> F3["🔄 OPENAI WHISPER<br/><b>Backup STT</b>"]
    
    %% AI Processing & Decision
    F1 --> G["🤖 LLM PROCESSING<br/><b>Intelligence & Reasoning</b>"]
    F2 --> G
    F3 --> G
    
    G --> H["⚡ GROQ API<br/><b>Llama-3.3-70b-Versatile</b>"]
    G --> I["🌐 WEB SEARCH<br/><b>Current Information</b>"]
    
    %% Web Search Sub-flow
    I --> I1["🦆 DUCKDUCKGO<br/><b>Privacy Search</b>"]
    I1 --> I2["📄 WEB SCRAPER<br/><b>Content Extraction</b>"]
    I2 --> H
    
    %% Response Generation
    H --> J["🗣️ TEXT-TO-SPEECH<br/><b>Text → Audio Conversion</b>"]
    J --> J1["🎵 MICROSOFT EDGE TTS<br/><b>High Quality (FREE)</b>"]
    J --> J2["🔊 OPENAI TTS<br/><b>Premium Option</b>"]
    
    %% Response Delivery
    J1 --> K["📤 RESPONSE<br/><b>Text + Audio</b>"]
    J2 --> K
    K --> C
    C --> L["💬 USER INTERFACE<br/><b>Chat + Voice Output</b>"]
    
    %% Configuration (Side connections)
    M["🔐 API KEYS<br/><b>Modal Secrets</b>"] -.-> E
    N["👤 PERSONAL CONTEXT<br/><b>Professional Info</b>"] -.-> E
    
    %% Enhanced styling for visibility
    classDef userLayer fill:#e8f5e9,stroke:#2e7d32,stroke-width:4px,color:#1b5e20,font-size:14px,font-weight:bold
    classDef infraLayer fill:#c8e6c9,stroke:#388e3c,stroke-width:4px,color:#1b5e20,font-size:14px,font-weight:bold
    classDef coreLayer fill:#a5d6a7,stroke:#43a047,stroke-width:4px,color:#1b5e20,font-size:14px,font-weight:bold
    classDef aiLayer fill:#81c784,stroke:#2e7d32,stroke-width:4px,color:#1b5e20,font-size:14px,font-weight:bold
    classDef configLayer fill:#66bb6a,stroke:#1b5e20,stroke-width:3px,color:#1b5e20,font-size:12px,font-weight:bold
    
    class A,B,L userLayer
    class C,D infraLayer
    class E coreLayer
    class F,F1,F2,F3,G,H,I,I1,I2,J,J1,J2,K aiLayer
    class M,N configLayer
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Modal.com account
- Groq API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mohan-this-side/Jackie-Personal-AI-Voice-Assistant.git
   cd Jackie-Personal-AI-Voice-Assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**
   ```bash
   cp mohan_context_template.py mohan_context.py
   # Edit mohan_context.py with your information
   ```

4. **Configure Modal secrets**
   ```bash
   modal secret create groq-secret GROQ_API_KEY=your_groq_key
   modal secret create openai-secret OPENAI_API_KEY=your_openai_key
   ```

5. **Deploy to Modal**
   ```bash
   modal deploy main.py
   ```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI + WebSocket | Real-time communication |
| **AI/LLM** | Groq API (Llama 3.3 70B) | Ultra-fast language model |
| **Speech-to-Text** | Groq Whisper, Local Whisper | Voice recognition |
| **Text-to-Speech** | Microsoft Edge TTS, OpenAI | Voice synthesis |
| **Web Search** | DuckDuckGo API | Current information |
| **Infrastructure** | Modal.com | Serverless deployment |
| **Security** | Modal Secrets | Encrypted API keys |

## 📁 Project Structure

```
📦 Jackie-Personal-AI-Voice-Assistant/
├── 🐍 main.py                    # Main application
├── 📋 requirements.txt           # Dependencies
├── 🔧 setup_validator.py         # Environment validation
├── 🚀 deploy.sh                  # Deployment script
├── 📚 README.md                  # Documentation
├── 🏗️  ARCHITECTURE.md           # Detailed architecture
├── 🔒 SECURITY.md                # Security guidelines
├── 📖 setup_guide.md             # Setup instructions
├── 📄 LICENSE                    # MIT License
├── 🔐 mohan_context_template.py  # Context template
└── 🧪 test_groq.py               # API testing
```

## 🎮 Usage

### Web Interface
1. Open the Modal app URL in your browser
2. Click the microphone button to start voice conversation
3. Speak your question naturally
4. Jackie responds with both text and voice

### Example Conversations
- *"Tell me about your experience in data science"*
- *"What are the latest trends in AI?"*
- *"What technologies do you work with?"*
- *"Search for recent developments in machine learning"*

## ⚡ Performance

- **Response Time**: ~3-7 seconds end-to-end
- **STT Processing**: 1-2 seconds (Groq Whisper)
- **LLM Generation**: 2-3 seconds (Groq API)
- **TTS Synthesis**: 1-2 seconds (Edge TTS)
- **Concurrent Users**: Scales automatically on Modal

## 🔒 Security Features

- ✅ Encrypted API keys via Modal Secrets
- ✅ HTTPS/WSS secure communication
- ✅ No sensitive data in repository
- ✅ Privacy-focused web search (DuckDuckGo)
- ✅ Configurable personal context

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for lightning-fast LLM inference
- [Modal.com](https://modal.com/) for seamless serverless deployment
- [FastAPI](https://fastapi.tiangolo.com/) for the robust web framework
- [OpenAI](https://openai.com/) for Whisper and GPT models

---

<div align="center">
<strong>Built with ❤️ by Mohan Bhosale</strong><br/>
<em>Showcasing modern AI technologies in a production-ready voice assistant</em>
</div> 
