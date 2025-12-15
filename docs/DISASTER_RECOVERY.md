# 🚨 Disaster Recovery Plan

## Recovery Time Objective (RTO)
**Target:** 4 hours from incident to full service restoration

## Recovery Point Objective (RPO)
**Target:** Maximum 24 hours of data loss (daily backups)

---

## 🔥 Disaster Scenarios

### Scenario 1: Complete Database Loss

**Symptoms:**
- PostgreSQL won't start
- Data directory corrupted
- All data lost

**Recovery Steps:**

1. **Assess Damage** (15 min)
   ```bash
   # Check if database is recoverable
   pg_isready -h localhost -p 5432
   
   # Check data directory
   ls -la /var/lib/postgresql/data/
   ```

2. **Identify Latest Backup** (5 min)
   ```bash
   # List available backups
   ls -lht /app/backups/ | head -10
   
   # Or check S3
   aws s3 ls s3://your-backup-bucket/backups/postgres/ --recursive
   ```

3. **Download Backup (if from S3)** (10 min)
   ```bash
   # Get latest backup
   LATEST=$(aws s3 ls s3://your-backup-bucket/backups/postgres/ | sort | tail -1 | awk '{print $4}')
   aws s3 cp "s3://your-backup-bucket/backups/postgres/$LATEST" /app/backups/
   ```

4. **Stop All Services** (2 min)
   ```bash
   docker-compose down
   ```

5. **Restore Database** (30 min - 2 hours depending on size)
   ```bash
   # Extract timestamp from backup filename
   TIMESTAMP=$(echo $LATEST | sed 's/postgres_backup_\(.*\)\.sql\.gz/\1/')
   
   # Run restore script
   ./scripts/restore-database.sh $TIMESTAMP local
   ```

6. **Verify Data Integrity** (15 min)
   ```bash
   # Check row counts
   psql -h localhost -U postgres -d chatbot_analytics -c "SELECT COUNT(*) FROM analytics;"
   psql -h localhost -U postgres -d chatbot_analytics -c "SELECT COUNT(*) FROM usage_tracking;"
   
   # Check latest timestamps
   psql -h localhost -U postgres -d chatbot_analytics -c "SELECT MAX(timestamp) FROM analytics;"
   ```

7. **Restart Services** (5 min)
   ```bash
   docker-compose up -d
   ```

8. **Run Smoke Tests** (10 min)
   ```bash
   # Test health endpoint
   curl http://localhost:5000/api/health
   
   # Test query
   curl -X POST http://localhost:5000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What is Bitcoin?", "language": "en"}'
   ```

9. **Monitor for 1 Hour**
   - Check error rates in Sentry
   - Monitor response times
   - Check database connection pool

10. **Post-Incident Review** (Next day)
    - Document what happened
    - Update runbook
    - Improve backup frequency if needed

**Total Time:** 2-4 hours

---

### Scenario 2: Vector Database (ChromaDB) Corruption

**Recovery Steps:**

1. **Stop Backend Services**
   ```bash
   docker-compose stop backend telegram-bot discord-bot
   ```

2. **Identify Latest Backup**
   ```bash
   ls -lht /app/backups/chroma_backup_*.tar.gz | head -5
   ```

3. **Backup Current (Corrupted) Data**
   ```bash
   mv /app/data/chroma_db /app/data/chroma_db_corrupted_$(date +%Y%m%d)
   ```

4. **Restore from Backup**
   ```bash
   TIMESTAMP="20241215_020000"  # Replace with actual
   ./scripts/restore-database.sh $TIMESTAMP local
   ```

5. **Restart Services**
   ```bash
   docker-compose up -d backend telegram-bot discord-bot
   ```

6. **Verify**
   ```bash
   # Test query
   curl -X POST http://localhost:5000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Test query", "language": "en"}'
   ```

**Total Time:** 30-60 minutes

---

