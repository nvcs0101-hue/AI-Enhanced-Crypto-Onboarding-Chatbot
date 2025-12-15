# 🏗️ System Architecture - Enhanced Chatbot

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                          │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  Web Widget  │   Telegram   │   Discord    │   REST API        │
│   (React)    │     Bot      │     Bot      │  (Third-party)    │
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬──────────┘
       │              │              │                 │
       └──────────────┴──────────────┴─────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Flask Backend    │
                    │   (API Gateway)    │
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌──────▼──────┐
│ Privacy Layer  │   │  Usage Tracker  │   │  Analytics  │
│ - PII Detection│   │ - Tier Limits   │   │ - Metrics   │
│ - Consent Mgmt │   │ - Billing       │   │ - Insights  │
└───────┬────────┘   └────────┬────────┘   └──────┬──────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   RAG Pipeline     │
                    │ - Query Processing │
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌──────▼──────────┐
│ Conv. Memory   │   │  LLM Manager    │   │   Validator     │
│ - Context Mgmt │   │ - Smart Routing │   │ - Safety Check  │
│ - Multi-turn   │   │ - Fallbacks     │   │ - Disclaimers   │
└───────┬────────┘   └────────┬────────┘   └──────┬──────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌──────▼──────────┐
│    Gemini      │   │     OpenAI      │   │   Perplexity    │
│  (FREE/Cheap)  │   │   (Quality)     │   │  (Real-time)    │
│  80% queries   │   │   15% queries   │   │   5% queries    │
└────────────────┘   └─────────────────┘   └─────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │    ChromaDB        │
                    │  Vector Storage    │
                    │  (Knowledge Base)  │
                    └────────────────────┘
```

---

## Component Details

### 1. User Interfaces Layer

**Web Chat Widget** (`frontend/src/ChatWidget.jsx`)
- React 18+ with styled-components
- Responsive design, typing indicators
- Multi-language selector
- Message history

**Telegram Bot** (`backend/telegram_bot.py`)
- Inline keyboards for language selection
- Command support: /start, /help, /language
- Group chat support
- Rate limiting per user

**Discord Bot** (`backend/discord_bot.py`)
- Slash commands: /ask, /help, /language
- Rich embeds with source citations
- Server-wide deployment
- Permission management

**REST API** (`backend/app.py`)
- OpenAPI/Swagger documentation
- CORS configuration
- Rate limiting
- JWT authentication (optional)

---

### 2. Backend Core Layer

**Flask API Gateway** (`backend/app.py`)
- Request routing
- Authentication/authorization
- Rate limiting (Flask-Limiter)
- Error handling
- CORS configuration
- Health checks

**Middleware Stack:**
```python
Request → Privacy Check → Usage Check → RAG Pipeline → Validation → Response
```

---

### 3. Enhancement Modules

#### Privacy Layer (`backend/src/privacy_compliance.py`)
```python
class PrivacyCompliance:
    - PII Detection (email, phone, crypto addresses)
    - Automatic redaction
    - GDPR consent management
    - Right to be forgotten
    - Data portability
    - Region-specific rules (EU vs US)
```

**Flow:**
1. Detect PII in query
2. Redact if found
3. Check consent (EU users)
4. Log for audit
5. Process cleaned query

#### Usage Tracker (`backend/src/usage_tracker.py`)
```python
class UsageTracker:
    - Three pricing tiers (FREE, PRO, ENTERPRISE)
    - Query counting per user
    - Monthly reset logic
    - Overage calculation
    - Tier upgrade management
    - Billing reports
```

**Flow:**
1. Check user's current tier
2. Verify query count < limit
3. Track query if allowed
4. Calculate overages
5. Generate monthly bill

#### Analytics System (`backend/src/analytics.py`)
```python
class Analytics:
    - Interaction logging
    - Query categorization (8 categories)
    - Cost tracking per provider
    - Response time monitoring
    - User insights
    - Top questions identification
    - Cache recommendations
