# Deployment Guide

This guide covers various deployment options for the AI-Enhanced Crypto Onboarding Chatbot.

## 📋 Prerequisites

Before deploying, ensure you have:
- OpenAI API key (or alternative LLM API key)
- Bot tokens (if deploying Telegram/Discord bots)
- Git repository with your code
- Documentation files in `backend/data/docs/`

## 🚂 Railway Deployment (Recommended)

Railway offers the easiest deployment with $5 monthly free credit.

### Step 1: Prepare Your Repository

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Deploy via CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add environment variables
railway variables set OPENAI_API_KEY=<your-key>
railway variables set TELEGRAM_BOT_TOKEN=<your-token>
railway variables set DISCORD_BOT_TOKEN=<your-token>

# Deploy
railway up
```

### Step 3: Configure Services

In the Railway dashboard:
1. Create separate services for:
   - Backend API
   - Telegram bot
   - Discord bot
2. Set start commands:
   - API: `cd backend && gunicorn app:app`
   - Telegram: `cd backend && python telegram_bot.py`
   - Discord: `cd backend && python discord_bot.py`

### Step 4: Set Up Domain (Optional)

In Railway dashboard:
1. Go to Settings → Domains
2. Generate a domain or add your custom domain

## 🪂 Fly.io Deployment

Fly.io offers free tier with 3 shared VMs.

### Step 1: Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

### Step 2: Launch App

```bash
# Login
flyctl auth login

# Launch (this creates fly.toml)
flyctl launch

# Set secrets
flyctl secrets set OPENAI_API_KEY=<your-key>
flyctl secrets set TELEGRAM_BOT_TOKEN=<your-token>
flyctl secrets set DISCORD_BOT_TOKEN=<your-token>

# Deploy
flyctl deploy
```

### Step 3: Scale (Optional)

```bash
# Scale to 2 instances
flyctl scale count 2

# Increase memory
flyctl scale memory 512
```

## 🎨 Render Deployment

Render offers free tier with 750 hours/month.

### Step 1: Connect Repository

1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository

### Step 2: Configure Service

**Build Command:**
```bash
cd backend && pip install -r requirements.txt
```

**Start Command:**
```bash
cd backend && gunicorn app:app
```

### Step 3: Add Environment Variables

In Render dashboard, add:
- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `DISCORD_BOT_TOKEN`
- `PYTHON_VERSION` = `3.11.0`

### Step 4: Deploy

Click "Create Web Service" and wait for deployment.

## 🐳 Docker Deployment

### Local Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Production Docker

```bash
# Use production compose file
docker-compose -f docker-compose.yml up -d
```

### Docker on VPS

1. **Provision a VPS** (DigitalOcean, Linode, AWS EC2)

2. **Install Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

3. **Clone repository:**
```bash
git clone <your-repo-url>
cd AI-Enhanced-Crypto-Onboarding-Chatbot
```

4. **Create .env file:**
```bash
cp backend/.env.example backend/.env
# Edit with your API keys
nano backend/.env
```

5. **Deploy:**
```bash
docker-compose up -d
```

6. **Set up reverse proxy (Nginx):**
```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/chatbot
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## ☁️ Cloud Platform Deployments

### AWS Elastic Beanstalk

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize:
```bash
cd backend
eb init -p python-3.11 crypto-chatbot
```

3. Create environment:
```bash
eb create production
```

4. Set environment variables:
```bash
eb setenv OPENAI_API_KEY=<your-key>
```

5. Deploy:
```bash
eb deploy
```

### Google Cloud Run

1. Install gcloud CLI

2. Build container:
```bash
gcloud builds submit --tag gcr.io/<PROJECT-ID>/crypto-chatbot
```

3. Deploy:
```bash
gcloud run deploy crypto-chatbot \
  --image gcr.io/<PROJECT-ID>/crypto-chatbot \
  --platform managed \
  --set-env-vars OPENAI_API_KEY=<your-key>
```

### Azure Container Instances

1. Create resource group:
```bash
az group create --name crypto-chatbot-rg --location eastus
```

2. Deploy:
```bash
az container create \
  --resource-group crypto-chatbot-rg \
  --name crypto-chatbot \
  --image <your-docker-image> \
  --dns-name-label crypto-chatbot \
  --ports 5000 \
  --environment-variables OPENAI_API_KEY=<your-key>
```

## 🔄 CI/CD Setup

The project includes GitHub Actions workflow for automatic deployment.

### GitHub Actions Setup

1. **Add secrets to GitHub:**
   - Go to Settings → Secrets and Variables → Actions
   - Add:
     - `OPENAI_API_KEY`
     - `RAILWAY_TOKEN` (for Railway deployment)
     - `TELEGRAM_BOT_TOKEN`
     - `DISCORD_BOT_TOKEN`

2. **Push to main branch:**
```bash
git push origin main
```

The workflow will automatically:
- Run tests
- Build Docker images
- Deploy to Railway (if configured)

## 🔒 Security Best Practices

1. **Never commit API keys**
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Enable HTTPS**
   - Use SSL certificates
   - Enable force_https in deployment configs

3. **Set up rate limiting**
   - Already configured in Flask app
   - Consider Cloudflare for additional protection

4. **Use secrets management**
   - Railway: Built-in secrets
   - AWS: AWS Secrets Manager
   - GCP: Secret Manager

5. **Monitor logs**
   - Set up log aggregation
   - Enable alerts for errors

## 📊 Monitoring

### Health Checks

All deployments should monitor the health endpoint:
```
GET /api/health
```

### Logging

Logs are stored in `backend/logs/chatbot.log`

For production, use:
- **Datadog** for log aggregation
- **Sentry** for error tracking
- **Prometheus + Grafana** for metrics

### Uptime Monitoring

Use services like:
- UptimeRobot (free)
- Pingdom
- StatusCake

## 🚀 Performance Optimization

1. **Enable caching:**
   - Redis for frequent queries
   - Configure in `docker-compose.yml`

2. **Scale horizontally:**
   - Multiple gunicorn workers
   - Load balancer (Nginx/HAProxy)

3. **Use CDN:**
   - Cloudflare for frontend
   - AWS CloudFront

4. **Database optimization:**
   - Index frequently queried fields
   - Use connection pooling

## 🆘 Troubleshooting

### Common Issues

**Issue: Build fails**
```bash
# Check Python version
python --version  # Should be 3.11+

# Clear cache and rebuild
docker-compose down -v
docker-compose build --no-cache
```

**Issue: Out of memory**
```bash
# Increase container memory
# In fly.toml:
memory_mb = 1024  # Increase as needed
```

**Issue: API timeout**
```bash
# Increase gunicorn timeout
# In Dockerfile:
CMD ["gunicorn", "--timeout", "120", "app:app"]
```

## 📞 Support

For deployment issues:
- Check [troubleshooting guide](TROUBLESHOOTING.md)
- Open a GitHub issue
- Contact support@example.com

## 🎓 Next Steps

After deployment:
1. Test all endpoints
2. Set up monitoring
3. Configure custom domain
4. Add SSL certificate
5. Set up backups
6. Configure logging
7. Add analytics

---

**Need help?** Join our [Discord community](#) or open an issue on GitHub.
