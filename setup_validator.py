#!/usr/bin/env python3
"""
Mohan Voice Assistant - Setup Validator
Comprehensive validation tool that tests all components of the AI voice assistant.

This script validates:
- Python dependencies
- Modal CLI setup and authentication  
- API key configuration (Groq, OpenAI)
- API connections and functionality
- Project file structure
- Configuration validation

Usage:
    python setup_validator.py

Author: Mohan Bhosale
"""

import sys
import os
import time
import subprocess
import json
from typing import Dict, List, Tuple, Optional

class SetupValidator:
    def __init__(self):
        self.results: Dict[str, bool] = {}
        self.errors: List[str] = []
        
    def print_header(self, text: str):
        print(f"\n{'='*60}")
        print(f"🔧 {text}")
        print('='*60)
        
    def print_test(self, test_name: str, success: bool, details: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.results[test_name] = success
        
    def run_command(self, command: str) -> Tuple[bool, str]:
        """Run a shell command and return success status and output"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def test_python_dependencies(self):
        """Test if required Python packages are installed"""
        self.print_header("TESTING PYTHON DEPENDENCIES")
        
        required_packages = [
            'modal', 'groq', 'openai', 'fastapi', 'websockets'
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.print_test(f"Import {package}", True)
            except ImportError:
                self.print_test(f"Import {package}", False, f"Run: pip install {package}")
                self.errors.append(f"Missing package: {package}")
    
    def test_modal_setup(self):
        """Test Modal CLI setup and authentication"""
        self.print_header("TESTING MODAL SETUP")
        
        # Test Modal CLI installation
        success, output = self.run_command("modal --version")
        self.print_test("Modal CLI installed", success, output.strip() if success else "Run: pip install modal")
        
        if not success:
            self.errors.append("Modal CLI not installed")
            return
        
        # Test Modal authentication
        success, output = self.run_command("modal secret list")
        self.print_test("Modal authentication", success, "Run: modal setup" if not success else "Authenticated")
        
        if not success:
            self.errors.append("Modal not authenticated")
    
    def test_modal_secrets(self):
        """Test Modal secrets configuration"""
        self.print_header("TESTING MODAL SECRETS")
        
        success, output = self.run_command("modal secret list")
        if success:
            secrets = output.lower()
            
            # Check for Groq API key
            groq_secret = "groq-api-key" in secrets or "groq_api_key" in secrets
            self.print_test("Groq API key secret", groq_secret, 
                          "Run: modal secret create groq-api-key GROQ_API_KEY=your_key" if not groq_secret else "Found")
            
            # Check for OpenAI API key (optional)
            openai_secret = "openai-api-key" in secrets or "openai_api_key" in secrets
            self.print_test("OpenAI API key secret", openai_secret, 
                          "Optional: modal secret create openai-api-key OPENAI_API_KEY=your_key" if not openai_secret else "Found")
            
            if not groq_secret:
                self.errors.append("Missing Groq API key secret")
        else:
            self.print_test("Access Modal secrets", False, "Check Modal authentication")
            self.errors.append("Cannot access Modal secrets")
    
    def test_groq_api_connection(self):
        """Test Groq API connection"""
        self.print_header("TESTING GROQ API CONNECTION")
        
        try:
            from groq import Groq
            
            # Try to get API key from environment or prompt
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                print("📝 Groq API key not found in environment variables")
                api_key = input("Enter your Groq API key (starts with gsk_): ").strip()
            
            if not api_key or not api_key.startswith("gsk_"):
                self.print_test("Groq API key format", False, "Key should start with 'gsk_'")
                self.errors.append("Invalid Groq API key format")
                return
            
            # Test API connection
            client = Groq(api_key=api_key)
            
            start_time = time.time()
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello from Groq!' in exactly those words."}
                ],
                max_tokens=50
            )
            response_time = time.time() - start_time
            
            response_text = response.choices[0].message.content.strip()
            
            self.print_test("Groq API connection", True, f"Response time: {response_time:.2f}s ⚡")
            self.print_test("Groq response quality", "Hello from Groq!" in response_text, 
                          f"Got: {response_text}")
            
            if response_time > 2.0:
                print("    ⚠️  Response time is slower than expected. Check your internet connection.")
                
        except Exception as e:
            self.print_test("Groq API connection", False, str(e))
            self.errors.append(f"Groq API error: {str(e)}")
    
    def test_openai_api_connection(self):
        """Test OpenAI API connection (optional)"""
        self.print_header("TESTING OPENAI API CONNECTION (Optional)")
        
        try:
            import openai
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("📝 OpenAI API key not found (optional for STT/TTS)")
                choice = input("Do you have an OpenAI API key to test? (y/n): ").strip().lower()
                if choice == 'y':
                    api_key = input("Enter your OpenAI API key (starts with sk-): ").strip()
                else:
                    self.print_test("OpenAI API (optional)", True, "Skipped - using alternatives")
                    return
            
            if api_key and api_key.startswith("sk-"):
                client = openai.OpenAI(api_key=api_key)
                
                # Test a simple API call
                response = client.models.list()
                self.print_test("OpenAI API connection", True, "Connected successfully")
            else:
                self.print_test("OpenAI API key format", False, "Key should start with 'sk-'")
                
        except Exception as e:
            self.print_test("OpenAI API connection", False, str(e))
            print("    💡 This is optional - you can use free alternatives")
    
    def test_project_files(self):
        """Test if required project files exist"""
        self.print_header("TESTING PROJECT FILES")
        
        required_files = ["main.py"]
        optional_files = ["requirements.txt", "README.md"]
        
        for file in required_files:
            exists = os.path.exists(file)
            self.print_test(f"File: {file}", exists, 
                          f"Create this file with your Modal app code" if not exists else "Found")
            if not exists:
                self.errors.append(f"Missing required file: {file}")
        
        for file in optional_files:
            exists = os.path.exists(file)
            self.print_test(f"File: {file} (optional)", exists, 
                          "Recommended to create" if not exists else "Found")
    
    def test_modal_app_syntax(self):
        """Test if main.py has valid Modal app syntax"""
        self.print_header("TESTING MODAL APP SYNTAX")
        
        if not os.path.exists("main.py"):
            self.print_test("main.py syntax", False, "File doesn't exist")
            return
        
        try:
            with open("main.py", "r") as f:
                content = f.read()
            
            # Check for essential Modal components
            checks = [
                ("modal import", "import modal" in content),
                ("Modal app", "modal.App(" in content or "app = modal.App" in content),
                ("Modal function", "@app.function" in content),
                ("ASGI app", "@modal.asgi_app" in content),
                ("WebSocket endpoint", "/ws" in content and "WebSocket" in content),
                ("Groq client", "groq" in content.lower()),
            ]
            
            for check_name, passed in checks:
                self.print_test(check_name, passed, 
                              "Check your main.py file" if not passed else "Found")
                
        except Exception as e:
            self.print_test("main.py syntax", False, str(e))
            self.errors.append("Cannot read main.py file")
    
    def generate_summary(self):
        """Generate a summary of all tests"""
        self.print_header("VALIDATION SUMMARY")
        
        total_tests = len(self.results)
        passed_tests = sum(self.results.values())
        
        print(f"📊 Tests passed: {passed_tests}/{total_tests}")
        print(f"📈 Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.errors:
            print(f"\n🚨 Issues found ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! Your Groq voice assistant is ready to deploy!")
            print("🚀 Next steps:")
            print("   1. Run: modal serve main.py")
            print("   2. Test in your browser")
            print("   3. Deploy: modal deploy main.py")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} issues need to be fixed before deployment.")
            print("💡 Fix the issues above and run this validator again.")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("🤖 Mohan's Voice Assistant - Setup Validator")
        print("⚡ Powered by Groq for ultra-fast responses")
        
        self.test_python_dependencies()
        self.test_modal_setup()
        self.test_modal_secrets()
        self.test_groq_api_connection()
        self.test_openai_api_connection()
        self.test_project_files()
        self.test_modal_app_syntax()
        
        return self.generate_summary()

if __name__ == "__main__":
    validator = SetupValidator()
    success = validator.run_all_tests()
    
    sys.exit(0 if success else 1)