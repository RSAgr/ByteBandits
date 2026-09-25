"""Hybrid PostgreSQL retrieval over the existing instruction_documents table."""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

MODEL_NAME = "all-MiniLM-L6-v2"


def connection_string() -> str:
    """Use the same PostgreSQL environment variables as the ingestion script."""
    return (
        f"postgresql://{os.environ.get('POSTGRES_USER', 'algomate')}:"
        f"{os.environ.get('POSTGRES_PASSWORD', 'change-me-for-production')}@"
        f"{os.environ.get('POSTGRES_HOST', 'localhost')}:"
        f"{os.environ.get('POSTGRES_PORT', '5432')}/"
        f"{os.environ.get('POSTGRES_DB', 'algomate')}"
    )


def search_knowledge(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Rank documents using PostgreSQL lexical and pgvector cosine similarity."""
    query = query.strip()
    if not query:
        raise ValueError("query must not be empty")
    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20")

    load_dotenv(Path(__file__).parents[1] / ".env", override=False)

    # Load the same sentence-transformer used to create the stored vectors.
    from sentence_transformers import SentenceTransformer
    import psycopg

    model = SentenceTransformer(MODEL_NAME)
    embedding = model.encode(query).tolist()
    vector = "[" + ",".join(str(float(value)) for value in embedding) + "]"

    statement = """
        WITH query AS (
            SELECT websearch_to_tsquery('english', %s) AS terms
        ),
        lexical AS (
            SELECT d.id,
                   ts_rank_cd(to_tsvector('english', d.instruction || ' ' || COALESCE(d.code, '')),
                              query.terms) AS bm25_score
            FROM instruction_documents AS d CROSS JOIN query
            WHERE to_tsvector('english', d.instruction || ' ' || COALESCE(d.code, '')) @@ query.terms
            ORDER BY bm25_score DESC
            LIMIT %s
        ),
        semantic AS (
            SELECT id,
                   1 - (instruction_embedding <=> %s::vector) AS semantic_score
            FROM instruction_documents
            ORDER BY instruction_embedding <=> %s::vector
            LIMIT %s
        ),
        candidates AS (
            SELECT id FROM lexical UNION SELECT id FROM semantic
        )
        SELECT d.id, d.instruction, d.code, d.metadata,
               COALESCE(l.bm25_score, 0) AS bm25_score,
               COALESCE(s.semantic_score, 0) AS semantic_score,
               (COALESCE(l.bm25_score / NULLIF(max(l.bm25_score) OVER (), 0), 0) * 0.5
                + COALESCE(s.semantic_score, 0) * 0.5) AS score
        FROM candidates c
        JOIN instruction_documents d ON d.id = c.id
        LEFT JOIN lexical l ON l.id = d.id
        LEFT JOIN semantic s ON s.id = d.id
        ORDER BY score DESC, d.id
        LIMIT %s
    """
    with psycopg.connect(connection_string(), row_factory=psycopg.rows.dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(statement, (query, top_k, vector, vector, top_k, top_k))
            return cursor.fetchall()