```

**Tracked Metrics:**
- Total queries & success rate
- Average response time
- Cost per query & total spend
- Category distribution
- Language usage
- LLM provider utilization
- Cache hit rate

---

### 4. RAG Pipeline Layer

**Core Pipeline** (`backend/src/rag_pipeline.py`)

```python
def query_rag(user_question, language, user_id):
    # 1. Get conversation context
    context = conversation_memory.get_context(user_id)
    
    # 2. Retrieve relevant docs
    docs = vectorstore.similarity_search(user_question, k=5)
    
    # 3. Route to optimal LLM
    response = llm_manager.query_with_routing(
        query=user_question,
        context=context,
        documents=docs
    )
    
    # 4. Validate response
    validated = validator.validate(
        query=user_question,
        response=response,
        sources=docs
    )
    
    # 5. Log analytics
    analytics.log_interaction(...)
    
    # 6. Update conversation
    conversation_memory.add_message(user_id, "assistant", response)
    
    return validated
```

#### Conversation Memory (`backend/src/conversation_memory.py`)
```python
class ConversationMemory:
    conversations = {
        "user_id": {
            "messages": deque(maxlen=10),  # Last 10 messages
            "last_active": timestamp,
            "created_at": timestamp
        }
    }
    
    - TTL: 30 minutes
    - Auto-cleanup expired
    - Token-aware truncation (max 2000 tokens)
```

#### LLM Manager (`backend/src/llm_manager.py`)
```python
class LLMManager:
    def calculate_complexity_score(query) -> int:
        # Score 1-10 based on:
        - Length (words)
        - Technical terms
        - Question complexity
        - Context requirements
    
    def _select_provider(query) -> LLMProvider:
        score = calculate_complexity_score(query)
        
        if score < 4:
            return GEMINI       # FREE, 80% of queries
        elif score < 7:
            return OPENAI       # Quality, 15% of queries
        else:
            return PERPLEXITY   # Real-time data, 5% of queries
    
    def query_with_routing(query, context, docs):
        provider = _select_provider(query)
        
        try:
            return _query_provider(provider, ...)
        except Exception:
            # Fallback chain
            for fallback in [OPENAI, GEMINI, PERPLEXITY]:
                try:
                    return _query_provider(fallback, ...)
                except:
                    continue
            
            raise AllProvidersFailedError()
```

**Provider Selection Logic:**

| Complexity Score | Provider | Reasoning | Cost |
|-----------------|----------|-----------|------|
| 1-3 (Simple) | Gemini | Fast, free, sufficient | $0 |
| 4-6 (Moderate) | OpenAI | Balanced quality/cost | $0.0002 |
| 7-10 (Complex) | Perplexity | Real-time, comprehensive | $0.0003 |

#### Response Validator (`backend/src/response_validator.py`)
```python
class ResponseValidator:
    DANGER_PHRASES = [
        "guaranteed returns",
        "100% safe",
        "no risk",
        "definitely will",
        ...
    ]
    
    def validate(query, response, sources):
        warnings = []
        
        # 1. Check dangerous claims
        if contains_danger_phrases(response):
            warnings.append("Unrealistic financial claims")
            response = tone_down_response(response)
        
        # 2. Add disclaimers
        if is_financial_advice(query):
            response += FINANCIAL_DISCLAIMER
        
        # 3. Check source citations
        if not references_sources(response, sources):
            warnings.append("No source citations")
        
        # 4. Calculate confidence
        confidence = calculate_confidence(response, sources)
        
        return {
            'answer': response,
            'validation': {
                'is_safe': len(warnings) == 0,
                'warnings': warnings,
                'confidence_score': confidence
            }
        }
```

---

### 5. LLM Provider Layer

**OpenAI GPT-4o-mini**
- Cost: $0.15/1M input tokens
- Quality: 10/10
- Speed: 8/10
- Use case: Complex queries requiring accuracy

**Google Gemini Pro**
- Cost: FREE (with limits)
- Quality: 7/10
- Speed: 9/10
- Use case: Simple queries, high volume

**Perplexity API**
- Cost: $0.20/1M tokens
- Quality: 9/10
- Speed: 7/10
- Use case: Real-time data, research queries

**Fallback Chain:**
```
Primary (selected) → OpenAI → Gemini → Perplexity → Error
```

---

### 6. Knowledge Base Layer

**ChromaDB** (`backend/data/chroma_db/`)
```python
vectorstore = Chroma(
    collection_name="crypto_docs",
    embedding_function=HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    ),
    persist_directory="./data/chroma_db"
)
```

**Document Processing:**
1. Load .md files from `data/docs/`
2. Split into chunks (500 chars, 50 overlap)
3. Generate embeddings
4. Store in ChromaDB
5. Build index

**Retrieval:**
```python
# Semantic search (k=5 most relevant)
docs = vectorstore.similarity_search(query, k=5)

