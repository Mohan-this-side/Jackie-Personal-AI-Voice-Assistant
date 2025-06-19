#!/bin/bash

# Mohan Voice Assistant - Deployment Script
# Automates the deployment process to Modal.com

set -e  # Exit on any error

echo "🚀 Mohan Voice Assistant - Deployment Script"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Modal CLI is installed
print_status "Checking Modal CLI installation..."
if ! command -v modal &> /dev/null; then
    print_error "Modal CLI not found. Installing..."
    pip install modal
else
    print_success "Modal CLI is installed"
fi

# Check if user is authenticated with Modal
print_status "Checking Modal authentication..."
if ! modal secret list &> /dev/null; then
    print_warning "Not authenticated with Modal. Please run:"
    echo "  modal setup"
    exit 1
else
    print_success "Modal authentication verified"
fi

# Check for required secrets
print_status "Checking required API keys..."
SECRET_COUNT=$(modal secret list | grep -E "(groq-api-key|openai-api-key)" | wc -l)

if [ "$SECRET_COUNT" -eq 0 ]; then
    print_error "No API keys found. You need at least Groq API key."
    echo ""
    echo "To add Groq API key:"
    echo "  modal secret create groq-api-key GROQ_API_KEY=your_key_here"
    echo ""
    echo "To add OpenAI API key (optional):"
    echo "  modal secret create openai-api-key OPENAI_API_KEY=your_key_here"
    exit 1
else
    print_success "API keys configured ($SECRET_COUNT found)"
fi

# Validate Python dependencies
print_status "Checking Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip check &> /dev/null || {
        print_warning "Some dependencies may be incompatible. Installing/updating..."
        pip install -r requirements.txt
    }
    print_success "Dependencies validated"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Run setup validator
print_status "Running setup validation..."
if [ -f "setup_validator.py" ]; then
    python setup_validator.py
    if [ $? -ne 0 ]; then
        print_error "Setup validation failed. Please fix issues before deploying."
        exit 1
    fi
    print_success "Setup validation passed"
else
    print_warning "setup_validator.py not found, skipping validation"
fi

# Ask for deployment type
echo ""
echo "Select deployment type:"
echo "1) Development (modal serve) - with hot reload"
echo "2) Production (modal deploy) - permanent deployment"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        print_status "Starting development server..."
        print_warning "This will run with hot reload. Press Ctrl+C to stop."
        modal serve main.py
        ;;
    2)
        print_status "Deploying to production..."
        modal deploy main.py
        
        if [ $? -eq 0 ]; then
            print_success "Production deployment successful!"
            echo ""
            echo "🎉 Your AI voice assistant is now live!"
            echo ""
            echo "Next steps:"
            echo "1. Test your deployment URL"
            echo "2. Share with potential employers"
            echo "3. Monitor usage in Modal dashboard"
            echo ""
            echo "Dashboard: https://modal.com/apps"
        else
            print_error "Deployment failed"
            exit 1
        fi
        ;;
    *)
        print_error "Invalid choice. Please run the script again."
        exit 1
        ;;
esac 