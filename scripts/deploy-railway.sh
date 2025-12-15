#!/bin/bash

# Deployment script for Railway
set -e

echo "Starting Railway deployment..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Check for required environment variables
if [ -z "$RAILWAY_TOKEN" ]; then
    echo "Error: RAILWAY_TOKEN environment variable not set"
    exit 1
fi

# Login to Railway
echo "Logging in to Railway..."
railway login --browserless

# Link to project
echo "Linking to Railway project..."
railway link

# Set environment variables
echo "Setting environment variables..."
railway variables set FLASK_PORT=5000
railway variables set FLASK_HOST=0.0.0.0

# Deploy
echo "Deploying to Railway..."
railway up

echo "Deployment complete!"
echo "Check your deployment at: https://railway.app"
