# 📋 Deployment Requirements Checklist

## Complete Requirements for Production Deployment

---

## 🔑 1. API Keys & Credentials (Required)

### LLM Providers (At least one required)
- [ ] **OpenAI API Key** 
  - Get from: https://platform.openai.com/api-keys
  - Cost: $0.15 per 1M tokens (GPT-4o-mini)
  - Tier: At least Tier 1 ($5 credit added)
  
- [ ] **Google Gemini API Key** (Recommended - FREE tier)
  - Get from: https://makersuite.google.com/app/apikey
  - Cost: FREE up to 60 requests/minute
  - Best for: 80% of simple queries
  
- [ ] **Perplexity API Key** (Optional)
  - Get from: https://www.perplexity.ai/settings/api
  - Cost: $0.20 per 1M tokens
  - Best for: Real-time data queries

### Bot Tokens (If deploying bots)
- [ ] **Telegram Bot Token**
  - Get from: @BotFather on Telegram
  - Command: `/newbot`
  - Free, unlimited messages
  
- [ ] **Discord Bot Token**
  - Get from: https://discord.com/developers/applications
  - Create New Application → Bot → Copy Token
  - Free, unlimited messages

### Database Credentials
- [ ] **PostgreSQL Password** (Auto-generated in `.env.secrets.example`)
- [ ] **Flask Secret Key** (Auto-generated in `.env.secrets.example`)

### Monitoring (Highly Recommended)
- [ ] **Sentry DSN**
  - Sign up: https://sentry.io (FREE tier: 5K events/month)
  - Create Project → Get DSN
  - Required for: Error tracking

### Backup Storage (Highly Recommended)
- [ ] **AWS S3 Bucket**
  - Sign up: https://aws.amazon.com
  - Cost: ~$0.023/GB/month
  - Required for: Off-site backups
  
- [ ] **AWS Access Keys**
  - IAM → Users → Security Credentials
  - Create Access Key
  - Needed for: S3 uploads

---

## 💻 2. Infrastructure Requirements

### Option A: Railway (Recommended)
- [ ] **Railway Account**
  - Sign up: https://railway.app
  - Free tier: $5/month credit
  - Paid: $20/month for production
  
- [ ] **Railway CLI Installed**
  ```bash
  npm install -g @railway/cli
  ```

### Option B: Fly.io
- [ ] **Fly.io Account**
  - Sign up: https://fly.io
  - Free tier: 3 shared VMs
  
- [ ] **Fly CLI Installed**
  ```bash
  curl -L https://fly.io/install.sh | sh
  ```

### Option C: Self-Hosted (VPS)
- [ ] **Server with minimum specs:**
  - 2 vCPU
  - 4GB RAM
  - 50GB SSD
  - Ubuntu 22.04 LTS
  
- [ ] **Domain name** (optional but recommended)
  - From: Namecheap, Google Domains, etc.
  - Cost: ~$10-15/year

---

## 🛠️ 3. Software Dependencies

### Local Development Tools
- [ ] **Git** - `git --version`
- [ ] **Python 3.11+** - `python3 --version`
- [ ] **Node.js 18+** - `node --version` (for Railway CLI)
- [ ] **Docker** - `docker --version`
- [ ] **Docker Compose** - `docker-compose --version`

### Optional Testing Tools
- [ ] **Bats** (Script testing) - `brew install bats-core`
- [ ] **k6** (Load testing) - `brew install k6`
- [ ] **Bandit** (Security) - `pip install bandit`
- [ ] **Safety** (Dependency check) - `pip install safety`

---

## 📁 4. Required Files & Configuration

### Environment Files (MUST CREATE)
- [ ] **`backend/.env.secrets`**
  ```bash
  cp backend/.env.secrets.example backend/.env.secrets
  # Then edit with your actual keys
  ```

### Documentation Files (MUST HAVE)
- [ ] **Knowledge base documents** in `backend/data/docs/`
  - Minimum 5-10 markdown files
  - Topics: Bitcoin, Ethereum, Wallets, DeFi, etc.
  - See `backend/data/docs/sample.md` for format

