# 📋 Week 1-2 Implementation Checklist

> **Goal:** Set up staging environment and establish production-ready foundations

**Timeline:** Weeks 1-2 (Dec 15 - Dec 28, 2024)  
**Budget:** $6,000  
**Team:** 1 DevOps Engineer  
**Status:** 🟢 Ready to Start

---

## ✅ Task List

### Day 1-2: Staging Environment Setup

- [x] Create staging deployment workflow (`.github/workflows/staging-deploy.yml`)
- [x] Create staging Docker Compose configuration (`docker-compose.staging.yml`)
- [x] Create staging environment variables template (`.env.staging.example`)
- [ ] Configure Railway staging project
  - [ ] Create new Railway project for staging
  - [ ] Link GitHub repository
  - [ ] Set up environment variables
  - [ ] Generate `RAILWAY_STAGING_TOKEN`
  - [ ] Get `RAILWAY_STAGING_PROJECT_ID`
- [ ] Add GitHub secrets
  - [ ] `RAILWAY_STAGING_TOKEN`
  - [ ] `RAILWAY_STAGING_PROJECT_ID`
  - [ ] `STAGING_URL`
  - [ ] `OPENAI_API_KEY`
  - [ ] `GOOGLE_API_KEY`
  - [ ] `PERPLEXITY_API_KEY`
  - [ ] `SECRET_KEY` (generate new for staging)
  - [ ] `TELEGRAM_BOT_TOKEN_STAGING` (optional)
  - [ ] `DISCORD_BOT_TOKEN_STAGING` (optional)

### Day 3-4: Database & Monitoring Setup

- [x] Create database initialization script (`scripts/init-db.sql`)
- [x] Create backup script (`scripts/backup-database.sh`)
- [x] Create restore script (`scripts/restore-database.sh`)
- [x] Create monitoring setup script (`scripts/init-monitoring.sh`)
- [ ] Set up PostgreSQL staging database
  - [ ] Deploy PostgreSQL on Railway
  - [ ] Run `init-db.sql`
  - [ ] Verify tables created
- [ ] Configure Sentry error tracking
  - [ ] Sign up for Sentry (free tier)
  - [ ] Create new project
  - [ ] Get DSN
  - [ ] Add to GitHub secrets
  - [ ] Run `./scripts/init-monitoring.sh`

### Day 5-6: Integration & Testing

- [ ] Test staging deployment
  - [ ] Push to `develop` branch
  - [ ] Verify GitHub Actions runs
  - [ ] Check Railway deployment
  - [ ] Verify health endpoint: `curl $STAGING_URL/api/health`
- [ ] Test database connectivity
  - [ ] Verify PostgreSQL connection
  - [ ] Check tables exist
  - [ ] Insert test record
- [ ] Test backup system
  - [ ] Run manual backup: `./scripts/backup-database.sh`
  - [ ] Verify backup created
  - [ ] Test restore: `./scripts/restore-database.sh <timestamp> local`
- [ ] Test monitoring
  - [ ] Trigger test error
  - [ ] Check Sentry dashboard
  - [ ] Verify error captured

### Day 7-8: Documentation & Handoff

- [x] Create staging documentation (`docs/STAGING.md`)
- [ ] Update main README with staging instructions
- [ ] Create runbook for common operations
  - [ ] How to deploy to staging
  - [ ] How to rollback
  - [ ] How to check logs
  - [ ] How to run backups manually
- [ ] Team training
  - [ ] Walk through staging workflow
  - [ ] Demo backup/restore
  - [ ] Show monitoring dashboards

---

## 🎯 Success Criteria

By end of Week 2, we should have:

- ✅ Staging environment automatically deploys on PR creation
- ✅ Separate staging database (PostgreSQL)
- ✅ Automated daily backups with 7-day retention
- ✅ Error tracking with Sentry
- ✅ Health monitoring endpoint with metrics
- ✅ Documentation for staging operations
- ✅ Team trained on staging workflow

---

## 📊 Key Metrics to Track

| Metric | Target | How to Check |
|--------|--------|--------------|
| Deployment Success Rate | >95% | GitHub Actions history |
| Average Deploy Time | <5 min | GitHub Actions logs |
| Health Check Uptime | 99%+ | `curl $STAGING_URL/api/health` |
| Backup Success Rate | 100% | Check `/app/backups/` directory |
| Error Detection Time | <5 min | Sentry alert latency |

---

## 🛠️ Required Tools & Accounts

### Sign Up / Configure:
- [ ] Railway account (https://railway.app)
- [ ] Sentry account (https://sentry.io)
- [ ] GitHub repository secrets configured
- [ ] Separate Telegram bot for staging (optional)
- [ ] Separate Discord bot for staging (optional)

### Install Locally (for testing):
```bash
# Railway CLI
npm install -g @railway/cli

# Docker (already installed in dev container)
docker --version

# PostgreSQL client tools
apt-get update && apt-get install -y postgresql-client

# Verify installations
railway --version
docker-compose --version
psql --version
```

---

## 💰 Cost Breakdown

| Item | Cost | Provider |
|------|------|----------|
| DevOps Engineer (2 weeks) | $6,000 | Team |
| Railway Staging (Hobby Plan) | $5/month | Railway |
| Sentry (Free Tier) | $0 | Sentry |
| GitHub Actions (Free for public repos) | $0 | GitHub |
| **Total** | **$6,005** | - |

---

## 🚨 Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Railway quota exceeded | High | Low | Monitor usage, upgrade if needed |
| Secrets not configured | High | Medium | Checklist before first deploy |
| Database migration fails | Medium | Low | Test on local staging first |
| Backup storage fills up | Medium | Low | 7-day retention + S3 upload |

---

## 📞 Support & Resources

**Railway:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

**Sentry:**
- Docs: https://docs.sentry.io
- Support: support@sentry.io

**PostgreSQL:**
- Docs: https://www.postgresql.org/docs/

**Team:**
- Staging issues: #staging-support Slack channel
- Emergency: On-call DevOps engineer

---

## 🎬 Next Steps After Week 2

Once staging is stable, proceed to **Week 3-4: Monitoring & Alerting**

Week 3-4 tasks:
- [ ] Set up DataDog/New Relic
- [ ] Configure alerting rules
- [ ] Create monitoring dashboards
- [ ] Set up log aggregation
- [ ] Configure PagerDuty for on-call

---

## 📝 Daily Standup Template

Use this for daily check-ins:

**✅ Completed Yesterday:**
- [List completed tasks]

**🚧 Working on Today:**
- [List today's tasks]

**🚫 Blockers:**
- [Any issues or dependencies]

**📊 Progress:**
- [X/Y tasks completed]

---

## ✨ Quick Reference Commands

```bash
# Deploy to staging manually
railway up --environment staging

# Check staging logs
railway logs --environment staging --tail

# Run backup
./scripts/backup-database.sh

# Restore from backup
./scripts/restore-database.sh 20241215_020000 local

# Check health
curl https://staging.yourdomain.com/api/health

# Test API
curl -X POST https://staging.yourdomain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Bitcoin?", "language": "en"}'

# SSH into Railway container
railway shell --environment staging

# Reset staging database
docker-compose -f docker-compose.staging.yml down -v
docker-compose -f docker-compose.staging.yml up -d
```

---

**Remember:** Staging is your safety net. Never skip testing on staging before deploying to production! 🛡️

---

**Last Updated:** December 15, 2024  
**Owner:** DevOps Team  
**Reviewers:** Backend Team, PM
