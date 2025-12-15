-- PostgreSQL Database Initialization Script
-- Creates tables for analytics and usage tracking

-- Analytics table for query tracking
CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,
    category VARCHAR(100),
    response_time_ms INTEGER,
    llm_provider VARCHAR(50),
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 6),
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',
    platform VARCHAR(50)  -- telegram, discord, web
);

-- Usage tracking table
CREATE TABLE IF NOT EXISTS usage_tracking (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    tier VARCHAR(20) DEFAULT 'FREE',
    monthly_queries INTEGER DEFAULT 0,
    monthly_tokens INTEGER DEFAULT 0,
    monthly_cost DECIMAL(10, 2) DEFAULT 0.00,
    total_queries INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10, 2) DEFAULT 0.00,
    reset_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversation history table
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- user, assistant
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255)
);

-- Privacy consent table (GDPR compliance)
CREATE TABLE IF NOT EXISTS user_consent (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    consent_given BOOLEAN DEFAULT false,
    consent_date TIMESTAMP,
    data_retention_days INTEGER DEFAULT 365,
    marketing_consent BOOLEAN DEFAULT false,
    analytics_consent BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cache performance tracking
CREATE TABLE IF NOT EXISTS cache_stats (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) NOT NULL,
    hit_count INTEGER DEFAULT 0,
    miss_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp);
CREATE INDEX IF NOT EXISTS idx_analytics_category ON analytics(category);
CREATE INDEX IF NOT EXISTS idx_usage_user_id ON usage_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_consent_user_id ON user_consent(user_id);

-- Create views for common queries
CREATE OR REPLACE VIEW daily_analytics AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total_queries,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(response_time_ms) as avg_response_time_ms,
    SUM(tokens_used) as total_tokens,
    SUM(cost_usd) as total_cost,
    COUNT(CASE WHEN success = false THEN 1 END) as error_count
FROM analytics
GROUP BY DATE(timestamp)
ORDER BY date DESC;

CREATE OR REPLACE VIEW llm_provider_stats AS
SELECT 
    llm_provider,
    COUNT(*) as query_count,
    AVG(response_time_ms) as avg_response_time,
    SUM(tokens_used) as total_tokens,
    SUM(cost_usd) as total_cost,
    COUNT(CASE WHEN success = false THEN 1 END) as error_count
FROM analytics
WHERE llm_provider IS NOT NULL
GROUP BY llm_provider;

CREATE OR REPLACE VIEW user_tier_distribution AS
SELECT 
    tier,
    COUNT(*) as user_count,
    AVG(monthly_queries) as avg_monthly_queries,
    SUM(monthly_cost) as total_monthly_revenue
FROM usage_tracking
GROUP BY tier;

-- Function to automatically reset monthly usage
CREATE OR REPLACE FUNCTION reset_monthly_usage()
RETURNS void AS $$
BEGIN
    UPDATE usage_tracking
    SET 
        monthly_queries = 0,
        monthly_tokens = 0,
        monthly_cost = 0.00,
        reset_date = CURRENT_DATE
    WHERE reset_date < DATE_TRUNC('month', CURRENT_DATE);
END;
$$ LANGUAGE plpgsql;

-- Seed some test data for staging
INSERT INTO usage_tracking (user_id, tier, monthly_queries, total_queries) VALUES
    ('test_free_user', 'FREE', 15, 150),
    ('test_pro_user', 'PRO', 450, 2500),
    ('test_enterprise_user', 'ENTERPRISE', 8500, 45000)
ON CONFLICT (user_id) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Database initialization complete';
    RAISE NOTICE 'Tables created: analytics, usage_tracking, conversations, user_consent, cache_stats';
    RAISE NOTICE 'Views created: daily_analytics, llm_provider_stats, user_tier_distribution';
    RAISE NOTICE 'Test users seeded: test_free_user, test_pro_user, test_enterprise_user';
END $$;
