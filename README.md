# 🤖 AI-Enhanced Crypto Onboarding Chatbot

An AI-powered onboarding chatbot for crypto projects that combines Retrieval-Augmented Generation (RAG) with Large Language Models to provide personalized, multilingual guidance for protocol navigation, staking, bridging, and wallet setup.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18.2+-blue.svg)

## 🌟 Features

- **🧠 RAG-Powered Responses**: Accurate answers based on your project's documentation
- **🌍 Multilingual Support**: 10+ languages including English, Spanish, Chinese, Hindi, French, German, Japanese, Korean, Portuguese, and Russian
- **💬 Multiple Platforms**: 
  - Web chat widget
  - Telegram bot
  - Discord bot
  - REST API
- **🔒 Secure & Scalable**: Rate limiting, CORS protection, and production-ready deployment
- **📚 Easy Documentation Integration**: Simply add markdown files to get started
- **🎨 Beautiful UI**: Modern, responsive chat interface with typing indicators and smooth animations

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Python 3.11+ with Flask/FastAPI
- LangChain for RAG orchestration
- ChromaDB for vector storage
- HuggingFace embeddings
- OpenAI GPT-4o-mini (or alternative LLMs)

**Frontend:**
- React 18+ with styled-components
- Axios for API communication
- Responsive design with mobile support

**Deployment:**
- Docker & Docker Compose
- Railway, Fly.io, or Render support
- GitHub Actions CI/CD

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ (for frontend)
- OpenAI API key (or alternative LLM API key)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/nvcs0101-hue/AI-Enhanced-Crypto-Onboarding-Chatbot.git
cd AI-Enhanced-Crypto-Onboarding-Chatbot
```

2. **Run the setup script**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

3. **Configure environment variables**
```bash
cd backend
cp .env.example .env
# Edit .env and add your API keys
```

4. **Add your documentation**
```bash
# Add markdown files to backend/data/docs/
# These will be used to build the knowledge base
```

5. **Build the knowledge base**
```bash
cd backend
source venv/bin/activate
python src/build_knowledge_base.py
```

6. **Start the backend**
```bash
python app.py
```

7. **Start the frontend** (in a new terminal)
```bash
cd frontend
npm start
```

Visit `http://localhost:3000` to see the chat widget!

## 📖 Usage

### REST API

**Chat Endpoint**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I stake Ethereum?",
    "language": "en"
  }'
```

**Response**
```json
{
  "response": "To stake Ethereum, follow these steps...",
  "status": "success",
  "language": "English",
  "timestamp": "2025-12-15T10:30:00Z"
}
```

### Telegram Bot

1. Set `TELEGRAM_BOT_TOKEN` in `.env`
2. Run the bot:
```bash
cd backend
source venv/bin/activate
python telegram_bot.py
```

3. Find your bot on Telegram and start chatting!

**Available Commands:**
- `/start` - Welcome message
- `/help` - Show help
- `/language` - Change language
- `/examples` - See example questions

### Discord Bot

1. Set `DISCORD_BOT_TOKEN` in `.env`
2. Run the bot:
```bash
cd backend
source venv/bin/activate
python discord_bot.py
```

3. Invite the bot to your server and use slash commands!

**Available Commands:**
- `/ask <question>` - Ask the assistant
- `/help` - Show help
- `/examples` - See examples
- `/about` - About the bot

## 🐳 Docker Deployment

### Development
```bash
docker-compose -f docker-compose.dev.yml up
```

### Production
```bash
docker-compose up -d
```

This starts:
- Flask API backend
- Telegram bot
- Discord bot
- Redis cache
- PostgreSQL database (optional)

## 🌐 Deployment Options

### Railway (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

1. Click the button above or use the CLI:
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

2. Set environment variables in Railway dashboard:
   - `OPENAI_API_KEY`
   - `TELEGRAM_BOT_TOKEN` (optional)
   - `DISCORD_BOT_TOKEN` (optional)

### Fly.io

```bash
flyctl launch
flyctl secrets set OPENAI_API_KEY=your_key
flyctl deploy
```

### Render

1. Connect your GitHub repository
2. Set build command: `cd backend && pip install -r requirements.txt`
3. Set start command: `cd backend && gunicorn app:app`
4. Add environment variables

## 📁 Project Structure

```
AI-Enhanced-Crypto-Onboarding-Chatbot/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── build_knowledge_base.py  # Vector DB builder
│   │   └── rag_pipeline.py          # RAG query engine
│   ├── tests/
│   │   ├── test_api.py
│   │   └── test_rag_pipeline.py
│   ├── data/
│   │   └── docs/                     # Your documentation here
│   ├── app.py                        # Flask API
│   ├── telegram_bot.py               # Telegram integration
│   ├── discord_bot.py                # Discord integration
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── ChatWidget.jsx            # Main chat component
│   │   └── index.js
│   ├── public/
│   │   ├── index.html
│   │   └── embed.js                  # Embeddable widget script
│   └── package.json
├── scripts/
│   ├── setup.sh                      # Setup script
│   └── deploy-railway.sh             # Railway deployment
├── docker-compose.yml
├── docker-compose.dev.yml
└── README.md
```

## 🧪 Testing

Run the test suite:
```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov=src
```

Run linting:
```bash
flake8 .
black --check .
```

## 🔧 Configuration

### Environment Variables

See [backend/.env.example](backend/.env.example) for all available configuration options.

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key

**Optional:**
- `TELEGRAM_BOT_TOKEN` - For Telegram integration
- `DISCORD_BOT_TOKEN` - For Discord integration
- `LLM_MODEL` - LLM model to use (default: gpt-4o-mini)
- `EMBEDDING_MODEL` - Embedding model (default: all-MiniLM-L6-v2)

### Customization

**Change LLM Provider:**
Edit `backend/src/rag_pipeline.py` and replace `ChatOpenAI` with your preferred provider (e.g., Google Gemini, Anthropic Claude).

**Adjust RAG Settings:**
Modify parameters in `backend/src/rag_pipeline.py`:
- `chunk_size` - Size of document chunks (default: 1000)
- `chunk_overlap` - Overlap between chunks (default: 200)
- `retrieval_k` - Number of documents to retrieve (default: 4)

## 💰 Monetization

### Pricing Tiers

**Free Tier:**
- 5 questions/day
- Single language
- Community support

**Premium ($99-$499/month):**
- Unlimited queries
- All languages
- Custom branding
- Priority support
- Analytics dashboard

**Enterprise ($999+/month):**
- Multi-protocol support
- Custom model fine-tuning
- On-premise deployment
- SLA guarantees
- Dedicated support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for RAG orchestration
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [OpenAI](https://openai.com/) for LLM capabilities
- [HuggingFace](https://huggingface.co/) for embeddings

## 📞 Support

- 📧 Email: support@example.com
- 💬 Discord: [Join our server](#)
- 🐛 Issues: [GitHub Issues](https://github.com/nvcs0101-hue/AI-Enhanced-Crypto-Onboarding-Chatbot/issues)

## 🗺️ Roadmap

- [ ] Add support for more LLM providers (Anthropic, Cohere)
- [ ] Implement conversation memory
- [ ] Add voice input/output
- [ ] Create admin dashboard
- [ ] Multi-tenancy support
- [ ] Advanced analytics
- [ ] Plugin system for custom integrations

---

**Built with ❤️ for the crypto community**