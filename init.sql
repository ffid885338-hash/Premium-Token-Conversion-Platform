CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    oauth_provider VARCHAR(50) NOT NULL,
    oauth_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    username VARCHAR(100) NOT NULL,
    telegram_username VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key VARCHAR(64) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 60,
    total_calls INTEGER DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversion_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    telegram_username VARCHAR(100),
    conversion_type VARCHAR(50) NOT NULL,
    input_token_hash VARCHAR(64) NOT NULL,
    result_token_hint VARCHAR(32) NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_config (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed default administrative settings
INSERT INTO system_config (key, value) VALUES ('maintenance_mode', 'false') ON CONFLICT DO NOTHING;
INSERT INTO system_config (key, value) VALUES ('telegram_alerts_active', 'true') ON CONFLICT DO NOTHING;