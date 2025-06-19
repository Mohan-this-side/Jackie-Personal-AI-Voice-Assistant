"""
Mohan Groq Assistant - AI Voice Assistant
A production-ready voice assistant powered by Groq for fast inference,
featuring speech-to-text, text-to-speech, and web search capabilities.

Author: Mohan Bhosale
Technologies: Groq API, Modal, FastAPI, WebSocket, Whisper, Edge TTS
"""

import modal
import json
import asyncio
import base64
import os
from typing import Optional, Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from groq import Groq
import openai

# Modal image configuration with required dependencies
image = modal.Image.debian_slim().pip_install([
    "fastapi[all]==0.104.1",
    "websockets==12.0",
    "groq==0.4.1",
    "openai==1.3.8",
    "python-multipart==0.0.6",
    "aiofiles==23.2.1",
    "requests==2.31.0",
    "torch==2.1.0",
    "transformers==4.35.2",
    "datasets[audio]==2.14.6",
    "librosa==0.10.1",
    "soundfile==0.12.1",
    "edge-tts==6.1.9",
    "whisper==1.1.10",
    "torchaudio==2.1.0",
    "numpy==1.24.3",
    "scipy==1.11.4",
    "beautifulsoup4==4.12.2",
    "duckduckgo-search==3.9.6",
    "httpx==0.24.1",
])

# Create Modal app
app = modal.App("mohan-voice-assistant", image=image)

# Import context from external file (kept private)
try:
    from mohan_context import get_context
    MOHAN_CONTEXT = get_context()
except ImportError:
    # Fallback context if mohan_context.py is not available
    MOHAN_CONTEXT = """
    You are Jackie, an AI assistant representing a Data Science professional. 
    You should answer questions about data science, machine learning, and technology topics.
    Be professional, knowledgeable, and helpful in your responses.
    
    If asked about specific professional experience, politely explain that you need the 
    personal context file to provide detailed information about the professional's background.
    You can still help with general data science questions and current tech trends.
    """
    print("⚠️  Personal context file not found. Using fallback context.")

# Store active WebSocket connections
active_connections: Dict[int, WebSocket] = {}