# Each doc contains:
{
    'content': "...",
    'source': "ethereum-staking.md",
    'metadata': {...}
}
```

---

## Request Flow (End-to-End)

### Example: User asks "How to stake ETH?"

```
1. USER INTERFACE
   └─> Web/Telegram/Discord receives query

2. FLASK API GATEWAY
   └─> POST /api/chat
       Body: {"message": "How to stake ETH?", "language": "en"}

3. PRIVACY LAYER
   ├─> Check for PII → None detected
   └─> Check consent (if EU) → OK

4. USAGE TRACKER
   ├─> Get user tier → FREE (100 queries/month)
   ├─> Check count → 45/100 used
   └─> Allow query ✓

5. RAG PIPELINE
   ├─> Get conversation context → "Previous: What is Ethereum?"
   └─> Vector search → 5 relevant docs about staking

6. LLM MANAGER
   ├─> Calculate complexity → Score: 5 (moderate)
   ├─> Select provider → OpenAI (quality needed)
   └─> Query with context → "Staking allows you to..."

7. RESPONSE VALIDATOR
   ├─> Check dangerous phrases → None
   ├─> Add financial disclaimer → ✓
   ├─> Calculate confidence → 85%
   └─> Return validated response

8. ANALYTICS
   └─> Log interaction:
       - Category: "staking"
       - Provider: "openai"
       - Cost: $0.0002
       - Response time: 2.1s

9. CONVERSATION MEMORY
   └─> Store message pair:
       - User: "How to stake ETH?"
       - Assistant: "Staking allows you to..."

10. RESPONSE TO USER
    └─> JSON:
        {
          "answer": "Staking allows you to earn rewards...[DISCLAIMER]",
          "sources": [...],
          "language": "en",
          "validation": {
            "is_safe": true,
            "confidence_score": 85
          }
        }
```

**Total time:** ~2.5 seconds  
**Cost:** $0.0002 (OpenAI)  
**If simple query:** Would use Gemini → $0 cost

---

## Data Flow Diagram

```
┌──────────────┐
│     User     │
└──────┬───────┘
       │
       │ "How to stake ETH?"
       ▼
┌──────────────────────┐
│  Privacy Compliance  │─────► PII Detection
└──────┬───────────────┘       Consent Check
       │
       │ Cleaned query
       ▼
┌──────────────────────┐
│   Usage Tracker      │─────► Check tier limit
└──────┬───────────────┘       Update count
       │
       │ Authorized
       ▼
┌──────────────────────┐
│ Conversation Memory  │─────► Get last 10 messages
└──────┬───────────────┘       Format context
       │
       │ Context: "User asked about Ethereum..."
       ▼
┌──────────────────────┐
│    ChromaDB Vector   │─────► Semantic search
│       Search         │       Return top 5 docs
└──────┬───────────────┘
       │
       │ Docs: [ethereum-staking.md, rewards.md, ...]
       ▼
┌──────────────────────┐
│    LLM Manager       │─────► Calculate complexity: 5
│  (Smart Routing)     │       Select provider: OpenAI
└──────┬───────────────┘       Fallback: Gemini
       │
       │ Provider: OpenAI
       ▼
┌──────────────────────┐
│   OpenAI GPT-4o      │─────► Generate response
└──────┬───────────────┘       Using context + docs
       │
       │ "Staking allows you to earn rewards by..."
       ▼
┌──────────────────────┐
│  Response Validator  │─────► Check danger phrases
│                      │       Add disclaimers
└──────┬───────────────┘       Calculate confidence
       │
       │ Validated + Disclaimer
       ▼
┌──────────────────────┐
│     Analytics        │─────► Log: category, cost, time
└──────┬───────────────┘       Update metrics
       │
       │ Logged
       ▼
┌──────────────────────┐
│ Conversation Memory  │─────► Store Q&A pair
└──────┬───────────────┘       Update timestamp
       │
       │ Stored
       ▼
┌──────────────────────┐
│   Return to User     │
└──────────────────────┘
   JSON Response:
   {
     "answer": "...[DISCLAIMER]",
     "sources": [...],
     "validation": {
       "is_safe": true,
       "confidence": 85
     }
   }
