-- Ensure pgvector extension is enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify vector extension
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'vector'
    ) THEN
        RAISE NOTICE 'pgvector extension successfully initialized.';
    END IF;
END $$;
