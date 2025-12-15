import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Test configuration
export const options = {
  stages: [
    { duration: '1m', target: 10 },   // Ramp up to 10 users
    { duration: '3m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 100 },  // Ramp up to 100 users
    { duration: '3m', target: 50 },   // Ramp down to 50 users
    { duration: '1m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    'http_req_duration': ['p(95)<2000'], // 95% of requests must complete below 2s
    'http_req_failed': ['rate<0.01'],     // Less than 1% of requests should fail
    'errors': ['rate<0.05'],              // Less than 5% error rate
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

// Test queries
const testQueries = [
  "What is Bitcoin?",
  "How do I buy cryptocurrency?",
  "What is blockchain?",
  "How do I create a wallet?",
  "What is Ethereum?",
  "How do I stake crypto?",
  "What are gas fees?",
  "How do I secure my wallet?",
];

export default function () {
  // Health check
  const healthRes = http.get(`${BASE_URL}/api/health`);
  check(healthRes, {
    'health check status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // Chat query
  const query = testQueries[Math.floor(Math.random() * testQueries.length)];
  const payload = JSON.stringify({
    message: query,
    language: 'en',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const chatRes = http.post(`${BASE_URL}/api/chat`, payload, params);
  
  const chatCheck = check(chatRes, {
    'chat status is 200': (r) => r.status === 200,
    'chat response has answer': (r) => JSON.parse(r.body).answer !== undefined,
    'chat response time < 5s': (r) => r.timings.duration < 5000,
  });
  
  if (!chatCheck) {
    errorRate.add(1);
  }

  sleep(2);
}

export function handleSummary(data) {
  return {
    'load-test-results.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
