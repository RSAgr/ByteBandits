-- all-MiniLM-L6-v2, used by data/load_embeddings_to_postgres.py, emits 384 dimensions.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS instruction_documents (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    instruction TEXT NOT NULL,
    instruction_embedding vector(384) NOT NULL,
    code TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    content_hash TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS instruction_documents_metadata_idx
    ON instruction_documents USING GIN (metadata);

-- Exact nearest-neighbour search works immediately. Add an HNSW index after the
-- collection becomes large enough for approximate vector search to be useful.
-- CREATE INDEX instruction_documents_embedding_hnsw_idx
--     ON instruction_documents USING hnsw (instruction_embedding vector_cosine_ops);