```

---

## Performance Characteristics

### Latency Breakdown

| Component | Average Time | Optimization |
|-----------|-------------|--------------|
| Privacy check | 10ms | Regex-based, fast |
| Usage check | 5ms | In-memory dict |
| Vector search | 100ms | ChromaDB index |
| LLM query | 1000-2000ms | Depends on provider |
| Validation | 50ms | Pattern matching |
| Analytics log | 20ms | Async write |
| **Total** | **1.2-2.2s** | Acceptable |

### Throughput

- **Current**: 50-100 concurrent requests
- **Bottleneck**: LLM API rate limits
- **Scaling**: Add more LLM providers

### Cost Per Query

| Scenario | Provider | Cost |
|----------|----------|------|
| Simple query | Gemini | $0.00 |
| Moderate query | OpenAI | $0.0002 |
| Complex query | Perplexity | $0.0003 |
| **Average** | **Mixed** | **$0.00006** |

With 80% Gemini routing:
- 80,000 queries @ $0 = $0
- 15,000 queries @ $0.0002 = $3
- 5,000 queries @ $0.0003 = $1.50
- **Total: $4.50 per 100K queries**

vs. All OpenAI:
- 100,000 queries @ $0.0002 = $20
- **Savings: 77.5%**

---

## Scaling Considerations

### Horizontal Scaling

```
           ┌──────────────┐
           │ Load Balancer│
           └───────┬──────┘
                   │
         ┌─────────┼─────────┐
         │         │         │
    ┌────▼───┐ ┌──▼────┐ ┌──▼────┐
    │ Flask  │ │ Flask │ │ Flask │
    │ App 1  │ │ App 2 │ │ App 3 │
    └────┬───┘ └───┬───┘ └───┬───┘
         │         │         │
         └─────────┼─────────┘
                   │
         ┌─────────▼─────────┐
         │  Shared ChromaDB  │
         │  (or Pinecone)    │
         └───────────────────┘
```

### Caching Layer

Add Redis for:
- Frequent queries (top 20%)
- Session management
- Rate limiting
- Analytics aggregation

```python
@cache.memoize(timeout=3600)  # 1 hour
def query_rag(query, language):
    ...
```

**Expected impact:**
- 50% latency reduction
- 80% cost reduction on cached queries
- Better user experience

---

## Security Architecture

### Authentication Flow

```
User → API Gateway → JWT Validation → Rate Limit → Process Request
                         │
                         ├─> Valid → Continue
                         └─> Invalid → 401 Unauthorized
```

### Data Protection

1. **At Rest:**
   - Encrypted ChromaDB storage
   - Hashed user IDs (SHA-256)
   - Secure environment variables

2. **In Transit:**
   - HTTPS/TLS 1.3
   - Encrypted websocket connections

3. **In Use:**
   - PII redaction before LLM processing
   - No logging of sensitive data
   - Automatic session expiration

---

## Monitoring & Observability

### Health Checks

```bash
GET /api/health
{
  "status": "healthy",
  "components": {
    "database": "ok",
    "llm_providers": {
      "openai": "ok",
      "gemini": "ok",
      "perplexity": "ok"
    },
    "cache": "ok"
  },
  "uptime_seconds": 86400
}
```

### Metrics

```python
# Prometheus format
chatbot_queries_total{tier="free", provider="gemini"} 85432
chatbot_query_duration_seconds{provider="openai"} 1.25
chatbot_costs_total_usd 127.50
chatbot_cache_hit_rate 0.65
```

### Alerting

```yaml
alerts:
  - name: HighErrorRate
    condition: error_rate > 5%
    action: email_ops_team
  
  - name: LowCacheHitRate
    condition: cache_hit_rate < 50%
    action: investigate_queries
  
  - name: BudgetExceeded
    condition: daily_cost > $100
    action: throttle_requests
```

---

## Future Enhancements

1. **Real-time Streaming**: WebSocket for live responses
2. **Voice Interface**: Speech-to-text integration
3. **Custom Models**: Fine-tuned models for specific projects
4. **Advanced Caching**: Redis with intelligent invalidation
5. **A/B Testing**: Experiment with different prompts
6. **Customer Success Dashboard**: Usage insights for users
7. **Auto Knowledge Updates**: Periodic doc refresh
8. **Sentiment Analysis**: Track user satisfaction
9. **Fraud Detection**: Identify abuse patterns
10. **Multi-tenancy**: Separate knowledge bases per project

---

This architecture provides:
- ✅ High availability through redundancy
- ✅ Cost optimization through smart routing
- ✅ Scalability through stateless design
- ✅ Security through layered defense
- ✅ Compliance through privacy-first approach
- ✅ Observability through comprehensive metrics