### Configuration Files (Already Created)
- [x] `docker-compose.yml` - Production config
- [x] `docker-compose.staging.yml` - Staging config
- [x] `railway.toml` - Railway configuration
- [x] `fly.toml` - Fly.io configuration
- [x] `Dockerfile` - Container image

---

## 🔐 5. Security Requirements

### Before Production Deployment
- [ ] **Strong passwords set**
  - PostgreSQL: 32+ characters
  - Flask SECRET_KEY: 64+ hex characters
  - All auto-generated in `.env.secrets.example`

- [ ] **Separate staging/production keys**
  - Different OpenAI keys for staging vs production
  - Different bot tokens for staging vs production
  - Prevents staging bugs affecting production

- [ ] **Secrets not in git**
  - `.env.secrets` in `.gitignore` ✓
  - No API keys in code
  - Use environment variables only

- [ ] **Security scan passed**
  ```bash
  ./scripts/security-scan.sh
  # Should show 0 critical vulnerabilities
  ```

---

## 📊 6. GitHub Requirements (For CI/CD)

### Repository Setup
- [ ] **GitHub repository created**
  - Public or private
  - Code pushed to `main` branch

### GitHub Secrets (For Staging/Production)
Go to: Settings → Secrets and Variables → Actions

**Required Secrets:**
- [ ] `RAILWAY_STAGING_TOKEN` - From Railway dashboard
- [ ] `RAILWAY_STAGING_PROJECT_ID` - From Railway project
- [ ] `RAILWAY_PROD_TOKEN` - Separate for production
- [ ] `RAILWAY_PROD_PROJECT_ID` - Separate project
- [ ] `STAGING_URL` - Your staging URL
- [ ] `PRODUCTION_URL` - Your production URL
- [ ] `OPENAI_API_KEY` - Production key
- [ ] `GOOGLE_API_KEY` - Production key
- [ ] `PERPLEXITY_API_KEY` - Production key
- [ ] `SECRET_KEY` - Flask secret
- [ ] `POSTGRES_PASSWORD` - Database password
- [ ] `SENTRY_DSN` - Error tracking
- [ ] `TELEGRAM_BOT_TOKEN` (if using Telegram)
- [ ] `DISCORD_BOT_TOKEN` (if using Discord)

### Staging Secrets (Separate!)
- [ ] `OPENAI_API_KEY_STAGING` - Different from production!
- [ ] `GOOGLE_API_KEY_STAGING` - Different from production!
- [ ] `TELEGRAM_BOT_TOKEN_STAGING` - Separate bot!
- [ ] `DISCORD_BOT_TOKEN_STAGING` - Separate bot!

---

## 🧪 7. Pre-Deployment Testing

### Local Testing
- [ ] **Application starts successfully**
  ```bash
  docker-compose up
  # Check: http://localhost:5000/api/health
  ```

- [ ] **Knowledge base built**
  ```bash
  cd backend
  python src/build_knowledge_base.py
  # Should create chromadb database
  ```

- [ ] **Query works**
  ```bash
  curl -X POST http://localhost:5000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "What is Bitcoin?", "language": "en"}'
  # Should return answer
  ```

- [ ] **Bots respond** (if configured)
  - Telegram: Send message to bot
  - Discord: Use slash command

### Staging Testing (Before Production)
- [ ] **Staging deployed successfully**
- [ ] **Health endpoint returns 200**
- [ ] **Smoke tests pass**
- [ ] **Load test passed** (100 concurrent users, <2s response)
- [ ] **Security scan clean** (0 critical vulnerabilities)
- [ ] **Backup/restore tested**

---

## 💰 8. Budget Requirements