class WebSearcher:
    """Handles web search functionality using DuckDuckGo API"""
    
    def __init__(self):
        """Initialize web search capabilities"""
        pass
    
    async def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search the web using DuckDuckGo
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, snippet, and source
        """
        try:
            from duckduckgo_search import DDGS
            
            print(f"🔍 Searching web for: '{query}'")
            
            with DDGS() as ddgs:
                results = []
                search_results = ddgs.text(query, max_results=max_results)
                
                for result in search_results:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', ''),
                        'source': result.get('href', '').split('/')[2] if result.get('href') else ''
                    })
                
                print(f"✅ Found {len(results)} search results")
                return results
                
        except Exception as e:
            print(f"❌ Web search failed: {e}")
            return []
    
    async def get_page_content(self, url: str, max_chars: int = 2000) -> str:
        """
        Fetch and extract text content from a webpage
        
        Args:
            url: URL to fetch content from
            max_chars: Maximum characters to return
            
        Returns:
            Extracted text content
        """
        try:
            import httpx
            from bs4 import BeautifulSoup
            
            print(f"📄 Fetching content from: {url}")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, follow_redirects=True)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in soup(["script", "style", "nav", "header", "footer"]):
                        element.decompose()
                    
                    # Extract and clean text
                    text = soup.get_text()
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    # Limit text length
                    if len(text) > max_chars:
                        text = text[:max_chars] + "..."
                    
                    print(f"✅ Extracted {len(text)} characters")
                    return text
                    
        except Exception as e:
            print(f"❌ Failed to fetch content from {url}: {e}")
            
        return ""
    
    async def search_and_summarize(self, query: str) -> str:
        """
        Search web and return formatted summary
        
        Args:
            query: Search query string
            
        Returns:
            Formatted search results summary
        """
        try:
            results = await self.search_web(query, max_results=3)
            
            if not results:
                return "I couldn't find current information on that topic. Could you try rephrasing your question?"
            
            # Format search results
            search_summary = f"Here's what I found about '{query}':\n\n"
            
            for i, result in enumerate(results, 1):
                search_summary += f"{i}. **{result['title']}** ({result['source']})\n"
                search_summary += f"   {result['snippet']}\n\n"
            
            # Get detailed content from first result
            if results[0]['url']:
                detailed_content = await self.get_page_content(results[0]['url'])
                if detailed_content:
                    search_summary += f"**Additional details from {results[0]['source']}:**\n"
                    search_summary += f"{detailed_content[:800]}...\n\n"
            
            search_summary += f"*Information retrieved from web search - {len(results)} sources*"
            return search_summary
            
        except Exception as e:
            print(f"❌ Search and summarize failed: {e}")
            return "I encountered an issue while searching for current information. Please try again."


class VoiceAssistant:
    """Main voice assistant class handling speech-to-text, LLM, and text-to-speech"""
    
    def __init__(self):
        """Initialize the voice assistant with API clients and models"""
        # Initialize Groq client for fast LLM inference
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Initialize OpenAI client for fallback STT/TTS (optional)
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
        
        # Initialize local models (loaded on first use)
        self.local_whisper = None
        
        # Initialize web search
        self.web_searcher = WebSearcher()
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """
        Convert speech to text using multiple STT options with fallbacks
        
        Args:
            audio_data: Raw audio data in bytes
            
        Returns:
            Transcribed text string
        """
        try:
            print(f"🎤 Processing audio data: {len(audio_data)} bytes")
            
            # Option 1: Groq Whisper (fastest and most cost-effective)
            if os.getenv("GROQ_API_KEY"):
                transcription = await self._groq_speech_to_text(audio_data)
                if transcription:
                    return transcription
            
            # Option 2: Local Whisper (completely free)
            transcription = await self._local_speech_to_text(audio_data)
            if transcription:
                return transcription
            
            # Option 3: OpenAI Whisper (fallback)
            if self.openai_client:
                transcription = await self._openai_speech_to_text(audio_data)
                if transcription:
                    return transcription
            
            print("⚠️ All STT options failed or returned poor results")
            return ""
            
        except Exception as e:
            print(f"❌ Speech-to-text processing failed: {e}")
            return ""
    
    async def _groq_speech_to_text(self, audio_data: bytes) -> str:
        """Process audio using Groq Whisper API"""
        try:
            import tempfile
            import wave
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file.flush()
                
                # Validate audio file
                try:
                    with wave.open(tmp_file.name, 'rb') as wav_file:
                        duration = wav_file.getnframes() / wav_file.getframerate()
                        if duration < 0.5:
                            print("⚠️ Audio too short, skipping...")
                            os.unlink(tmp_file.name)
                            return ""
                except Exception as e:
                    print(f"⚠️ Could not validate audio file: {e}")
                
                # Try Groq Whisper models
                models = ["whisper-large-v3", "distil-whisper-large-v3-en"]
                
                for model in models:
                    try:
                        with open(tmp_file.name, "rb") as audio_file:
                            response = self.groq_client.audio.transcriptions.create(
                                model=model,
                                file=audio_file,
                                response_format="text",
                                language="en",
                                temperature=0.0
                            )
                        
                        transcription = response.strip() if response else ""
                        print(f"✅ Groq {model}: '{transcription}'")
                        
                        # Filter out common misrecognitions
                        if transcription and len(transcription) > 2:
                            if transcription.lower() not in ["thank you", "thank you.", "thanks", "thanks."]:
                                os.unlink(tmp_file.name)
                                return transcription
                                
                    except Exception as e:
                        print(f"❌ Groq {model} failed: {e}")
                        continue
                
                os.unlink(tmp_file.name)
                
        except Exception as e:
            print(f"❌ Groq Whisper processing failed: {e}")
        
        return ""
    
    async def _local_speech_to_text(self, audio_data: bytes) -> str:
        """Process audio using local Whisper model"""
        try:
            import whisper
            import io
            import soundfile as sf
            import numpy as np
            from scipy import signal
            
            # Load Whisper model if not already loaded
            if self.local_whisper is None:
                print("🔄 Loading local Whisper model...")
                self.local_whisper = whisper.load_model("base")
            
            # Convert audio data to array
            audio_array, sample_rate = sf.read(io.BytesIO(audio_data))
            
            # Convert to mono if stereo
            if len(audio_array.shape) > 1:
                audio_array = np.mean(audio_array, axis=1)
            
            # Resample to 16kHz if needed
            if sample_rate != 16000:
                num_samples = int(len(audio_array) * 16000 / sample_rate)
                audio_array = signal.resample(audio_array, num_samples)
            
            # Normalize audio
            if np.max(np.abs(audio_array)) > 0:
                audio_array = audio_array / np.max(np.abs(audio_array))
            
            # Check duration
            duration = len(audio_array) / 16000
            if duration < 0.5:
                print("⚠️ Audio too short for transcription")
                return ""
            
            # Transcribe
            result = self.local_whisper.transcribe(
                audio_array, 
                fp16=False,
                language="en",
                temperature=0.0
            )
            
            transcription = result["text"].strip() if result.get("text") else ""
            print(f"✅ Local Whisper: '{transcription}'")
            
            if transcription and len(transcription) > 2:
                return transcription
            
        except Exception as e:
            print(f"❌ Local Whisper failed: {e}")
        
        return ""
    
    async def _openai_speech_to_text(self, audio_data: bytes) -> str:
        """Process audio using OpenAI Whisper API"""
        try:
            audio_file = ("audio.wav", audio_data, "audio/wav")
            response = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",
                temperature=0.0
            )
            
            transcription = response.text.strip() if response.text else ""
            print(f"✅ OpenAI Whisper: '{transcription}'")
            
            if transcription and len(transcription) > 2:
                return transcription
                
        except Exception as e:
            print(f"❌ OpenAI Whisper failed: {e}")
        
        return ""
    
    async def generate_response(self, user_message: str) -> str:
        """
        Generate response using Groq LLM with optional web search
        
        Args:
            user_message: User's input message
            
        Returns:
            Generated response text
        """
        try:
            print(f"🧠 Generating response for: '{user_message}'")
            
            # Check if we need current information
            if self._needs_web_search(user_message):
                print("🌐 Searching web for current information...")
                
                # Extract search query
                search_query = self._extract_search_query(user_message)
                web_info = await self.web_searcher.search_and_summarize(search_query)
                
                # Enhanced context with web information
                enhanced_context = MOHAN_CONTEXT + f"""

