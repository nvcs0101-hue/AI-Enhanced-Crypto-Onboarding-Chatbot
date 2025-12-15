# API Documentation

## Overview

The AI-Enhanced Crypto Onboarding Chatbot provides a REST API for integrating chat functionality into your applications.

**Base URL:** `http://localhost:5000` (development)

## Authentication

Currently, the API does not require authentication. For production deployments, consider implementing API key authentication.

## Rate Limiting

- **Rate Limit:** 20 requests per minute per IP address
- **Status Code:** 429 (Too Many Requests)

## Endpoints

### 1. Health Check

Check the health status of the API.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-15T10:30:00Z",
  "service": "crypto-onboarding-chatbot"
}
```

---

### 2. Get Supported Languages

Retrieve a list of supported languages.

**Endpoint:** `GET /api/languages`

**Response:**
```json
{
  "languages": [
    {"code": "en", "name": "English"},
    {"code": "es", "name": "Español"},
    {"code": "zh", "name": "中文"},
    {"code": "hi", "name": "हिन्दी"},
    {"code": "fr", "name": "Français"},
    {"code": "de", "name": "Deutsch"},
    {"code": "ja", "name": "日本語"},
    {"code": "ko", "name": "한국어"},
    {"code": "pt", "name": "Português"},
    {"code": "ru", "name": "Русский"}
  ]
}
```

---

### 3. Chat

Send a message to the chatbot and receive an AI-generated response.

**Endpoint:** `POST /api/chat`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "How do I stake Ethereum?",
  "language": "en",
  "return_sources": false
}
```

**Parameters:**
- `message` (string, required): User's question (max 1000 characters)
- `language` (string, optional): Language code for response (default: "en")
- `return_sources` (boolean, optional): Include source documents (default: false)

**Success Response (200 OK):**
```json
{
  "response": "To stake Ethereum, follow these steps:\n\n1. Choose a staking method...",
  "status": "success",
  "language": "English",
  "timestamp": "2025-12-15T10:30:00Z"
}
```

**With Sources:**
```json
{
  "response": "To stake Ethereum...",
  "status": "success",
  "language": "English",
  "timestamp": "2025-12-15T10:30:00Z",
  "sources": [
    {
      "content": "Staking involves...",
      "metadata": {
        "source": "staking_guide.md"
      }
    }
  ]
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "No message provided",
  "details": "The 'message' field is required and cannot be empty",
  "status": "error"
}
```

**Error Response (429 Too Many Requests):**
```json
{
  "error": "Rate limit exceeded",
  "details": "Too many requests. Please try again later.",
  "status": "error"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Internal server error",
  "details": "An unexpected error occurred while processing your request",
  "status": "error",
  "timestamp": "2025-12-15T10:30:00Z"
}
```

## Code Examples

### Python

```python
import requests

url = "http://localhost:5000/api/chat"
headers = {"Content-Type": "application/json"}
data = {
    "message": "How do I set up MetaMask?",
    "language": "en"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print(result["response"])
```

### JavaScript

```javascript
const url = 'http://localhost:5000/api/chat';

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'How do I bridge tokens to Polygon?',
    language: 'en'
  })
})
  .then(response => response.json())
  .then(data => console.log(data.response))
  .catch(error => console.error('Error:', error));
```

### cURL

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is impermanent loss?",
    "language": "en",
    "return_sources": true
  }'
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Endpoint doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

## Best Practices

1. **Handle Errors Gracefully:** Always check the status code and handle errors appropriately
2. **Respect Rate Limits:** Implement exponential backoff if rate limited
3. **Validate Input:** Ensure messages are within the character limit
4. **Use Appropriate Language Codes:** Use the codes from the `/api/languages` endpoint
5. **Implement Timeouts:** Set reasonable timeout values for API requests

## CORS

The API supports Cross-Origin Resource Sharing (CORS) for the following origins:
- `http://localhost:3000` (development)
- Your production domain (configure in `.env`)

## Webhooks (Coming Soon)

Webhook support for real-time notifications will be added in a future release.

## Support

For API support, please:
- Check the [main documentation](../README.md)
- Open an issue on GitHub
- Contact support@example.com
