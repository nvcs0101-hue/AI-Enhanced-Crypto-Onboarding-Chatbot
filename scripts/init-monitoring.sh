#!/bin/bash

# Monitoring Setup Script
# Initializes Sentry error tracking and basic health monitoring

set -e

echo "=========================================="
echo "📊 Monitoring Setup"
echo "=========================================="
echo ""

# Check if required tools are installed
command -v pip >/dev/null 2>&1 || { echo "❌ pip is required but not installed."; exit 1; }

echo "📦 Installing monitoring dependencies..."
pip install sentry-sdk[flask]==1.39.2 python-dotenv==1.0.0
echo "✅ Dependencies installed"
echo ""

# Install Sentry
echo "🔧 Setting up Sentry error tracking..."
read -p "Enter your Sentry DSN (or press Enter to skip): " SENTRY_DSN

if [ -n "$SENTRY_DSN" ]; then
    # Add Sentry to .env if not exists
    if ! grep -q "SENTRY_DSN" backend/.env 2>/dev/null; then
        echo "SENTRY_DSN=$SENTRY_DSN" >> backend/.env
        echo "SENTRY_ENVIRONMENT=${ENVIRONMENT:-production}" >> backend/.env
        echo "SENTRY_TRACES_SAMPLE_RATE=0.1" >> backend/.env
    fi
    echo "✅ Sentry DSN configured"
else
    echo "⏭️  Sentry setup skipped"
fi
echo ""

# Create monitoring initialization file
echo "📝 Creating monitoring initialization..."
cat > backend/src/monitoring.py <<'PYEOF'
"""
Monitoring and error tracking initialization.
Integrates Sentry for error tracking and custom metrics.
"""

import os
import logging
from functools import wraps
from typing import Optional, Dict, Any
import time

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sentry integration
SENTRY_DSN = os.getenv('SENTRY_DSN')
SENTRY_ENABLED = bool(SENTRY_DSN)

if SENTRY_ENABLED:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[FlaskIntegration()],
            environment=os.getenv('SENTRY_ENVIRONMENT', 'production'),
            traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
            send_default_pii=False,  # Don't send PII
            before_send=lambda event, hint: sanitize_event(event),
        )
        logger.info("✅ Sentry error tracking initialized")
    except ImportError:
        logger.warning("⚠️  Sentry SDK not installed, error tracking disabled")
        SENTRY_ENABLED = False
    except Exception as e:
        logger.error(f"❌ Failed to initialize Sentry: {e}")
        SENTRY_ENABLED = False
else:
    logger.info("ℹ️  Sentry disabled (no DSN configured)")


def sanitize_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Remove sensitive data from Sentry events."""
    # Remove API keys from environment
    if 'contexts' in event and 'os' in event['contexts']:
        env = event['contexts']['os'].get('environment', {})
        sensitive_keys = ['API_KEY', 'SECRET', 'TOKEN', 'PASSWORD']
        for key in list(env.keys()):
            if any(s in key.upper() for s in sensitive_keys):
                env[key] = '***REDACTED***'
    
    return event


def track_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Manually track an error."""
    if SENTRY_ENABLED:
        import sentry_sdk
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)
            sentry_sdk.capture_exception(error)
    else:
        logger.error(f"Error: {error}", exc_info=True)


def track_event(event_name: str, data: Optional[Dict[str, Any]] = None):
    """Track a custom event."""
    if SENTRY_ENABLED:
        import sentry_sdk
        sentry_sdk.capture_message(
            event_name,
            level='info',
            extras=data or {}
        )
    logger.info(f"Event: {event_name}", extra=data or {})