### Minimum Monthly Cost (Free Tier)
| Service | Cost | Required? |
|---------|------|-----------|
| Railway (Hobby) | $5 | ✅ Yes |
| OpenAI API | ~$5-10 | ✅ Yes (or use Gemini free) |
| Gemini API | FREE | ⭐ Recommended |
| Sentry (Free tier) | $0 | ⭐ Recommended |
| Domain name | ~$1/month | Optional |
| **TOTAL** | **$6-16/month** | - |

### Recommended Production Cost
| Service | Cost | Purpose |
|---------|------|---------|
| Railway (Pro) | $20 | Better performance |
| OpenAI API | $50 | 15% of traffic |
| Gemini API | FREE | 80% of traffic |
| Perplexity API | $10 | 5% of traffic |
| Sentry (Team) | $26 | 20K events/month |
| S3 Storage | $5 | Backups |
| Domain + SSL | $1 | Professional URL |
| **TOTAL** | **~$112/month** | - |

### Expected Costs at Scale
- **100 users/day:** $112/month
- **1,000 users/day:** $250/month
- **10,000 users/day:** $800/month

---

## 📈 9. Monitoring Requirements

### Must Have (Production)
- [ ] **Sentry Error Tracking**
  - Catches all exceptions
  - Sends alerts on critical errors
  - Free tier sufficient for start

- [ ] **Health Endpoint**
  - `/api/health` returns status
  - Includes uptime, request count, error rate
  - Already implemented ✓

- [ ] **Uptime Monitoring** (Free options)
  - UptimeRobot: https://uptimerobot.com (free)
  - Pingdom: https://pingdom.com (paid)
  - Checks every 5 minutes

### Nice to Have
- [ ] **Log Aggregation** - Papertrail, Loggly
- [ ] **APM** - DataDog, New Relic
- [ ] **Status Page** - Statuspage.io

---

## 🗄️ 10. Data Requirements

### Knowledge Base
- [ ] **Minimum 10 documentation files** in `backend/data/docs/`
  - Format: Markdown (.md)
  - Topics: Crypto fundamentals, wallets, trading, security
  - Example structure:
    ```
    backend/data/docs/
    ├── bitcoin.md
    ├── ethereum.md
    ├── wallets.md
    ├── defi.md
    ├── trading.md
    └── security.md
    ```

### Database
- [ ] **PostgreSQL** (for analytics) - Handled by Railway/Docker
- [ ] **ChromaDB** (for vector search) - Included in Docker image
- [ ] **Redis** (for caching) - Optional but recommended

---

## 🚀 11. Deployment Checklist

### Pre-Deployment
- [ ] All API keys obtained and tested
- [ ] `.env.secrets` configured with production keys
- [ ] Knowledge base built and tested locally
- [ ] Security scan passed
- [ ] Load test passed (if high traffic expected)
- [ ] Backup/restore tested
- [ ] Team trained on monitoring dashboards

### Staging Deployment
- [ ] Staging environment deployed
- [ ] Separate staging API keys configured
- [ ] Smoke tests passed on staging
- [ ] Manual testing completed
- [ ] Performance acceptable (<2s response time)

### Production Deployment
- [ ] Production Railway/Fly project created
- [ ] Production secrets configured
- [ ] Domain name pointed (if using custom domain)
- [ ] SSL certificate active (auto via Railway/Fly)
- [ ] Monitoring alerts configured
- [ ] Backup cron job running
- [ ] On-call rotation established
- [ ] Rollback plan documented

### Post-Deployment
- [ ] Health endpoint monitored (should return 200)
- [ ] First queries tested successfully
- [ ] Error rate acceptable (<1%)
- [ ] Response time acceptable (<2s p95)
- [ ] Backup ran successfully
- [ ] Team notified of go-live

---

## 📞 12. Support Requirements

### Documentation
- [ ] **README.md** - Overview and quick start ✓
- [ ] **DEPLOYMENT.md** - Deployment guide ✓
- [ ] **STAGING.md** - Staging environment guide ✓
- [ ] **DISASTER_RECOVERY.md** - Emergency procedures ✓
- [ ] **API.md** - API documentation ✓

