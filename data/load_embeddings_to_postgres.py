"""Embed JSONL instruction/code records and store them in PostgreSQL.

Input records need an ``instruction`` field and may use either ``code`` or the
legacy ``output`` field. Every remaining field, including GitHub and website
URLs, is stored in the metadata JSONB column.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_INPUT = Path(__file__).with_name("samples.jsonl")


def connection_string() -> str:
    return (
        f"postgresql://{os.environ.get('POSTGRES_USER', 'algomate')}:"
        f"{os.environ.get('POSTGRES_PASSWORD', 'change-me-for-production')}@"
        f"{os.environ.get('POSTGRES_HOST', 'localhost')}:"
        f"{os.environ.get('POSTGRES_PORT', '5432')}/"
        f"{os.environ.get('POSTGRES_DB', 'algomate')}"
    )


def vector_literal(values) -> str:
    """Format a pgvector literal without losing the embedding precision."""
    return "[" + ",".join(str(float(value)) for value in values) + "]"


def document_hash(instruction: str, code: Optional[str]) -> str:
    payload = f"{instruction}\n{code or ''}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_records(input_file: Path):
    with input_file.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                print(
                    f"Skipping malformed JSON on line {line_number}: {error.msg} "
                    f"(column {error.colno})"
                )
                continue
            instruction = record.pop("instruction", "").strip()
            code = record.pop("code", record.pop("output", None))
            record.pop("embedding", None)  # Recreate it so every vector uses MODEL_NAME.
            if not instruction:
                print(f"Skipping line {line_number}: no instruction")
                continue
            yield instruction, code, record


def main():
    parser = argparse.ArgumentParser(description="Load instruction embeddings into PostgreSQL.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="JSONL dataset to import")
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()

    # Match Docker Compose: this project's .env must win over unrelated shell
    # variables inherited from the machine.
    load_dotenv(Path(__file__).parents[1] / ".env", override=True)
    records = list(read_records(args.input))
    if not records:
        print("No valid records found.")
        return

    print(f"Loading {MODEL_NAME} and embedding {len(records)} records...")
    model = SentenceTransformer(MODEL_NAME)
    # Initialize PyTorch before importing psycopg-binary. On some Windows
    # installations their native dependencies otherwise conflict.
    model.encode(["embedding warm-up"], batch_size=1)
    import psycopg

    statement = """
        INSERT INTO instruction_documents
            (instruction, instruction_embedding, code, metadata, content_hash)
        VALUES (%s, %s::vector, %s, %s::jsonb, %s)
        ON CONFLICT (content_hash) DO UPDATE SET
            instruction_embedding = EXCLUDED.instruction_embedding,
            metadata = EXCLUDED.metadata,
            updated_at = now()
    """
    with psycopg.connect(connection_string()) as connection:
        with connection.cursor() as cursor:
            for start in range(0, len(records), args.batch_size):
                batch = records[start : start + args.batch_size]
                embeddings = model.encode(
                    [record[0] for record in batch], batch_size=args.batch_size
                )
                rows = [
                    (
                        instruction,
                        vector_literal(embedding),
                        code,
                        json.dumps(metadata),
                        document_hash(instruction, code),
                    )
                    for (instruction, code, metadata), embedding in zip(batch, embeddings)
                ]
                cursor.executemany(statement, rows)
                print(f"Imported {min(start + len(batch), len(records))}/{len(records)} records")
        connection.commit()
    print(f"Upserted {len(records)} records into instruction_documents.")


if __name__ == "__main__":
    main()
