#!/bin/bash

# Local Security Scan
# Run before committing code

set -e

echo "🔒 Running Security Scans..."
echo ""

cd "$(dirname "$0")/.."

# Install tools if not present
if ! command -v bandit &> /dev/null; then
    echo "Installing bandit..."
    pip install bandit
fi

if ! command -v safety &> /dev/null; then
    echo "Installing safety..."
    pip install safety
fi

# Run Bandit
echo "1️⃣ Running Bandit (Python security linter)..."
bandit -r backend/src -ll || echo "⚠️  Bandit found issues"
echo ""

# Run Safety
echo "2️⃣ Running Safety (dependency vulnerabilities)..."
cd backend
safety check || echo "⚠️  Safety found vulnerabilities"
cd ..
echo ""

# Check for common secrets patterns
echo "3️⃣ Checking for exposed secrets..."
if grep -r "sk-[a-zA-Z0-9]\{32,\}" backend/ 2>/dev/null; then
    echo "❌ Found potential OpenAI API key!"
    exit 1
fi

if grep -r "AIza[0-9A-Za-z-_]\{35\}" backend/ 2>/dev/null; then
    echo "❌ Found potential Google API key!"
    exit 1
fi

if grep -r "postgres://.*:.*@" backend/ 2>/dev/null; then
    echo "❌ Found database credentials in code!"
    exit 1
fi

echo "✅ No obvious secrets found in code"
echo ""

echo "✅ Security scan complete!"
