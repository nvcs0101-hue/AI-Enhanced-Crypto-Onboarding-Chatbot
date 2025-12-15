# Load Testing with k6

## Installation

```bash
# macOS
brew install k6

# Ubuntu/Debian
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Docker
docker pull grafana/k6
```

## Running Tests

### Local Testing
```bash
# Test against local server
k6 run tests/load/k6-test.js

# Test against staging
k6 run -e BASE_URL=https://staging.yourdomain.com tests/load/k6-test.js

# Quick smoke test (10 users, 1 minute)
k6 run --vus 10 --duration 1m tests/load/k6-test.js
```

### Production-Like Testing
```bash
# 100 concurrent users for 10 minutes
k6 run --vus 100 --duration 10m tests/load/k6-test.js

# Spike test (sudden traffic spike)
k6 run --stage 1m:10 --stage 30s:200 --stage 2m:10 tests/load/k6-test.js
```

### With Docker
```bash
docker run --network=host -v $PWD:/tests grafana/k6 run /tests/tests/load/k6-test.js
```

## Interpreting Results

### Key Metrics

- **http_req_duration**: Request duration (target: p95 < 2s)
- **http_req_failed**: Failed requests (target: < 1%)
- **http_reqs**: Total requests per second
- **vus**: Virtual users (concurrent users)

### Success Criteria

✅ **Pass:**
- 95th percentile response time < 2 seconds
- Error rate < 1%
- No service crashes
- Database connections stable

❌ **Fail:**
- Response times > 5 seconds
- Error rate > 5%
- Service crashes or OOM errors
- Database connection pool exhaustion

## Continuous Load Testing

Add to CI/CD pipeline:

```yaml
# .github/workflows/load-test.yml
- name: Run load tests
  run: |
    k6 run --quiet tests/load/k6-test.js
```

## Monitoring During Load Tests

Watch these metrics:
- CPU usage (target: < 80%)
- Memory usage (target: < 85%)
- Database connections (target: < 80 of 100)
- Redis memory (target: < 200MB)
- Error rate in Sentry

```bash
# Monitor with Docker
docker stats

# Monitor with htop
htop
```