### Scenario 3: Complete Infrastructure Loss (Railway/Server Down)

**Recovery Steps:**

1. **Provision New Infrastructure** (30 min)
   ```bash
   # New Railway project
   railway init
   
   # Or new server
   # Provision Ubuntu 22.04 server
   ```

2. **Install Dependencies** (15 min)
   ```bash
   # Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Docker Compose
   sudo apt install docker-compose-plugin
   ```

3. **Clone Repository** (5 min)
   ```bash
   git clone https://github.com/your-org/crypto-chatbot.git
   cd crypto-chatbot
   ```

4. **Restore Environment Variables** (10 min)
   ```bash
   # From password manager or secrets vault
   cp .env.secrets.backup backend/.env
   ```

5. **Download Latest Backups from S3** (15 min)
   ```bash
   aws s3 sync s3://your-backup-bucket/backups/ /app/backups/
   ```

6. **Restore Databases** (1-2 hours)
   ```bash
   TIMESTAMP="20241215_020000"
   ./scripts/restore-database.sh $TIMESTAMP local
   ```

7. **Deploy Services** (10 min)
   ```bash
   docker-compose up -d
   ```

8. **Update DNS** (5 min + propagation time)
   ```bash
   # Point domain to new server IP
   # Wait for DNS propagation (5-60 minutes)
   ```

9. **Verify and Monitor** (30 min)
   - Run smoke tests
   - Check all endpoints
   - Monitor error rates

**Total Time:** 3-4 hours + DNS propagation

---

## 🔄 DR Drills

### Quarterly DR Drill Schedule

**Q1 (March):** Scenario 1 - Database Loss
**Q2 (June):** Scenario 2 - ChromaDB Corruption
**Q3 (September):** Scenario 3 - Complete Infrastructure Loss
**Q4 (December):** Combined scenario (multiple failures)

### Drill Procedure

1. **Schedule** - Announce 1 week in advance
2. **Prepare** - Create test backup, document current state
3. **Execute** - Follow DR plan exactly
4. **Time** - Record actual time vs. RTO
5. **Debrief** - What worked, what didn't
6. **Update** - Improve DR plan based on learnings

---

## 📞 Emergency Contacts

| Role | Name | Phone | Email | Backup |
|------|------|-------|-------|--------|
| **On-Call Engineer** | TBD | +1-XXX-XXX-XXXX | oncall@company.com | TBD |
| **DevOps Lead** | TBD | +1-XXX-XXX-XXXX | devops@company.com | TBD |
| **CTO** | TBD | +1-XXX-XXX-XXXX | cto@company.com | - |

---

## 🔐 Access in Emergency

**Secrets Location:**
- Password Manager: 1Password vault "Production Secrets"
- Backup: Encrypted USB drive in safe (Office 301)
- CEO has master key

**Service Access:**
- Railway: admin@company.com account
- AWS: root account (MFA with CEO phone)
- GitHub: Organization owner access
- Sentry: admin@company.com account

---

## 📊 Post-Incident Checklist

After resolving any incident:

- [ ] Document what happened (5 Ws)
- [ ] Calculate actual RTO achieved
- [ ] Calculate data loss (RPO)
- [ ] Update runbook with learnings
- [ ] Test backup/restore if not already done
- [ ] Review monitoring alerts (did they fire?)
- [ ] Schedule post-mortem meeting (within 48 hours)
- [ ] Implement improvements to prevent recurrence

---

## 📈 Continuous Improvement

**Monthly Review:**
- Review backup success rate (target: 100%)
- Review restore test results
- Update contact information
- Verify S3 backups are accessible

**Quarterly Updates:**
- Run DR drill
- Update RTO/RPO based on business needs
- Review and update emergency contacts
- Test all access credentials

---

**Last Reviewed:** December 15, 2024  
**Next Review:** March 15, 2025  
**Owner:** DevOps Team  
**Approved By:** CTO
