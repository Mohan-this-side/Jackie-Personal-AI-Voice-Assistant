# 🏗️ Jackie AI Assistant - Detailed Architecture

This document provides a comprehensive overview of Jackie's system architecture, technology stack, and data flow patterns.

## 🌐 High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        UI[React-like UI]
        WS_Client[WebSocket Client]
        Audio_API[Web Audio API]
    end

    subgraph "Network Layer"
        HTTPS[HTTPS/WSS]
        CDN[Modal CDN]
    end

    subgraph "Modal.com Infrastructure"
        subgraph "Application Layer"
            FastAPI[FastAPI Server]
            WebSocket[WebSocket Handler]
            ASGI[ASGI Application]
        end
        
        subgraph "Business Logic Layer"
            VoiceAssistant[Voice Assistant Core]
            WebSearcher[Web Search Engine]
            ContextManager[Context Manager]
        end
        
        subgraph "AI Processing Layer"
            STT_Pipeline[Speech-to-Text Pipeline]
            LLM_Engine[Language Model Engine]
            TTS_Pipeline[Text-to-Speech Pipeline]
        end
    end

    subgraph "External AI Services"
        Groq[Groq API<br/>LLM + STT]
        OpenAI[OpenAI API<br/>STT/TTS Fallback]
        EdgeTTS[Microsoft Edge TTS]
        LocalWhisper[Local Whisper Model]
    end

    subgraph "Data Services"
        DuckDuckGo[DuckDuckGo Search API]
        WebScraper[BeautifulSoup Scraper]
    end

    subgraph "Configuration"
        Secrets[Modal Secrets]
        Context[Personal Context]
        Config[Environment Config]
    end

    %% Client connections
    Browser --> UI
    UI --> Audio_API
    UI --> WS_Client
    
    %% Network flow
    WS_Client -.-> HTTPS
    HTTPS -.-> CDN
    CDN -.-> FastAPI
    
    %% Application flow
    FastAPI --> WebSocket
    WebSocket --> VoiceAssistant
    VoiceAssistant --> STT_Pipeline
    VoiceAssistant --> LLM_Engine
    VoiceAssistant --> TTS_Pipeline
    VoiceAssistant --> WebSearcher
    
    %% AI service connections
    STT_Pipeline --> Groq
    STT_Pipeline --> LocalWhisper
    STT_Pipeline --> OpenAI
    LLM_Engine --> Groq
    TTS_Pipeline --> EdgeTTS
    TTS_Pipeline --> OpenAI
    
    %% Data service connections
    WebSearcher --> DuckDuckGo
    WebSearcher --> WebScraper
    
    %% Configuration
    VoiceAssistant --> Secrets
    VoiceAssistant --> Context
    FastAPI --> Config

    %% Styling
    classDef client fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef network fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef modal fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef ai fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef data fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef config fill:#f1f8e9,stroke:#33691e,stroke-width:2px

    class Browser,UI,WS_Client,Audio_API client
    class HTTPS,CDN network
    class FastAPI,WebSocket,ASGI,VoiceAssistant,WebSearcher,ContextManager,STT_Pipeline,LLM_Engine,TTS_Pipeline modal
    class Groq,OpenAI,EdgeTTS,LocalWhisper ai
    class DuckDuckGo,WebScraper data
    class Secrets,Context,Config config
```

## 🔄 Data Flow Architecture

### **1. Voice Interaction Flow**

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant WebSocket
    participant VoiceAssistant
    participant STT as STT Pipeline
    participant LLM as LLM Engine
    participant TTS as TTS Pipeline
    participant Groq
    participant EdgeTTS

    User->>Browser: 🎤 Speaks into microphone
    Browser->>Browser: 📹 Records audio (Web Audio API)
    Browser->>WebSocket: 📤 Sends audio data (base64)
    
    WebSocket->>VoiceAssistant: 🔄 Process audio request
    VoiceAssistant->>STT: 🎤 Convert speech to text
    
    alt Primary STT (Groq)
        STT->>Groq: 📡 Send audio data
        Groq-->>STT: 📝 Return transcription
    else Fallback STT (Local Whisper)
        STT->>STT: 🏠 Process locally
    end
    
    STT-->>VoiceAssistant: ✅ Return transcribed text
    VoiceAssistant->>WebSocket: 📤 Send transcription
    WebSocket->>Browser: 📥 Display transcription
    
    VoiceAssistant->>LLM: 🧠 Generate response
    LLM->>Groq: 📡 Send query + context
    Groq-->>LLM: 💬 Return AI response
    
    VoiceAssistant->>TTS: 🔊 Convert text to speech
    TTS->>EdgeTTS: 📡 Generate audio
    EdgeTTS-->>TTS: 🎵 Return audio data
    
    TTS-->>VoiceAssistant: ✅ Return audio
    VoiceAssistant->>WebSocket: 📤 Send response + audio
    WebSocket->>Browser: 📥 Receive response
    Browser->>User: 🔊 Play audio response
```