CURRENT INFORMATION FROM WEB SEARCH:
{web_info}

INSTRUCTIONS: You now have access to current information from the web search above.
Use this information to answer questions about current events, latest news, trends, etc.
Always mention that you searched the web for current information.
Combine Mohan's expertise with current information when relevant.
"""
                
                completion = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": enhanced_context},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=1000,
                    temperature=0.7,
                    stream=False
                )
            else:
                # Regular response for Mohan-specific questions
                completion = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": MOHAN_CONTEXT},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=800,
                    temperature=0.7,
                    stream=False
                )
            
            response = completion.choices[0].message.content
            print(f"✅ Generated response: {len(response)} characters")
            return response
            
        except Exception as e:
            print(f"❌ Groq LLM Error: {e}")
            return ("I apologize, but I'm having trouble processing that request right now. "
                   "However, I'd be happy to tell you about Mohan's experience in data science "
                   "and his current work at Cohere Health. Could you please try asking your question again?")
    
    def _needs_web_search(self, user_message: str) -> bool:
        """Determine if a question requires current information from the web"""
        current_info_keywords = [
            "latest", "recent", "current", "today", "this week", "this month", "2024", "2025",
            "news", "breaking", "update", "trending", "happening now", "what's new",
            "current events", "recent developments", "latest trends", "new releases",
            "market", "stock", "price", "crypto", "bitcoin", "ai news", "technology news"
        ]
        
        user_lower = user_message.lower()
        return any(keyword in user_lower for keyword in current_info_keywords)
    
    def _extract_search_query(self, user_message: str) -> str:
        """Extract search query from user message"""
        # Remove question words and clean up for better search
        query = user_message.replace("what's", "").replace("what is", "").replace("tell me about", "")
        query = query.replace("what are", "").replace("?", "").strip()
        return query
    
    async def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech using multiple TTS options with fallbacks
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio data in bytes
        """
        try:
            # Option 1: Edge TTS (Microsoft's free service)
            audio_data = await self._edge_text_to_speech(text)
            if audio_data:
                return audio_data
            
            # Option 2: OpenAI TTS (fallback if API key available)
            if self.openai_client:
                audio_data = await self._openai_text_to_speech(text)
                if audio_data:
                    return audio_data
            
            # Option 3: Simple beep as final fallback
            return self._generate_simple_beep()
            
        except Exception as e:
            print(f"❌ All TTS options failed: {e}")
            return self._generate_simple_beep()
    
    async def _edge_text_to_speech(self, text: str) -> bytes:
        """Generate speech using Microsoft Edge TTS"""
        try:
            import edge_tts
            
            communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
            audio_data = b""
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            if audio_data:
                print("✅ Edge TTS generation successful")
                return audio_data
                
        except Exception as e:
            print(f"❌ Edge TTS failed: {e}")
        
        return b""
    
    async def _openai_text_to_speech(self, text: str) -> bytes:
        """Generate speech using OpenAI TTS"""
        try:
            response = self.openai_client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            print("✅ OpenAI TTS generation successful")
            return response.content
            
        except Exception as e:
            print(f"❌ OpenAI TTS failed: {e}")
        
        return b""
    
    def _generate_simple_beep(self) -> bytes:
        """Generate a simple beep as absolute fallback"""
        try:
            import numpy as np
            import io
            import soundfile as sf
            
            # Generate simple beep
            sample_rate = 22050
            duration = 0.5
            frequency = 440
            
            t = np.linspace(0, duration, int(sample_rate * duration))
            beep = np.sin(2 * np.pi * frequency * t) * 0.3
            
            buffer = io.BytesIO()
            sf.write(buffer, beep, sample_rate, format='WAV')
            print("⚠️ Using simple beep fallback")
            return buffer.getvalue()
            
        except:
            print("❌ Even beep generation failed")
            return b""