def monitor_performance(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Log slow operations
            if duration > 5.0:
                logger.warning(
                    f"Slow operation: {func.__name__} took {duration:.2f}s"
                )
                track_event(
                    'slow_operation',
                    {
                        'function': func.__name__,
                        'duration': duration
                    }
                )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            track_error(
                e,
                {
                    'function': func.__name__,
                    'duration': duration,
                    'args': str(args)[:100],  # Truncate
                }
            )
            raise
    
    return wrapper


# Health check metrics
class HealthMetrics:
    """Track application health metrics."""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.llm_calls = {'openai': 0, 'gemini': 0, 'perplexity': 0}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def record_request(self):
        self.request_count += 1
    
    def record_error(self):
        self.error_count += 1
    
    def record_llm_call(self, provider: str):
        if provider in self.llm_calls:
            self.llm_calls[provider] += 1
    
    def record_cache_hit(self):
        self.cache_hits += 1
    
    def record_cache_miss(self):
        self.cache_misses += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        uptime = time.time() - self.start_time
        cache_total = self.cache_hits + self.cache_misses
        cache_rate = (
            (self.cache_hits / cache_total * 100)
            if cache_total > 0 else 0
        )
        
        return {
            'uptime_seconds': round(uptime, 2),
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': (
                round(self.error_count / self.request_count * 100, 2)
                if self.request_count > 0 else 0
            ),
            'llm_calls': self.llm_calls,
            'cache_hit_rate': round(cache_rate, 2),
        }


# Global metrics instance
metrics = HealthMetrics()


def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status."""
    return {
        'status': 'healthy',
        'environment': os.getenv('ENVIRONMENT', 'unknown'),
        'monitoring_enabled': SENTRY_ENABLED,
        'metrics': metrics.get_metrics(),
    }


# Export public API
__all__ = [
    'track_error',
    'track_event',
    'monitor_performance',
    'metrics',
    'get_health_status',
]
PYEOF

echo "✅ Monitoring module created"
echo ""

# Update app.py to use monitoring
echo "🔧 Integrating monitoring into Flask app..."
echo ""
echo "Add the following to backend/app.py:"
echo ""
cat <<'EOF'
# At the top of app.py, add:
from src.monitoring import track_error, monitor_performance, metrics, get_health_status

# Update health endpoint:
@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check with metrics."""
    try:
        return jsonify(get_health_status()), 200
    except Exception as e:
        track_error(e)
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# Add error handler:
@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler."""
    track_error(error)
    metrics.record_error()
    return jsonify({'error': 'Internal server error'}), 500
EOF

echo ""
echo "✅ Integration instructions provided"
echo ""

# Create cron job for backups
echo "⏰ Setting up automated backups..."
read -p "Enable daily automated backups? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    chmod +x scripts/backup-database.sh
    chmod +x scripts/restore-database.sh
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "0 2 * * * cd $(pwd) && ./scripts/backup-database.sh >> /var/log/backup.log 2>&1") | crontab -
    
    echo "✅ Backup cron job configured (runs daily at 2 AM)"
else
    echo "⏭️  Automated backups skipped"
fi
echo ""

# Test Sentry integration
if [ -n "$SENTRY_DSN" ]; then
    echo "🧪 Testing Sentry integration..."
    python3 -c "
from backend.src.monitoring import track_event, track_error
try:
    track_event('monitoring_setup', {'status': 'testing'})
    print('✅ Sentry test event sent')
except Exception as e:
    print(f'❌ Sentry test failed: {e}')
"
fi
echo ""

echo "=========================================="
echo "✅ Monitoring Setup Complete!"
echo "=========================================="
echo ""
echo "📊 What's configured:"
echo "  ✓ Sentry error tracking"
echo "  ✓ Performance monitoring"
echo "  ✓ Health check endpoint with metrics"
echo "  ✓ Automated database backups"
echo ""
echo "📝 Next steps:"
echo "  1. Update backend/app.py with monitoring code (see above)"
echo "  2. Test error tracking: curl http://localhost:5000/api/health"
echo "  3. Check Sentry dashboard: https://sentry.io"
echo "  4. Run manual backup: ./scripts/backup-database.sh"
echo "  5. Set up alerts in Sentry for critical errors"
echo ""
echo "📊 Monitoring dashboards:"
echo "  • Sentry: https://sentry.io"
echo "  • Health: http://localhost:5000/api/health"
echo "  • Metrics: http://localhost:5000/api/stats"
echo ""