### **2. Web Search Integration Flow**

```mermaid
sequenceDiagram
    participant User
    participant LLM as LLM Engine
    participant WebSearcher
    participant DuckDuckGo
    participant Scraper as Web Scraper
    participant Context as Context Manager

    User->>LLM: ❓ "What are the latest AI trends?"
    LLM->>LLM: 🔍 Detect current info needed
    LLM->>WebSearcher: 🌐 Request web search
    
    WebSearcher->>DuckDuckGo: 🔎 Search query
    DuckDuckGo-->>WebSearcher: 📋 Return search results
    
    loop For each result
        WebSearcher->>Scraper: 📄 Extract page content
        Scraper-->>WebSearcher: 📝 Return cleaned text
    end
    
    WebSearcher-->>LLM: 📊 Compiled search results
    LLM->>Context: 🔄 Combine with personal context
    Context-->>LLM: 📋 Enhanced context
    LLM-->>User: 💬 AI response with current info
```

## 🛠️ Technology Stack Breakdown

### **Frontend Technologies**
```mermaid
graph LR
    subgraph "Browser APIs"
        WebAudio[Web Audio API<br/>🎤 Audio Recording]
        WebSocket_API[WebSocket API<br/>📡 Real-time Communication]
        MediaRecorder[MediaRecorder API<br/>🎬 Audio Capture]
    end
    
    subgraph "UI Framework"
        HTML5[HTML5<br/>📄 Structure]
        CSS3[CSS3<br/>🎨 Styling & Animation]
        JavaScript[Vanilla JavaScript<br/>⚡ Interactivity]
    end
    
    subgraph "Audio Processing"
        Base64[Base64 Encoding<br/>🔐 Audio Transport]
        AudioContext[Audio Context<br/>🎵 Audio Management]
    end

    WebAudio --> MediaRecorder
    MediaRecorder --> Base64
    WebSocket_API --> JavaScript
    HTML5 --> CSS3
    CSS3 --> JavaScript
```

### **Backend Technologies**
```mermaid
graph TB
    subgraph "Web Framework"
        FastAPI[FastAPI 0.104.1<br/>🚀 High-performance API]
        Uvicorn[Uvicorn<br/>⚡ ASGI Server]
        WebSockets[WebSockets 12.0<br/>🔄 Real-time Communication]
    end
    
    subgraph "AI/ML Libraries"
        Groq_Client[Groq 0.4.1<br/>🧠 Ultra-fast LLM]
        OpenAI_Client[OpenAI 1.3.8<br/>🤖 Fallback AI Services]
        Whisper[Whisper 1.1.10<br/>🎤 Local Speech Recognition]
        Transformers[Transformers 4.35.2<br/>🔧 Model Loading]
    end
    
    subgraph "Audio Processing"
        LibROSA[LibROSA 0.10.1<br/>🎵 Audio Analysis]
        SoundFile[SoundFile 0.12.1<br/>📁 Audio I/O]
        TorchAudio[TorchAudio 2.1.0<br/>🔊 Audio Tensor Ops]
        EdgeTTS[Edge-TTS 6.1.9<br/>🗣️ Microsoft TTS]
    end
    
    subgraph "Data Processing"
        NumPy[NumPy 1.24.3<br/>🔢 Numerical Computing]
        SciPy[SciPy 1.11.4<br/>📊 Scientific Computing]
        PyTorch[PyTorch 2.1.0<br/>🧮 Deep Learning]
    end
    
    subgraph "Web & Search"
        HTTPX[HTTPX 0.24.1<br/>🌐 Async HTTP Client]
        BeautifulSoup[BeautifulSoup4<br/>🍲 HTML Parsing]
        DuckDuckGo_Search[DuckDuckGo-Search<br/>🔍 Privacy Search]
    end

    FastAPI --> WebSockets
    FastAPI --> Groq_Client
    Groq_Client --> OpenAI_Client
    Whisper --> LibROSA
    LibROSA --> SoundFile
    EdgeTTS --> TorchAudio
```

