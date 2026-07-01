-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify version
SELECT extversion FROM pg_extension WHERE extname = 'vector';

-- Documents table (Voyage 3-large = 1024 dim)
CREATE TABLE IF NOT EXISTS documents (
    id           BIGSERIAL PRIMARY KEY,
    source       VARCHAR(255)  NOT NULL,        -- e.g. 'depot_faq', 'product_catalog'
    content      TEXT          NOT NULL,
    metadata     JSONB         DEFAULT '{}',    -- flexible key-value
    embedding    vector(1024)  NOT NULL,
    created_at   TIMESTAMP     DEFAULT NOW(),
    updated_at   TIMESTAMP     DEFAULT NOW()
);

-- Index for cosine similarity search (matches Voyage output)
CREATE INDEX IF NOT EXISTS documents_embedding_idx 
    ON documents 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Metadata filter indexes (production pattern)
CREATE INDEX IF NOT EXISTS documents_source_idx ON documents(source);
CREATE INDEX IF NOT EXISTS documents_metadata_gin_idx ON documents USING gin(metadata);

-- Verify
\d documents