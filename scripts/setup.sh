#!/bin/bash

# Setup script for local development
set -e

echo "🚀 Setting up AI-Enhanced Crypto Onboarding Chatbot..."

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if ! printf '%s\n' "$required_version" "$python_version" | sort -V -C; then
    echo "Error: Python $required_version or higher is required"
    exit 1
fi

echo "✓ Python $python_version detected"

# Create virtual environment
echo "Creating virtual environment..."
cd backend
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Backend dependencies installed"

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env and add your API keys"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p data/docs logs chroma_db

# Build knowledge base if docs exist
if [ -d "data/docs" ] && [ "$(ls -A data/docs)" ]; then
    echo "Building knowledge base..."
    python src/build_knowledge_base.py
else
    echo "⚠️  No documents found in data/docs. Sample documentation will be created on first run."
fi

# Return to root
cd ..

# Setup frontend
echo "Setting up frontend..."
if command -v npm &> /dev/null; then
    cd frontend
    echo "Installing frontend dependencies..."
    npm install
    echo "✓ Frontend dependencies installed"
    cd ..
else
    echo "⚠️  npm not found. Skipping frontend setup. Install Node.js to build the frontend."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Edit backend/.env and add your API keys"
echo "  2. Add your crypto documentation to backend/data/docs/"
echo "  3. Start the backend: cd backend && source venv/bin/activate && python app.py"
echo "  4. Start the frontend: cd frontend && npm start"
echo ""
echo "📚 For more information, see README.md"
