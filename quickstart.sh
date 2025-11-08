#!/bin/bash
# Quick Start Script for AI Agent

set -e

echo "===================================="
echo "AI Agent v2.0 - Quick Start"
echo "===================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env configuration..."
    cp .env.example .env
    echo "✓ .env created (edit this file to customize settings)"
fi

# Display menu
echo ""
echo "===================================="
echo "Choose an option:"
echo "===================================="
echo "1) Run CLI interface"
echo "2) Run Web API server"
echo "3) Run tests"
echo "4) Open static HTML version"
echo "5) Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "Starting CLI interface..."
        echo ""
        python main.py cli
        ;;
    2)
        echo ""
        echo "Starting Web API server..."
        echo "Server will be available at http://localhost:8080"
        echo "Press Ctrl+C to stop"
        echo ""
        python main.py web
        ;;
    3)
        echo ""
        echo "Running tests..."
        echo ""
        pytest -v
        ;;
    4)
        echo ""
        echo "Opening static HTML version..."
        if command -v python3 &> /dev/null; then
            echo "Starting local server at http://localhost:8000"
            echo "Press Ctrl+C to stop"
            python3 -m http.server 8000
        else
            echo "Opening index.html in browser..."
            if [[ "$OSTYPE" == "darwin"* ]]; then
                open index.html
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                xdg-open index.html
            else
                echo "Please open index.html in your browser"
            fi
        fi
        ;;
    5)
        echo ""
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac
