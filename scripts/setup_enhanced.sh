#!/bin/bash

# Setup script for AI-Enhanced Crypto Onboarding Chatbot
# This script helps configure API keys and test the enhanced features

set -e  # Exit on error

echo "========================================="
echo "🤖 AI Crypto Chatbot - Enhanced Setup"
echo "========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

cd backend

# Check if .env exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing .env file"
    else
        cp .env.example .env
        echo "✅ Created new .env file"
    fi
else
    cp .env.example .env
    echo "✅ Created .env file from template"
fi

echo ""
echo "========================================="
echo "📝 API Key Configuration"
echo "========================================="
echo ""
echo "You mentioned having Perplexity and Gemini API keys."
echo "Let's configure all three LLM providers for optimal cost savings!"
echo ""

# OpenAI API Key
echo "1️⃣  OpenAI API Key (GPT-4o-mini)"
echo "   - Cost: \$0.15 per 1M tokens"
echo "   - Best for: Complex queries requiring high accuracy"
echo "   - Get key: https://platform.openai.com/api-keys"
echo ""
read -p "Enter your OpenAI API key (or press Enter to skip): " OPENAI_KEY
if [ -n "$OPENAI_KEY" ]; then
    # Update .env file
    if grep -q "^OPENAI_API_KEY=" .env; then
        sed -i "s/^OPENAI_API_KEY=.*/OPENAI_API_KEY=$OPENAI_KEY/" .env
    else
        echo "OPENAI_API_KEY=$OPENAI_KEY" >> .env
    fi
    echo "✅ OpenAI key configured"
else
    echo "⏭️  Skipping OpenAI"
fi
echo ""

# Google Gemini API Key
echo "2️⃣  Google Gemini API Key (Gemini Pro)"
echo "   - Cost: FREE tier available! ⭐"
echo "   - Best for: Simple queries (80% of traffic)"
echo "   - Get key: https://makersuite.google.com/app/apikey"
echo ""
read -p "Enter your Gemini API key (or press Enter to skip): " GEMINI_KEY
if [ -n "$GEMINI_KEY" ]; then
    if grep -q "^GOOGLE_API_KEY=" .env; then
        sed -i "s/^GOOGLE_API_KEY=.*/GOOGLE_API_KEY=$GEMINI_KEY/" .env
    else
        echo "GOOGLE_API_KEY=$GEMINI_KEY" >> .env
    fi
    echo "✅ Gemini key configured"
else
    echo "⏭️  Skipping Gemini"
fi
echo ""

# Perplexity API Key
echo "3️⃣  Perplexity API Key"
echo "   - Cost: \$0.20 per 1M tokens"
echo "   - Best for: Real-time data queries"
echo "   - Get key: https://www.perplexity.ai/settings/api"
echo ""
read -p "Enter your Perplexity API key (or press Enter to skip): " PERPLEXITY_KEY
if [ -n "$PERPLEXITY_KEY" ]; then
    if grep -q "^PERPLEXITY_API_KEY=" .env; then
        sed -i "s/^PERPLEXITY_API_KEY=.*/PERPLEXITY_API_KEY=$PERPLEXITY_KEY/" .env
    else
        echo "PERPLEXITY_API_KEY=$PERPLEXITY_KEY" >> .env
    fi
    echo "✅ Perplexity key configured"
else
    echo "⏭️  Skipping Perplexity"
fi
echo ""

# Telegram Bot (optional)
echo "4️⃣  Telegram Bot Token (Optional)"
echo "   - Get token: https://t.me/BotFather"
echo ""
read -p "Enter your Telegram bot token (or press Enter to skip): " TELEGRAM_TOKEN
if [ -n "$TELEGRAM_TOKEN" ]; then
    if grep -q "^TELEGRAM_BOT_TOKEN=" .env; then
        sed -i "s/^TELEGRAM_BOT_TOKEN=.*/TELEGRAM_BOT_TOKEN=$TELEGRAM_TOKEN/" .env
    else
        echo "TELEGRAM_BOT_TOKEN=$TELEGRAM_TOKEN" >> .env
    fi
    echo "✅ Telegram token configured"
else
    echo "⏭️  Skipping Telegram"
fi
echo ""

# Discord Bot (optional)
echo "5️⃣  Discord Bot Token (Optional)"
echo "   - Get token: https://discord.com/developers/applications"
echo ""
read -p "Enter your Discord bot token (or press Enter to skip): " DISCORD_TOKEN
if [ -n "$DISCORD_TOKEN" ]; then
    if grep -q "^DISCORD_BOT_TOKEN=" .env; then
        sed -i "s/^DISCORD_BOT_TOKEN=.*/DISCORD_BOT_TOKEN=$DISCORD_TOKEN/" .env
    else
        echo "DISCORD_BOT_TOKEN=$DISCORD_TOKEN" >> .env
    fi
    echo "✅ Discord token configured"
else
    echo "⏭️  Skipping Discord"
fi
echo ""

echo "========================================="
echo "📦 Installing Dependencies"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python packages..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

echo "========================================="
echo "🗄️  Building Knowledge Base"
echo "========================================="
echo ""

# Check if docs directory has files
if [ -d "data/docs" ] && [ "$(ls -A data/docs/*.md 2>/dev/null)" ]; then
    echo "Found documentation files. Building knowledge base..."
    python src/build_knowledge_base.py
    echo "✅ Knowledge base built"
else
    echo "⚠️  No documentation files found in data/docs/"
    echo "Add your project's .md files to data/docs/ and run:"
    echo "  python backend/src/build_knowledge_base.py"
fi
echo ""

echo "========================================="
echo "🧪 Running Tests"
echo "========================================="
echo ""

read -p "Do you want to run integration tests? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    cd ..
    python tests/test_integration.py
    cd backend
fi
echo ""

echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "🎉 Your AI Crypto Chatbot is ready with enhanced features:"
echo ""
echo "  ✓ Multi-LLM routing (OpenAI/Gemini/Perplexity)"
echo "  ✓ 70-80% cost optimization"
echo "  ✓ Conversation memory"
echo "  ✓ Response validation"
echo "  ✓ Analytics tracking"
echo "  ✓ Usage-based pricing"
echo "  ✓ GDPR/CCPA compliance"
echo ""
echo "🚀 Start the backend server:"
echo "   cd backend && python app.py"
echo ""
echo "🌐 Start the frontend:"
echo "   cd frontend && npm install && npm start"
echo ""
echo "🐳 Or use Docker:"
echo "   docker-compose up"
echo ""
echo "📖 Documentation:"
echo "   - API Reference: docs/API.md"
echo "   - Deployment Guide: docs/DEPLOYMENT.md"
echo "   - Enhancements: ENHANCEMENTS.md"
echo ""
echo "💡 Pro Tip: With Gemini's free tier, you can handle 80% of queries"
echo "   at ZERO cost by routing simple questions automatically!"
echo ""
echo "Happy building! 🚀"