@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("groq-api-key"),  # Required
        modal.Secret.from_name("openai-api-key"),  # Optional
    ],
    keep_warm=1,  # Keep one instance warm for faster response
    timeout=300,  # 5 minute timeout
)
@modal.asgi_app()
def fastapi_app():
    """Create and configure the FastAPI application"""
    
    # Initialize the voice assistant
    voice_assistant = VoiceAssistant()
    web_app = FastAPI(title="Mohan Groq Assistant", version="1.0.0")
    
    @web_app.get("/")
    async def get_homepage():
        """Serve the main chat interface"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Chat with Jackie - Mohan's AI Assistant</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }
                
                .container {
                    max-width: 800px;
                    width: 100%;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                    padding: 30px;
                    backdrop-filter: blur(10px);
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                
                h1 {
                    color: #2c3e50;
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                
                .subtitle {
                    color: #7f8c8d;
                    font-size: 1.1em;
                    margin-bottom: 20px;
                }
                
                .powered-by {
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    padding: 10px 20px;
                    border-radius: 25px;
                    font-weight: 600;
                    display: inline-block;
                }
                
                .chat-container {
                    height: 400px;
                    border: 2px solid #e9ecef;
                    border-radius: 15px;
                    padding: 20px;
                    overflow-y: auto;
                    margin-bottom: 20px;
                    background: #f8f9fa;
                }
                
                .message {
                    margin-bottom: 15px;
                    padding: 12px 16px;
                    border-radius: 18px;
                    max-width: 80%;
                    word-wrap: break-word;
                }
                
                .user-message {
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    margin-left: auto;
                    text-align: right;
                }
                
                .assistant-message {
                    background: #e9ecef;
                    color: #2c3e50;
                }
                
                .controls {
                    display: flex;
                    gap: 15px;
                    margin-bottom: 20px;
                }
                
                .btn {
                    flex: 1;
                    padding: 15px 20px;
                    border: none;
                    border-radius: 12px;
                    font-size: 1.1em;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                
                .btn-primary {
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                }
                
                .btn-primary:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
                }
                
                .btn-secondary {
                    background: #e74c3c;
                    color: white;
                }
                
                .btn-secondary:hover {
                    background: #c0392b;
                    transform: translateY(-2px);
                }
                
                .btn:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                    transform: none;
                }
                
                .status {
                    text-align: center;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 10px;
                    color: #495057;
                    font-weight: 500;
                    margin-bottom: 20px;
                }
                
                .features {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-top: 20px;
                }
                
                .feature {
                    text-align: center;
                    padding: 15px;
                    background: rgba(102, 126, 234, 0.1);
                    border-radius: 12px;
                    border: 1px solid rgba(102, 126, 234, 0.2);
                }
                
                .feature-icon {
                    font-size: 2em;
                    margin-bottom: 10px;
                }
                
                .recording {
                    animation: pulse 1.5s infinite;
                }
                
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
                
                @media (max-width: 600px) {
                    .container {
                        padding: 20px;
                        margin: 10px;
                    }
                    
                    h1 {
                        font-size: 2em;
                    }
                    
                    .controls {
                        flex-direction: column;
                    }
                    
                    .features {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 Jackie AI Assistant</h1>
                    <p class="subtitle">Ask me anything about Mohan Bhosale's professional experience!</p>
                    <div class="powered-by">⚡ Powered by Groq & Edge AI</div>
                </div>
                
                <div id="chatContainer" class="chat-container">
                    <div class="message assistant-message">
                        👋 Hi! I'm Jackie, Mohan's AI assistant. I can tell you about his experience as a Data Scientist, 
                        his current work at Cohere Health, technical skills, and achievements. You can also ask me about 
                        current AI/tech trends! Try asking: "Tell me about Mohan's current role" or "What are his key achievements?"
                    </div>
                </div>
                
                <div class="status" id="status">🎤 Ready to chat - Click the microphone to start</div>
                
                <div class="controls">
                    <button class="btn btn-primary" id="talkBtn">🎤 Start Recording</button>
                    <button class="btn btn-secondary" id="stopBtn" disabled>🛑 Stop Audio</button>
                </div>
                
                <div class="features">
                    <div class="feature">
                        <div class="feature-icon">🎤</div>
                        <div><strong>Voice Chat</strong><br>Natural speech interaction</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">⚡</div>
                        <div><strong>Ultra Fast</strong><br>Powered by Groq AI</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🌐</div>
                        <div><strong>Current Info</strong><br>Real-time web search</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🎯</div>
                        <div><strong>Expert Knowledge</strong><br>Mohan's professional background</div>
                    </div>
                </div>
            </div>

            <script>
                let ws = null;
                let mediaRecorder = null;
                let audioChunks = [];
                let isRecording = false;
                let isProcessing = false;
                let isSpeaking = false;
                let currentAudio = null;

                function connectWebSocket() {
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const wsUrl = `${protocol}//${window.location.host}/ws`;
                    
                    ws = new WebSocket(wsUrl);
                    
                    ws.onopen = function() {
                        console.log('🔗 WebSocket connected');
                        updateStatus('🎤 Connected - Ready to chat!');
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'transcription') {
                            addMessage('user', data.text);
                        } else if (data.type === 'response') {
                            addMessage('assistant', data.text);
                            if (data.audio) {
                                playAudio(data.audio);
                            }
                        }
                    };
                    
                    ws.onclose = function() {
                        console.log('❌ WebSocket disconnected');
                        updateStatus('❌ Disconnected - Reconnecting...');
                        setTimeout(connectWebSocket, 3000);
                    };
                    
                    ws.onerror = function(error) {
                        console.log('❌ WebSocket error:', error);
                        updateStatus('❌ Connection error - Please refresh');
                    };
                }

                async function toggleTalk() {
                    if (isRecording) {
                        stopRecording();
                    } else {
                        await startRecording();
                    }
                }

                async function startRecording() {
                    try {
                        stopCurrentAudio();
                        
                        const stream = await navigator.mediaDevices.getUserMedia({ 
                            audio: {
                                sampleRate: 16000,
                                channelCount: 1,
                                echoCancellation: true,
                                noiseSuppression: true
                            } 
                        });
                        
                        audioChunks = [];
                        mediaRecorder = new MediaRecorder(stream, {
                            mimeType: 'audio/webm;codecs=opus'
                        });
                        
                        mediaRecorder.ondataavailable = function(event) {
                            if (event.data.size > 0) {
                                audioChunks.push(event.data);
                            }
                        };
                        
                        mediaRecorder.onstop = function() {
                            stream.getTracks().forEach(track => track.stop());
                            if (audioChunks.length > 0) {
                                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                                sendAudio(audioBlob);
                            }
                        };
                        
                        mediaRecorder.start();
                        isRecording = true;
                        updateButtons();
                        updateStatus('🔴 Recording... Release button when done');
                        
                    } catch (error) {
                        console.error('❌ Error starting recording:', error);
                        updateStatus('❌ Microphone access denied - Please enable microphone');
                    }
                }

                function stopRecording() {
                    if (mediaRecorder && isRecording) {
                        mediaRecorder.stop();
                        isRecording = false;
                        isProcessing = true;
                        updateButtons();
                        updateStatus('⚡ Processing your question...');
                    }
                }

                function stopCurrentAudio() {
                    if (currentAudio) {
                        currentAudio.pause();
                        currentAudio.currentTime = 0;
                        currentAudio = null;
                        isSpeaking = false;
                        updateButtons();
                        updateStatus('🎤 Audio stopped - Ready for next question');
                    }
                }

                function sendAudio(audioBlob) {
                    const reader = new FileReader();
                    reader.onload = function() {
                        const base64Audio = reader.result.split(',')[1];
                        ws.send(JSON.stringify({
                            type: 'audio',
                            data: base64Audio,
                            mimeType: audioBlob.type,
                            size: audioBlob.size
                        }));
                    };
                    reader.readAsDataURL(audioBlob);
                }

                function playAudio(base64Audio) {
                    try {
                        stopCurrentAudio();
                        
                        currentAudio = new Audio(`data:audio/wav;base64,${base64Audio}`);
                        isSpeaking = true;
                        isProcessing = false;
                        updateButtons();
                        updateStatus('🔊 Jackie is speaking - Click Stop to interrupt');
                        
                        currentAudio.onended = function() {
                            currentAudio = null;
                            isSpeaking = false;
                            updateButtons();
                            updateStatus('✅ Ready for next question');
                        };
                        
                        currentAudio.onerror = function() {
                            currentAudio = null;
                            isSpeaking = false;
                            isProcessing = false;
                            updateButtons();
                            updateStatus('🎤 Ready to chat');
                        };
                        
                        currentAudio.play().catch(e => {
                            console.log('Audio play failed:', e);
                            currentAudio = null;
                            isSpeaking = false;
                            isProcessing = false;
                            updateButtons();
                            updateStatus('🎤 Ready to chat');
                        });
                        
                    } catch (e) {
                        console.log('Audio creation failed:', e);
                        isProcessing = false;
                        updateButtons();
                        updateStatus('🎤 Ready to chat');
                    }
                }

                function addMessage(sender, text) {
                    const chatContainer = document.getElementById('chatContainer');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${sender}-message`;
                    messageDiv.textContent = text;
                    chatContainer.appendChild(messageDiv);
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }

                function updateStatus(message) {
                    document.getElementById('status').textContent = message;
                }

                function updateButtons() {
                    const talkBtn = document.getElementById('talkBtn');
                    const stopBtn = document.getElementById('stopBtn');
                    
                    if (isRecording) {
                        talkBtn.textContent = '🔴 Recording...';
                        talkBtn.classList.add('recording');
                        talkBtn.disabled = false;
                        stopBtn.disabled = true;
                    } else if (isProcessing) {
                        talkBtn.textContent = '⚡ Processing...';
                        talkBtn.classList.remove('recording');
                        talkBtn.disabled = true;
                        stopBtn.disabled = true;
                    } else {
                        talkBtn.textContent = '🎤 Start Recording';
                        talkBtn.classList.remove('recording');
                        talkBtn.disabled = false;
                        stopBtn.disabled = !isSpeaking;
                    }
                }

                // Event listeners
                document.getElementById('talkBtn').addEventListener('click', toggleTalk);
                document.getElementById('stopBtn').addEventListener('click', stopCurrentAudio);

                // Keyboard shortcuts
                document.addEventListener('keydown', function(e) {
                    if (e.code === 'Space' && !isRecording && !isProcessing) {
                        e.preventDefault();
                        toggleTalk();
                    }
                    if (e.code === 'Escape' && (isSpeaking || isRecording)) {
                        e.preventDefault();
                        if (isSpeaking) stopCurrentAudio();
                        if (isRecording) stopRecording();
                    }
                });

                // Initialize
                connectWebSocket();
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    @web_app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """Handle WebSocket connections for real-time voice chat"""
        await websocket.accept()
        connection_id = id(websocket)
        active_connections[connection_id] = websocket
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message["type"] == "audio":
                    # Process voice message
                    audio_data = base64.b64decode(message["data"])
                    print(f"📨 Received audio: {len(audio_data)} bytes")
                    
                    # Step 1: Convert speech to text
                    user_text = await voice_assistant.speech_to_text(audio_data)
                    
                    if user_text and user_text.strip():
                        # Send transcription back to client
                        await websocket.send_text(json.dumps({
                            "type": "transcription",
                            "text": user_text.strip()
                        }))
                        
                        # Step 2: Generate response
                        response_text = await voice_assistant.generate_response(user_text.strip())
                        
                        # Step 3: Convert response to speech
                        response_audio = await voice_assistant.text_to_speech(response_text)
                        
                        # Send response back to client
                        await websocket.send_text(json.dumps({
                            "type": "response",
                            "text": response_text,
                            "audio": base64.b64encode(response_audio).decode() if response_audio else ""
                        }))
                    else:
                        # Handle unclear audio
                        await websocket.send_text(json.dumps({
                            "type": "transcription",
                            "text": "[Could not understand audio - please try speaking more clearly]"
                        }))
                        
                        error_response = ("I didn't catch that clearly. Could you please speak a bit louder and more clearly? "
                                        "I'm here to answer any questions about Mohan's experience in data science!")
                        response_audio = await voice_assistant.text_to_speech(error_response)
                        
                        await websocket.send_text(json.dumps({
                            "type": "response",
                            "text": error_response,
                            "audio": base64.b64encode(response_audio).decode() if response_audio else ""
                        }))
                        
        except WebSocketDisconnect:
            if connection_id in active_connections:
                del active_connections[connection_id]
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
            if connection_id in active_connections:
                del active_connections[connection_id]
    
    return web_app


# Local development entry point
if __name__ == "__main__":
    print("🚀 Use 'modal serve main.py' to run this application!")