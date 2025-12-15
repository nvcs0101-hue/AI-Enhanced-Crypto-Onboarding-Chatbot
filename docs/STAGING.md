# 🧪 Staging Environment Guide

## Overview

The staging environment is a **production-like environment** for testing changes before deploying to production. It helps catch bugs, test integrations, and validate new features safely.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    STAGING PIPELINE                      │
└─────────────────────────────────────────────────────────┘

Developer → Push to `develop` → GitHub Actions
              │
              ├─> Run Tests
              ├─> Build Docker Image
              ├─> Deploy to Railway Staging
              ├─> Health Check
              └─> Comment on PR with URL
              
Production Deploy: Only after PR approval & merge to `main`
```

---

## 🚀 Quick Start

### 1. Prerequisites

- GitHub repository with actions enabled
- Railway account (free tier works)
- Environment secrets configured

### 2. Configure Secrets

Go to GitHub Settings → Secrets and Variables → Actions:

```bash
# Required secrets:
RAILWAY_STAGING_TOKEN         # Railway API token
RAILWAY_STAGING_PROJECT_ID    # Railway project ID for staging
STAGING_URL                   # https://staging.yourdomain.com
OPENAI_API_KEY               # API keys (same as production)
GOOGLE_API_KEY
PERPLEXITY_API_KEY
SECRET_KEY                   # Different from production!

# Optional:
TELEGRAM_BOT_TOKEN_STAGING   # Separate staging bot
DISCORD_BOT_TOKEN_STAGING    # Separate staging bot
SENTRY_DSN                   # Error tracking
SLACK_WEBHOOK_URL            # Notifications
```

### 3. Deploy to Staging

**Option A: Automatic (on PR)**
```bash
git checkout -b feature/my-new-feature
git commit -am "Add new feature"
git push origin feature/my-new-feature
# Create PR → Automatic deployment to staging
```

**Option B: Manual**
```bash
git checkout develop
git pull
# Triggers staging deployment automatically
```

**Option C: Local Staging**
```bash
docker-compose -f docker-compose.staging.yml up
```

---

## 🔧 Configuration

### Environment Variables (Staging)

Copy `.env.staging.example` to `.env`:

```bash
cd backend
cp .env.staging.example .env
# Edit .env with your staging credentials
```

**Key differences from production:**

| Variable | Production | Staging |
|----------|-----------|---------|
| `FLASK_ENV` | production | staging |
| `FLASK_DEBUG` | false | false |
| `TELEGRAM_BOT_TOKEN` | prod-bot-token | staging-bot-token |
| `DISCORD_BOT_TOKEN` | prod-bot-token | staging-bot-token |
| `SECRET_KEY` | secret-prod-key | **different-staging-key** |
| `RATE_LIMIT_PER_MINUTE` | 60 | 100 (more lenient) |
| `SENTRY_ENVIRONMENT` | production | staging |
| `RETENTION_DAYS` | 30 | 7 (faster cleanup) |

### Docker Compose Staging

```bash
# Start staging environment
docker-compose -f docker-compose.staging.yml up -d

# View logs
docker-compose -f docker-compose.staging.yml logs -f

# Stop staging
docker-compose -f docker-compose.staging.yml down
```

**Staging stack includes:**
- Backend API (port 5001)
- Redis cache (port 6380)
- PostgreSQL (port 5433)
- Telegram bot (staging token)
- Discord bot (staging token)

---

## 🧪 Testing on Staging

### 1. Automated Tests

Tests run automatically on PR:
- Unit tests
- Integration tests
- Linting (flake8, black)
- Coverage report

### 2. Manual Testing

**API Testing:**
```bash
# Health check
curl https://staging.yourdomain.com/api/health

# Test query
curl -X POST https://staging.yourdomain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test query", "language": "en"}'

# Check metrics
curl https://staging.yourdomain.com/api/stats
```

**Bot Testing:**
- Telegram: Message @YourStagingBot
- Discord: Use staging bot in test server

### 3. Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Test 1000 requests, 10 concurrent
ab -n 1000 -c 10 -H "Content-Type: application/json" \
   -p test-payload.json \
   https://staging.yourdomain.com/api/chat
```

---

## 📊 Monitoring Staging

### Health Endpoint

```bash
curl https://staging.yourdomain.com/api/health
```

Response:
```json
{
  "status": "healthy",
  "environment": "staging",
  "monitoring_enabled": true,
  "metrics": {
    "uptime_seconds": 86400,
    "total_requests": 1523,
    "total_errors": 3,
    "error_rate": 0.2,
    "llm_calls": {
      "openai": 305,
      "gemini": 1200,
      "perplexity": 18
    },
    "cache_hit_rate": 45.2
  }
}
```

### Logs

**Railway Dashboard:**
```
railway logs --environment staging
```

**Docker:**
```bash
docker-compose -f docker-compose.staging.yml logs -f backend
```

**Sentry:**
- Visit https://sentry.io
- Filter by environment: staging

---

## 🔄 CI/CD Workflow

### Staging Deployment Flow

