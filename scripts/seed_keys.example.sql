-- Create api_keys table if not exists
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key_string VARCHAR(256) UNIQUE NOT NULL,
    engine VARCHAR(64) DEFAULT 'gemini',
    key_type VARCHAR(32) DEFAULT 'free',
    status VARCHAR(32) DEFAULT 'active',
    cooldowns_json JSONB DEFAULT '{}'::jsonb,
    models_mapping JSONB DEFAULT '{}'::jsonb,
    total_requests INT DEFAULT 0,
    failed_requests INT DEFAULT 0,
    last_used_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() AT TIME ZONE 'utc'),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() AT TIME ZONE 'utc')
);

CREATE INDEX IF NOT EXISTS idx_api_keys_engine ON api_keys(engine);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_type ON api_keys(key_type);
CREATE INDEX IF NOT EXISTS idx_api_keys_status ON api_keys(status);

-- Seed keys template
INSERT INTO api_keys (key_string, engine, key_type, status, models_mapping)
VALUES 
  ('YOUR_API_KEY_1', 'gemini', 'free', 'active', '{"name": "Key #1"}'::jsonb)
ON CONFLICT (key_string) DO NOTHING;
