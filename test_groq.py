"""
Groq API Connection Test
Tests the Groq API connection and basic functionality for the Mohan Voice Assistant.

Usage:
    export GROQ_API_KEY="your_groq_api_key_here"
    python test_groq.py
"""

import os
import sys
from groq import Groq


def test_groq_connection():
    """Test Groq API connection and basic functionality"""
    try:
        # Get API key from environment variable
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            print("❌ ERROR: GROQ_API_KEY environment variable not set")
            print("💡 Set it with: export GROQ_API_KEY='your_api_key_here'")
            sys.exit(1)
        
        if not api_key.startswith("gsk_"):
            print("❌ ERROR: Invalid Groq API key format")
            print("💡 Groq API keys should start with 'gsk_'")
            sys.exit(1)
        
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        print("🧪 Testing Groq connection...")
        print("🔗 Using model: llama-3.3-70b-versatile")
        
        # Test API call
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are Mohan Bhosale's AI assistant."},
                {"role": "user", "content": "Tell me about Mohan's Data Science background in 2 sentences."}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        # Display results
        print("✅ SUCCESS! Groq is working!")
        print("🤖 Response:", response.choices[0].message.content)
        print("⚡ Model: Ultra-fast inference with Groq!")
        print("💰 Cost-effective: Groq offers competitive pricing")
        
        # Test model info
        print("\n📊 API Response Details:")
        print(f"   - Model: {response.model}")
        print(f"   - Tokens used: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        
    except Exception as e:
        print("❌ ERROR:", str(e))
        print("💡 Check your API key and internet connection")
        print("🔗 Get your API key at: https://console.groq.com")
        sys.exit(1)


if __name__ == "__main__":
    test_groq_connection()