```yaml
Pull Request Opened/Updated:
  ↓
Run Tests (pytest, flake8, black)
  ↓
Build Docker Image
  ↓
Deploy to Railway Staging
  ↓
Health Check (retry 3x)
  ↓
Comment on PR with Staging URL
  ↓
Manual Testing by Reviewer
  ↓
Approve PR
  ↓
Merge to main → Production Deployment
```

### Rollback Procedure

**If staging deployment fails:**

1. **Check logs:**
```bash
railway logs --environment staging
```

2. **Rollback to previous version:**
```bash
railway rollback --environment staging
```

3. **Or redeploy last working commit:**
```bash
git revert HEAD
git push origin develop
```

---

## 🗄️ Database Management

### Staging Database

- **Separate from production** (important!)
- **Smaller dataset** for faster testing
- **Reset weekly** to match production schema

### Reset Staging Database

```bash
# Backup current staging data
./scripts/backup-database.sh

# Restore from production backup (sanitized)
./scripts/restore-database.sh 20241215_020000 s3

# Or start fresh
docker-compose -f docker-compose.staging.yml down -v
docker-compose -f docker-compose.staging.yml up -d
python backend/src/build_knowledge_base.py
```

### Test Data

Create test data for staging:

```python
# scripts/seed-staging-data.py
from backend.src.usage_tracker import UsageTracker, PricingTier

tracker = UsageTracker()

# Create test users
test_users = [
    ('test_free_user', PricingTier.FREE),
    ('test_pro_user', PricingTier.PRO),
    ('test_enterprise_user', PricingTier.ENTERPRISE),
]

for user_id, tier in test_users:
    tracker.upgrade_tier(user_id, tier)
    print(f"Created {tier.value} user: {user_id}")
```

Run:
```bash
python scripts/seed-staging-data.py
```

---

## 🔒 Security

### Staging-Specific Considerations

1. **Separate Bot Tokens** - Never use production tokens in staging
2. **Different Secret Keys** - Staging must have its own SECRET_KEY
3. **Relaxed Rate Limits** - For testing, but still protect against abuse
4. **Test Credit Cards** - Use Stripe test mode
5. **Anonymized Data** - Never use real production data with PII

### Access Control

- Staging URL should NOT be public
- Use HTTP auth or IP whitelist:

```nginx
# In nginx config
location / {
    auth_basic "Staging Environment";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://backend:5000;
}
```

Or use Railway's built-in authentication.

---

## 🐛 Troubleshooting

### Common Issues

**1. Staging deployment fails**
```bash
# Check GitHub Actions logs
# Common causes:
- Test failures
- Missing environment variables
- Railway quota exceeded

# Solution:
- Fix tests
- Add missing secrets
- Upgrade Railway plan
```

**2. Database connection error**
```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.staging.yml ps postgres

# Check connection string
echo $POSTGRES_URL

# Restart database
docker-compose -f docker-compose.staging.yml restart postgres
```

**3. Staging shows old version**
```bash
# Check deployment status
railway status --environment staging

# Force redeploy
railway up --environment staging
```

**4. Sentry not receiving errors**
```bash
# Verify DSN is correct
echo $SENTRY_DSN

# Test manually
python -c "from backend.src.monitoring import track_event; track_event('test')"
```

---

## 📋 Staging Checklist

Before merging to production:

- [ ] All tests pass on staging
- [ ] Manual smoke testing completed
- [ ] Performance testing shows acceptable response times
- [ ] No errors in Sentry dashboard
- [ ] Database migrations tested
- [ ] Bot integrations working (Telegram/Discord)
- [ ] API endpoints responding correctly
- [ ] Multi-LLM routing working
- [ ] Analytics tracking properly
- [ ] Privacy compliance features functional
- [ ] Backup/restore tested
- [ ] Code review approved
- [ ] Product owner sign-off

---

## 🎓 Best Practices

### 1. Keep Staging Close to Production

- Same Docker images
- Same infrastructure (Railway/Fly.io)
- Same environment variables (except tokens/keys)
- Same monitoring tools

### 2. Test Everything on Staging First

- Never deploy to production without staging validation
- Test edge cases and error scenarios
- Verify rollback procedures

### 3. Reset Regularly

- Weekly database refresh from production (sanitized)
- Clear old test data
- Update dependencies

### 4. Monitor Staging

- Set up alerts for staging errors
- Review staging logs regularly
- Track staging performance metrics

### 5. Document Issues

- Log bugs found in staging
- Document fixes and workarounds
- Share learnings with team

---

## 📞 Getting Help

**Staging issues:**
- Check GitHub Actions logs
- Review Railway dashboard
- Check Sentry for errors
- Ask in team Slack/Discord

**Emergency rollback:**
```bash
railway rollback --environment staging
```

**Need production data in staging:**
```bash
# Sanitize and restore
./scripts/backup-database.sh  # on production
./scripts/sanitize-backup.sh 20241215_020000
./scripts/restore-database.sh 20241215_020000_sanitized s3
```

---

## 🚀 Next Steps

After staging is working:

1. **Enable automatic deploys** to staging on `develop` branch
2. **Set up production deployment** on `main` branch merge
3. **Configure blue-green deployment** for zero-downtime
4. **Add E2E tests** (Playwright/Cypress)
5. **Set up performance monitoring** (DataDog/New Relic)

---

**Staging environment is your safety net. Use it religiously!** 🛡️
