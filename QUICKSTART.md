# 🚀 Quick Start Guide - Enhanced Features

## One-Command Setup

```bash
# Run the enhanced setup script
./scripts/setup_enhanced.sh
```

This interactive script will:
1. ✅ Configure all API keys (OpenAI, Gemini, Perplexity)
2. ✅ Install dependencies
3. ✅ Build knowledge base
4. ✅ Run integration tests
5. ✅ Verify everything works

---

## Manual Setup (5 minutes)

### 1. Configure API Keys

```bash
cd backend
cp .env.example .env
nano .env  # or use your preferred editor
```

Add your keys:
```bash
# At minimum, add ONE of these:
OPENAI_API_KEY=sk-...           # OR
GOOGLE_API_KEY=AIza...          # OR (recommended for cost savings!)
PERPLEXITY_API_KEY=pplx-...     # OR
```

**💡 Recommendation**: Use Gemini (FREE) + OpenAI for best cost/quality balance

### 2. Install & Build

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build knowledge base (add your .md files to data/docs/ first)
python src/build_knowledge_base.py
```

### 3. Start Services

**Option A: Docker (Recommended)**
```bash
docker-compose up
```

**Option B: Manual**
```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend
cd frontend
npm install
npm start

# Terminal 3: Telegram (optional)
cd backend
python telegram_bot.py

# Terminal 4: Discord (optional)
cd backend
python discord_bot.py
```

---

## Testing Your Setup

### 1. Health Check
```bash
curl http://localhost:5000/api/health
```

### 2. Test Query
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Ethereum?",
    "language": "en"
  }'
```

### 3. Check Analytics
```bash
curl http://localhost:5000/api/stats
```

### 4. Run Integration Tests
```bash
python tests/test_integration.py
```

---

## Key Features & Endpoints

### 💬 Chat
```bash
POST /api/chat
Body: {"message": "How to stake ETH?", "language": "en", "user_id": "optional"}
```

### 📊 Analytics
```bash
GET /api/stats                    # System overview
GET /api/top-questions            # Most asked questions
GET /api/usage/<user_id>          # User usage stats
GET /api/billing/<user_id>        # Billing info
```

### 💰 Account Management
```bash
POST /api/upgrade                 # Upgrade tier
Body: {"user_id": "abc", "tier": "pro"}

GET /api/usage/<user_id>          # Check limits
```

### 🔐 Privacy (GDPR)
```bash
POST /api/consent                 # Grant consent
DELETE /api/data/<user_id>        # Delete all data
GET /api/data/<user_id>/export    # Export data
```

---

## Cost Optimization Tips

### Automatic Routing (Built-in!)
The system **automatically** routes queries to save money:

- **Simple query**: "What is Bitcoin?"
  - → Routed to Gemini (FREE)
  - Cost: $0.00

- **Complex query**: "Explain the technical architecture of Ethereum's proof-of-stake..."
  - → Routed to OpenAI (quality)
  - Cost: ~$0.0002

### Expected Savings

**Typical usage (100,000 queries/month):**

| Scenario | Cost Before | Cost After | Savings |
|----------|-------------|------------|---------|
| All OpenAI | $1,500/mo | - | - |
| With routing | - | $300-450/mo | **70-80%** |

**Why it works:**
- 80% of queries are simple → Gemini (free)
- 20% of queries are complex → OpenAI (quality)

---

## Pricing Tiers

### For Your Users

| Tier | Price | Queries/Month | Best For |
|------|-------|---------------|----------|
| FREE | $0 | 100 | Testing, personal use |
| PRO | $299 | 10,000 | Small teams, startups |
| ENTERPRISE | $1,999 | Unlimited | Large organizations |

Users automatically see limits when exceeded:
```json
{
  "error": "Query limit exceeded",
  "details": "You have reached your monthly limit. Please upgrade.",
  "usage": {
    "tier": "free",
    "queries_used": 100,
    "queries_remaining": 0
  }
}
```

---

## Monitoring & Debugging

### View Logs
```bash
# Backend logs
tail -f backend/app.log

# Docker logs
docker-compose logs -f backend
```

### Enable Debug Mode
```bash
# In .env
LOG_LEVEL=DEBUG
```

### Check Performance
```bash
# Get analytics summary
curl http://localhost:5000/api/stats | jq

# Response includes:
# - Total queries
# - Success rate
# - Average cost per query
# - Response times
# - Top categories
```

---

## Common Issues

### "No LLM API key configured"
**Solution**: Add at least one API key to `.env`:
```bash
GOOGLE_API_KEY=your_gemini_key  # Recommended (free!)
```

### "ChromaDB collection not found"
**Solution**: Build knowledge base first:
```bash
cd backend
python src/build_knowledge_base.py
```

### "Rate limit exceeded"
**Solution**: Either:
1. Upgrade user tier: `POST /api/upgrade`
2. Wait for monthly reset
3. Add more LLM providers for load distribution

---

## Production Deployment

### Environment Variables for Production

```bash
# Security
FLASK_ENV=production
SECRET_KEY=your_random_secret_key_here

# LLM Keys (add all for redundancy)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
PERPLEXITY_API_KEY=pplx-...

# Optional: Database for persistence
POSTGRES_URL=postgresql://user:pass@host/db
REDIS_URL=redis://host:6379

# Optional: Bot tokens
TELEGRAM_BOT_TOKEN=...
DISCORD_BOT_TOKEN=...
```

### Deploy with Docker

```bash
# Build
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### Deploy to Railway/Fly.io

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for platform-specific guides.

---

## Next Steps

1. **Add Documentation**: Place your project's .md files in `backend/data/docs/`
2. **Rebuild Knowledge Base**: `python backend/src/build_knowledge_base.py`
3. **Test Thoroughly**: `python tests/test_integration.py`
4. **Monitor Usage**: Check `/api/stats` regularly
5. **Optimize**: Review `/api/top-questions` to cache common queries
6. **Scale**: Add more LLM providers as traffic grows

---

## Getting Help

- **Documentation**: See `docs/` folder
- **Enhancements Guide**: Read `ENHANCEMENTS.md`
- **API Reference**: Check `docs/API.md`
- **Integration Tests**: Run `tests/test_integration.py`

---

## Key Benefits Summary

✅ **70-80% cost reduction** through intelligent LLM routing  
✅ **Multi-turn conversations** with automatic context management  
✅ **Safety validation** prevents dangerous financial advice  
✅ **Usage-based pricing** with automatic enforcement  
✅ **GDPR/CCPA compliant** for EU market access  
✅ **Comprehensive analytics** for data-driven decisions  
✅ **Multi-platform support** (Web, Telegram, Discord, API)  
✅ **Production-ready** with Docker & CI/CD  

---

**You're ready to go! 🚀**

Start with: `./scripts/setup_enhanced.sh`
