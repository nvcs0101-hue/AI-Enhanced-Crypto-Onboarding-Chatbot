#!/bin/bash

# Run Load Test Against Staging or Production

set -e

echo "⚡ Load Testing Framework"
echo "========================"
echo ""

# Check if k6 is installed
if ! command -v k6 &> /dev/null; then
    echo "❌ k6 not installed"
    echo "   Install: brew install k6"
    echo "   Or: https://k6.io/docs/getting-started/installation/"
    exit 1
fi

# Select environment
echo "Select environment to test:"
echo "  1) Local (http://localhost:5000)"
echo "  2) Staging"
echo "  3) Production (⚠️  Use with caution!)"
read -p "Choice (1-3): " ENV_CHOICE

case $ENV_CHOICE in
    1)
        BASE_URL="http://localhost:5000"
        ;;
    2)
        read -p "Enter staging URL: " BASE_URL
        ;;
    3)
        echo ""
        echo "⚠️  WARNING: Testing production can impact real users!"
        read -p "Are you sure? (yes/no): " CONFIRM
        if [[ ! $CONFIRM =~ ^[Yy][Ee][Ss]$ ]]; then
            echo "Cancelled"
            exit 0
        fi
        read -p "Enter production URL: " BASE_URL
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎯 Target: $BASE_URL"
echo ""

# Health check first
echo "Checking if service is up..."
if ! curl -f "$BASE_URL/api/health" > /dev/null 2>&1; then
    echo "❌ Service is not responding at $BASE_URL"
    exit 1
fi
echo "✅ Service is up"
echo ""

# Select test profile
echo "Select test profile:"
echo "  1) Smoke (10 users, 1 min)"
echo "  2) Standard (100 users, 10 min)"
echo "  3) Stress (200 users, 15 min)"
echo "  4) Spike (10 → 500 → 10 users)"
read -p "Choice (1-4): " PROFILE

case $PROFILE in
    1)
        echo "Running smoke test..."
        k6 run --vus 10 --duration 1m -e BASE_URL="$BASE_URL" tests/load/k6-test.js
        ;;
    2)
        echo "Running standard load test..."
        k6 run -e BASE_URL="$BASE_URL" tests/load/k6-test.js
        ;;
    3)
        echo "Running stress test..."
        k6 run --vus 200 --duration 15m -e BASE_URL="$BASE_URL" tests/load/k6-test.js
        ;;
    4)
        echo "Running spike test..."
        k6 run --stage 1m:10 --stage 30s:500 --stage 2m:10 -e BASE_URL="$BASE_URL" tests/load/k6-test.js
        ;;
esac

echo ""
echo "✅ Load test complete!"
echo "📊 Results saved to load-test-results.json"