### Team Access
- [ ] At least 2 people have Railway/Fly access
- [ ] At least 2 people have AWS/S3 access
- [ ] At least 2 people have Sentry access
- [ ] On-call rotation defined
- [ ] Escalation path documented

---

## ⚡ Quick Start Commands

### 1. Install Tools
```bash
# Install Railway CLI
npm install -g @railway/cli

# Install testing tools (optional)
brew install bats-core k6
pip install bandit safety
```

### 2. Configure Secrets
```bash
# Copy template
cp backend/.env.secrets.example backend/.env.secrets

# Edit with your keys
nano backend/.env.secrets
```

### 3. Test Locally
```bash
# Build knowledge base
cd backend
python src/build_knowledge_base.py

# Start services
docker-compose up

# Test health
curl http://localhost:5000/api/health

# Test query
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Bitcoin?", "language": "en"}'
```

### 4. Deploy to Staging
```bash
# Login to Railway
railway login

# Link project
railway link

# Deploy
railway up --environment staging

# Check deployment
railway logs --environment staging
```

### 5. Deploy to Production
```bash
# Deploy to production
railway up --environment production

# Verify
curl https://your-domain.com/api/health
```

---

## 🎯 Minimum Requirements Summary

**To deploy, you MUST have:**
1. ✅ At least 1 LLM API key (OpenAI or Gemini)
2. ✅ Railway or Fly.io account
3. ✅ `.env.secrets` file configured
4. ✅ Knowledge base documents (10+ markdown files)
5. ✅ Docker installed locally (for testing)
6. ✅ Security scan passed
7. ✅ Health endpoint returns 200 locally

**Recommended but not required:**
- ⭐ Sentry for error tracking
- ⭐ S3 for backups
- ⭐ Bot tokens (Telegram/Discord)
- ⭐ Load testing passed
- ⭐ Staging environment

---

## 📋 Deployment Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Setup** | 2 hours | Get API keys, configure secrets |
| **Local Testing** | 1 hour | Test queries, build knowledge base |
| **Staging Deploy** | 1 hour | Deploy to staging, test |
| **Production Deploy** | 30 min | Deploy to production |
| **Monitoring Setup** | 1 hour | Configure Sentry, alerts |
| **TOTAL** | **5.5 hours** | From zero to production |

---

## ✅ Verification Checklist

Before marking deployment as complete:

- [ ] Health endpoint returns 200
- [ ] Query returns correct answer
- [ ] Bots respond (if configured)
- [ ] Sentry captures test error
- [ ] Backup runs successfully
- [ ] Logs are accessible
- [ ] Error rate < 1%
- [ ] Response time < 2s (p95)
- [ ] SSL certificate active
- [ ] Team has access to all systems

---

## 🆘 Common Issues & Solutions

### Issue 1: "OpenAI API key invalid"
**Solution:** Double-check key, ensure billing enabled, check quota

### Issue 2: "Module not found"
**Solution:** `pip install -r backend/requirements.txt`

### Issue 3: "Knowledge base empty"
**Solution:** Run `python src/build_knowledge_base.py`

### Issue 4: "Port already in use"
**Solution:** `docker-compose down`, then `docker-compose up`

### Issue 5: "Railway deployment failed"
**Solution:** Check Railway logs: `railway logs`

---

## 📚 Additional Resources

- **Railway Docs:** https://docs.railway.app
- **Fly.io Docs:** https://fly.io/docs
- **OpenAI API:** https://platform.openai.com/docs
- **Gemini API:** https://ai.google.dev/docs
- **Telegram Bots:** https://core.telegram.org/bots
- **Discord Bots:** https://discord.com/developers/docs

---

**Total Setup Time:** 5-6 hours (first time)  
**Minimum Cost:** $6-16/month  
**Recommended Cost:** $112/month  
**Difficulty:** ⭐⭐⭐ Intermediate  

**You're ready to deploy when all ✅ Required items are checked!**