### **Infrastructure & Deployment**
```mermaid
graph TB
    subgraph "Modal.com Platform"
        Container[Debian Slim Container<br/>🐧 Lightweight Linux]
        AutoScale[Auto-scaling<br/>📈 Dynamic Resources]
        Secrets[Encrypted Secrets<br/>🔐 API Key Management]
        Monitoring[Built-in Monitoring<br/>📊 Performance Tracking]
    end
    
    subgraph "Network & Security"
        HTTPS_TLS[HTTPS/TLS 1.3<br/>🔒 Encrypted Communication]
        WSS[WebSocket Secure<br/>🛡️ Secure Real-time]
        CDN[Global CDN<br/>🌍 Fast Content Delivery]
    end
    
    subgraph "Development Tools"
        Python38[Python 3.8+<br/>🐍 Runtime Environment]
        PIP[Pip Package Manager<br/>📦 Dependency Management]
        Git[Git Version Control<br/>📝 Source Control]
    end

    Container --> AutoScale
    AutoScale --> Secrets
    Secrets --> Monitoring
    HTTPS_TLS --> WSS
    WSS --> CDN
```

## 🎯 Component Architecture

### **1. Voice Assistant Core**

```mermaid
classDiagram
    class VoiceAssistant {
        +groq_client: Groq
        +openai_client: OpenAI
        +local_whisper: WhisperModel
        +web_searcher: WebSearcher
        +speech_to_text(audio_data)
        +generate_response(user_message)
        +text_to_speech(text)
        -_groq_speech_to_text()
        -_local_speech_to_text()
        -_openai_speech_to_text()
        -_edge_text_to_speech()
        -_needs_web_search()
    }
    
    class WebSearcher {
        +search_web(query, max_results)
        +get_page_content(url, max_chars)
        +search_and_summarize(query)
    }
    
    class STTProcessor {
        +groq_whisper()
        +local_whisper()
        +openai_whisper()
        +fallback_chain()
    }
    
    class TTSProcessor {
        +edge_tts()
        +openai_tts()
        +simple_beep()
        +fallback_chain()
    }
    
    VoiceAssistant --> WebSearcher
    VoiceAssistant --> STTProcessor
    VoiceAssistant --> TTSProcessor
```

### **2. API Integration Architecture**

```mermaid
graph TB
    subgraph "API Priority Chain"
        direction TB
        Primary[Primary APIs<br/>⚡ Groq + Edge TTS]
        Secondary[Secondary APIs<br/>🔄 OpenAI Fallbacks]
        Local[Local Processing<br/>🏠 Whisper + Beep]
    end
    
    subgraph "Groq Integration"
        GroqLLM[Groq LLM<br/>llama-3.3-70b-versatile<br/>💰 ~$0.02/hour]
        GroqSTT[Groq Whisper<br/>whisper-large-v3<br/>🎤 Ultra-fast STT]
    end
    
    subgraph "Microsoft Integration"
        EdgeTTS_Service[Edge TTS<br/>en-US-AriaNeural<br/>🗣️ FREE High-quality]
    end
    
    subgraph "OpenAI Integration"
        OpenAI_LLM[OpenAI GPT<br/>Fallback Only<br/>💰 Pay-per-use]
        OpenAI_STT[OpenAI Whisper<br/>whisper-1<br/>🎤 Fallback STT]
        OpenAI_TTS[OpenAI TTS<br/>tts-1 alloy voice<br/>🔊 Fallback TTS]
    end
    
    Primary --> GroqLLM
    Primary --> GroqSTT
    Primary --> EdgeTTS_Service
    
    Secondary --> OpenAI_LLM
    Secondary --> OpenAI_STT
    Secondary --> OpenAI_TTS
    
    Local --> LocalWhisper[Local Whisper<br/>base model<br/>🏠 FREE Processing]
    Local --> BeepFallback[Simple Beep<br/>numpy generated<br/>🔊 Last resort]
```

## ⚡ Performance Architecture

### **Response Time Breakdown**

```mermaid
gantt
    title Jackie Response Timeline (Target: <7 seconds)
    dateFormat X
    axisFormat %s

    section Audio Processing
    Audio Capture (Browser)    :0, 1s
    STT Processing (Groq)      :1s, 2s
    
    section AI Processing  
    LLM Generation (Groq)      :2s, 4s
    Web Search (if needed)     :3s, 5s
    
    section Audio Generation
    TTS Processing (Edge)      :4s, 6s
    Audio Playback (Browser)   :6s, 7s
```

### **Scalability Architecture**

```mermaid
graph TB
    subgraph "Modal Auto-scaling"
        Cold[Cold Start<br/>~30s initial load]
        Warm[Warm Instances<br/>keep_warm=1]
        Scale[Auto Scale<br/>0 to ∞ instances]
    end
    
    subgraph "Performance Optimization"
        Cache[Model Caching<br/>Faster subsequent calls]
        Parallel[Parallel Processing<br/>STT + Web Search]
        Streaming[Streaming Responses<br/>Real-time feedback]
    end
    
    subgraph "Resource Management"
        CPU[CPU: 2 cores<br/>Sufficient for AI calls]
        Memory[Memory: 1GB<br/>Model loading + processing]
        Timeout[Timeout: 5 min<br/>Long enough for processing]
    end
    
    Cold --> Warm
    Warm --> Scale
    Scale --> Cache
    Cache --> Parallel
    Parallel --> Streaming
```

## 🔒 Security Architecture

### **Data Flow Security**

```mermaid
graph TB
    subgraph "Client Security"
        HTTPS_Client[HTTPS Only<br/>🔒 Encrypted transport]
        WSS_Client[WSS Protocol<br/>🛡️ Secure WebSocket]
        NoStorage[No Local Storage<br/>🚫 No data persistence]
    end
    
    subgraph "Application Security"
        EnvVars[Environment Variables<br/>🔐 No hardcoded secrets]
        Secrets_Modal[Modal Secrets<br/>🗝️ Encrypted key storage]
        Isolation[Container Isolation<br/>🏠 Separate instances]
    end
    
    subgraph "API Security"
        APIKey[API Key Rotation<br/>🔄 Regular key updates]
        RateLimit[Rate Limiting<br/>⏱️ Abuse prevention]
        Monitoring[Usage Monitoring<br/>📊 Anomaly detection]
    end
    
    subgraph "Privacy Protection"
        NoLogs[No Conversation Logs<br/>🚫 No data retention]
        Anonymous[Anonymous Usage<br/>👤 No user tracking]
        Personal[Private Context<br/>🔒 Gitignored personal data]
    end

    HTTPS_Client --> WSS_Client
    WSS_Client --> NoStorage
    EnvVars --> Secrets_Modal
    Secrets_Modal --> Isolation
    APIKey --> RateLimit
    RateLimit --> Monitoring
    NoLogs --> Anonymous
    Anonymous --> Personal
```

## 📊 Monitoring & Analytics Architecture

### **Performance Monitoring**

```mermaid
graph LR
    subgraph "Real-time Metrics"
        ResponseTime[Response Time<br/>📈 <7s target]
        ErrorRate[Error Rate<br/>📉 <1% target]
        Throughput[Throughput<br/>🔄 Requests/minute]
    end
    
    subgraph "Modal Dashboard"
        Logs[Application Logs<br/>📝 Debug information]
        Usage[Resource Usage<br/>💻 CPU/Memory/Network]
        Costs[Cost Tracking<br/>💰 API usage costs]
    end
    
    subgraph "Browser Analytics"
        ClientMetrics[Client Performance<br/>⚡ Browser timing]
        AudioQuality[Audio Quality<br/>🎵 STT/TTS success rate]
        UserExperience[User Experience<br/>👤 Interaction patterns]
    end

    ResponseTime --> Logs
    ErrorRate --> Usage
    Throughput --> Costs
    ClientMetrics --> AudioQuality
    AudioQuality --> UserExperience
```

---

## 🚀 Deployment Architecture

### **CI/CD Pipeline**

```mermaid
graph LR
    subgraph "Development"
        LocalDev[Local Development<br/>modal serve]
        Testing[Setup Validation<br/>setup_validator.py]
        Security[Security Check<br/>No secrets in code]
    end
    
    subgraph "Deployment"
        Deploy[Production Deploy<br/>modal deploy]
        Monitor[Health Check<br/>Endpoint monitoring]
        Scale[Auto-scaling<br/>Based on demand]
    end
    
    subgraph "Maintenance"
        Updates[Dependency Updates<br/>Regular security patches]
        Backup[Configuration Backup<br/>Modal secrets backup]
        Monitoring[Performance Monitoring<br/>Continuous optimization]
    end

    LocalDev --> Testing
    Testing --> Security
    Security --> Deploy
    Deploy --> Monitor
    Monitor --> Scale
    Scale --> Updates
    Updates --> Backup
    Backup --> Monitoring
```

This architecture demonstrates a **production-grade AI system** with:

- ⚡ **High Performance**: Sub-second AI inference with Groq
- 🔒 **Enterprise Security**: Encrypted secrets, private data handling
- 📈 **Scalable Infrastructure**: Serverless auto-scaling on Modal
- 🛡️ **Fault Tolerance**: Multiple fallback systems
- 🌐 **Modern Tech Stack**: Latest AI APIs and frameworks
- 📊 **Observability**: Comprehensive monitoring and analytics 